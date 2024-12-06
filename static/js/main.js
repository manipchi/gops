const socket = io();

let username;

document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    socket.on('update_hand', (data) => {
        console.log('Received update_hand event:', data); // Debug log
        const handCardsDiv = document.getElementById('hand-cards');
        handCardsDiv.innerHTML = ''; // Clear existing cards
    
        if (!data.hand || data.hand.length === 0) {
            console.error('Received an empty hand:', data); // Debug
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
    
        console.log('Updated hand displayed:', data.hand); // Debug log
    });
    

    socket.on('update_prize', (data) => {
        console.log('Received update_prize event:', data); // Debug log
        document.getElementById('prize-card').innerText = `Prize Card: ${data.prize_card}`;
        document.getElementById('accumulated-prizes').innerText = `Accumulated Prizes: ${data.accumulated_prizes.join(', ')}`;
    });
    
});

document.getElementById('return-home-btn').addEventListener('click', () => {
    // Redirect to home page
    window.location.href = "{{ url_for('index') }}";
});


document.getElementById('join-btn').addEventListener('click', () => {
    console.log('Join Game button clicked.'); // Debug
    socket.emit('join'); // Emit the event without sending a username
});


// Handle waiting message
socket.on('waiting', (data) => {
    document.getElementById('waiting-message').innerText = data.message;
});

// Start game
socket.on('game_start', (data) => {
    document.getElementById('join-game').style.display = 'none';
    document.getElementById('play-section').style.display = 'block';
    document.getElementById('game-over').style.display = 'none';
});


socket.on('update_hand', (data) => {
    console.log('Received update_hand event:', data); // Debug log
    const handCardsDiv = document.getElementById('hand-cards');
    handCardsDiv.innerHTML = ''; // Clear existing cards

    let selectedCard = null; // Track the currently selected card

    data.hand.forEach((card) => {
        const cardElement = document.createElement('div');
        cardElement.classList.add('card');
        cardElement.textContent = card;
    
        // Add click event for card selection
        cardElement.addEventListener('click', () => {
            if (selectedCard) {
                selectedCard.classList.remove('selected'); // Remove highlight from previously selected card
            }
            selectedCard = cardElement;
            cardElement.classList.add('selected'); // Highlight the current selection
            socket.emit('select_card', { card }); // Notify server of selected card
            console.log(`Selected card: ${card}`);
        });
    
        handCardsDiv.appendChild(cardElement);
    });
    

    console.log('Updated hand displayed:', data.hand); // Debug log
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
    console.log('Received update_prize event:', data); // Debug log

    const prizeCardElement = document.getElementById('prize-card');
    const accumulatedPrizesElement = document.getElementById('accumulated-prizes');

    if (!prizeCardElement || !accumulatedPrizesElement) {
        console.error('Prize card or accumulated prizes elements are missing in the DOM.');
        return;
    }

    prizeCardElement.innerText = `Prize Card: ${data.prize_card}`;
    accumulatedPrizesElement.innerText = `Accumulated Prizes: ${data.accumulated_prizes.join(', ')}`;
});



socket.on('round_result', (data) => {
    console.log('Round result received:', data);
    const roundInfo = document.getElementById('round-info');
    // Only show what the opponent played
    roundInfo.textContent = `${data.message} Opponent played ${data.opponent_card}.`;

    const scoresElement = document.getElementById('scores');
    let scoresText = "Scores: ";
    for (const [player, score] of Object.entries(data.scores)) {
        scoresText += `${player}: ${score} `;
    }
    scoresElement.textContent = scoresText.trim();
});

socket.on('game_over', (data) => {
    // Hide the play section (previously 'game')
    document.getElementById('play-section').style.display = 'none';
    
    // Show the game-over section (previously 'game-over')
    document.getElementById('game-over-section').style.display = 'block';
    
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
