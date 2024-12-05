const socket = io();

let username;

// Join game
document.getElementById('join-btn').addEventListener('click', () => {
    username = document.getElementById('username').value;

    if (username) {
        socket.emit('join', { username: username });
        document.getElementById('waiting-message').innerText = "Looking for a match...";
    }
});

// Handle waiting message
socket.on('waiting', (data) => {
    document.getElementById('waiting-message').innerText = data.message;
});

// Start game
socket.on('game_start', (data) => {
    document.getElementById('join-game').style.display = 'none';
    document.getElementById('game').style.display = 'block';
    document.getElementById('game-over').style.display = 'none';
});

// Handle player disconnection
socket.on('player_disconnected', (data) => {
    console.log("Player disconnected event received:", data.message);

    // Ensure the game screen is hidden
    document.getElementById('game').style.display = 'none';

    // Show the game-over screen
    const gameOverDiv = document.getElementById('game-over');
    const gameOverMessage = document.getElementById('game-over-message');
    gameOverDiv.style.display = 'block';
    gameOverMessage.innerText = data.message;

    console.log("Game-over screen displayed with message:", data.message);
});

// Return to home button functionality
document.getElementById('return-home-btn').addEventListener('click', () => {
    document.getElementById('game').style.display = 'none';
    document.getElementById('game-over').style.display = 'none';
    document.getElementById('join-game').style.display = 'block';
    document.getElementById('waiting-message').innerText = '';
});

// Card value conversion helper
function card_to_value(card) {
    if (card === 'A') return 1;
    if (card === 'J') return 11;
    if (card === 'Q') return 12;
    if (card === 'K') return 13;
    return parseInt(card);
}
