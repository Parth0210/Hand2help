const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");
const videoEl = document.getElementById("signVideo");

let lastVideos = [];


clearBtn.onclick = () => chatBox.innerHTML = "";

input.addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
});

function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = `message ${sender}`;
    msg.innerHTML = `
        ${text}
        <div class="time">${new Date().toLocaleTimeString()}</div>
    `;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function playVideoSequence(videos) {
    if (!videos || videos.length === 0) return;

    lastVideos = [...videos]; // store for replay
    let index = 0;

    const playNext = () => {
        // Fade out
        videoEl.classList.add("fade-out");

        setTimeout(() => {
            videoEl.src = `/static/avatar_videos/${videos[index]}`;
            videoEl.load();

            videoEl.onloadeddata = () => {
                // Fade in
                videoEl.classList.remove("fade-out");
                videoEl.classList.add("fade-in");
                videoEl.play();
            };
        }, 300); // fade-out duration
    };

    playNext();

    videoEl.onended = () => {
        index++;
        if (index < videos.length) {
            playNext();
        }
    };
}


async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";
    sendBtn.disabled = true;

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await res.json();
        addMessage(data.reply, "bot");

        if (data.videos && data.videos.length > 0) {
            playVideoSequence(data.videos);
        }

    } catch (e) {
        addMessage("Server error", "bot");
    }

    sendBtn.disabled = false;
}

const replayBtn = document.getElementById("replayBtn");

replayBtn.onclick = () => {
    if (lastVideos.length > 0) {
        playVideoSequence(lastVideos);
    }
};
