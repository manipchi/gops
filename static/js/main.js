const socket = io();

document.addEventListener("DOMContentLoaded", () => {
    let selectedCard = null; // Track the currently selected card

    // Helper function to toggle navigation links
    function toggleNavLinks(visible) {
        const navLinks = document.getElementById("nav-links");
        if (navLinks) {
            navLinks.style.display = visible ? "flex" : "none";
        }
    }

    // Toggle UI based on game state
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
