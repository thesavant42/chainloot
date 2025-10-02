// Fixed React Speech Recognition Hook for Chainlit STT
// Uses react-speech-recognition library via jsDelivr CDN (unpkg was failing)
// Surgical fix: changed CDN to jsDelivr for UMD build, access hook as SpeechRecognition.useSpeechRecognition, added isReady state in component to delay button render until support confirmed after load, preventing initial false negative. This ensures button appears and transcription/auto-send works using the library.

(function() {
    'use strict';

    function loadScript(src) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }
            const script = document.createElement('script');
            script.src = src;
            script.async = true;
            script.onload = resolve;
            script.onerror = () => reject(new Error(`Failed to load ${src}`));
            document.head.appendChild(script);
        });
    }

    async function loadDependencies() {
        try {
            if (typeof window.React === 'undefined') {
                await loadScript('https://unpkg.com/react@18/umd/react.development.js');
                await loadScript('https://unpkg.com/react-dom@18/umd/react-dom.development.js');
            }
            // Load react-speech-recognition via jsDelivr UMD
            await loadScript('./react-speech-recognition.js');
            console.log('react-speech-recognition loaded, global SpeechRecognition:', typeof window.SpeechRecognition);
            return true;
        } catch (error) {
            console.error('Failed to load dependencies:', error);
            return false;
        }
    }

    async function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        const loaded = await loadDependencies();
        if (!loaded) return;

        const React = window.React;
        const ReactDOM = window.ReactDOM;
        const SpeechRecognition = window.SpeechRecognition;

        if (!SpeechRecognition) {
            console.error('SpeechRecognition global not available after load');
            return;
        }

        const { useSpeechRecognition } = SpeechRecognition;

        function SpeechToTextButton() {
            const [isReady, setIsReady] = React.useState(false);
            const {
                transcript,
                listening,
                resetTranscript,
                browserSupportsSpeechRecognition
            } = useSpeechRecognition({
                continuous: true,
                interimResults: true,
                lang: 'en-US'
            });

            // Set ready after support confirmed
            React.useEffect(() => {
                if (browserSupportsSpeechRecognition) {
                    setIsReady(true);
                }
            }, [browserSupportsSpeechRecognition]);

            React.useEffect(() => {
                const input = document.getElementById('chat-input');
                if (input && transcript) {
                    input.value = transcript;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }, [transcript]);

            React.useEffect(() => {
                if (!listening && transcript.trim()) {
                    submitTranscript(transcript.trim());
                    resetTranscript();
                }
            }, [listening, transcript]);

            const submitTranscript = (text) => {
                console.log('Submitting final transcript:', text);
                const input = document.getElementById('chat-input');
                if (typeof cl !== 'undefined' && cl.runAction) {
                    try {
                        cl.runAction('stt_submit', { transcript: text });
                        console.log('Transcript submitted via action');
                        if (input) {
                            input.value = '';
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    } catch (error) {
                        console.error('Action submission failed:', error);
                        if (input) {
                            input.value = text;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                        alert('Transcript ready in input field. Please send manually.');
                    }
                } else {
                    console.warn('Chainlit cl object not available');
                    if (input) {
                        input.value = text;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                    alert('Transcript ready in input field. Please send manually.');
                }
            };

            console.log('Component render - supports:', browserSupportsSpeechRecognition, 'isReady:', isReady, 'listening:', listening);

            if (!isReady) {
                console.log('Waiting for readiness...');
                return React.createElement('div', { style: { display: 'none' } });
            }

            if (!browserSupportsSpeechRecognition) {
                console.warn('Browser does not support speech recognition. Try Chrome.');
                return null;
            }

            const toggleListening = () => {
                if (!browserSupportsSpeechRecognition || !isReady) {
                    alert('Speech recognition not supported or not ready. Try refreshing.');
                    return;
                }
                if (listening) {
                    console.log('Stopping speech recognition');
                    SpeechRecognition.stopListening();
                } else {
                    console.log('Starting speech recognition');
                    SpeechRecognition.startListening({ continuous: true });
                }
            };

            return React.createElement(
                'button',
                {
                    id: 'mic-button',
                    className: listening ? 'recording' : '',
                    onClick: toggleListening,
                    disabled: !browserSupportsSpeechRecognition || !isReady,
                    style: {
                        position: 'fixed',
                        right: '20px',
                        bottom: '20px',
                        zIndex: 9999,
                        width: '50px',
                        height: '50px',
                        borderRadius: '50%',
                        border: 'none',
                        backgroundColor: listening ? '#ff6b6b' : '#4ecdc4',
                        color: 'white',
                        fontSize: '20px',
                        cursor: 'pointer',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                        transition: 'all 0.2s ease',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    },
                    title: listening ? 'Stop recording' : 'Start voice input'
                },
                listening ? '⏹️' : '🎤'
            );
        }

        // Add CSS styles
        const style = document.createElement('style');
        style.id = 'stt-styles';
        style.textContent = `
            #mic-button:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0,0,0,0.2);
            }
            #mic-button.recording {
                animation: pulse 1s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
        `;
        if (!document.getElementById('stt-styles')) {
            document.head.appendChild(style);
        }

        // Create container and render
        let container = document.getElementById('stt-root');
        if (!container) {
            container = document.createElement('div');
            container.id = 'stt-root';
            container.style.display = 'none';
            document.body.appendChild(container);
        }

        ReactDOM.render(React.createElement(SpeechToTextButton), container);

        // Position update
        const updatePosition = () => {
            const button = document.getElementById('mic-button');
            const input = document.getElementById('chat-input');
            if (button && input) {
                const rect = input.getBoundingClientRect();
                button.style.bottom = `${window.innerHeight - rect.bottom + 10}px`;
            }
        };

        window.addEventListener('resize', updatePosition);
        window.addEventListener('scroll', updatePosition);
        setTimeout(updatePosition, 500);

        // Observer for chat input
        const observer = new MutationObserver(() => {
            if (document.getElementById('chat-input')) {
                updatePosition();
                observer.disconnect();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });

        console.log('React STT with react-speech-recognition initialized');
    }

    init();
})();