
# chainloot

customized chainlit stack for yoda Robot

## Goal 
Goal is to unify and simplify the architecture required to run the Robot

-- [] Should Support hot swapping of different models hosted on LM Studio
-- [] Should support a prompt catalog for hot swapping "roles", ai assistant vs. roleplaying character
-- [] Should support character profiles, to change the chat participants
-- [] should support TTS-WebUI API Integration
-- [] Should support multi-modal functionality, for image recognition and tool usage.
  -- [] Reasoning should be a checkbox toggle, disabled by default
-- [] Should have widgets to adjust sampler settings for text response on the fly
-- [] Should have widgets to adjust sampler settings for speech on the fly
-- [] Should be able to select from available voices via a drop-down selector text-input
-- [] Should Integrate Whisper-like ASR Automatic Speech Recognition

## Status


## Structure

chainlit/ Top Level Directory
- docs/                             # Folder for documentation and support files, API schema docs
- docs/chatterbox-openapi.json      # Minimal OpenAI-compatible TTS API docs
- docs/gradioopenapi.json           # Detailed Gradio TTS API docs
- ./README.md                       # This file
- ./app.py                          # Man chainlit app code
- ./.env                            # API keys go here (if needed)




More Info:

Chainlit Docs
https://docs.chainlit.io/get-started/overview

Chainlit API Reference 
https://docs.chainlit.io/api-reference/lifecycle-hooks/on-chat-start

https://docs.chainlit.io/api-reference/lifecycle-hooks/on-audio-chunk
https://docs.chainlit.io/api-reference/lifecycle-hooks/on-audio-end
https://docs.chainlit.io/api-reference/chat-profiles
https://docs.chainlit.io/api-reference/chat-settings
https://docs.chainlit.io/api-reference/action
https://docs.chainlit.io/api-reference/elements/audio
https://docs.chainlit.io/api-reference/integrations/langchain
