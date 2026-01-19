let arr1 = new Array(128);
let piece_moved = '';
let piece_captured = '';
let castling = '';
let no_of_rooks = 0;
let currentTurn = 'white'; // Track whose turn it is

let castling_rights = "KQkq";
let Move_count = 0;
let Temp_Move_Count = 0;
let Half_Move_count = 0;

let old_arr = 
    [
        ['r','n','b','q','k','b','n','r'],
        ['p','p','p','p','p','p','p','p'],
        ['*','*','*','*','*','*','*','*'],
        ['*','*','*','*','*','*','*','*'],
        ['*','*','*','*','*','*','*','*'],
        ['*','*','*','*','*','*','*','*'],
        ['P','P','P','P','P','P','P','P'],
        ['R','N','B','Q','K','B','N','R']
    ];

let new_arr = 
    [
        ['r','n','b','q','k','b','n','r'],
        ['p','p','p','p','p','p','p','p'],
        ['*','*','*','*','*','*','*','*'],
        ['*','*','*','*','*','*','*','*'],
        ['*','*','*','*','*','*','*','*'],
        ['*','*','*','*','*','*','*','*'],
        ['P','P','P','P','P','P','P','P'],
        ['R','N','B','Q','K','B','N','R']
    ];

let Prev_Fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
let Curr_Fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

// setInterval(() => {
//     document.querySelectorAll('.chess-piece').forEach(piece => {
//         CheckDraggable(piece);
//     });
// }, 1000); // Runs every 1 second

function initializeChessDragAndDrop() {
    document.querySelectorAll('.chess-piece').forEach(piece => {
        if (!piece.hasAttribute('data-listener')) {
            piece.setAttribute('data-listener', 'true');
            piece.addEventListener('dragstart', (event) => {
                event.target.classList.add('dragging');
            });

            piece.addEventListener('dragend', (event) => {
                event.target.classList.remove('dragging');
            });
        }
    });

    document.querySelectorAll('.chess-square').forEach(square => {
        if (!square.hasAttribute('data-listener')) {
            square.setAttribute('data-listener', 'true');
            square.addEventListener('dragover', (event) => {
                event.preventDefault();
            });

            square.addEventListener('drop', async (event) => { // Added async back
                event.preventDefault();
                const draggedPiece = document.querySelector('.dragging');
                if (draggedPiece) {
                    const targetTd = event.target.closest('td');
                    if (targetTd) {
                        const targetPiece = targetTd.querySelector('.chess-piece');
                        if (targetPiece) {
                            targetPiece.parentElement.removeChild(targetPiece);
                        }
                        draggedPiece.parentElement.removeChild(draggedPiece);
                        targetTd.appendChild(draggedPiece);

                        try {
                            let Temp_Half_Count = Half_Move_count;
                            var x = await checkIfCorrectPersonMoves();
                            console.log(x);
                            if (x === 0) {
                                revertbacktofen();
                            }

                            createchessboardarray();
                            console.log("Array:");
                            console.log(new_arr);
                            findthemove();
                            createfen();
                            var y = await checkvalidityofmove();
                            console.log(y);
                            if (y === 0) {
                                revertbacktofen();
                                Curr_Fen = Prev_Fen;
                                console.log("cuurent_fen" + Curr_Fen);
                                console.log("previous_fen" + Prev_Fen);
                                Half_Move_count = Temp_Half_Count;
                            } else {
                                send_data_to_database();
                            }
                        } catch (error) {
                            console.error("Error in async functions:", error);
                        }
                    }
                }
            });
        }
    });
}

// Call this function once to initialize the drag-and-drop behavior
initializeChessDragAndDrop();


