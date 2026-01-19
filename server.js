const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql2');
const path = require('path');
const { spawn } = require('child_process');
const { platform } = require('process');
const session = require('express-session');
const MySQLStore = require('express-mysql-session')(session);
const util = require('util');
const exec = util.promisify(require('child_process').exec);

const app = express();
const port = 3000;

app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false } // Set to true if using HTTPS
}));

let PlayerID = null;

const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'Apple@1824',
    database: 'userdb'
});

db.connect((err) => {
    if (err) {
        console.error('Error connecting to MySQL:', err);
        throw err;
    }
    console.log('Connected to MySQL Database.');
});

// Middleware to parse request bodies
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// ********** ROUTES FOR SIGNUP AND LOGIN **********
app.get('/signup', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'signup.html'));
});

app.post('/signup', (req, res) => {
    const { username, password, email, phone_number } = req.body;

    const sql = 'INSERT INTO users (username, password, email, phone_number) VALUES (?, ?, ?, ?)';
    db.query(sql, [username, password, email, phone_number], (err, result) => {
        if (err) throw err;
        console.log('User data inserted:', result);
        res.redirect('/chess1.html');
    });
});

app.get('/get_id', (req, res) => {
    if (req.session.playerID) {
        res.status(200).json({
            Id: req.session.playerID // Return the username from session
        });
    } else {
        res.status(404).json({ error: 'ID not found' });
    }
});

app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.get('/PlayOnline-loggedin', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'PlayOnline-Loggedin.html'));
});

app.get('/PlayvsComputer-loggedin', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'PlayvsComputer-Loggedin.html'));
});

app.get('/chess1-loggedin', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'Chess1-Loggedin.html'));
});

app.get('/How-To-Play', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'How_To_Play.html'));
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const sql = 'SELECT * FROM users WHERE username = ?';

    db.query(sql, [username], (err, results) => {
        if (err) {
            console.error('Error querying the database:', err);
            return res.redirect('/login?error=Database%20error');
        }

        if (results.length > 0) {
            const user = results[0];

            if (password == user.password) {
                // Set session variable
                req.session.playerID = username; // Store username in session
                return res.redirect('/chess1-loggedin');
            } else {
                return res.redirect('/login?error=Invalid%20credentials');
            }
        } else {
            return res.redirect('/login?error=No%20user%20found%20with%20that%20username');
        }
    });
});

const isAuthenticated = (req, res, next) => {
    if (req.session.playerID) {
        next(); // User is authenticated, proceed to the next middleware
    } else {
        res.redirect('/login'); // Not authenticated, redirect to login
    }
};

app.get('/chess1-loggedin', isAuthenticated, (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'Chess1-Loggedin.html'));
});





// ********** ROUTES FOR FEN AND GAME MANAGEMENT **********
let currentFEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w - - 0 1"; // Default FEN
let previousFEN = currentFEN; // Track previous FEN
let moveCount = 0;
let pgn = '';
let playerColor = null;
let gameId = null;
let pythonProcess = null; // Store the reference to the Python process globally

