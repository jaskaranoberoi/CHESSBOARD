// game.js
const Chess = require('chess.js').Chess;
const game = new Chess();

// Function to make a move
function makeMove(move) {
    const result = game.move(move);
    return result ? game.fen() : 'Invalid move';
}

// Function to get the game state
function getGameState() {
    return game.fen();
}

// Function to get the game history
function getGameHistory() {
    return game.history();
}

// Function to undo a move
function undoMove() {
    game.undo();
    return game.fen();
}

// Export the functions
module.exports = {
    makeMove,
    getGameState,
    getGameHistory,
    undoMove
};
