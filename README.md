
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
Status: Working on STT / ASR. Trying to hook the microphone button to trigger the browser microphone API.

Bug in mirophone detection

```
16:18:31.313 index.mjs:219 Uncaught (in promise) Error: Session ended: please call .begin() first
    at CTe.end (index.mjs:219:1775)
    at Zae.<anonymous> (index.mjs:308:15931)
    at ca.emit (index.mjs:136:20)
    at Zae.emitEvent (socket.js:498:20)
    at Zae.onevent (socket.js:485:18)
    at Zae.onpacket (socket.js:455:22)
    at ca.emit (index.mjs:136:20)
    at manager.js:204:18
end @ index.mjs:219
(anonymous) @ index.mjs:308
ca.emit @ index.mjs:136
emitEvent @ socket.js:498
onevent @ socket.js:485
onpacket @ socket.js:455
ca.emit @ index.mjs:136
(anonymous) @ manager.js:204
Promise.then
(anonymous) @ websocket-constructor.browser.js:5
ondecoded @ manager.js:203
ca.emit @ index.mjs:136
add @ index.js:146
ondata @ manager.js:190
ca.emit @ index.mjs:136
onPacket @ socket.js:341
ca.emit @ index.mjs:136
onPacket @ transport.js:98
onData @ transport.js:90
ws.onmessage @ websocket.js:68
```
``

--
- Models can now be dynamically refreshed, selected from the dropdown in the settings menu
- Voices can now be swapped from the settings menu
- Prompt catalog is mostly stub functionality. Ideal state would be a text box entry form to manually enter and edit prompts, or delete them.
- Current character profile changing is mostly a stub. Same as above, would prefer a text edit form to update and delete profiles.
- Whisper ASR integration needs more investigation. TTS-WebUI has whisper integration built in, but it's not clear to me if they support streams in that implementation.
- Multimodal functionality will require some consideration and careful design, with good test cases.

![model_settings](https://github.com/thesavant42/chainloot/blob/main/docs/model-settings.png?raw=true)
## Structure

chainlit/ Top Level Directory
- docs/                             # Folder for documentation and support files, API schema docs
- docs/chatterbox-openapi.json      # Minimal OpenAI-compatible TTS API docs
- docs/gradioopenapi.json           # Detailed Gradio TTS API docs
- ./README.md                       # This file
- ./app.py                          # Man chainlit app code
- ./.env                            # API keys go here (if needed)

## Open Questions

Q: Is there a way to utilize the Whisper service in TTS-WebUI for Speech to text in Chainlit?

A: <TBD>

## Components

### TTS-WEBUI Local Servers:

-  Gradio UI at http://192.168.1.98:7770
-  React UI at http://192.168.1.98:3000.

### Chatterbox TTS Endpoint

- http://192.168.1.98:7778/v1/audio/speech - OpenAI compatible TTS endpoint

Windows-curl friendly TTS Test string

```
 curl -X POST http://192.168.1.98:7778/v1/audio/speech -H "Content-Type: application/json" -d '{"model":"chatterbox","input":"Hello world! This is a streaming test.","voice":"random","stream":true}' --proxy http://127.0.0.1:8080
 ```

### LM Studio Server
- http://192.168.1.98:1234/ - base URL
- http://192.168.1.98:1234/v1 - OpenAPI Compatible endpoints base

## External Docs

### Chainlit Docs

- https://docs.chainlit.io/get-started/overview

### Chainlit API Reference

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

