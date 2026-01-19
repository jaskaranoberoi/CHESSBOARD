import numpy as np
from PossibleChessMoves import generate_legal_boards
from MoveValidator import is_legal_move, fen_to_array

# ---------- helper coercer (same as earlier, robust) ----------
def _coerce_candidate_to_8x8(cand_raw):
    if isinstance(cand_raw, (tuple, list)) and len(cand_raw) == 2:
        maybe = cand_raw[1]
    else:
        maybe = cand_raw

    # numpy array input
    if isinstance(maybe, np.ndarray):
        arr = maybe.astype(str)
        if arr.shape == (8, 8):
            return arr, None

    # list/tuple of 8 rows
    if isinstance(maybe, (list, tuple)):
        if len(maybe) == 8:
            rows = []
            for r in maybe:
                if isinstance(r, (list, tuple, np.ndarray)):
                    rowchars = [ (str(x)[0] if str(x) != '' else '*') for x in r ]
                    if len(rowchars) != 8:
                        return None, f"row-length {len(rowchars)} != 8"
                    rows.append(rowchars)
                else:
                    s = str(r).replace(" ", "")
                    if len(s) == 8:
                        rows.append(list(s))
                    else:
                        return None, f"row-string length {len(s)} != 8"
            return np.array(rows, dtype=str), None

    # string forms
    if isinstance(maybe, str):
        s = maybe.strip()
        if "/" in s:
            parts = s.split("/")
            if len(parts) == 8 and all(len(p) == 8 for p in parts):
                return np.array([list(p) for p in parts], dtype=str), None
        if len(s) == 64:
            rows = [list(s[i*8:(i+1)*8]) for i in range(8)]
            return np.array(rows, dtype=str), None

    return None, "unsupported candidate format"

def _count_mismatches(obs, cand):
    mismatches = 0
    for r in range(8):
        for c in range(8):
            if str(obs[r][c]) != str(cand[r][c]):
                mismatches += 1
    return mismatches

def _gained_coords(prev, obs):
    coords = []
    for r in range(8):
        for c in range(8):
            if prev[r][c] == '*' and str(obs[r][c]) != '*':
                coords.append((r,c))
    return coords

def _has_kings(arr):
    flat = arr.flatten()
    return np.count_nonzero(flat == 'K') == 1 and np.count_nonzero(flat == 'k') == 1

# ---------- robust, verbose validate_or_recover ----------
def validate_or_recover(fen_before, fen_after, observed_array, turn,
                        mismatch_tolerance=3, require_valid_kings=True, debug=True):
    """
    Returns ("valid", None) or ("recovered", candidate_np) or ("invalid", None).
    When debug=True the function prints step-by-step diagnostics so you can see what's happening.
    """
    if debug:
        print("=== validate_or_recover START ===")
        print("Prev FEN:", fen_before)
        print("New FEN: ", fen_after)
        print("Turn provided:", turn)
        print("Mismatch tolerance:", mismatch_tolerance)
        print()

    # 1) Strict validation using your move validator
    try:
        strict_ok = is_legal_move(fen_before, fen_after)
    except Exception as e:
        strict_ok = False
        if debug:
            print("is_legal_move raised an exception (continuing to recovery):", repr(e))

    if strict_ok:
        if debug:
            print("Strict validator PASSED -> move is valid.")
            print("=== validate_or_recover END (valid) ===")
        return "valid", None

    if debug:
        print("Strict validator did NOT pass. Entering recovery mode.")
        print()

    # 2) Prepare arrays
    try:
        prev = fen_to_array(fen_before)   # your function -> numpy 8x8 expected
    except Exception as e:
        if debug:
            print("ERROR parsing prev_fen with fen_to_array:", repr(e))
        return "invalid", None

    # observed coercion
    observed = np.array(observed_array, dtype=str)
    if observed.shape != (8,8):
        coerced_obs, reason = _coerce_candidate_to_8x8(observed_array)
        if coerced_obs is None:
            if debug:
                print("Observed array could not be coerced to 8x8:", reason)
                print("Observed raw value:", observed_array)
                print("=== validate_or_recover END (invalid) ===")
            return "invalid", None
        observed = coerced_obs

    if debug:
        print("Prev board (from FEN -> array):")
        print(prev)
        print("Observed board (coerced to 8x8):")
        print(observed)
        print()

    # 3) Generate candidates
    candidates_raw = None
    try:
        candidates_raw = generate_legal_boards(prev, turn)
    except Exception as e:
        if debug:
            print("generate_legal_boards raised exception:", repr(e))
        return "invalid", None

    if candidates_raw is None:
        if debug:
            print("generate_legal_boards returned None.")
        return "invalid", None

    if debug:
        print(f"generate_legal_boards produced {len(candidates_raw)} raw candidates (may include move tuples).")
        print()

    # 4) Coerce, sanitize, score each candidate
    scored = []
    skipped = []
    gained_coords = _gained_coords(prev, observed)

    for idx, cand_raw in enumerate(candidates_raw):
        cand_np, reason = _coerce_candidate_to_8x8(cand_raw)
        if cand_np is None:
            skipped.append((idx, reason))
            continue
        if require_valid_kings and not _has_kings(cand_np):
            skipped.append((idx, "missing/extra kings"))
            continue

        support = 0
        for (r,c) in gained_coords:
            if cand_np[r,c] == observed[r,c]:
                support += 1
        mism = _count_mismatches(observed, cand_np)
        scored.append((support, mism, cand_np, cand_raw, idx))

    if debug:
        print("Candidates coerced:", len(scored))
        print("Candidates skipped:", len(skipped))
        if len(skipped) and debug:
            print("First skipped reasons (up to 5):")
            for s in skipped[:5]:
                print(" idx", s[0], "reason:", s[1])
        print()

    if not scored:
        if debug:
            print("No valid candidates after coercion/sanity checks.")
            print("=== validate_or_recover END (invalid) ===")
        return "invalid", None

    # pick best: maximize support then minimize mismatches
    scored.sort(key=lambda t: (-t[0], t[1]))
    best_support, best_mism, best_np, best_raw, best_idx = scored[0]

    if debug:
        print("Top 5 scored candidates (support, mismatches, idx):")
        for i, (s, m, arr, raw, idx) in enumerate(scored[:5]):
            print(f"#{i}: support={s}, mismatches={m}, raw_idx={idx}")
            print(arr)
            print("---")
        print("Selected best candidate index:", best_idx)
        print("Best support:", best_support, "Best mismatches:", best_mism)
        print()

    if best_mism <= mismatch_tolerance:
        if debug:
            print("Best candidate within mismatch tolerance. Returning recovered board (numpy 8x8).")
            print("=== validate_or_recover END (recovered) ===")
        return "recovered", best_np

    if debug:
        print(f"Best candidate mismatches ({best_mism}) exceed tolerance ({mismatch_tolerance}).")
        print("=== validate_or_recover END (invalid) ===")
    return "invalid", None
