# Local Whisper API Service integrartion

I am aiming to build a **real-time conversational AI** that runs entirely on your local network. The user interacts by speaking, and the AI responds with synthesized speech. I've identified the three main stages of this process:

1.  **Speech-to-Text (STT):** Capturing the user's voice with Chainlit, sending it to your local Whisper server, and getting the transcribed text back.
2.  **LLM Inference:** Sending the transcribed text to your local Large Language Model (hosted via LM Studio) to generate a response.
3.  **Text-to-Speech (TTS):** Sending the LLM's text response to your local TTS server to generate audio.

The core of the project is adapting the cloud-based Chainlit Whisper example to use your local, OpenAI-compatible APIs. This is a very practical and well-defined goal.

-----

## Implementation Outline

Here is a step-by-step guide to bring your "Local Whisper" project to life, based on the structure of the Chainlit cookbook example.

### 1\. Project Setup

~~First, prepare your development environment.~~ DONE!

  * **Clone the Repository:** If you haven't already, clone your `chainloot` repository to your local machine.
  * **Create a Virtual Environment:** It's best practice to isolate your project's dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
  * **Install Libraries:** Install Chainlit and the OpenAI Python client.
    ```bash
    pip install chainlit openai
    ```

### 2\. Verify Your Local Endpoints

    OpenAI-Compatible Text to Speech  (TTS) API:    http://192.168.1.98:7778/v1/audio/speech
    OpenAI-Compatible Whisper (STT) API:            http://192.168.1.98:7778/v1/audio/transcriptions
    TTS-WebUI Audio Models List (chatterbox)        http://192.168.1.98:7778/v1/audio/models
    List Voices API (chatterbox-tts):               http://192.168.1.98:7778/v1/audio/voices
    LM Studio - List Models (LM Studio api):        http://192.168.1.98:1234/api/v0/models
    LM Studio - (OpenAPI) Chat Completion API:      http://192.168.1.98:1234/v1

### 3\. Write the Chainlit Application

Create a Python file (e.g., `app.py`) in your repository. The logic will involve initializing two separate `OpenAI` clients—one for your LLM and another for your audio services, since they are on different ports.

Here's a general code structure to follow. We will want to preserve the existing functionality used to select model, voice, sampler parameters, prompt, character, etc. But this example outlines all of the components in general required to complete the task.

```python
import chainlit as cl
from openai import OpenAI
from pathlib import Path

# --- API Client Configuration ---

# Client for LM Studio (Chat Completions)
# The API key can be anything, but it's required.
llm_client = OpenAI(
    base_url="http://192.168.1.98:1234/v1",
    api_key="lm-studio",
)

# Client for TTS/STT Server
# The API key can be anything, but it's required.
audio_client = OpenAI(
    base_url="http://192.168.1.98:7778/v1",
    api_key="local-audio",
)

# --- Chainlit App Logic ---

@cl.on_chat_start
async def start():
    await cl.Message(content="Welcome! Record a message to start the conversation.").send()

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.AudioChunk):
    # This function is called when an audio recording is finished.
    if chunk.is_start:
        # Prepare a buffer to store audio bytes
        cl.user_session.set("audio_buffer", [chunk.data])
        return

    # Append subsequent chunks to the buffer
    cl.user_session.get("audio_buffer").append(chunk.data)

    if chunk.is_end:
        # Audio recording is complete, process the whole audio
        audio_bytes = b"".join(cl.user_session.get("audio_buffer"))
        audio_file = (f"temp_audio_{cl.user_session.get('id')}.wav", audio_bytes)
        
        # --- 1. Speech-to-Text (STT) ---
        transcription_response = audio_client.audio.transcriptions.create(
            model="whisper-1", # Model name might not matter for your local server
            file=audio_file,
        )
        user_text = transcription_response.text
        
        # Display the transcribed text to the user
        await cl.Message(author="You", content=user_text, author_is_user=True).send()
        
        # --- 2. LLM Inference ---
        msg = cl.Message(author="Assistant", content="")
        await msg.send()

        stream = llm_client.chat.completions.create(
            model="your-local-model-name", # Replace with your model identifier from LM Studio
            messages=[{"role": "user", "content": user_text}],
            stream=True,
        )

        full_response = ""
        for part in stream:
            token = part.choices[0].delta.content or ""
            full_response += token
            await msg.stream_token(token)
        
        await msg.update()

        # --- 3. Text-to-Speech (TTS) ---
        tts_response = audio_client.audio.speech.create(
            model="tts-1", # Model name might not matter
            voice="your-chosen-voice", # Replace with a valid voice
            input=full_response,
        )

        # Convert the audio response to bytes and send to the UI
        audio_bytes = tts_response.read()
        await cl.Message(
            author="Assistant",
            elements=[
                cl.Audio(
                    name="response.mp3",
                    content=audio_bytes,
                    auto_play=True, # Set to True to play automatically
                )
            ]
        ).send()

```

**Key adjustments in the code:**

  * **`llm_client` and `audio_client`**: We define two separate clients because your services are hosted on different ports (`1234` and `7778`).
  * **Model Names**: Replace `"your-local-model-name"` and `"your-chosen-voice"` with the actual identifiers your local servers expect. Even if the server only has one model loaded, the API often still requires a value in that field.
  * **`cl.on_audio_chunk`**: This is a more modern way to handle audio in Chainlit compared to the older cookbook example. It captures the audio stream chunk by chunk and processes it once the recording is finished.
  * **`auto_play=True`**: This makes the experience much more conversational, as the user doesn't have to manually press play on the audio response.

### 4\. Run the Application

1.  Make sure all your local servers (LM Studio, TTS-WebUI) are running.
2.  Open your terminal in the project directory.
3.  Run the Chainlit app:
    ```bash
    chainlit run app.py
    ```
    
4.  Open your browser to the address provided by Chainlit (usually `http://localhost:8000`) and start talking\! 
