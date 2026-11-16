
const STORAGE_KEY = "chatbot_session";

// Recover previous session or create a new one
let savedSession;

try {
    savedSession = JSON.parse(
        sessionStorage.getItem(STORAGE_KEY)
    );
} catch {
    savedSession = null;
}

const conversationId =
    savedSession?.conversationId ||
    (
        Date.now().toString(36) +
        Math.random().toString(36).substring(2)
    );

let chatHistory = Array.isArray(savedSession?.messages)
    ? savedSession.messages
    : [];

let waitingForResponse = false;

// HTML elements
const status = document.getElementById("status");
const messages = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");

// Markdown configuration
marked.setOptions({
    breaks: true,
    gfm: true
});

// Save conversation to browser storage
function saveSession() {
    sessionStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
            conversationId: conversationId,
            messages: chatHistory
        })
    );
}

// Render a message
function renderMessage(text, sender) {
    const message = document.createElement("div");

    message.className = `message ${sender}`;

    if (sender === "bot") {
        const html = marked.parse(text);
        message.innerHTML = DOMPurify.sanitize(html);
    } else {
        message.textContent = text;
    }

    messages.appendChild(message);
}

// Add message and save it
function addMessage(text, sender) {
    chatHistory.push({
        text: text,
        sender: sender
    });

    renderMessage(text, sender);
    saveSession();

    messages.scrollTop = messages.scrollHeight;
}

// Restore previous conversation
function restoreConversation() {
    messages.innerHTML = "";

    chatHistory.forEach(msg => {
        renderMessage(msg.text, msg.sender);
    });

    messages.scrollTop = messages.scrollHeight;
}

// Restore messages before connecting
restoreConversation();

// Connect to FastAPI
const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";

const socket = new WebSocket(
    `${protocol}//${window.location.host}/ws/chat/${conversationId}`
);

socket.onopen = () => {
    status.textContent = "Restoring conversation...";
    status.style.color = "#facc15";

    // Send cached conversation to Python
    socket.send(JSON.stringify({
        type: "restore",
        messages: chatHistory.map(msg => ({
            role: msg.sender === "bot" ? "assistant" : "user",
            content: msg.text
        }))
    }));
};

socket.onmessage = (event) => {
    let data;

    try {
        data = JSON.parse(event.data);
    } catch (error) {
        console.error("[WS] Invalid server response:", event.data);
        return;
    }

    if (data.type === "ready") {
        status.textContent = "Connected";
        status.style.color = "#4ade80";
        input.disabled = false;
        input.focus();
        return;
    }

    if (data.type === "message") {
        addMessage(data.content, "bot");

        waitingForResponse = false;
        input.disabled = false;
        input.focus();
        return;
    }

    if (data.type === "error") {
        console.error("[WS] Server error:", data.content);

        addMessage(data.content, "bot");

        waitingForResponse = false;
        input.disabled = false;
    }
};

socket.onclose = () => {
    status.textContent = "Disconnected";
    status.style.color = "#f87171";
    input.disabled = true;
};

socket.onerror = (error) => {
    console.error("[WS] Error:", error);
    status.textContent = "Connection error";
};

// Send user prompt
form.addEventListener("submit", (event) => {
    event.preventDefault();

    const message = input.value.trim();

    if (!message || waitingForResponse) return;
    if (socket.readyState !== WebSocket.OPEN) return;

    addMessage(message, "user");

    socket.send(JSON.stringify({
        type: "message",
        content: message
    }));

    input.value = "";
    input.disabled = true;
    waitingForResponse = true;
});
