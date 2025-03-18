function sendMessage() {
    var user_input = document.getElementById("user-input").value.trim();
    if (user_input === "") return;

    var chatBox = document.getElementById("chat-box");

    // Display user message
    var userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.innerText = user_input;
    chatBox.appendChild(userMessage);

    // Clear input
    document.getElementById("user-input").value = "";

    // Show typing indicator
    var typingIndicator = document.createElement("div");
    typingIndicator.className = "bot-message typing-indicator";
    typingIndicator.innerText = "Robo is typing...";
    chatBox.appendChild(typingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Send data to backend
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({ 'user_input': user_input })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok.");
        }
        return response.json();
    })
    .then(data => {
        // Remove typing indicator
        typingIndicator.remove();

        // Display bot response
        var botMessage = document.createElement("div");
        botMessage.className = "bot-message";
        botMessage.innerText = data.response || "Sorry, I didn't understand that.";
        chatBox.appendChild(botMessage);

        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        console.error("Error:", error);
        typingIndicator.remove(); // Remove typing if error occurs
        var errorMessage = document.createElement("div");
        errorMessage.className = "bot-message error-message";
        errorMessage.innerText = "Oops! Something went wrong. Please try again.";
        chatBox.appendChild(errorMessage);

        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}
