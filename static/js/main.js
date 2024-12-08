const socket = io();

document.addEventListener("DOMContentLoaded", () => {
    function toggleGameUI(isGameActive) {
        const body = document.body;
        if (isGameActive) {
            body.classList.add("in-game");
        } else {
            body.classList.remove("in-game");
        }
    }

    // Handle Join Game Button
    document.getElementById("join-btn").addEventListener("click", () => {
        socket.emit("join");
    });

    // Handle "Waiting for Opponent" Message
    socket.on("waiting", (data) => {
        const waitingMessage = document.getElementById("waiting-message");
        if (waitingMessage) {
            waitingMessage.innerText = data.message;
        }
    });

    // Handle Game Start
    socket.on("game_start", (data) => {
        console.log("Game started with players:", data.players);
        toggleGameUI(true); // Hide unnecessary elements
        const playSection = document.getElementById("play-section");
        playSection.style.display = "block"; // Show the game area
    });

    // Handle Card Update
    socket.on("update_hand", (data) => {
        const handCardsDiv = document.getElementById("hand-cards");
        handCardsDiv.innerHTML = ""; // Clear previous cards

        data.hand.forEach((card) => {
            const cardElement = document.createElement("div");
            cardElement.classList.add("card");
            cardElement.textContent = card;

            // Add click event to select a card
            cardElement.addEventListener("click", () => {
                socket.emit("select_card", { card });
                cardElement.classList.add("selected");
                console.log(`Selected card: ${card}`);
            });

            handCardsDiv.appendChild(cardElement);
        });
    });

    // Handle Prize Card Update
    socket.on("update_prize", (data) => {
        document.getElementById("prize-card").innerText = `Prize Card: ${data.prize_card}`;
        document.getElementById("accumulated-prizes").innerText = `Accumulated Prizes: ${data.accumulated_prizes.join(", ")}`;
    });

    // Handle Game Over
    socket.on("game_over", (data) => {
        console.log("Game over. Winner:", data.winner);
        toggleGameUI(false); // Reset UI to pre-game state
        const gameOverMessage = document.getElementById("game-over-message");
        gameOverMessage.innerText = `Game Over! Winner: ${data.winner}`;
        document.getElementById("game-over-section").style.display = "block";
    });

    // Handle Player Disconnect
    socket.on("player_disconnected", (data) => {
        console.log(data.message);
        const gameOverMessage = document.getElementById("game-over-message");
        gameOverMessage.innerText = data.message;
        toggleGameUI(false); // Reset UI to pre-game state
        document.getElementById("game-over-section").style.display = "block";
    });

    // Return to Home Button
    document.getElementById("return-home-btn").addEventListener("click", () => {
        toggleGameUI(false);
        document.getElementById("join-section").style.display = "block";
        document.getElementById("play-section").style.display = "none";
        document.getElementById("game-over-section").style.display = "none";
        document.getElementById("waiting-message").innerText = "";
    });
});
