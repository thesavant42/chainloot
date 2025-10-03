# Audio Processing Flow Diagram

## Before Fix (Broken)

```
┌─────────────────────────────────────────────────────────────┐
│                    Chainlit React UI                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐              ┌───────────────┐           │
│  │ Paperclip    │              │ Microphone    │           │
│  │ (Upload WAV) │              │ (Record)      │           │
│  └──────┬───────┘              └───────┬───────┘           │
│         │                               │                    │
└─────────┼───────────────────────────────┼────────────────────┘
          │                               │
          │                               │ Audio Chunks
          │ File Upload                   │ (NOT CAPTURED!)
          │                               ▼
          │                        ┌──────────────────┐
          │                        │ @cl.on_audio_start│◄─── Logs only
          │                        └──────────────────┘
          │                               │
          │                        ┌──────────────────┐
          ▼                        │ @cl.on_audio_end │◄─── Logs only
   ┌─────────────┐                └──────────────────┘
   │ @cl.on_message│                      │
   │             │                        │
   │ ✅ Receives  │                        ▼
   │ Audio Element│                  ❌ No Audio Data!
   │             │                  (Audio lost)
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Whisper STT │
   │ ✅ Works!    │
   └─────────────┘
```

## After Fix (Working)

```
┌─────────────────────────────────────────────────────────────┐
│                    Chainlit React UI                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐              ┌───────────────┐           │
│  │ Paperclip    │              │ Microphone    │           │
│  │ (Upload WAV) │              │ (Record)      │           │
│  └──────┬───────┘              └───────┬───────┘           │
│         │                               │                    │
└─────────┼───────────────────────────────┼────────────────────┘
          │                               │
          │                               │ Audio Chunks
          │ File Upload                   │ (NOW CAPTURED!)
          │                               ▼
          │                        ┌──────────────────┐
          │                        │ @cl.on_audio_chunk│
          │                        │                  │
          │                        │ if is_start:     │
          │                        │   init buffer    │
          │                        │ else:            │
          │                        │   append chunk   │
          │                        │ if is_end:       │
          │                        │   process audio  │
          │                        └────────┬─────────┘
          │                                 │
          │                          ✅ Audio Buffer
          │                                 │
          ▼                                 ▼
   ┌─────────────┐              ┌─────────────────┐
   │ @cl.on_message│             │ Whisper STT     │
   │             │              │ ✅ Transcribes   │
   │ ✅ Receives  │              └────────┬────────┘
   │ Audio Element│                       │
   │             │                        │
   └──────┬──────┘                        │
          │                               │
          │                               │
          ▼                               ▼
   ┌─────────────┐              ┌────────────────┐
   │ Whisper STT │              │ Transcribed    │
   │ ✅ Works!    │              │ Text           │
   └─────────────┘              └────────┬───────┘
          │                               │
          │                               │
          ▼                               ▼
   ┌──────────────────────────────────────────┐
   │            LLM (LM Studio)               │
   │         Generates Response               │
   └──────────────┬───────────────────────────┘
                  │
                  ▼
   ┌──────────────────────────────────────────┐
   │         TTS (Chatterbox)                 │
   │         Generates Audio                  │
   │         🔊 Auto-plays                    │
   └──────────────────────────────────────────┘
```

## Key Implementation Details

### Audio Chunk Handler

```python
@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.AudioChunk):
    if chunk.is_start:
        # Initialize buffer
        cl.user_session.set("audio_buffer", [])
    
    elif chunk.is_end:
        # Process complete audio
        audio_bytes = b"".join(cl.user_session.get("audio_buffer"))
        
        # 1. Transcribe with Whisper
        transcription = stt_client.audio.transcriptions.create(...)
        
        # 2. Send to LLM
        response = await client.chat.completions.create(...)
        
        # 3. Generate TTS
        tts_audio = await tts_client.audio.speech.create(...)
        
    else:
        # Accumulate chunks
        cl.user_session.get("audio_buffer").append(chunk.data)
```

## Audio Element Types

### 1. File Upload (Paperclip Widget)
- **Source**: User uploads a `.wav` file
- **Handler**: `@cl.on_message`
- **Arrives as**: `cl.Audio` element in `message.elements`
- **Content**: Available via `element.path` or `element.content`
- **Status**: ✅ Always worked

### 2. Microphone Recording (Mic Widget)
- **Source**: User records audio via browser microphone
- **Handler**: `@cl.on_audio_chunk` ⚠️ (was missing!)
- **Arrives as**: Streaming `cl.AudioChunk` objects
- **Content**: `chunk.data` bytes that must be buffered
- **Status**: ✅ Now works with fix

## Workflow Comparison

### File Upload Path
```
User uploads WAV
    ↓
@cl.on_message triggered
    ↓
Read from element.path or element.content
    ↓
Send to Whisper STT
    ↓
Process response
```

### Microphone Recording Path
```
User clicks mic icon
    ↓
@cl.on_audio_chunk (is_start=True)
    ↓
User speaks
    ↓
@cl.on_audio_chunk (multiple times)
    ↓
User ends recording
    ↓
@cl.on_audio_chunk (is_end=True)
    ↓
Combine buffered chunks
    ↓
Send to Whisper STT
    ↓
Process response
```

## Why Two Different Paths?

1. **Performance**: Streaming audio requires real-time buffering, while file uploads are already complete
2. **Browser API**: WebRTC/MediaRecorder APIs stream chunks, while file inputs provide complete files
3. **User Experience**: Microphone recording shows real-time feedback (waveform), while file upload is instantaneous
4. **Network Efficiency**: Streaming can support low-latency VAD (Voice Activity Detection) in the future

## Testing the Fix

### Test 1: Microphone Recording (Primary Fix)
```
1. Click microphone icon
2. Speak: "Test microphone recording"
3. Click to stop recording
4. Expected: 
   - Transcription appears
   - LLM responds
   - TTS plays automatically
```

### Test 2: File Upload (Regression Test)
```
1. Click paperclip icon
2. Upload stives.wav
3. Expected:
   - Transcription appears
   - LLM responds
   - TTS plays automatically
```

### Test 3: Text Input (Regression Test)
```
1. Type: "Hello, how are you?"
2. Press Enter
3. Expected:
   - LLM responds
   - TTS plays automatically
```

## Debugging Tips

If microphone recording still doesn't work after the fix:

1. **Check browser permissions**: Microphone access must be granted
2. **Check browser console**: Look for WebRTC errors or permission issues
3. **Check Chainlit logs**: Should see "AUDIO DIAG: on_audio_chunk START/END"
4. **Check audio format**: Browser should send PCM/WAV compatible data
5. **Check Whisper API**: Test with `curl` using test_stt.md instructions
6. **Check sample rate**: Config shows 24000 Hz (verify browser matches)

## Related Files

- `app.py`: Main implementation with `@cl.on_audio_chunk` callback
- `.chainlit/config.toml`: Audio configuration (sample_rate, enabled flags)
- `FIX_DOCUMENTATION.md`: Detailed explanation of the fix
- `whisper-task.md`: Original implementation reference
- `test_stt.md`: Testing instructions for Whisper API
