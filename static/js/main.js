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
    socket.on("update_hand", (data) => {
        console.log("Received update_hand event:", data); // Debug log
        const handCardsDiv = document.getElementById("hand-cards");
        handCardsDiv.innerHTML = ""; // Clear existing cards

        if (!data.hand || data.hand.length === 0) {
            console.error("Received an empty hand:", data); // Debug
            return;
        }

        let selectedCard = null; // Track the currently selected card

        data.hand.forEach((card) => {
            const cardElement = document.createElement("div");
            cardElement.classList.add("card");
            cardElement.textContent = card;

            // Add click event for card selection
            cardElement.addEventListener("click", () => {
                if (selectedCard) {
                    selectedCard.classList.remove("selected"); // Remove highlight from previously selected card
                }
                selectedCard = cardElement;
                cardElement.classList.add("selected"); // Highlight the current selection
                socket.emit("select_card", { card }); // Notify server of selected card
                console.log(`Selected card: ${card}`);
            });

            handCardsDiv.appendChild(cardElement);
        });

        console.log("Updated hand displayed:", data.hand); // Debug log
    });

    // Update prize card and accumulated prizes
    socket.on("update_prize", (data) => {
        console.log("Received update_prize event:", data); // Debug log
        document.getElementById("prize-card").innerText = `Prize Card: ${data.prize_card}`;
        document.getElementById("accumulated-prizes").innerText = `Accumulated Prizes: ${data.accumulated_prizes.join(", ")}`;
    });

    // Join Game button click event
    document.getElementById("join-btn").addEventListener("click", () => {
        console.log("Join Game button clicked."); // Debug
        socket.emit("join"); // Emit the event without sending a username
    });

    // Handle waiting message
    socket.on("waiting", (data) => {
        document.getElementById("waiting-message").innerText = data.message;
    });

    // Start game
    socket.on("game_start", (data) => {
        console.log("Game started:", data); // Debug log
        document.getElementById("join-section").style.display = "none";
        document.getElementById("play-section").style.display = "block";
        toggleNavLinks(false); // Hide navigation links during gameplay
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
