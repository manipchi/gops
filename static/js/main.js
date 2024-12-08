const socket = io();

let username;

document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    // Helper function to toggle navigation links
    function toggleNavLinks(visible) {
        const navLinks = document.getElementById("nav-links");
        if (navLinks) {
            navLinks.style.display = visible ? "flex" : "none";
        }
    }

    // Update hand of cards
    socket.on('update_hand', (data) => {
        const handCardsDiv = document.getElementById('hand-cards');
        handCardsDiv.innerHTML = ''; // Clear existing cards
    
        if (!data.hand || data.hand.length === 0) {
            console.error('No cards received.');
            return;
        }
    
        data.hand.forEach((card) => {
            const cardElement = document.createElement('div');
            cardElement.classList.add('card');
            cardElement.textContent = card;
    
            // Add click event to select a card
            cardElement.addEventListener('click', () => {
                socket.emit('select_card', { card });
            });
    
            handCardsDiv.appendChild(cardElement);
        });
    });
    

    // Update prize card and accumulated prizes
    socket.on('update_prize', (data) => {
        const prizeCardElement = document.getElementById('prize-card');
        const accumulatedPrizesElement = document.getElementById('accumulated-prizes');
    
        if (prizeCardElement) {
            prizeCardElement.innerText = `Prize Card: ${data.prize_card}`;
        }
    
        if (accumulatedPrizesElement) {
            accumulatedPrizesElement.innerText = `Accumulated Prizes: ${data.accumulated_prizes.join(', ')}`;
        }
    });
    

    // Join Game button click event
    document.getElementById("join-btn").addEventListener("click", () => {
        console.log("Join Game button clicked."); // Debug
        socket.emit("join"); // Emit the event without sending a username
    });

    socket.on('waiting', (data) => {
        // Show the waiting message
        const waitingMessage = document.getElementById('waiting-message');
        if (waitingMessage) {
            waitingMessage.innerText = data.message;
        }
    });

    // Start game
    socket.on('game_start', (data) => {
        console.log('Game started with players:', data.players);
    
        // Hide the join game section
        const joinSection = document.getElementById('join-section');
        if (joinSection) {
            joinSection.style.display = 'none';
        }
    
        // Show the play section
        const playSection = document.getElementById('play-section');
        if (playSection) {
            playSection.style.display = 'block';
        }
    });
    

    // Round result
    socket.on("round_result", (data) => {
        console.log("Round result received:", data);
        const roundInfo = document.getElementById("round-info");
        roundInfo.textContent = `${data.message} Opponent played ${data.opponent_card}.`;

        const scoresElement = document.getElementById("scores");
        let scoresText = "Scores: ";
        for (const [player, score] of Object.entries(data.scores)) {
            scoresText += `${player}: ${score} `;
        }
        scoresElement.textContent = scoresText.trim();
    });

    // Game over
    socket.on("game_over", (data) => {
        console.log("Game over:", data); // Debug log
        document.getElementById("play-section").style.display = "none";
        document.getElementById("game-over-section").style.display = "block";
        toggleNavLinks(true); // Show navigation links after gameplay

        let gameOverMessage = `Game Over! Winner: ${data.winner}`;
        if (data.accumulated_prizes && data.accumulated_prizes.length > 0) {
            gameOverMessage += `\nUnclaimed Prizes: ${data.accumulated_prizes.join(", ")}`;
        }
        document.getElementById("game-over-message").innerText = gameOverMessage;
    });

    // Handle player disconnection
    socket.on("player_disconnected", (data) => {
        document.getElementById("play-section").style.display = "none";
        document.getElementById("game-over-section").style.display = "block";
        document.getElementById("game-over-message").innerText = data.message;
    });

    // Return to home button functionality
    document.getElementById("return-home-btn").addEventListener("click", () => {
        console.log("Returning to home."); // Debug log
        document.getElementById("join-section").style.display = "block";
        document.getElementById("play-section").style.display = "none";
        document.getElementById("game-over-section").style.display = "none";
        document.getElementById("waiting-message").innerText = "";
        toggleNavLinks(true); // Show navigation links
    });

    // Error handling
    socket.on("error", (data) => {
        alert(data.message); // Display the error message in an alert
    });

    // Card value conversion helper
    function card_to_value(card) {
        if (card === "A") return 1;
        if (card === "J") return 11;
        if (card === "Q") return 12;
        if (card === "K") return 13;
        return parseInt(card);
    }
});
