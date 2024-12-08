const socket = io();

document.addEventListener("DOMContentLoaded", () => {
    let selectedCard = null; // Track the currently selected card

    // Helper function to reset the game UI
    function resetGameUI() {
        // Clear all game-related messages and UI elements
        document.getElementById("prize-card").innerText = "Prize Card: ";
        document.getElementById("accumulated-prizes").innerText = "Accumulated Prizes: None";
        document.getElementById("round-info").innerText = "";
        document.getElementById("scores").innerText = "";
        const handCardsDiv = document.getElementById("hand-cards");
        handCardsDiv.innerHTML = ""; // Clear hand cards
        selectedCard = null; // Reset selected card
    }

    // Handle "Return to Home" Button
    document.getElementById("return-home-btn").addEventListener("click", () => {
        // Reset the UI to the original home page
        resetGameUI();
        document.getElementById("join-section").style.display = "block"; // Show the Join Game section
        document.getElementById("play-section").style.display = "none"; // Hide the play section
        document.getElementById("game-over-section").style.display = "none"; // Hide the game over section
        const waitingMessage = document.getElementById("waiting-message");
        if (waitingMessage) waitingMessage.innerText = ""; // Clear waiting message
    });

    // Handle Join Game Button
    document.getElementById("join-btn").addEventListener("click", () => {
        // Emit join event
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
        resetGameUI(); // Clear previous game data
        document.getElementById("join-section").style.display = "none"; // Hide the Join Game section
        document.getElementById("play-section").style.display = "block"; // Show the play section
    });

    // Handle Card Update
    socket.on("update_hand", (data) => {
        const handCardsDiv = document.getElementById("hand-cards");
        handCardsDiv.innerHTML = ""; // Clear previous cards

        if (!data.hand || data.hand.length === 0) {
            console.error("No cards received.");
            return;
        }

        data.hand.forEach((card) => {
            const cardElement = document.createElement("div");
            cardElement.classList.add("card");
            cardElement.textContent = card;

            // Add click event to select a card
            cardElement.addEventListener("click", () => {
                if (selectedCard) {
                    selectedCard.classList.remove("selected"); // Deselect the previously selected card
                }
                selectedCard = cardElement;
                cardElement.classList.add("selected"); // Highlight the selected card
                socket.emit("select_card", { card }); // Send selected card to the server
                console.log(`Selected card: ${card}`);
            });

            handCardsDiv.appendChild(cardElement);
        });
    });

    // Handle Prize Card Update
    socket.on("update_prize", (data) => {
        const prizeCardElement = document.getElementById("prize-card");
        const accumulatedPrizesElement = document.getElementById("accumulated-prizes");

        if (prizeCardElement) {
            prizeCardElement.innerText = `Prize Card: ${data.prize_card}`;
        }

        if (accumulatedPrizesElement) {
            accumulatedPrizesElement.innerText = `Accumulated Prizes: ${data.accumulated_prizes.join(", ")}`;
        }
    });

    // Handle Round Results
    socket.on("round_result", (data) => {
        console.log("Round result received:", data);

        // Display round info
        const roundInfo = document.getElementById("round-info");
        roundInfo.textContent = `${data.message} Opponent played ${data.opponent_card}.`;

        // Update scores
        const scoresElement = document.getElementById("scores");
        let scoresText = "Scores: ";
        for (const [player, score] of Object.entries(data.scores)) {
            scoresText += `${player}: ${score} `;
        }
        scoresElement.textContent = scoresText.trim();
    });

    // Handle Game Over
    socket.on("game_over", (data) => {
        console.log("Game over. Winner:", data.winner);

        // Hide the play section
        document.getElementById("play-section").style.display = "none";

        // Show only the Game Over section with the return button
        const gameOverSection = document.getElementById("game-over-section");
        gameOverSection.style.display = "block";

        // Update the game over message
        const gameOverMessage = document.getElementById("game-over-message");
        gameOverMessage.innerText = `Game Over! Winner: ${data.winner}\nFinal Scores: ${Object.entries(data.final_scores)
            .map(([player, score]) => `${player}: ${score}`)
            .join(", ")}`;
    });

    // Handle Player Disconnect
    socket.on("player_disconnected", (data) => {
        console.log(data.message);
        const gameOverMessage = document.getElementById("game-over-message");
        gameOverMessage.innerText = data.message;
        document.getElementById("play-section").style.display = "none";
        document.getElementById("game-over-section").style.display = "block";
    });
});
