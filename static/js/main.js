// static/js/main.js

const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

let username;
let room;

document.getElementById('join-btn').addEventListener('click', () => {
    username = document.getElementById('username').value;
    room = document.getElementById('room').value;

    if (username && room) {
        socket.emit('join', {'username': username, 'room': room});
    }
});

socket.on('waiting', (data) => {
    document.getElementById('waiting-message').innerText = data.message;
});

socket.on('game_start', (data) => {
    document.getElementById('join-game').style.display = 'none';
    document.getElementById('game').style.display = 'block';
});

socket.on('update_hand', (data) => {
    const handDiv = document.getElementById('hand-cards');
    handDiv.innerHTML = '';

    data.hand.forEach(card => {
        const btn = document.createElement('button');
        btn.innerText = card;
        btn.addEventListener('click', () => {
            btn.disabled = true;
            socket.emit('play_card', {'username': username, 'room': room, 'card': card_to_value(card)});
        });
        handDiv.appendChild(btn);
    });

    document.getElementById('your-hand').innerText = 'Your Hand:';
});

socket.on('update_prize', (data) => {
    document.getElementById('prize-card').innerText = `Prize Card: ${data.prize_card}`;
});

socket.on('round_result', (data) => {
    document.getElementById('round-info').innerText = data.message;
    document.getElementById('scores').innerText = `Scores - ${data.player1}: ${data.scores[data.player1]} | ${data.player2}: ${data.scores[data.player2]}`;
});

socket.on('game_over', (data) => {
    alert(`Game Over! Winner: ${data.winner}`);
    location.reload();
});

function card_to_value(card) {
    if (card === 'A') return 1;
    if (card === 'J') return 11;
    if (card === 'Q') return 12;
    if (card === 'K') return 13;
    return parseInt(card);
}
