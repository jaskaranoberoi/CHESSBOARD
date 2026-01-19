import numpy as np
from pathlib import Path
import torch
import cv2


def rotate_array_180(input_array):
    """
    Rotates a 2D numpy array by 180 degrees.
    """
    # Use np.rot90 with k=2 to perform two 90-degree counter-clockwise rotations.
    rotated_array = np.rot90(input_array, k=2)
    return rotated_array

# --- Model Loading ---
# Ensure the paths are correct for your system
model_ChessCorner = torch.hub.load(r'C:\Users\karan\yolov5', 'custom', path=r'C:\Users\karan\OneDrive\Desktop\ChessBoard_Final_LocalHost\Models\exp4\weights\best.pt', source='local')
model = torch.hub.load(r'C:\Users\karan\yolov5', 'custom', path=r"C:\Users\karan\OneDrive\Desktop\ChessBoard_Final_LocalHost\Models\BestModel\best.pt", source='local')


def get_chessboard11(PathOfImage):
    # --- Part 1 & 2: Corner Detection and Sorting ---
    model_ChessCorner.conf = 0.3
    Image_path = PathOfImage
    result_ChessCorner = model_ChessCorner(Image_path)
    detections_ChessCorner = result_ChessCorner.xyxy[0].cpu().numpy()
    
    if len(detections_ChessCorner) < 4:
        print("Error: Could not detect 4 corners of the chessboard.")
        return None

    Corner_Coordinates = []
    for detection in detections_ChessCorner:
        center_x = (detection[0] + detection[2]) / 2
        center_y = (detection[1] + detection[3]) / 2
        Corner_Coordinates.append([center_x, center_y])

    Corner_Coordinates_Array = np.array(Corner_Coordinates)
    s = Corner_Coordinates_Array.sum(axis=1)
    sorted_corners = np.zeros((4, 2), dtype="float32")
    sorted_corners[0] = Corner_Coordinates_Array[np.argmin(s)]
    sorted_corners[2] = Corner_Coordinates_Array[np.argmax(s)]
    diff = np.diff(Corner_Coordinates_Array, axis=1)
    sorted_corners[1] = Corner_Coordinates_Array[np.argmin(diff)]
    sorted_corners[3] = Corner_Coordinates_Array[np.argmax(diff)]
    
    # --- Part 3: Perspective Transform ---
    board_size = 800
    destination_points = np.array([
        [0, 0], [board_size - 1, 0],
        [board_size - 1, board_size - 1], [0, board_size - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(sorted_corners, destination_points)
    
    # --- Part 4: Piece Detection using Raw Model Output ---
    ChessBoard = np.full((8, 8), '*', dtype=str)
    results = model(Image_path)
    results.save() # Saves the annotated image from the run

    piece_centers = []
    piece_names_list = []
    
    # Access the raw detection tensor: [xmin, ymin, xmax, ymax, confidence, class_id]
    raw_detections = results.xyxy[0].cpu().numpy()

    # Set our own confidence threshold. Start low to catch everything.
    # You can tune this value (e.g., 0.2, 0.3, 0.4) to find the best balance.
    confidence_threshold = 0.35

    print(f"\nFound {len(raw_detections)} raw detections. Filtering with a {confidence_threshold} threshold...")

    for detection in raw_detections:
        confidence = detection[4]
        
        # Manually apply our confidence check
        if confidence >= confidence_threshold:
            xmin, ymin, xmax, ymax = detection[:4]
            class_id = int(detection[5])
            piece_name = model.names[class_id] # Get name from the model's class list
            
            height = ymax - ymin
            avg_x = (xmin + xmax) / 2
            avg_y = ymax - (height * 0.1) 
            
            piece_centers.append([avg_x, avg_y])
            piece_names_list.append(piece_name)
            
    if not piece_centers:
        print("No pieces were detected with the current confidence threshold.")
        return ChessBoard
        
    piece_centers_np = np.array(piece_centers, dtype="float32").reshape(-1, 1, 2)
    transformed_centers = cv2.perspectiveTransform(piece_centers_np, M)
    
    # --- Part 4.5: Visual Debugging ---
    original_image = cv2.imread(PathOfImage)
    warped_image = cv2.warpPerspective(original_image, M, (board_size, board_size))
    square_size = board_size / 8
    
    # Draw grid lines
    for i in range(1, 8):
        pos = int(i * square_size)
        cv2.line(warped_image, (0, pos), (board_size - 1, pos), (0, 255, 0), 2)
        cv2.line(warped_image, (pos, 0), (pos, board_size - 1), (0, 255, 0), 2)

    # Draw a circle at the transformed center of each detected piece
    for center in transformed_centers:
        tx, ty = int(center[0][0]), int(center[0][1])
        cv2.circle(warped_image, (tx, ty), 10, (0, 0, 255), -1)

    cv2.imwrite("warped_chessboard_with_debug.jpg", warped_image)
    print("Saved a debug view to 'warped_chessboard_with_debug.jpg'")

    # --- Part 5: Map Pieces to Board ---
    for i, center in enumerate(transformed_centers):
        tx, ty = center[0][0], center[0][1]
        col = int(tx // square_size)
        row = int(ty // square_size)

        if 0 <= row < 8 and 0 <= col < 8:
            piece_name = piece_names_list[i]
            piece_char = '?'
            if 'Black_rook' in piece_name: piece_char = 'r'
            elif 'Black_bishop' in piece_name: piece_char = 'b'
            elif 'Black_knight' in piece_name: piece_char = 'n'
            elif 'Black_pawn' in piece_name: piece_char = 'p'
            elif 'Black_queen' in piece_name: piece_char = 'q'
            elif 'Black_king' in piece_name: piece_char = 'k'
            elif 'White_pawn' in piece_name: piece_char = 'P'
            elif 'White_knight' in piece_name: piece_char = 'N'
            elif 'White_bishop' in piece_name: piece_char = 'B'
            elif 'White_king' in piece_name: piece_char = 'K'
            elif 'White_Queen' in piece_name: piece_char = 'Q'
            elif 'White_rook' in piece_name: piece_char = 'R'
            
            ChessBoard[row][col] = piece_char
    
    print("\nFinal Chessboard Configuration:")
    print(ChessBoard)
    rotated_180 = rotate_array_180(ChessBoard)
    print(rotated_180)
    return rotated_180


# # --- Main execution block ---
# img_path = r"C:\Users\karan\OneDrive\Desktop\C53.jpg"
# final_board = get_chessboard(img_path)
# if final_board is not None:
#     print("\nFunction finished successfully.")