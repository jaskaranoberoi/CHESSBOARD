function ChessBoard_Creation() 
{
    //Python Script will be called that will give FEN pos
    //FEN = Image_Detection.py 
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

    FEN = "1rb1kb2/p1ppppp1/1p2q1np/1rn4P/4P3/2NB1Q2/PPPPNPP1/R1KB2R1 w KQkq - 0 1";
    let count=0;
    let count_slash = 8;
    let temp = String.fromCharCode(97);
    let j = 0;

    for(let i = 0; i < FEN.length; i++)
    {
        let Comp_Id = temp + count_slash;  // Use `count_slash` for rows instead of `i`
        
        if(FEN[i] == "/")
        {
            count_slash--;  // Move to the next row
            j = 0; 
            temp = String.fromCharCode(97);  
            continue;
        }
        else if(FEN[i] == " " && count_slash == 1)
        {
            break;
        }
        else if(FEN[i] == "P")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♙";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(FEN[i] == "R")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♖";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(FEN[i] == "N")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♘";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(FEN[i] == "B")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♗";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(FEN[i] == "Q")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♕";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(FEN[i] == "K")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♔";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(FEN[i] == "p")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♟";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(FEN[i] == "r")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♜";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(FEN[i] == "n")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♞";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(FEN[i] == "b")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♝";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(FEN[i] == "q")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♛";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(FEN[i] == "k")
        {
            let element1 = document.getElementById(Comp_Id);
            element1.innerHTML = "♚";
            j++;
            temp = String.fromCharCode(97 + j);
        }
        else if(parseInt(FEN[i]) > 0)
        {
            let emptySquares = parseInt(FEN[i]);
            while(emptySquares > 0)
            {
                j++;
                temp = String.fromCharCode(97 + j);
                emptySquares--; 
            }
        }
    }
}

function LoadPlayVsComputer(url) {
    window.location.href = url;
}
// This function will be called when the user clicks the "Hint" button
function getBestMove() {
    let fen = getFENFromBoard(); // Get the FEN string from the current board
    fetch('/getBestMove', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fen: fen }), // Send FEN to server
    })
    .then(response => response.json())
    .then(data => {
        let bestMove = data.bestMove; // Get best move from server response
        highlightBestMove(bestMove);  // Implement this to highlight the move on the board
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
