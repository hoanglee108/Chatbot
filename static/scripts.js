document.addEventListener("DOMContentLoaded", () => {
  const historyBtn = document.getElementById("history-btn");
  const sidebar = document.querySelector(".sidebar");
  const main = document.querySelector(".main");
  const newChatBtn = document.querySelector('button[title="New Chat"]');
  const sendBtn = document.querySelector(".send-btn");
  const textarea = document.querySelector(".input-container textarea");
  const chatBox = document.getElementById("chat-box");
  const welcome = document.getElementById("welcome-msg");

  let firstMessageSent = false;

  function sendMessage() {
    const text = textarea.value.trim();
    if (text !== "") {
      // Ẩn lời chào & mở rộng chat-box lần đầu
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
  });

  newChatBtn.addEventListener("click", () => {
    chatBox.innerHTML = "";
    textarea.value = "";
    textarea.style.height = "auto";
    if (welcome) welcome.classList.remove("hide");
    firstMessageSent = false;
  });
});
