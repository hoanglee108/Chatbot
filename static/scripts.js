document.addEventListener("DOMContentLoaded", () => {
  const historyBtn = document.getElementById("history-btn");
  const sidebar = document.querySelector(".sidebar");
  const main = document.querySelector(".main");
  const newChatBtn = document.querySelector('button[title="New Chat"]');
  const sendBtn = document.querySelector(".send-btn");
  const textarea = document.querySelector(".input-container textarea");
  const chatBox = document.getElementById("chat-box");
  const welcome = document.getElementById("welcome-msg");
  const historyList = document.getElementById("history-list");

  let firstMessageSent = false;

  function sendMessage() {
    const text = textarea.value.trim();
    if (text !== "") {
      if (!firstMessageSent) {
        if (welcome) welcome.classList.add("hide");
        chatBox.classList.add("full-chat");
        firstMessageSent = true;
      }

      const userBubble = document.createElement("div");
      userBubble.classList.add("chat-bubble", "user-bubble");
      userBubble.textContent = text;
      chatBox.appendChild(userBubble);

      const botBubble = document.createElement("div");
      botBubble.classList.add("chat-bubble", "bot-bubble");
      chatBox.appendChild(botBubble);

      fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text })
      }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        function readChunk() {
          reader.read().then(({ done, value }) => {
            if (done) return;
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split("\n\n").filter(line => line.startsWith("data: "));
            lines.forEach(line => {
              const text = line.replace("data: ", "");
              botBubble.textContent += text;
              chatBox.scrollTop = chatBox.scrollHeight;
            });
            readChunk();
          });
        }

        readChunk();
      });

      textarea.value = "";
      textarea.style.height = "auto";
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  textarea.addEventListener("input", () => {
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
  });

  historyBtn.addEventListener("click", () => {
    sidebar.classList.toggle("expanded");
    main.classList.toggle("blurred");

    fetch("/api/history_list")
      .then(res => res.json())
      .then(files => {
        historyList.innerHTML = "";
        files.forEach(file => {
          const item = document.createElement("div");
          item.textContent = file;
          item.classList.add("history-item");
          item.addEventListener("click", () => {
            fetch(`/api/load_chat/${file}`)
              .then(res => res.json())
              .then(chat => {
                chatBox.innerHTML = "";
                chat.forEach(msg => {
                  const bubble = document.createElement("div");
                  bubble.classList.add("chat-bubble", msg.role === "user" ? "user-bubble" : "bot-bubble");
                  bubble.textContent = msg.content;
                  chatBox.appendChild(bubble);
                });
                firstMessageSent = true;
                if (welcome) welcome.classList.add("hide");
              });
          });
          historyList.appendChild(item);
        });
      });
  });

  newChatBtn.addEventListener("click", () => {
    if (chatBox.children.length > 0) {
      const messages = [];
      chatBox.querySelectorAll(".chat-bubble").forEach(bubble => {
        messages.push({
          role: bubble.classList.contains("user-bubble") ? "user" : "assistant",
          content: bubble.textContent.trim()
        });
      });

      fetch("/api/save_chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat: messages })
      });
    }

    chatBox.innerHTML = "";
    textarea.value = "";
    textarea.style.height = "auto";
    if (welcome) welcome.classList.remove("hide");
    firstMessageSent = false;
  });
});