app.post('/process', (req, res) => {
    const { playerColor: color } = req.body;
    playerColor = color;
    gameId = 'game_' + Date.now() + '_' + Math.floor(Math.random() * 1000);

    console.log("Player Color: ", playerColor === 0 ? "White" : "Black");
    console.log("Generated Game ID: ", gameId);

    pythonProcess = spawn('python', ['Chess_Move.py', playerColor]); // Store the Python process

    pythonProcess.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python script exited with code ${code}`);
    });

    // Insert initial game data into the database
    const sql = 'INSERT INTO game_records (game_id, fen, move_count) VALUES (?, ?, ?)';
    db.query(sql, [gameId, currentFEN, moveCount], (err, result) => {
        if (err) {
            console.error('Error inserting game data into database:', err);
            return res.status(500).json({ error: 'Database error' });
        }
        console.log('Game data inserted:', result);
        res.status(200).json({ message: 'Player color processed and game data stored successfully' });
    });
});

app.post('/CreateGame', (req, res) => {
    const { GameId, PColor } = req.body;
    const P_Id = req.session.playerID;
    
    const sql = 'INSERT INTO create_game VALUES (?, ?, ?)';
    
    db.query(sql, [P_Id, GameId, PColor], (err, result) => {
        if (err) {
            console.error('Error inserting into create_game:', err);
            return res.status(500).send('Database error');
        }
        res.status(200).send('Game created successfully');
    });
});

app.post('/JoinGame', (req, res) => {
    const { GameId } = req.body;
    const P_Id = req.session.playerID;  // This is Player 2's ID

    // Chess starting position FEN
    const startingFEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

    // Check if the GameId exists in the create_game table
    const checkGameQuery = 'SELECT * FROM create_game WHERE GameID = ?';

    db.query(checkGameQuery, [GameId], (err, result) => {
        if (err) {
            console.error('Error querying the database:', err);
            return res.status(500).json({ success: false, message: 'Database error' });
        }

        if (result.length === 0) {
            return res.status(404).json({ success: false, message: 'Game ID not found' });
        }

        console.log("Result from create_game:", result[0]);  // Log the full result for debugging

        const existingGame = result[0]; // Get the existing game details
        const P1_Id = existingGame.PlayerId; // Corrected to 'PlayerId'
        const P1_Color = existingGame.PlayerColor; // Corrected to 'PlayerColor'
        const P2_Color = (P1_Color === 'white') ? 'black' : 'white';  // Assign opposite color
        const MoveCount = 0;  // Start move count at 0

        console.log("P1_Id:", P1_Id);  // Log Player 1 ID

        // Insert the game details into the game_going_on table
        const insertGameGoingOnQuery = `
            INSERT INTO game_going_on (P1_Id, P2_Id, GameId, P1_Color, P2_Color, MoveCount, FEN)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        `;

        db.query(insertGameGoingOnQuery, [P1_Id, P_Id, GameId, P1_Color, P2_Color, MoveCount, startingFEN], (insertErr) => {
            if (insertErr) {
                console.error('Error inserting into game_going_on:', insertErr);
                return res.status(500).json({ success: false, message: 'Database error on insert' });
            }

            // After successfully inserting into game_going_on, delete the game from create_game
            const deleteGameQuery = 'DELETE FROM create_game WHERE GameID = ?';
            db.query(deleteGameQuery, [GameId], (deleteErr) => {
                if (deleteErr) {
                    console.error('Error deleting from create_game:', deleteErr);
                    return res.status(500).json({ success: false, message: 'Database error on delete' });
                }

                res.status(200).json({ success: true, message: 'Game started successfully', startingFEN });
            });
        });
    });
});


app.get('/get_current_game_info', (req, res) => {
    const playerId = req.session.playerID;
    if (!playerId) {
        return res.status(401).json({ error: 'User not authenticated' });
    }

    // Query to fetch the current game info for the player
    const sql = `SELECT GameId, 
                        MAX(MoveCount) AS MoveCount,
                        (CASE 
                            WHEN P1_Id = 'Test' THEN P1_Color 
                            ELSE P2_Color 
                        END) AS playerColor
                    FROM game_going_on 
                    WHERE P1_Id = 'Test' OR P2_Id = 'Test'
                    GROUP BY GameId, P1_Color, P2_Color, P1_Id, P2_Id`;


    db.query(sql, [playerId, playerId, playerId], (err, results) => {
        if (err) {
            console.error('Error querying the database:', err);
            return res.status(500).json({ error: 'Database error' });
        }

        if (results.length === 0) {
            return res.status(404).json({ error: 'Game not found' });
        }

        const gameInfo = results[0];
        res.status(200).json({
            playerId,
            gameId: gameInfo.GameId,
            moveCount: gameInfo.MoveCount,
            playerColor: gameInfo.playerColor
        });
    });
});

app.post('/checkvalid', async (req, res) => {
    const { Curr_fen } = req.body;
    const playerId = req.session.playerID; // Example player ID; this can be passed from the client if needed

    try {
        // Get the last FEN with the maximum move count for this player
        const [rows] = await db.promise().query(`
            SELECT FEN 
            FROM game_going_on 
            WHERE P1_Id = ? OR P2_Id = ?
            ORDER BY MoveCount DESC
            LIMIT 1
        `, [playerId, playerId]);
        

        const last_fen = rows.length > 0 ? rows[0].FEN : null;

        if (!last_fen) {
            return res.status(404).json({ error: 'No FEN found for this player' });
        }

        console.log("Last Fen = ", last_fen);
        console.log("Current Fen = ", Curr_fen);

        // Call the Python script with both the current and last FENs
        const pythonScript = `python check_validity.py "${last_fen}" "${Curr_fen}"`;

        exec(pythonScript, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error executing Python script: ${stderr}`);
                return res.status(500).json({ error: 'Error validating move' });
            }

            // Assuming Python script returns "valid" or "invalid"
            const isValid = stdout.trim() === 'valid';
            // if(isValid==false)
            // {
            //     Curr_fen = Prev_Fen;
            // }
            res.json({ isValid: isValid });
        });

    } catch (error) {
        console.error('Database error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/get_last_fen', (req, res) => {
    const playerId = req.session.playerID;

    const query = `
        SELECT FEN 
        FROM game_going_on 
        WHERE (P1_Id = ? OR P2_Id = ?) 
        ORDER BY MoveCount DESC 
        LIMIT 1;
    `;

    db.query(query, [playerId, playerId], (error, rows) => {
        if (error) {
            console.error('Database query error:', error);
            return res.status(500).send('Internal Server Error');
        }
        
        if (rows.length > 0) {
            res.json({ fen: rows[0].FEN });
        } else {
            res.json({ fen: null });
        }
    });
});

app.post('/SendingDataa', (req, res) => {
    // Step 1: Retrieve playerId from the session
    const playerId = req.session.playerID;

    // Step 2: Retrieve move_count and Curr_Fen from the request body
    const { Curr_Fen, Move_count } = req.body;

    // Step 3: Retrieve the game details where the player is either P1 or P2
    const gameQuery = `
        SELECT P1_Id, P2_Id, GameId, P1_Color, P2_Color 
        FROM game_going_on
        WHERE (p1_id = ? OR p2_id = ?)
    `;

    db.query(gameQuery, [playerId, playerId], (error, rows) => {
        if (error) {
            console.error('Database query error:', error);
            return res.status(500).send('Internal Server Error');
        }

        if (rows.length === 0) {
            return res.status(404).json({ error: 'No game found for this player' });
        }

        const game = rows[0];
        const { P1_Id, P2_Id, GameId, P1_Color, P2_Color } = game;

        // Step 4: Insert a new record into the table with all the values
        const insertQuery = `
            INSERT INTO game_going_on (P1_Id, P2_Id, GameId, P1_Color, P2_Color, MoveCount, FEN) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        `;

        const values = [P1_Id, P2_Id, GameId, P1_Color, P2_Color, Move_count, Curr_Fen];

        db.query(insertQuery, values, (error) => {
            if (error) {
                console.error('Database insertion error:', error);
                return res.status(500).send('Internal Server Error');
            }
            console.log("Here");
            // Step 5: Send success response
            res.json({ message: 'Move inserted successfully' });
        });
    });
});





// New endpoint to handle undo requests
app.post('/undo', (req, res) => {
    if (previousFEN) {
        // Revert to previous FEN state
        //currentFEN = previousFEN;

        undoFlag = true;

        // Respond to the client
        res.status(200).json({ undo: true, fen: currentFEN });

        // Update the previousFEN state
        //previousFEN = null; // Clear previousFEN or set to an appropriate value
    } else {
        res.status(400).json({ error: 'No previous FEN state to revert to' });
    }
});

// Variable to track undo state
let undoFlag = false;

// Endpoint to check if undo is needed
app.get('/check_undo', (req, res) => {
    res.json({ undo: undoFlag });
});

// Reset the undo flag
app.post('/reset_undo', (req, res) => {
    undoFlag = false;
    res.status(200).json({ message: 'Undo flag reset successfully' });
});

// New endpoint to kill the Python script
app.post('/stop_script', (req, res) => {
    if (pythonProcess) {
        pythonProcess.kill();  // Kill the Python process
        console.log('Python script terminated.');
        res.status(200).json({ message: 'Python script terminated' });
        currentFEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w - - 0 1";
        moveCount = 0;
        previousFEN = null;
    } else {
        res.status(400).json({ error: 'No Python script is running' });
    }
});

// Endpoint to update the FEN
app.post('/update_fen', (req, res) => {
    const { fen, pgn: newPgn, move_count } = req.body;

    console.log('Received data from client:');
    console.log('FEN:', fen);
    console.log('PGN:', newPgn);
    console.log('Move Count:', move_count);

    previousFEN = currentFEN; // Store the current FEN as previous before updating
    currentFEN = fen;       // Update the current FEN
    pgn = newPgn;           // Update the PGN
    moveCount = move_count; // Update the move count

    // Insert a new record for every move's FEN
    const sql = 'INSERT INTO game_records (game_id, fen, move_count) VALUES (?, ?, ?)';
    db.query(sql, [gameId, fen, move_count], (err, result) => {
        if (err) {
            console.error('Error inserting FEN into game_moves:', err);
            return res.status(500).json({ error: 'Database error' });
        }
        console.log('FEN stored for game move:', result);
        res.status(200).json({ message: 'FEN stored successfully for the move' });
    });
});

app.get('/get_fen', (req, res) => {
    if (currentFEN) {
        res.status(200).json({
            fen: currentFEN,
            move_count: moveCount,
            pgn: pgn
        });
    } else {
        res.status(404).json({ error: 'FEN not found' });
    }
});

// Serve the main HTML page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'Chess1.html'));
});

