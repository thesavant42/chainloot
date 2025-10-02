
# chainloot

Customized Chainlit stack for Yoda Robot

## Goal 

Goal is to unify and simplify the architecture required to run the Robot

- [x] Should support hot swapping of different models hosted on LM Studio
- [x] Should support TTS-WebUI API Integration
    - [x] Reasoning should be a checkbox toggle, disabled by default
- [x] Should have widgets to adjust sampler settings for text response on the fly
- [x] Should have widgets to adjust sampler settings for speech on the fly
- [x] Should be able to select from available voices via a drop-down selector text-input
- [x] Should support a prompt catalog for hot swapping "roles", AI assistant vs. roleplaying character
- [x] Should support character profiles, to change the chat participants
- [ ] Should Integrate Whisper-like ASR (Automatic Speech Recognition)
- [ ] Should support multi-modal functionality, for image recognition and tool usage.

## Status

ALERT: NO MORE BROWSER-BASED STT! MOVING TO INTERNALLY-HOSTED WHISPER
Pivot on STT: The tts endpoint server now supports openai-compatible speech to text.

Implement Speech to text using Chainlit's integrated microphone widget, send request to http://192.168.1.98:7778/v1/audio/transcriptions and then return the transcription to the Chainlit API.
No new bugs! If fixing a bug means introducing a different bug, the bug is not fixed, and the task has not succeeded.

### Endpoints
OpenAI-Compatible Text to Speech  (TTS) API: 	http://192.168.1.98:7778/v1/audio/speech
OpenAI-Compatible Whisper (STT) API: 			http://192.168.1.98:7778/v1/audio/transcriptions
TTS-WebUI Audio Models List (chatterbox)		http://192.168.1.98:7778/v1/audio/models
List Voices API (chatterbox-tts):				http://192.168.1.98:7778/v1/audio/voices
LM Studio - List Models (LM Studio api):        http://192.168.1.98:1234/api/v0/models
LM Studio - (OpenAPI) Chat Completion API:      http://192.168.1.98:1234/v1

### Docs
SwaggerDoc:								        http://192.168.1.98:7778/docs#/
OpenAPI JSON:							        http://192.168.1.98:7778/openapi.json
Gradio UI for TTS-WebUI:				        http://192.168.1.98:7770/
Gradio UI API Doc:						        http://192.168.1.98:7770/openapi.json
React UI for TTS-WebUI:					        http://192.168.1.98:3000/

### Windows-curl friendly TTS Test string

```
 curl -X POST http://192.168.1.98:7778/v1/audio/speech -H "Content-Type: application/json" -d '{"model":"chatterbox","input":"Hello world! This is a streaming test.","voice":"random","stream":true}' --proxy http://127.0.0.1:8080
 ```



![model_settings](https://github.com/thesavant42/chainloot/blob/main/docs/model-settings.png?raw=true)

## Structure

chainlit/ Top Level Directory
- docs/                             # Folder for documentation and support files, API schema docs
- docs/chainlit-docs/
- docs/tts-webui-apis/              # OpenAPI docs for Chatterbox, TTS-WebUI
- ./README.md                       # This file
- ./app.py                          # Man chainlit app code
- ./.env                            # API keys go here (if needed)


### Chainlit Docs

- https://docs.chainlit.io/get-started/overview
- https://docs.chainlit.io/api-reference/lifecycle-hooks/on-chat-start
- https://docs.chainlit.io/api-reference/lifecycle-hooks/on-audio-chunk
- https://docs.chainlit.io/api-reference/lifecycle-hooks/on-audio-end
- https://docs.chainlit.io/api-reference/chat-profiles
- https://docs.chainlit.io/api-reference/chat-settings
- https://docs.chainlit.io/api-reference/action
- https://docs.chainlit.io/api-reference/elements/audio
- https://docs.chainlit.io/api-reference/integrations/langchain

### TTS-WebUI

- https://github.com/rsxdalv/TTS-WebUI
- https://github.com/rsxdalv/TTS-WebUI/blob/main/documentation/external_extensions.md

