const socket = io();

let username;

document.getElementById('join-btn').addEventListener('click', () => {
    username = document.getElementById('username').value;

    if (username) {
        socket.emit('join', {'username': username});
    }
});

socket.on('waiting', (data) => {
    document.getElementById('waiting-message').innerText = data.message;
});

socket.on('game_start', (data) => {
    document.getElementById('join-game').style.display = 'none';
    document.getElementById('game').style.display = 'block';
});

let selectedCard = null;

socket.on('update_hand', (data) => {
    const handDiv = document.getElementById('hand-cards');
    handDiv.innerHTML = '';

    data.hand.forEach(card => {
        const btn = document.createElement('button');
        btn.innerText = card;
        btn.dataset.cardValue = card_to_value(card); // Store the card value
        btn.classList.add('card-button');
        btn.addEventListener('click', () => {
            selectedCard = btn.dataset.cardValue;
            highlightSelectedCard(btn);
            socket.emit('select_card', {'username': username, 'card': selectedCard});
        });
        handDiv.appendChild(btn);
    });

    document.getElementById('your-hand').innerText = 'Your Hand:';
});

function highlightSelectedCard(selectedBtn) {
    const buttons = document.querySelectorAll('#hand-cards .card-button');
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
    selectedCard = null;
    document.getElementById('round-info').innerText = data.message;
    document.getElementById('scores').innerText = `Scores - ${data.player1}: ${data.scores[data.player1]} | ${data.player2}: ${data.scores[data.player2]}`;
});

socket.on('game_over', (data) => {
    if (data.accumulated_prizes && data.accumulated_prizes.length > 0) {
        alert(`Game Over! Winner: ${data.winner}\nUnclaimed Prizes: ${data.accumulated_prizes.join(', ')}`);
    } else {
        alert(`Game Over! Winner: ${data.winner}`);
    }
    location.reload();
});

socket.on('player_disconnected', (data) => {
    alert(data.message);
    location.reload();
});

socket.on('error', (data) => {
    alert(data.message);
});

function card_to_value(card) {
    if (card === 'A') return 1;
    if (card === 'J') return 11;
    if (card === 'Q') return 12;
    if (card === 'K') return 13;
    return parseInt(card);
}
