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
    let silenceTimer; // For timeout-based end detection
    const SILENCE_TIMEOUT = 2000; // ms after last speech

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
        console.log('STT Start - Socket check:', {
            io: !!window.io,
            socket: window.io?.socket?.connected
        });
    };
    
    // When recognition ends
    recognition.onend = () => {
        isRecording = false;
        micButton.innerHTML = "🎤"; // Emojis are stupid.
        micButton.style.backgroundColor = "#f0f0f0";
        console.log("Speech recognition ended.");
        clearTimeout(silenceTimer);

        console.log('STT End - Socket check:', {
            io: !!window.io,
            socket: window.io?.socket?.connected,
            transcript: finalTranscript.trim(),
            hasContent: !!finalTranscript.trim()
        });

        if (finalTranscript.trim()) {
            console.log("Submitting final transcript:", finalTranscript.trim());
            const input = document.querySelector('textarea[placeholder*="message"], input[type="text"][placeholder*="message"], .cl-input, .message-input');
            if (input) {
                input.value = finalTranscript.trim();
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true })); // Additional change event for React
                // Simulate space keydown to enable submit button (enhanced)
                input.focus();
                const spaceDown = new KeyboardEvent('keydown', {
                    key: ' ',
                    code: 'Space',
                    keyCode: 32,
                    which: 32,
                    bubbles: true,
                    cancelable: true,
                    composed: true
                });
                const spaceUp = new KeyboardEvent('keyup', {
                    key: ' ',
                    code: 'Space',
                    keyCode: 32,
                    which: 32,
                    bubbles: true,
                    cancelable: true,
                    composed: true
                });
                input.dispatchEvent(spaceDown);
                input.dispatchEvent(spaceUp);
                // Dispatch on document for better bubbling
                document.dispatchEvent(spaceDown);
                document.dispatchEvent(spaceUp);
                console.log("Keydown simulation dispatched on input and document");
            }

            // Function to submit via socket.io
            function submitTranscript(content) {
                if (window.io && window.io.socket) {
                    window.io.socket.emit('message', {
                        type: 'user_message',
                        content: content
                    });
                    console.log("Submitted via socket.io");
                    if (input) {
                        input.value = '';
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                    return true;
                }
                return false;
            }

            // Try immediate submit
            if (submitTranscript(finalTranscript.trim())) {
                // Success, done
            } else {
                // Poll for socket load (up to 5s)
                console.log("Socket not ready, polling...");
                const pollInterval = setInterval(() => {
                    if (window.io && window.io.socket) {
                        clearInterval(pollInterval);
                        if (submitTranscript(finalTranscript.trim())) {
                            console.log("Submitted via delayed socket.io");
                        }
                    }
                }, 100);
                setTimeout(() => {
                    clearInterval(pollInterval);
                    if (!window.io) {
                        console.warn("Socket poll timeout - falling back to UI simulation");
                        // Log all buttons for debugging selector
                        console.log('All buttons at fallback time:', Array.from(document.querySelectorAll('button')).map(b => ({
                            className: b.className,
                            type: b.type,
                            textContent: b.textContent.trim(),
                            disabled: b.disabled,
                            innerHTML: b.innerHTML.substring(0, 50)
                        })));
                        // UI submit simulation as fallback - prefer Enter on input for reliability
                        const submitBtn = document.querySelector('#chat-submit, button[type="submit"][class*="bg-primary"], .send-button, button[type="submit"], .cl-submit-button, .cl-button[type="submit"], button.cl-button, button.rounded-full.h-8.w-8[type="submit"]');
                        if (input) {
                            console.log("Simulating Enter keydown on input for submit");
                            input.focus();
                            const enterDown = new KeyboardEvent('keydown', {
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true,
                                cancelable: true,
                                composed: true,
                                shiftKey: false // No shift for line break
                            });
                            const enterUp = new KeyboardEvent('keyup', {
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true,
                                cancelable: true,
                                composed: true
                            });
                            input.dispatchEvent(enterDown);
                            document.dispatchEvent(enterDown);
                            input.dispatchEvent(enterUp);
                            document.dispatchEvent(enterUp);
                            // Dispatch submit event on form
                            const form = input.closest('form');
                            if (form) {
                                console.log("Dispatching submit event on form");
                                form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                            }
                            // Also try button click if Enter fails
                            if (submitBtn) {
                                console.log("Also attempting button click on:", submitBtn);
                                if (submitBtn.disabled) {
                                    submitBtn.disabled = false;
                                }
                                submitBtn.click();
                                if (submitBtn.disabled === false) submitBtn.disabled = true;
                            }
                            // Check if input cleared after short delay
                            setTimeout(() => {
                                if (input && input.value.trim()) {
                                    console.error("UI simulation failed - input not cleared");
                                } else {
                                    console.log("UI simulation success - input cleared");
                                }
                            }, 1000);
                        } else {
                            console.error("No input found for Enter simulation");
                        }
                    }
                }, 5000);
            }
        } else {
            console.log("No transcript to submit.");
        }
        finalTranscript = '';  // Reset for next session
    };

    // Process results as they come in
    recognition.onresult = (event) => {
        let interimTranscript = '';
        let hasSpeech = false;
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interimTranscript += event.results[i][0].transcript;
            }
            if (event.results[i][0].transcript.trim()) hasSpeech = true;
        }
        // Update input with current transcript (final + interim)
        const currentTranscript = finalTranscript + interimTranscript;
        const input = document.querySelector('textarea[placeholder*="message"], input[type="text"][placeholder*="message"], .cl-input, .message-input');
        if (input && currentTranscript) {
            input.value = currentTranscript.trim();
            input.dispatchEvent(new Event('input', { bubbles: true }));
            // Simulate space keydown to enable submit button during interim
            input.focus();
            input.dispatchEvent(new KeyboardEvent('keydown', {
                key: ' ',
                code: 'Space',
                keyCode: 32,
                bubbles: true,
                cancelable: true
            }));
            input.dispatchEvent(new KeyboardEvent('keyup', {
                key: ' ',
                code: 'Space',
                keyCode: 32,
                bubbles: true,
                cancelable: true
            }));
        }
        console.log("Interim: ", interimTranscript);
        console.log("Final so far: ", finalTranscript);

        // Reset silence timer on speech
        if (hasSpeech) {
            clearTimeout(silenceTimer);
            silenceTimer = setTimeout(() => {
                if (isRecording) {
                    console.log("Silence detected - forcing end");
                    recognition.stop();
                }
            }, SILENCE_TIMEOUT);
        }
    };

    // Handle any errors
    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
    };

    // sendTranscriptToBackend function removed as it's now integrated into onend
});