function createchessboardarray() {
    for (let i = 0; i < 8; i++) {
        for (let j = 0; j < 8; j++) {
            const columnLetter = String.fromCharCode(97 + j);
            const rowNumber = 8 - i;
            const computedId = columnLetter + rowNumber;
            const element = document.getElementById(computedId);

            if (element) {
                const pieceElement = element.querySelector('.chess-piece');
                if (pieceElement) {
                    const piece = pieceElement.textContent.trim();

                    if (piece === '♙') {
                        new_arr[i][j] = 'P';
                    } else if (piece === '♖') {
                        new_arr[i][j] = 'R';
                    } else if (piece === '♗') {
                        new_arr[i][j] = 'B';
                    } else if (piece === '♘') {
                        new_arr[i][j] = 'N';
                    } else if (piece === '♕') {
                        new_arr[i][j] = 'Q';
                    } else if (piece === '♔') {
                        new_arr[i][j] = 'K';
                    } else if (piece === '♟') {
                        new_arr[i][j] = 'p';
                    } else if (piece === '♜') {
                        new_arr[i][j] = 'r';
                    } else if (piece === '♞') {
                        new_arr[i][j] = 'n';
                    } else if (piece === '♝') {
                        new_arr[i][j] = 'b';
                    } else if (piece === '♛') {
                        new_arr[i][j] = 'q';
                    } else if (piece === '♚') {
                        new_arr[i][j] = 'k';
                    }
                } else {
                    new_arr[i][j] = '*';
                }
            }
        }
    }
    console.log(new_arr);
}

function findthemove() {
    let Sq = [['', ''], ['', '']];
    let count = 0;
    piece_moved = '';
    piece_captured = '';
    castling = '';
    no_of_rooks = 0;

    for (let i = 0; i < 8; i++) {
        for (let j = 0; j < 8; j++) {
            if (new_arr[i][j] === 'r' || new_arr[i][j] === 'R') {
                no_of_rooks += 1;
            }

            if (new_arr[i][j] !== old_arr[i][j]) {
                if (count === 0) {
                    // Record start position of the move
                    Sq[count][0] = i;
                    Sq[count][1] = j;
                    count += 1;
                } else if (count === 1) {
                    // Record end position of the move
                    Sq[count][0] = i;
                    Sq[count][1] = j;
                    count += 1;
                }
            }

            // Detect Castling
            if (old_arr[i][j] === '*' && (new_arr[i][j] === 'K' || new_arr[i][j] === 'k')) {
                if (j === 2 && ((old_arr[i][0] === 'R' && new_arr[i][3] === 'R') || (old_arr[i][0] === 'r' && new_arr[i][3] === 'r'))) {
                    castling = (i === 0) ? 'O-O-O' : 'o-o-o';
                } else if (j === 6 && ((old_arr[i][7] === 'R' && new_arr[i][5] === 'R') || (old_arr[i][7] === 'r' && new_arr[i][5] === 'r'))) {
                    castling = (i === 0) ? 'O-O' : 'o-o';
                }
            }

            if (old_arr[i][j] === '*' && old_arr[i][j] !== new_arr[i][j]) {
                piece_moved = new_arr[i][j];
            } else if (old_arr[i][j] !== '*' && new_arr[i][j] !== '*' && old_arr[i][j] !== new_arr[i][j]) {
                piece_moved = new_arr[i][j];
                piece_captured = 'x';
            }
        }
    }

    console.log(Sq, piece_moved, piece_captured, castling_rights, no_of_rooks);
}

