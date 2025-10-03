# Fix for Microphone Audio Recording Issue

## Problem Statement

Audio uploaded through the React UI as `.wav` files was successfully transcribed via the local Whisper instance. However, audio recorded through the microphone widget in the Chainlit React UI was not being captured or uploaded for transcription.

### Symptoms:
- ✅ Uploaded `.wav` files worked correctly
- ❌ Microphone recordings did not trigger transcription
- The `on_audio_start` and `on_audio_end` callbacks were triggered
- The `on_message` callback was NOT receiving any audio elements from microphone recordings

## Root Cause

The application was missing the **`@cl.on_audio_chunk`** callback, which is the correct way to handle real-time audio recording from the microphone in Chainlit.

### How Chainlit Handles Audio:

1. **File Uploads (Paperclip Widget):** Audio files uploaded through the UI are delivered as `cl.Audio` elements in the `message.elements` array within the `@cl.on_message` callback.

2. **Microphone Recording (Mic Widget):** Audio recorded from the microphone is delivered as streaming chunks through the `@cl.on_audio_chunk` callback, NOT through `on_message`.

The existing code only implemented:
- `@cl.on_audio_start` - logs when recording starts
- `@cl.on_audio_end` - logs when recording ends
- `@cl.on_message` - handles uploaded files

But was missing:
- `@cl.on_audio_chunk` - **required to capture microphone audio chunks**

## Solution

Added the `@cl.on_audio_chunk` callback to handle microphone audio streaming:

```python
@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.AudioChunk):
    """Handle audio chunks from microphone recording."""
    if chunk.is_start:
        # Initialize audio buffer for new recording
        buffer = []
        cl.user_session.set("audio_buffer", buffer)
        return
    
    # Append audio chunk to buffer
    audio_buffer = cl.user_session.get("audio_buffer")
    if audio_buffer is not None:
        audio_buffer.append(chunk.data)
    
    if chunk.is_end:
        # Combine all chunks and process
        audio_bytes = b"".join(audio_buffer)
        # ... transcribe, send to LLM, generate TTS response
```

### How It Works:

1. **Recording Start (`chunk.is_start`):** Initializes an empty audio buffer in the user session
2. **During Recording:** Each audio chunk is appended to the buffer
3. **Recording End (`chunk.is_end`):** 
   - Combines all chunks into a single audio bytes object
   - Sends to Whisper STT API for transcription
   - Passes transcribed text to LLM
   - Generates TTS response and plays it back

## Changes Made

### File: `app.py`

**Added:** `@cl.on_audio_chunk` callback (lines 450-573)
- Buffers audio chunks during recording
- Processes complete audio when recording ends
- Reuses existing STT, LLM, and TTS logic

**Modified:** `@cl.on_audio_end` callback (line 582)
- Updated log message to reflect that audio is processed in `on_audio_chunk` instead of `on_message`

**Preserved:** All existing functionality
- File upload handling in `on_message` unchanged
- Text message handling unchanged
- TTS generation unchanged
- All settings and configurations unchanged

## Testing Recommendations

### Manual Testing (requires local services running):

1. **Test Microphone Recording:**
   - Click the microphone icon
   - Speak a test phrase
   - Press "P" or click to end recording
   - Verify transcription appears
   - Verify LLM response is generated
   - Verify TTS audio plays

2. **Test File Upload:**
   - Upload a `.wav` file using the paperclip icon
   - Verify transcription appears
   - Verify LLM response is generated
   - Verify TTS audio plays

3. **Test Text Input:**
   - Type a text message
   - Verify LLM response is generated
   - Verify TTS audio plays

## References

- Chainlit Audio Chunk Documentation: https://docs.chainlit.io/api-reference/lifecycle-hooks/on-audio-chunk
- Implementation reference: `whisper-task.md` (lines 83-97)
- Chainlit version: 2.8.2 (as specified in issue)

## Key Insights

The distinction between file uploads and microphone recording in Chainlit is critical:
- **File uploads** → `on_message` with `message.elements`
- **Microphone recording** → `on_audio_chunk` with streaming chunks

This is a common pattern in web audio applications where real-time recording is handled differently from file I/O for performance and latency reasons.
