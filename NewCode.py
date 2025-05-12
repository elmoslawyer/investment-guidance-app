# --- Microphone Input (Browser) with Direct Text Area Injection ---
st.subheader("🎤 Speak your financial situation")

components.html("""
    <script>
        const streamlitDoc = window.parent.document;

        function sendTextToStreamlit(text) {
            const inputBox = streamlitDoc.querySelector('textarea[placeholder^="Example: I just graduated"]');
            if (inputBox) {
                inputBox.value = text;
                inputBox.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }

        var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        function startListening() {
            recognition.start();
        }

        recognition.onresult = function(event) {
            var transcript = event.results[0][0].transcript;
            sendTextToStreamlit(transcript);
        }

        recognition.onerror = function(event) {
            console.error("Speech recognition error", event.error);
        }
    </script>

    <button onclick="startListening()">🎙️ Start Talking</button>
""", height=150)
