// /public/stt.js - Client-side STT using Web Speech API, hooked to existing mic button
document.addEventListener('DOMContentLoaded', () => {
  // Wait for dynamic UI load with MutationObserver
  const observer = new MutationObserver(() => {
    const micButton = document.querySelector('button.cl-mic-button, button[aria-label="Record audio"], button[data-icon="mic"], button[title*="Record"], button:has(svg[title*="microphone"]), button:has(svg[aria-hidden="true"] svg[title*="microphone"])');
    const inputField = document.querySelector('textarea.cl-input, input[type="text"][placeholder*="message"], textarea[placeholder*="Type your message"], .message-input');
    const sendButton = document.querySelector('button.cl-send-button, button[aria-label="Send"], button[data-icon="send"], .send-button');

    // Log for debugging
    console.log('STT Debug - All buttons:', document.querySelectorAll('button'));
    console.log('STT Debug - Potential mic:', micButton);
    console.log('STT Debug - Input:', inputField);
    console.log('STT Debug - Send:', sendButton);

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

    function sendTranscript(transcript, inputField, sendButton) {
      inputField.value = transcript;
      inputField.dispatchEvent(new Event('input', { bubbles: true }));

      // Simulate Enter key to send
      const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        which: 13,
        bubbles: true
      });
      inputField.dispatchEvent(enterEvent);

      // Fallback: Click send button
      setTimeout(() => {
        if (sendButton && !isListening) {
          sendButton.click();
        }
      }, 100);

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