app.get('/play', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'PlayvsComputer.html'));
});

app.get('/PlayOnline', (req, res) =>{
    res.sendFile(path.join(__dirname, 'public', 'PlayOnline.html'))
});



// Endpoint to get hint
app.post('/get_hint', (req, res) => {
    const { fen } = req.body;

    if (!fen) {
        return res.status(400).json({ error: 'FEN not provided' });
    }

    currentFEN = fen;  // Update the global 'currentFEN'
    console.log(`Received FEN: ${currentFEN}`);

    // Spawn the Python process and pass the FEN as an argument
    const python = spawn('python', ['get_best_move.py', currentFEN]);

    let pythonOutput = '';

    python.stdout.on('data', (data) => {
        pythonOutput += data.toString();  // Accumulate data from Python process
    });

    python.stderr.on('data', (data) => {
        console.error(`Error from Python script: ${data}`);
        if (!res.headersSent) {
            return res.status(500).send('Error getting hint');
        }
    });

    python.on('close', (code) => {
        if (code !== 0) {
            if (!res.headersSent) {
                return res.status(500).json({ error: 'Python script exited with error' });
            }
        }s

        const [bestMove, updatedFen] = pythonOutput.trim().split(';');  // Assuming output format "bestMove;FEN"
        if (!bestMove || !updatedFen) {
            return res.status(500).json({ error: 'Invalid output from Python script' });
        }

        // Send the response after everything is done
        if (!res.headersSent) {
            return res.json({ bestMove: bestMove, fen: updatedFen });
        }
    });
});


app.post('/get_highest_move_count', (req, res) => {
    const { gameCode } = req.body;

    const sql = `
        SELECT FEN, MoveCount AS moveCount
        FROM game_going_on
        WHERE GameId = ? AND MoveCount = (SELECT MAX(MoveCount) FROM game_going_on WHERE GameId = ?)
    `;

    db.query(sql, [gameCode, gameCode], (err, results) => {
        if (err) {
            console.error('Error fetching highest move count and FEN:', err);
            return res.status(500).json({ error: 'Database error' });
        }

        if (results.length > 0) {
            res.json({ moveCount: results[0].moveCount || 0, fen: results[0].FEN });
        } else {
            res.json({ moveCount: 0, fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" });
        }
    });
});


//Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});

// app.listen(port, '0.0.0.0', () => {
//     console.log(`Server is running on http://0.0.0.0:${port}`);
// });