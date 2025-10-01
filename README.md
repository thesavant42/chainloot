
# chainloot

Customized Chainlit stack for Yoda Robot

## Goal 
Goal is to unify and simplify the architecture required to run the Robot

- [x] Should support hot swapping of different models hosted on LM Studio
- [ ] Should support a prompt catalog for hot swapping "roles", AI assistant vs. roleplaying character
- [ ] Should support character profiles, to change the chat participants
- [x] Should support TTS-WebUI API Integration
- [ ] Should support multi-modal functionality, for image recognition and tool usage.
    - [x] Reasoning should be a checkbox toggle, disabled by default
- [x] Should have widgets to adjust sampler settings for text response on the fly
- [ ] Should have widgets to adjust sampler settings for speech on the fly
- [x] Should be able to select from available voices via a drop-down selector text-input
- [ ] Should Integrate Whisper-like ASR (Automatic Speech Recognition)

## Status
Currently have a few models hard coded into app.py for some quick testing. The better way to do it would be to query http://192.168.1.98:1234/api/v0/models

## Structure

chainlit/ Top Level Directory
- docs/                             # Folder for documentation and support files, API schema docs
- docs/chatterbox-openapi.json      # Minimal OpenAI-compatible TTS API docs
- docs/gradioopenapi.json           # Detailed Gradio TTS API docs
- ./README.md                       # This file
- ./app.py                          # Man chainlit app code
- ./.env                            # API keys go here (if needed)

## Open Questions

- Q: How can I populate the dropdown list of models in app.py from http://192.168.1.98:1234/api/v0/models ? The endpoint yields results similar to the following:

```json
{
  "data": [
    {
      "id": "qwen3-4b-instruct-2507",
      "object": "model",
      "type": "llm",
      "publisher": "unsloth",
      "arch": "qwen3",
      "compatibility_type": "gguf",
      "quantization": "Q4_K_S",
      "state": "loaded",
      "max_context_length": 262144,
      "loaded_context_length": 128000,
      "capabilities": [
        "tool_use"
      ]
    },
    {
      "id": "text-embedding-nomic-embed-text-v1.5",
      "object": "model",
      "type": "embeddings",
      "publisher": "nomic-ai",
      "arch": "nomic-bert",
      "compatibility_type": "gguf",
      "quantization": "Q4_K_M",
      "state": "not-loaded",
      "max_context_length": 2048
    },
    {
      "id": "phi-4-mini-instruct",
      "object": "model",
      "type": "llm",
      "publisher": "unsloth",
      "arch": "phi3",
      "compatibility_type": "gguf",
      "quantization": "Q4_K_M",
      "state": "not-loaded",
      "max_context_length": 131072
    },
    {
      "id": "qwen/qwen3-14b",
      "object": "model",
      "type": "llm",
      "publisher": "qwen",
      "arch": "qwen3",
      "compatibility_type": "gguf",
      "quantization": "Q4_K_M",
      "state": "not-loaded",
      "max_context_length": 32768,
      "capabilities": [
        "tool_use"
      ]
    },
    {
      "id": "text-embedding-mxbai-embed-large-v1",
      "object": "model",
      "type": "embeddings",
      "publisher": "mixedbread-ai",
      "arch": "bert",
      "compatibility_type": "gguf",
      "quantization": "F16",
      "state": "not-loaded",
      "max_context_length": 512
    },
    {
      "id": "qwen/qwen3-8b",
      "object": "model",
      "type": "llm",
      "publisher": "qwen",
      "arch": "qwen3",
      "compatibility_type": "gguf",
      "quantization": "Q4_K_M",
      "state": "not-loaded",
      "max_context_length": 32768,
      "capabilities": [
        "tool_use"
      ]
    }
  ],
  "object": "list"
}
```

A: <TBD>

Q: Is there an API endpoint from Chatterbox or TTS-WebUI that enumerates the voice list? This can be used to populate a dropdown for rapidly changing voice samples.

A: <TBD>

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

### TTS Sampler Settings

Here's config.json from a circuitpython project with similar goals, this can serve as the source of truth for the sampler settings. 

```
{
  "lm_studio_base_url": "http://192.168.1.98:1234/v1",
  "api_key": "sk-12345",
  "last_used_model": "smollm2-ft-masteryoda-motih",
  "logging_enabled": false,
  "sd_card_path": "/sd",
  "tts_base_url": "http://192.168.1.98:7778",
  "tts_model_name": "chatterbox",
  "tts_voice": "voices/chatterbox/whywishnotfar.wav",
  "tts_exaggeration": 0.5,
  "tts_cfg_weight": 0.5,
  "tts_temperature": 1.4,
  "tts_device": "cuda",
  "tts_dtype": "float32",
  "tts_seed": -1,
  "tts_chunked": true,
  "tts_response_format": "wav",
  "tts_speed": 1,
  "tts_stream": true,
  "tts_use_compilation": true,
  "tts_max_new_tokens": 1000,
  "tts_max_cache_len": 1500,
  "tts_desired_length": 100,
  "tts_max_length": 300
}
```


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

