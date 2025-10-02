// /public/stt.js - Client-side STT using Web Speech API, hooked to existing mic button
document.addEventListener('DOMContentLoaded', () => {
  // Wait for dynamic UI load with MutationObserver
  const observer = new MutationObserver(() => {
    // Robust element detection using JS filter for dynamic UI
    const allButtons = document.querySelectorAll('button');
    const inputField = document.querySelector('textarea.cl-input, input[type="text"][placeholder*="message"], textarea[placeholder*="Type your message"], .message-input');
    
    let micButton, sendButton;
    
    // Log all buttons for debugging
    console.log('STT Debug - All buttons count:', allButtons.length);
    allButtons.forEach((btn, index) => {
      console.log(`STT Debug - Button ${index} outerHTML:`, btn.outerHTML);
      console.log(`STT Debug - Button ${index} classes:`, btn.className);
      console.log(`STT Debug - Button ${index} aria-label:`, btn.getAttribute('aria-label'));
      console.log(`STT Debug - Button ${index} title:`, btn.title);
      console.log(`STT Debug - Button ${index} innerText:`, btn.innerText);
      console.log(`STT Debug - Button ${index} innerHTML:`, btn.innerHTML);
    });
    
    // Try position-based detection in input area
    const inputContainer = document.querySelector('.cl-input-container, .input-bar, .message-input-container, [class*="input"], .cl-footer');
    if (inputContainer) {
      const containerButtons = inputContainer.querySelectorAll('button');
      console.log('STT Debug - Container buttons:', containerButtons.length);
      if (containerButtons.length >= 3) {
        micButton = containerButtons[1]; // Second button is mic (attachment 0, mic 1, send 2)
        sendButton = containerButtons[2]; // Third button is send
        console.log('STT Debug - Position-based mic:', micButton ? micButton.outerHTML : 'null');
        console.log('STT Debug - Position-based send:', sendButton ? sendButton.outerHTML : 'null');
      }
    }
    
    // Fallback to expanded attribute and content-based
    if (!micButton) {
      micButton = Array.from(allButtons).find(btn =>
        btn.innerHTML.includes('mic') ||
        btn.innerHTML.includes('audio') ||
        btn.innerHTML.includes('record') ||
        btn.innerHTML.includes('🎤') ||
        btn.getAttribute('aria-label')?.includes('audio') ||
        btn.getAttribute('aria-label')?.includes('record') ||
        btn.getAttribute('aria-label')?.includes('mic') ||
        btn.title?.includes('audio') ||
        btn.title?.includes('record') ||
        btn.title?.includes('mic') ||
        btn.classList.contains('cl-mic-button') ||
        btn.classList.contains('audio-button') ||
        btn.classList.contains('cl-audio-button')
      );
    }
    
    if (!sendButton) {
      sendButton = Array.from(allButtons).find(btn =>
        btn.innerHTML.includes('send') ||
        btn.innerHTML.includes('➤') ||
        btn.innerHTML.includes('arrow') ||
        btn.getAttribute('aria-label')?.includes('send') ||
        btn.title?.includes('send') ||
        btn.classList.contains('cl-send-button') ||
        btn.classList.contains('send-button')
      );
    }
    
    console.log('STT Debug - Final mic:', micButton ? micButton.outerHTML : 'null');
    console.log('STT Debug - Final send:', sendButton ? sendButton.outerHTML : 'null');
    console.log('STT Debug - Input:', inputField);

    if (micButton && inputField && sendButton) {
      observer.disconnect(); // Stop observing once found
      attachListeners(micButton, inputField, sendButton);
      console.log('STT: Elements found and listeners attached.');
    } else {
      console.log('STT: Elements not found yet, continuing to observe...');
    }
  });
  observer.observe(document.body, { childList: true, subtree: true, attributes: true });

  function attachListeners(micButton, inputField, sendButton) {
    let recognition;
    let isListening = false;

    // Check browser support
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('STT: SpeechRecognition not supported in this browser. Use Chrome.');
      micButton.title = 'Speech not supported (use Chrome)';
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    micButton.addEventListener('click', (e) => {
      e.preventDefault(); // Prevent default Chainlit audio recording

      if (isListening) {
        recognition.stop();
        return;
      }

      // Secure context check (mic requires HTTPS/localhost)
      if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
        alert('STT: Microphone access requires HTTPS or localhost.');
        return;
      }

      recognition = new SpeechRecognition();
      recognition.lang = 'en-US';
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        isListening = true;
        micButton.classList.add('recording');
        micButton.title = 'Listening... Click to stop';
        inputField.placeholder = 'Listening for speech...';
        console.time('stt-latency');
      };

      recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        inputField.value = transcript;
        inputField.dispatchEvent(new Event('input', { bubbles: true }));

        if (event.results[event.results.length - 1].isFinal) {
          sendTranscript(transcript, inputField, sendButton);
        }
      };

      recognition.onerror = (event) => {
        console.error('STT Error:', event.error);
        let errorMsg = 'Speech recognition error: ';
        switch (event.error) {
          case 'not-allowed':
          case 'permission-denied':
            errorMsg += 'Microphone access denied. Please allow in browser settings.';
            break;
          case 'no-speech':
            errorMsg += 'No speech detected. Try again.';
            break;
          case 'audio-capture':
            errorMsg += 'Microphone issue. Check hardware.';
            break;
          case 'network':
            errorMsg += 'Network error (STT uses cloud processing).';
            break;
          default:
            errorMsg += event.error;
        }
        alert(errorMsg);
        stopListening(micButton, inputField);
      };

      recognition.onend = () => {
        stopListening(micButton, inputField);
      };

      recognition.start();
    });

    function stopListening(micButton, inputField) {
      isListening = false;
      if (recognition) recognition.stop();
      micButton.classList.remove('recording');
      micButton.title = 'Click to speak';
      inputField.placeholder = 'Type a message or click mic to speak';
      console.timeEnd('stt-latency');
    }

    async function sendTranscript(transcript, inputField, sendButton) {
      inputField.value = transcript;
      inputField.dispatchEvent(new Event('input', { bubbles: true }));

      // Get the unique session ID from the Chainlit window object
      const sessionId = window.chainlit ? window.chainlit.sessionId : null;

      if (!sessionId) {
        console.error("Chainlit session ID not found!");
        // Fallback to original simulation if no session ID
        const enterEvent = new KeyboardEvent('keydown', {
          key: 'Enter',
          code: 'Enter',
          keyCode: 13,
          which: 13,
          bubbles: true
        });
        inputField.dispatchEvent(enterEvent);
        setTimeout(() => {
          if (sendButton && !isListening) {
            sendButton.click();
          }
        }, 100);
        setTimeout(() => inputField.value = '', 200);
        return;
      }

      try {
        const response = await fetch("/voice-input", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            transcript: transcript,
            sessionId: sessionId
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        if (result.status !== "ok") {
          console.error("Backend processing failed:", result.message);
        } else {
          console.log("Transcript sent successfully to backend");
        }
      } catch (error) {
        console.error("Error sending transcript to backend:", error);
        // Fallback to original simulation on error
        const enterEvent = new KeyboardEvent('keydown', {
          key: 'Enter',
          code: 'Enter',
          keyCode: 13,
          which: 13,
          bubbles: true
        });
        inputField.dispatchEvent(enterEvent);
        setTimeout(() => {
          if (sendButton && !isListening) {
            sendButton.click();
          }
        }, 100);
      }

      // Clear input after send
      setTimeout(() => inputField.value = '', 200);
    }
  }

  // Add CSS for visual feedback
  const style = document.createElement('style');
  style.textContent = `
    button.recording {
      background-color: #ff4d4f !important;
      animation: pulse 1s infinite;
    }
    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.5; }
      100% { opacity: 1; }
    }
  `;
  document.head.appendChild(style);
});