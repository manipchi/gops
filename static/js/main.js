const socket = io();

let username;

document.addEventListener("DOMContentLoaded", () => {
    const socket = io(); // Connect to the WebSocket server

    document.getElementById('join-btn').addEventListener('click', () => {
        console.log('Attempting to join the game.'); // Debug
        socket.emit('join'); // No need to send a username
    });

    socket.on('waiting', (data) => {
        document.getElementById('waiting-message').innerText = data.message;
        console.log('Waiting message received:', data.message); // Debug
    });

    socket.on('game_start', (data) => {
        document.getElementById('join-game').style.display = 'none';
        document.getElementById('game').style.display = 'block';
        console.log('Game started with players:', data.players);
    });

    socket.on('error', (data) => {
        alert(data.message);
        console.log('Error message received:', data.message); // Debug
    });
});



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

// Update hand and other elements during the game
socket.on('update_hand', (data) => {
    const handDiv = document.getElementById('hand-cards');
    handDiv.innerHTML = '';

    data.hand.forEach(card => {
        const btn = document.createElement('button');
        btn.innerText = card;
        btn.dataset.cardValue = card_to_value(card);
        btn.classList.add('card-button');
        btn.addEventListener('click', () => {
            highlightSelectedCard(btn);
            socket.emit('select_card', { username: username, card: btn.dataset.cardValue });
        });
        handDiv.appendChild(btn);
    });

    document.getElementById('your-hand').innerText = 'Your Hand:';
});

// Highlight selected card
function highlightSelectedCard(selectedBtn) {
    const buttons = document.querySelectorAll('#hand-cards button');
    buttons.forEach(btn => {
        btn.classList.remove('selected');
    });
    selectedBtn.classList.add('selected');
}

socket.on('update_prize', (data) => {
    document.getElementById('prize-card').innerText = `Prize Card: ${data.prize_card}`;
    if (data.accumulated_prizes && data.accumulated_prizes.length > 0) {
        document.getElementById('accumulated-prizes').innerText = `Accumulated Prizes: ${data.accumulated_prizes.join(', ')}`;
    } else {
        document.getElementById('accumulated-prizes').innerText = 'Accumulated Prizes: None';
    }
});

socket.on('round_result', (data) => {
    const roundMessage = `${data.message}`;
    document.getElementById('round-info').innerText = roundMessage;
    document.getElementById('scores').innerText = `Your Score: ${data.scores[username]}`;

    // Reset card highlighting
    const buttons = document.querySelectorAll('#hand-cards button');
    buttons.forEach(btn => btn.classList.remove('selected'));
});


socket.on('game_over', (data) => {
    document.getElementById('game').style.display = 'none';
    document.getElementById('game-over').style.display = 'block';
    let gameOverMessage = `Game Over! Winner: ${data.winner}`;
    if (data.accumulated_prizes && data.accumulated_prizes.length > 0) {
        gameOverMessage += `\nUnclaimed Prizes: ${data.accumulated_prizes.join(', ')}`;
    }
    document.getElementById('game-over-message').innerText = gameOverMessage;
});


// Handle player disconnection
socket.on('player_disconnected', (data) => {
    document.getElementById('game').style.display = 'none';
    document.getElementById('game-over').style.display = 'block';
    document.getElementById('game-over-message').innerText = data.message;
});

// Return to home button functionality
document.getElementById('return-home-btn').addEventListener('click', () => {
    document.getElementById('game').style.display = 'none';
    document.getElementById('game-over').style.display = 'none';
    document.getElementById('join-game').style.display = 'block';
    document.getElementById('waiting-message').innerText = '';
});

socket.on('error', (data) => {
    alert(data.message); // Display the error message in an alert
});

// Card value conversion helper
function card_to_value(card) {
    if (card === 'A') return 1;
    if (card === 'J') return 11;
    if (card === 'Q') return 12;
    if (card === 'K') return 13;
    return parseInt(card);
}