function createfen() {
    let fen = "";
    
    // Loop through each row of the board (new_arr is a 2D array)
    for (let row = 0; row < new_arr.length; row++) {
        let emptyCount = 0;

        // Loop through each column of the row
        for (let col = 0; col < new_arr[row].length; col++) {
            let piece = new_arr[row][col];

            if (piece === '*') {
                // Count empty squares
                emptyCount++;
            } else {
                if (emptyCount > 0) {
                    // Append the number of empty squares before adding the piece
                    fen += emptyCount;
                    emptyCount = 0;
                }
                // Append the piece to the FEN string
                fen += piece;
            }
        }

        if (emptyCount > 0) {
            fen += emptyCount;
        }

        if (row < new_arr.length - 1) {
            fen += "/";
        }
    }

    addothercomponents()
    
    // Add the active color ('w' for white to move, 'b' for black to move)
    // fen += " " + (currentTurn === "white" ? "w" : "b");
    // fen += " " + "b";
    if(Move_count%2===0)
    {
        fen += " " + "b";
    }
    else
    {
        fen += " " + "w";
    }

    // Add castling rights (e.g., "KQkq" or "-" if no rights)
    fen += " " + (castling_rights !== "" ? castling_rights : "-");

    // Add en passant target square (currently we assume no en passant available, so "-")
    fen += " -";

    // Add half-move clock (e.g., 0 if no captures or pawn moves)
    fen += " " + Half_Move_count;

    // Add full move number (starting with 1)
    //fen += " " + (Move_count + 1);
    if(Move_count%2===0)
    {
        if(Move_count === 0)
        {
            //Temp_Move_Count=1;
            fen += " " + 1;
        }
        else
        {
            fen += " " + Math.ceil((Move_count + 1) / 2);

        }
    }
    else
    {
        Temp_Move_Count=Temp_Move_Count+1;
        console.log("I was here");
        fen += " " + (((Move_count + 1)/2)+1);
    }
    console.log("Move_count" + Move_count);
    Curr_Fen = fen;
    console.log(Curr_Fen);
}


function addothercomponents()
{
    if (no_of_rooks < 4) {
        if (ChessBoard_Current[0][0] !== 'r') {
            castling_rights = castling_rights.replace("q", "");
        }
        if (ChessBoard_Current[0][7] !== 'r') {
            castling_rights = castling_rights.replace("k", "");
        }
        if (ChessBoard_Current[7][0] !== 'R') {
            castling_rights = castling_rights.replace("Q", "");
        }
        if (ChessBoard_Current[7][7] !== 'R') {
            castling_rights = castling_rights.replace("K", "");
        }
    }
    
    if (castling === "O-O" || castling === "O-O-O" || castling === "o-o" || castling === "o-o-o") {
        if (Move_count % 2 === 0) {
            castling_rights = castling_rights.replace("KQ", "");
        } else {
            castling_rights = castling_rights.replace("kq", "");
        }
    }
    else if (piece_moved === 'K')
    {
        castling_rights = castling_rights.replace("KQ", "");
    }
    else if (piece_moved === 'k') 
    {
        castling_rights = castling_rights.replace("kq", "");
    } 
    else if (piece_moved === 'r' && ((Sq[0][0] === 0 && Sq[0][1] === 0) || (Sq[1][0] === 0 && Sq[1][1] === 0)))
    {
        castling_rights = castling_rights.replace("q", "");
    } 
    else if (piece_moved === 'r' && ((Sq[0][0] === 0 && Sq[0][1] === 7) || (Sq[1][0] === 0 && Sq[1][1] === 7)))
    {
        castling_rights = castling_rights.replace("k", "");
    } 
    else if (piece_moved === 'R' && ((Sq[0][0] === 7 && Sq[0][1] === 0) || (Sq[1][0] === 7 && Sq[1][1] === 0)))
    {
        castling_rights = castling_rights.replace("Q", "");
    } 
    else if (piece_moved === 'R' && ((Sq[0][0] === 7 && Sq[0][1] === 7) || (Sq[1][0] === 7 && Sq[1][1] === 7)))
    {
        castling_rights = castling_rights.replace("K", "");
    }
    
    if (piece_moved === 'P' || piece_moved === 'p')
    {
        Half_Move_count = 0;
    } 
    else if (piece_captured === "x")
    {
        Half_Move_count = 0;
    }
    else {
        Half_Move_count += 1;
    }

}

