
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
- [x] Should Integrate Whisper-like ASR (Automatic Speech Recognition)
- [ ] Should support multi-modal functionality, for image recognition and tool usage.

## Status

Latest commit: Transcription via microphone widget is complete.

![demo](https://github.com/thesavant42/chainloot/blob/main/docs/demo.png?raw=true)

--
Latest commit leverages the extremely timely addition of the OpenAI-compatible Whisper Speech to text service, so I am trying to use that. 
What DOES work: If I upload a .wav file through the chainlit interface, it will get transcribed.
What does NOT work: If I click the Chainlit React UI microphone button, the browser engages the microphone, and the widget responds visually to sound. But upon concluding the spoken dialog and pressing "P" to end recording, the front end SHOULD upload the wav for transcription, but it does not. There's no mesaging of any consequence in the browser console, and chainlit console sees the event but does not receive the audio:

Transcribing stives.wav
```
S C:\Users\jbras\Desktop\chainloot> chainlit run app.py
2025-10-02 22:33:21 - Loaded .env file
Using TTS voice: voices/chatterbox/whywishnotfar.wav
2025-10-02 22:33:28 - Your app is available at http://localhost:8000
2025-10-02 22:33:31 - Translated markdown file for en-US not found. Defaulting to chainlit.md.
2025-10-02 22:33:31 - AUDIO DIAG: Chat start - Session ID: a2e85d9a-43e2-4aac-88e4-00128cf33f5e, STT client base: http://192.168.1.98:7778/v1/
2025-10-02 22:33:57 - AUDIO DIAG: on_audio_start triggered - Session ID: a2e85d9a-43e2-4aac-88e4-00128cf33f5e
2025-10-02 22:34:04 - AUDIO DIAG: on_audio_end triggered - Session ID: a2e85d9a-43e2-4aac-88e4-00128cf33f5e. Audio will be processed in on_message.
2025-10-02 22:34:15 - AUDIO DIAG: on_audio_start triggered - Session ID: a2e85d9a-43e2-4aac-88e4-00128cf33f5e
2025-10-02 22:34:20 - AUDIO DIAG: on_audio_end triggered - Session ID: a2e85d9a-43e2-4aac-88e4-00128cf33f5e. Audio will be processed in on_message.
2025-10-02 22:37:25 - AUDIO DIAG: on_message triggered - Session ID: a2e85d9a-43e2-4aac-88e4-00128cf33f5e, Elements count: 1, Content: '...'
2025-10-02 22:37:25 - AUDIO DIAG: Message type: <class 'chainlit.message.Message'>, Elements types: ['Audio']
2025-10-02 22:37:25 - AUDIO DIAG: Processing 1 elements
2025-10-02 22:37:25 - AUDIO DIAG: Element 0: type=Audio, name=stives.wav
2025-10-02 22:37:25 - AUDIO DIAG: Element attributes: ['__annotations__', '__class__', '__dataclass_fields__', '__dataclass_params__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__is_pydantic_dataclass__', '__le__', '__lt__', '__match_args__', '__module__', '__ne__', '__new__', '__post_init__', '__pydantic_complete__', '__pydantic_config__', '__pydantic_core_schema__', '__pydantic_decorators__', '__pydantic_fields__', '__pydantic_fields_complete__', '__pydantic_serializer__', '__pydantic_validator__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__signature__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_create', 'auto_play', 'chainlit_key', 'content', 'display', 'for_id', 'from_dict', 'id', 'infer_type_from_mime', 'language', 'mime', 'name', 'object_key', 'path', 'persisted', 'remove', 'send', 'size', 'thread_id', 'to_dict', 'type', 'updatable', 'url']
2025-10-02 22:37:25 - AUDIO DIAG: Element dict: {'thread_id': 'c0b813ab-a4a5-44d0-8ae2-957a7f4ca6d2', 'name': 'stives.wav', 'id': 'ffdf0291-86f5-4d55-aebb-6ecd609929c1', 'chainlit_key': 'ffdf0291-86f5-4d55-aebb-6ecd609929c1', 'url': None, 'object_key': None, 'path': 'C:\\Users\\jbras\\Desktop\\chainloot\\.files\\a2e85d9a-43e2-4aac-88e4-00128cf33f5e\\ffdf0291-86f5-4d55-aebb-6ecd609929c1.wav', 'content': None, 'display': 'inline', 'size': None, 'for_id': '18aae1de-5409-4989-bcc3-eb078f793ce6', 'language': None, 'mime': 'audio/wav', 'auto_play': False, 'persisted': True, 'updatable': False}
2025-10-02 22:37:25 - AUDIO DIAG: Audio element content is None for stives.wav
2025-10-02 22:37:25 - AUDIO DIAG: Audio element from path - Name: stives.wav, Path: C:\Users\jbras\Desktop\chainloot\.files\a2e85d9a-43e2-4aac-88e4-00128cf33f5e\ffdf0291-86f5-4d55-aebb-6ecd609929c1.wav, Length: 499244 bytes
2025-10-02 22:37:25 - AUDIO DIAG: Found audio bytes, length: 499244
2025-10-02 22:37:25 - AUDIO DIAG: Calling STT API - Model: openai/whisper-small.en, URL: http://192.168.1.98:7778/v1/, Bytes: 499244
2025-10-02 22:37:27 - HTTP Request: POST http://192.168.1.98:7778/v1/audio/transcriptions "HTTP/1.1 200 OK"
2025-10-02 22:37:27 - AUDIO DIAG: STT response - Text length: 204, Text: 'As I was going to St. Ives, I met a man with seven...'
2025-10-02 22:37:34 - HTTP Request: POST http://192.168.1.98:1234/v1/chat/completions "HTTP/1.1 200 OK"
2025-10-02 22:37:34 - HTTP Request: POST http://192.168.1.98:7778/v1/audio/speech "HTTP/1.1 200 OK"
2025-10-02 22:37:34 - AUDIO DIAG: STT or processing error: peer closed connection without sending complete message body (incomplete chunked read)
```
Not represented here in the log is when I clicked the mic icon and spoke; those events do not appear in this log.

I continue:

Transcribing rdj-spacebar.wav:
```
2025-10-02 22:37:49 - AUDIO DIAG: on_audio_start triggered - Session ID: a2e85d9a-43e2-4aac-88e4-00128cf33f5e
2025-10-02 22:37:52 - AUDIO DIAG: on_audio_end triggered - Session ID: a2e85d9a-43e2-4aac-88e4-00128cf33f5e. Audio will be processed in on_message.
2025-10-02 22:38:42 - AUDIO DIAG: on_message triggered - Session ID: a2e85d9a-43e2-4aac-88e4-00128cf33f5e, Elements count: 1, Content: '...'
2025-10-02 22:38:42 - AUDIO DIAG: Message type: <class 'chainlit.message.Message'>, Elements types: ['Audio']
2025-10-02 22:38:42 - AUDIO DIAG: Processing 1 elements
2025-10-02 22:38:42 - AUDIO DIAG: Element 0: type=Audio, name=rdj-spacebar-cleaned.wav
2025-10-02 22:38:42 - AUDIO DIAG: Element attributes: ['__annotations__', '__class__', '__dataclass_fields__', '__dataclass_params__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__is_pydantic_dataclass__', '__le__', '__lt__', '__match_args__', '__module__', '__ne__', '__new__', '__post_init__', '__pydantic_complete__', '__pydantic_config__', '__pydantic_core_schema__', '__pydantic_decorators__', '__pydantic_fields__', '__pydantic_fields_complete__', '__pydantic_serializer__', '__pydantic_validator__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__signature__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_create', 'auto_play', 'chainlit_key', 'content', 'display', 'for_id', 'from_dict', 'id', 'infer_type_from_mime', 'language', 'mime', 'name', 'object_key', 'path', 'persisted', 'remove', 'send', 'size', 'thread_id', 'to_dict', 'type', 'updatable', 'url']
2025-10-02 22:38:42 - AUDIO DIAG: Element dict: {'thread_id': 'c0b813ab-a4a5-44d0-8ae2-957a7f4ca6d2', 'name': 'rdj-spacebar-cleaned.wav', 'id': 'b841329c-07bb-46e5-8031-0ad274971c13', 'chainlit_key': 'b841329c-07bb-46e5-8031-0ad274971c13', 'url': None, 'object_key': None, 'path': 'C:\\Users\\jbras\\Desktop\\chainloot\\.files\\a2e85d9a-43e2-4aac-88e4-00128cf33f5e\\b841329c-07bb-46e5-8031-0ad274971c13.wav', 'content': None, 'display': 'inline', 'size': None, 'for_id': 'ad25a94d-dcac-4e2e-95fe-18394190566f', 'language': None, 'mime': 'audio/wav', 'auto_play': False, 'persisted': True, 'updatable': False}
2025-10-02 22:38:42 - AUDIO DIAG: Audio element content is None for rdj-spacebar-cleaned.wav
2025-10-02 22:38:42 - AUDIO DIAG: Audio element from path - Name: rdj-spacebar-cleaned.wav, Path: C:\Users\jbras\Desktop\chainloot\.files\a2e85d9a-43e2-4aac-88e4-00128cf33f5e\b841329c-07bb-46e5-8031-0ad274971c13.wav, Length: 390328 bytes
2025-10-02 22:38:42 - AUDIO DIAG: Found audio bytes, length: 390328
2025-10-02 22:38:42 - AUDIO DIAG: Calling STT API - Model: openai/whisper-small.en, URL: http://192.168.1.98:7778/v1/, Bytes: 390328
2025-10-02 22:38:43 - HTTP Request: POST http://192.168.1.98:7778/v1/audio/transcriptions "HTTP/1.1 200 OK"
2025-10-02 22:38:43 - AUDIO DIAG: STT response - Text length: 75, Text: 'Every day the reset button to spacebar gets presse...'
2025-10-02 22:38:45 - HTTP Request: POST http://192.168.1.98:1234/v1/chat/completions "HTTP/1.1 200 OK"
2025-10-02 22:38:45 - HTTP Request: POST http://192.168.1.98:7778/v1/audio/speech "HTTP/1.1 200 OK"
PS C:\Users\jbras\Desktop\chainloot> 
```

End updat.e


ALERT: NO MORE BROWSER-BASED STT! MOVING TO INTERNALLY-HOSTED WHISPER
Pivot on STT: The tts endpoint server now supports openai-compatible speech to text.

Implement Speech to text using Chainlit's integrated microphone widget, send request to 
http://192.168.1.98:7778/v1/audio/transcriptions and then return the transcription to the Chainlit API.
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

