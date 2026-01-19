let playerColor = null;
let gameId = null;
let current = null;

async function setPlayerColor(color) {
    playerColor = color;
    console.log("Player Color: ", playerColor === 0 ? "White" : "Black");

    gameId = 'game_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
    console.log("Generated Game ID: ", gameId);

    document.getElementById('colorSelection').style.display = 'none';

    try {
        const response = await fetch('http://localhost:3000/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ playerColor }), 
        });

        const result = await response.json();
        console.log("Response from Node.js:", result);
    } catch (error) {
        console.error('Error:', error);
    }
}

async function fetchFEN() {
    try {
        const response = await fetch('http://localhost:3000/get_fen');
        const data = await response.json();

        if (response.ok) {
            return {
                fen: data.fen,
                move_count: data.move_count,
                pgn: data.pgn
            };
        } else {
            console.error('Error fetching FEN:', data.error);
            return null;
        }
    } catch (error) {
        console.error('Error fetching FEN:', error);
        return null;
    }
}

async function ChessBoard_Creation() {
    const data = await fetchFEN(); // Call fetchFEN and wait for it to complete

    if (data) {
        console.log('FEN:', data.fen);
        console.log('Move Count:', data.move_count);
        console.log('PGN:', data.pgn);
    } else {
        console.error('Failed to retrieve FEN data.');
    }
    var FEN = data.fen;
    var move_count = data.move_count;
    var pgn = data.pgn;
    current =   FEN
    // console.log(FEN)

    if (!FEN) {
        console.error('No FEN received');
        return;
    }
    // document.getElementById(move_count.toString()).style.display = 'block';
    document.getElementById(move_count.toString()).innerHTML = pgn;

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
            element1.innerHTML = "♙";
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "R") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♖";
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "N") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♘";
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "B") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♗";
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "Q") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♕";
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "K") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♔";
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "p") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♟";
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "r") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♜";
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "n") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♞";
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "b") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♝";
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "q") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♛";
            j++;
            temp = String.fromCharCode(97 + j);
        } else if (FEN[i] === "k") {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♚";
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
}

// Function to request undo
// Function to trigger the undo action
function triggerUndo() {
    fetch('/undo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({}) // Send an empty JSON object if no data is needed
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // No need to process the response if you don't need to use it
        console.log('Undo request was successful.');
    })
    .catch(error => {
        console.error('Error requesting undo:', error);
    });
}

async function triggerHint() {
    try {
        // Ensure the current FEN is set correctly before making the request
        if (!current) {
            console.error('Error: Current FEN is not available.');
            return;
        }

        const response = await fetch('/get_hint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fen: current }) // Ensure key is 'fen'
        });

        if (!response.ok) {
            // Fetch and log the error response body for debugging
            const errorData = await response.text();
            console.error('Error response:', errorData);
            throw new Error('Network response was not ok');
        }

        // Process the response to extract best move and FEN
        const data = await response.json();
        const { bestMove, fen } = data;

        console.log('Best Move:', bestMove);
        console.log('Updated FEN:', fen);

        const sq1 = bestMove.substring(0, 2);
        const sq2 = bestMove.substring(2, 4);

        const element1 = document.getElementById(sq1);
        const element2 = document.getElementById(sq2);

        if (element1 && element2) {
            const style1 = window.getComputedStyle(element1);
            const style2 = window.getComputedStyle(element2);

            // Get the background color
            const backgroundColor1 = style1.backgroundColor;
            const backgroundColor2 = style2.backgroundColor;

            // Temporarily change background color to 'red'
            element1.style.backgroundColor = 'red';
            element2.style.backgroundColor = 'red';

            setTimeout(() => {
                // Restore the original background color after 3 seconds
                element1.style.backgroundColor = backgroundColor1;
                element2.style.backgroundColor = backgroundColor2;
            }, 3000);
        } else {
            console.error('Error: Elements with IDs', sq1, 'or', sq2, 'not found.');
        }

        // Update the board or UI based on the best move and new FEN if necessary
        //current = fen; // Update the current FEN with the response
        
    } catch (error) {
        console.error('Error requesting hint:', error);
    }
}

async function triggerRedo() {
    fetch('stop_script', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({}) // Send an empty JSON object if no data is needed
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // No need to process the response if you don't need to use it
        console.log('Redo request was successful.');
        window.location.href = "/play";
        Chess_Starting_Position();
    })
    .catch(error => {
        console.error('Error requesting undo:', error);
    });
}

function Chess_Starting_Position()
{
    for (let i = 8; i >= 1; i--) 
        {
            for (let j = 0; j < 8; j++)
            {
                const columnLetter = String.fromCharCode(97 + j); // 'a' is 97 in ASCII
                const rowNumber = i; // Row number in the chessboard
                const computedId = columnLetter + rowNumber; // Generate the ID
    
                const element = document.getElementById(computedId);
    
                element.innerHTML = "";
            }
        }
    let k=0;
    for (k=1;k<=14;k++)
    {
        document.getElementById(k).innerHTML = "";
    }

}

ChessBoard_Creation();
setInterval(ChessBoard_Creation, 5000);

function LoadPlayVsComputer(url) {
    window.location.href = url;
}