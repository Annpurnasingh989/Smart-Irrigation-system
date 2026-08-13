document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("farmerMessage");
    const chat = document.getElementById("chatMessages");
    const micButton = document.getElementById("micButton");
    const voiceStatus = document.getElementById("voiceStatus");

    // =========================
    // SEND MESSAGE
    // =========================

    window.sendMessage = function () {

        const message = input.value.trim();

        if (message === "") {
            return;
        }

        // User message
        addMessage(message, "user");

        // Clear input
        input.value = "";

        // Demo AI response
        setTimeout(function () {

            const response = getAIResponse(message);

            addMessage(response, "bot");

        }, 600);
    };


    // =========================
    // ADD MESSAGE
    // =========================

    function addMessage(message, type) {

        const div = document.createElement("div");

        div.className = "message " + type;

        if (type === "user") {

            div.innerHTML = `
                <div class="message-avatar">
                    👨‍🌾
                </div>

                <div class="message-bubble">
                    <b>You</b>
                    <p>${escapeHTML(message)}</p>
                </div>
            `;

        } else {

            div.innerHTML = `
                <div class="message-avatar">
                    🤖
                </div>

                <div class="message-bubble">
                    <b>Farmer AI</b>
                    <p>${message}</p>
                </div>
            `;
        }

        chat.appendChild(div);

        chat.scrollTop = chat.scrollHeight;
    }


    // =========================
    // AI RESPONSE
    // =========================

    function getAIResponse(message) {

        const text = message.toLowerCase();

        if (
            text.includes("water") ||
            text.includes("irrigation") ||
            text.includes("पानी") ||
            text.includes("सिंचाई")
        ) {

            return `
                💧 <b>Irrigation Advice</b><br><br>
                Check soil moisture before irrigation.
                Avoid over-irrigation to save water.
            `;

        }


        if (
            text.includes("yellow") ||
            text.includes("पीला") ||
            text.includes("पीले") ||
            text.includes("peela")
        ) {

            return `
                🌱 <b>Crop Health Advice</b><br><br>
                Yellow leaves may be caused by
                nutrient deficiency, excessive water
                or disease.
                <br><br>
                You can also use <b>Leaf AI</b> for
                disease detection.
            `;

        }


        if (
            text.includes("wheat") ||
            text.includes("गेहूं") ||
            text.includes("gehun")
        ) {

            return `
                🌾 <b>Wheat Advice</b><br><br>
                Monitor soil moisture regularly and
                avoid unnecessary irrigation.
            `;

        }


        if (
            text.includes("rice") ||
            text.includes("धान") ||
            text.includes("dhan")
        ) {

            return `
                🌾 <b>Rice Advice</b><br><br>
                Rice generally requires more water.
                Monitor field moisture and avoid
                unnecessary water loss.
            `;

        }


        if (
            text.includes("soil") ||
            text.includes("मिट्टी") ||
            text.includes("mitti")
        ) {

            return `
                🌱 <b>Soil Advice</b><br><br>
                Check soil moisture before irrigation.
                Suitable moisture levels help reduce
                water wastage.
            `;

        }


        return `
            🤖 <b>Farmer AI</b><br><br>
            I understand your question.
            Please tell me your crop name and
            describe the farming problem in a little
            more detail.
        `;
    }


    // =========================
    // ENTER KEY
    // =========================

    input.addEventListener("keydown", function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();
        }

    });


    // =========================
    // QUICK QUESTIONS
    // =========================

    window.quickMessage = function (message) {

        input.value = message;

        sendMessage();
    };


    // =========================
    // CLEAR CHAT
    // =========================

    window.clearChat = function () {

        chat.innerHTML = `
            <div class="message bot">

                <div class="message-avatar">
                    🤖
                </div>

                <div class="message-bubble">

                    <b>Farmer AI</b>

                    <p>
                        Hello 👋<br><br>
                        How can I help you with farming?
                    </p>

                </div>

            </div>
        `;
    };


    // =========================
    // MICROPHONE
    // =========================

    window.startVoiceInput = function () {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Voice recognition is not supported in this browser.");
        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "hi-IN";
    recognition.continuous = false;
    recognition.interimResults = true;

    const input = document.getElementById("farmerMessage");
    const status = document.getElementById("voiceStatus");

    status.innerHTML = "🎤 Listening... Please speak.";

    recognition.start();

    recognition.onresult = function (event) {

        let text = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {

            text += event.results[i][0].transcript;

        }

        input.value = text;

        status.innerHTML =
            "✅ I heard: " + text;
    };

    recognition.onerror = function (event) {

        status.innerHTML =
            "❌ Voice Error: " + event.error;

        console.log("Speech error:", event.error);
    };

    recognition.onend = function () {

        console.log("Speech recognition ended.");

    };
};

    // =========================
    // SECURITY
    // =========================

    function escapeHTML(text) {

        const div = document.createElement("div");

        div.textContent = text;

        return div.innerHTML;
    }

});