const socket = io();

let username;

document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    socket.on('update_hand', (data) => {
        const handCardsDiv = document.getElementById('hand-cards');
        if (!handCardsDiv) {
            console.error('hand-cards element not found in the DOM.'); // Debug log
            return;
        }
        handCardsDiv.innerHTML = ''; // Clear existing cards

        if (!data.hand || data.hand.length === 0) {
            console.error('Received an empty hand:', data); // Debug log
            return;
        }

        data.hand.forEach((card) => {
            const cardElement = document.createElement('div');
            cardElement.classList.add('card');
            cardElement.textContent = card;
            cardElement.addEventListener('click', () => {
                socket.emit('select_card', { card });
            });
            handCardsDiv.appendChild(cardElement);
        });

        console.log('Updated hand:', data.hand); // Debug log
    });

    socket.on('update_prize', (data) => {
        const prizeCardElement = document.getElementById('prize-card');
        const accumulatedPrizesElement = document.getElementById('accumulated-prizes');

        if (!prizeCardElement || !accumulatedPrizesElement) {
            console.error('Prize card or accumulated prizes elements are missing in the DOM.'); // Debug log
            return;
        }

        prizeCardElement.innerText = `Prize Card: ${data.prize_card}`;
        accumulatedPrizesElement.innerText = `Accumulated Prizes: ${data.accumulated_prizes.join(', ')}`;
        console.log('Updated prize card and accumulated prizes:', data); // Debug log
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

socket.on('update_hand', (data) => {
    const handCardsDiv = document.getElementById('hand-cards');
    handCardsDiv.innerHTML = ''; // Clear any existing cards

    if (!data.hand || data.hand.length === 0) {
        console.error('Received an empty hand:', data); // Debugging
        return;
    }

    data.hand.forEach((card) => {
        const cardElement = document.createElement('div');
        cardElement.classList.add('card'); // Add CSS styling class
        cardElement.textContent = card; // Display the card value
        cardElement.addEventListener('click', () => {
            socket.emit('select_card', { card });
        });
        handCardsDiv.appendChild(cardElement); // Add to the DOM
    });

    console.log('Updated hand:', data.hand); // Debugging
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
    const prizeCardElement = document.getElementById('prize-card');
    const accumulatedPrizesElement = document.getElementById('accumulated-prizes');

    if (data.prize_card === null) {
        console.error('Prize card is null:', data); // Debugging
        return;
    }

    prizeCardElement.innerText = `Prize Card: ${data.prize_card}`;
    accumulatedPrizesElement.innerText = `Accumulated Prizes: ${data.accumulated_prizes.join(', ')}`;
    console.log('Updated prize card and accumulated prizes:', data); // Debugging
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
