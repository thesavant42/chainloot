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
    // why are we creating a mic button? The Chainlit UI has a microphone icon
    const micButton = document.createElement("button");
    micButton.id = "mic-button";
    micButton.innerHTML = "🎤"; // emojis are stupid.
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
        micButton.innerHTML = "🛑"; // Emojis are stupid.
        micButton.style.backgroundColor = "#ffdddd";
        console.log("Speech recognition started.");
    };
    
    // When recognition ends
    recognition.onend = () => {
        isRecording = false;
        micButton.innerHTML = "🎤"; // Emojis are stupid.
        micButton.style.backgroundColor = "#f0f0f0";
        console.log("Speech recognition ended.");

        if (finalTranscript) {
            console.log("Setting final transcript to input and submitting via API:", finalTranscript);
            const input = document.querySelector('textarea[placeholder*="message"], input[type="text"][placeholder*="message"], .cl-input');
            if (input) {
                input.value = finalTranscript.trim();
                input.dispatchEvent(new Event('input', { bubbles: true }));
                console.log("Final transcript set in input for visibility.");
            }
            // Send via Chainlit API endpoint
            fetch('/api/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: finalTranscript.trim()
                })
            }).then(response => {
                if (response.ok) {
                    console.log("Message sent successfully via API.");
                    // Clear input after successful send
                    if (input) {
                        input.value = '';
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                } else {
                    console.error("Failed to send message via API:", response.status);
                }
            }).catch(error => {
                console.error("Error sending message via API:", error);
            });
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
        // Update input with current transcript (final + interim)
        const currentTranscript = finalTranscript + interimTranscript;
        const input = document.querySelector('textarea[placeholder*="message"], input[type="text"][placeholder*="message"]');
        if (input && currentTranscript) {
            input.value = currentTranscript.trim();
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
        console.log("Interim: ", interimTranscript);
        console.log("Final so far: ", finalTranscript);
    };

    // Handle any errors
    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
    };

    async function sendTranscriptToBackend(transcript) {
        if (window.io && window.io.socket) {
            console.log("Sending transcript via socket.io emit:", transcript);
            window.io.socket.emit('message', {
                type: 'user_message',
                content: transcript.trim()
            });
            console.log("Transcript sent via socket.io.");
        } else {
            console.error("Socket.io not available. Ensure in active chat.");
        }
    }
});