async function checkvalidityofmove() {
    const Curr_fen = Curr_Fen;  // Assuming Curr_fen is a global variable
    console.log(Curr_fen);
    try {
        const response = await fetch('/checkvalid', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ Curr_fen: Curr_fen })
        });

        const result = await response.json();
        if (result.isValid) {
            console.log('Move is valid');
            return 1;
        } else {
            console.log('Move is invalid');
            return 0;
        }
    } catch (error) {
        console.error('Error:', error);
    }
}


async function fetchHighestMoveCount(gameCode) {
    try {
        console.log("Current Game Code: ", gameCode);
        const response = await fetch('/get_highest_move_count', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ gameCode: gameCode })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        if (Move_count === data.moveCount) { // Access moveCount from the returned object
            console.log("Move_count" + Move_count);
            console.log("data.moveCount" + data.moveCount);
            return;
        } else {
            Move_count = data.moveCount; // Update Move_count
            ChessBoard_Creation(data.fen); // Access fen from the returned object
            console.log("Move count updated from server: ", Move_count);
            Prev_Fen = Curr_Fen;
            Curr_Fen = data.fen;
            console.log("Fen updated from server: ", data.fen);
        }
    } catch (error) {
        console.error('Error fetching highest move count and FEN:', error);
        return null;
    }
}

async function checkIfCorrectPersonMoves() {
    try {
        const response = await fetch('/get_current_game_info', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Assuming you have a way to track move count
        const moveCount = data.moveCount;
        const currentPlayerColor = data.playerColor;
        Move_count = data.moveCount;

        // Determine whose move it is based on move count
        const isWhitesMove = moveCount % 2 === 0; // Even move count means white's turn
        const currentPlayer = isWhitesMove ? 'white' : 'black';

        // Check if the current player is the one making the move
        if (currentPlayer === currentPlayerColor) {
            console.log(`It's ${currentPlayerColor}'s turn to move.`);
            return 1;
        } else {
            console.log(`It's not ${currentPlayerColor}'s turn to move.`);
            return 0;
            // Optionally notify the player that it's not their turn
        }
    } catch (error) {
        console.error('Error fetching game info:', error);
    }
}


async function revertbacktofen() {
    try {
        const response = await fetch('/get_last_fen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log(data.fen);
        ChessBoard_Creation(data.fen); //Recreate the board.

        // Use setTimeout to ensure DOM updates before re-applying listeners
        // setTimeout(() => {
        //     CheckDraggable();
        // }, 0); // Execute immediately, but after the current call stack

        return data.fen || null;
    } catch (error) {
        console.error('Error fetching last FEN:', error);
    }
}



// 
async function ChessBoard_Creation(FEN) {
    if (!FEN) {
        console.error('No FEN received');
        return;
    }

    for (let i = 8; i >= 1; i--) {
        for (let j = 0; j < 8; j++) {
            const columnLetter = String.fromCharCode(97 + j);
            const rowNumber = i;
            const computedId = columnLetter + rowNumber;

            const element = document.getElementById(computedId);

            element.innerHTML = "";
        }
    }

    let count_slash = 8;
    let temp = String.fromCharCode(97);
    let j = 0;

    for (let i = 0; i < FEN.length; i++) {
        let Comp_Id = temp + count_slash;

        if (FEN[i] === "/") {
            count_slash--;
            j = 0;
            temp = String.fromCharCode(97);
            continue;
        } else if (FEN[i] === " " && count_slash === 1) {
            break;
        } else if (FEN[i] === "P") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♙</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "R") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♖</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "N") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♘</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "B") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♗</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "Q") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♕</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "K") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♔</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "p") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♟</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "r") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♜</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "n") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♞</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "b") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♝</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "q") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♛</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "k") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = `<div class="chess-piece" draggable="true">♚</div>`;
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (parseInt(FEN[i]) > 0) {
            let emptySquares = parseInt(FEN[i]);
            while (emptySquares > 0) {
                j++;
                temp = String.fromCharCode(97 + j);
                emptySquares--;
            }
        }
    }
    //CheckDraggable(); //Reapply the drag listeners.
    initializeChessDragAndDrop();
}



