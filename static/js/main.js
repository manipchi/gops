const socket = io();

document.addEventListener("DOMContentLoaded", () => {
    let selectedCard = null; // Track the currently selected card

    // Helper function to reset the game UI
    function resetGameUI() {
        console.log("Resetting game UI..."); // Debugging
        document.getElementById("prize-card").innerText = "Prize Card: ";
        document.getElementById("accumulated-prizes").innerText = "Accumulated Prizes: None";
        document.getElementById("round-info").innerText = "";
        document.getElementById("scores").innerText = "";
        document.getElementById("hand-cards").innerHTML = ""; // Clear hand cards
        selectedCard = null; // Reset selected card
    }

    // Toggle UI based on game state
    function toggleGameUI(isGameActive) {
        console.log(`Toggling game UI: ${isGameActive}`); // Debugging
        const joinSection = document.getElementById("join-section");
        const playSection = document.getElementById("play-section");
        const gameOverSection = document.getElementById("game-over-section");

        if (isGameActive) {
            joinSection.style.display = "none";
            playSection.style.display = "block";
            gameOverSection.style.display = "none";
        } else {
            joinSection.style.display = "block";
            playSection.style.display = "none";
            gameOverSection.style.display = "none";
        }
    }

    // Display "Searching for Game" message
    function showSearchingMessage() {
        const waitingMessage = document.getElementById("waiting-message");
        if (waitingMessage) {
            waitingMessage.innerText = "Searching for an opponent...";
            waitingMessage.style.display = "block"; // Ensure it's visible
        }
    }

    // Clear "Searching for Game" message
    function clearSearchingMessage() {
        const waitingMessage = document.getElementById("waiting-message");
        if (waitingMessage) {
            waitingMessage.innerText = "";
            waitingMessage.style.display = "none"; // Hide it
        }
    }

    // Handle Join Game Button
    document.getElementById("join-btn").addEventListener("click", () => {
        console.log("Join Game button clicked"); // Debugging
        showSearchingMessage(); // Show "Searching for Game" message
        socket.emit("join");
    });

    // Handle "Waiting for Opponent" Message
    socket.on("waiting", (data) => {
        console.log("Waiting for opponent:", data); // Debugging
        const waitingMessage = document.getElementById("waiting-message");
        if (waitingMessage) {
            waitingMessage.innerText = data.message;
        }
    });

    // Handle Game Start
    socket.on("game_start", (data) => {
        console.log("Game started with players:", data.players); // Debugging
        resetGameUI(); // Clear previous game data
        toggleGameUI(true); // Switch to game UI
        clearSearchingMessage(); // Clear the "Searching for Game" message
    });

    // Handle Card Update
    socket.on("update_hand", (data) => {
        console.log("Updating hand:", data.hand); // Debugging
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
        console.log("Updating prize card:", data); // Debugging
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
        console.log("Round result received:", data); // Debugging

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
        console.log("Game over. Winner:", data.winner); // Debugging

        // Hide the play section
        toggleGameUI(false); // Switch to game-over state

        // Show only the Game Over section
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
        console.log("Player disconnected:", data.message); // Debugging
        const gameOverMessage = document.getElementById("game-over-message");
        gameOverMessage.innerText = data.message;
        toggleGameUI(false); // Reset UI to pre-game state
        document.getElementById("game-over-section").style.display = "block";
    });

    // Return to Home Button
    document.getElementById("return-home-btn").addEventListener("click", () => {
        console.log("Returning to home..."); // Debugging
        resetGameUI(); // Clear game data
        toggleGameUI(false); // Switch to pre-game UI
        clearSearchingMessage(); // Clear the searching message
    });

    // Error handling
    socket.on("error", (data) => {
        console.error("Error received:", data.message); // Debugging
        alert(data.message); // Display the error message in an alert
    });
});
