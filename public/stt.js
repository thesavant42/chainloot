document.addEventListener("DOMContentLoaded", function() {
    // Check for browser support
    window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!window.SpeechRecognition) {
        console.error("Your browser does not support the Web Speech API.");
        // Optionally, hide the button if not supported
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let isRecording = false;
    let finalTranscript = ''; // <-- CHANGE 1: Variable to hold the full transcript

    // Create and style the microphone button
    const micButton = document.createElement("button");
    micButton.id = "mic-button";
    micButton.innerHTML = "🎤";
    micButton.style.position = "fixed";
    micButton.style.bottom = "15px";
    micButton.style.right = "15px";
    micButton.style.width = "50px";
    micButton.style.height = "50px";
    micButton.style.fontSize = "24px";
    micButton.style.borderRadius = "50%";
    micButton.style.border = "1px solid #ccc";
    micButton.style.cursor = "pointer";
    micButton.style.backgroundColor = "#f0f0f0";
    document.body.appendChild(micButton);

    micButton.addEventListener("click", () => {
        if (isRecording) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });

    // When recognition starts
    recognition.onstart = () => {
        isRecording = true;
        finalTranscript = ''; // Clear transcript on new recording
        micButton.innerHTML = "🛑";
        micButton.style.backgroundColor = "#ffdddd";
        console.log("Speech recognition started.");
    };
    
    // When recognition ends
    recognition.onend = () => {
        isRecording = false;
        micButton.innerHTML = "🎤";
        micButton.style.backgroundColor = "#f0f0f0";
        console.log("Speech recognition ended.");

        // <-- CHANGE 2: This is the new, reliable logic
        // Only send to backend if we have a final transcript
        if (finalTranscript) {
            console.log("Sending final transcript to backend:", finalTranscript);
            sendTranscriptToBackend(finalTranscript);
        } else {
            console.log("No final transcript to send.");
        }
    };

    // Process results as they come in
    recognition.onresult = (event) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interimTranscript += event.results[i][0].transcript;
            }
        }
        console.log("Interim: ", interimTranscript);
        console.log("Final: ", finalTranscript);
    };

    // Handle any errors
    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
    };

    async function sendTranscriptToBackend(transcript) {
        const sessionId = window.chainlit.sessionId;
        if (!sessionId) {
            console.error("Chainlit session ID not found!");
            return;
        }

        try {
            const response = await fetch("/voice-input", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    transcript: transcript.trim(), // Trim whitespace
                    sessionId: sessionId
                }),
            });
            if (!response.ok) {
                console.error("Backend request failed:", response.statusText);
            } else {
                console.log("Transcript sent successfully.");
            }
        } catch (error) {
            console.error("Error sending transcript:", error);
        }
    }
});