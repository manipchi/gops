const socket = io();

document.addEventListener("DOMContentLoaded", () => {
    let selectedCard = null;

    // Reset the game UI
    function resetGameUI() {
        console.log("Resetting game UI...");
        document.getElementById("prize-card").innerText = "Prize Card: ";
        document.getElementById("accumulated-prizes").innerText = "Accumulated Prizes: None";
        document.getElementById("round-info").innerText = "";
        document.getElementById("scores").innerText = "";
        document.getElementById("hand-cards").innerHTML = ""; // Clear hand cards
        selectedCard = null;
    }

    // Toggle visibility of game sections
    function toggleSections({ showJoin = false, showPlay = false, showGameOver = false }) {
        document.getElementById("join-section").style.display = showJoin ? "block" : "none";
        document.getElementById("play-section").style.display = showPlay ? "block" : "none";
        document.getElementById("game-over-section").style.display = showGameOver ? "block" : "none";
    }

    // Show "Searching for Opponent" message
    function showSearchingMessage() {
        const waitingMessage = document.getElementById("waiting-message");
        if (waitingMessage) {
            waitingMessage.innerText = "Searching for an opponent...";
            waitingMessage.style.display = "block";
        }
    }

    // Clear "Searching for Opponent" message
    function clearSearchingMessage() {
        const waitingMessage = document.getElementById("waiting-message");
        if (waitingMessage) {
            waitingMessage.innerText = "";
            waitingMessage.style.display = "none";
        }
    }

    // Handle "Join Game" button click
    document.getElementById("join-btn").addEventListener("click", () => {
        console.log("Join Game button clicked.");
        showSearchingMessage();
        toggleSections({ showJoin: false, showPlay: false, showGameOver: false });
        socket.emit("join");
    });

    // Handle "waiting" event from the server
    socket.on("waiting", (data) => {
        console.log("Received 'waiting' event from server:", data.message);
        const waitingMessage = document.getElementById("waiting-message");
        if (waitingMessage) {
            waitingMessage.innerText = data.message;
        }
    });

    // Handle "game_start" event
    socket.on("game_start", (data) => {
        console.log("Game started with players:", data.players);
        resetGameUI(); // Clear previous game data
        clearSearchingMessage(); // Clear the searching message
        toggleSections({ showJoin: false, showPlay: true, showGameOver: false });
    });

    // Handle "update_hand" event
    socket.on("update_hand", (data) => {
        console.log("Received 'update_hand' event:", data.hand);
        const handCardsDiv = document.getElementById("hand-cards");
        handCardsDiv.innerHTML = ""; // Clear previous cards

        if (!data.hand || data.hand.length === 0) {
            console.error("No cards received from server.");
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

    // Handle "update_prize" event
    socket.on("update_prize", (data) => {
        console.log("Received 'update_prize' event:", data);
        document.getElementById("prize-card").innerText = `Prize Card: ${data.prize_card}`;
        document.getElementById("accumulated-prizes").innerText = `Accumulated Prizes: ${data.accumulated_prizes.join(", ")}`;
    });

    // Handle "game_over" event
    socket.on("game_over", (data) => {
        console.log("Game over. Winner:", data.winner);
        toggleSections({ showJoin: false, showPlay: false, showGameOver: true });

        const gameOverMessage = document.getElementById("game-over-message");
        gameOverMessage.innerText = `Game Over! Winner: ${data.winner}\nFinal Scores: ${Object.entries(data.final_scores)
            .map(([player, score]) => `${player}: ${score}`)
            .join(", ")}`;
    });

    // Handle player disconnection
    socket.on("player_disconnected", (data) => {
        console.log("Player disconnected:", data.message);
        toggleSections({ showJoin: false, showPlay: false, showGameOver: true });

        const gameOverMessage = document.getElementById("game-over-message");
        gameOverMessage.innerText = data.message;
    });

    // Handle "Return to Home" button click
    document.getElementById("return-home-btn").addEventListener("click", () => {
        console.log("Returning to home...");
        resetGameUI();
        toggleSections({ showJoin: true, showPlay: false, showGameOver: false });
    });

    // Handle error messages
    socket.on("error", (data) => {
        console.error("Error received from server:", data.message);
        alert(data.message);
    });
});