async function send_data_to_database() {
    console.log("Move Count= " + Move_count);
    console.log("Curr_Fen" + Curr_Fen);
    try {
        const response = await fetch('/SendingDataa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                Curr_Fen: Curr_Fen,      // Send Curr_Fen as is
                Move_count: Move_count+1 // Increment and send Move_count
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        console.log('Game created successfully');
    } catch (error) {
        console.error('Error requesting creategame:', error);
    }
}


let playerColor = '';
let gameCode = '';

const createGameButton = document.getElementById('createGameButton');
const joinGameButton = document.getElementById('joinGameButton');
const gameCodeContainer = document.getElementById('gameCodeContainer');
const gameCodeInput = document.getElementById('gameCodeInput');
const submitGameCodeButton = document.getElementById('submitGameCodeButton');

// Function to create a game
createGameButton.addEventListener('click', () => {
    document.getElementById('colorSelectionContainer').style.display = 'block'; // Show color selection

    // Add event listeners for color selection
    document.getElementById('whiteButton').onclick = () => {
        playerColor = 'white';
        startGame();
    };
    document.getElementById('blackButton').onclick = () => {
        playerColor = 'black';
        startGame();
    };
});

// Function to start the game after color selection
function startGame() {
    gameCode = generateGameCode(); // Generate a unique game code
    alert(`Game created! Your game code is: ${gameCode}, You are playing as ${playerColor}`); // Display the game code
    // Here you can implement logic to save the game code on the server or in a database
    senddata(gameCode, playerColor);
    document.getElementById("buttonContainer").style.display = "none";
    document.getElementById("colorSelectionContainer").style.display = "none";
    document.getElementById("gameCodeContainer").style.display = "none";
    
}

async function senddata(gameCode, playerColor) {
    try {
        const response = await fetch('/CreateGame', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                GameId: gameCode,     // Send gameCode as GameId
                PColor: playerColor   // Send playerColor as PColor
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        console.log('Game created successfully');
    } catch (error) {
        console.error('Error requesting creategame:', error);
    }
}




// Function to join a game
joinGameButton.addEventListener('click', () => {
    gameCodeContainer.style.display = 'block'; // Show the game code input
});

// Function to submit the game code
submitGameCodeButton.addEventListener('click', () => {
    gameCode = gameCodeInput.value;
    if (gameCode) {
        checkGameIdAndJoin(gameCode);

    } else {
        alert('Please enter a valid game code.');
    }
});

async function checkGameIdAndJoin(gameCode) {
    try {
        const response = await fetch('/JoinGame', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ GameId: gameCode })
        });

        const data = await response.json();
        gameCode = data;

        if (!response.ok) {
            throw new Error(data.message || 'Network response was not ok');
        }

        if (data.success) {
            console.log('Joined game successfully');
            document.getElementById("buttonContainer").style.display = "none";
            document.getElementById("colorSelectionContainer").style.display = "none";
            document.getElementById("gameCodeContainer").style.display = "none";
            
            // Add any additional actions here (e.g., redirect to the game page)
        } else {
            console.error('Game not found:', data.message);
            alert('Game ID does not exist');
        }
    } catch (error) {
        console.error('Error checking Game ID:', error);
    }
}


// Function to generate a unique game code (example implementation)
function generateGameCode() {
    return Math.random().toString(36).substring(2, 8).toUpperCase(); // Generates a random 6-character code
    
}

function LoadPlayVsComputer(url) {
    window.location.href = url;
}

setInterval(function() {
    fetchHighestMoveCount(gameCode);
}, 5000);

//CheckDraggable();
//setInterval(CheckDraggable,2000);
// setInterval(ChessBoard_Creation, 2000);
