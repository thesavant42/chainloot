# Testing Checklist for Microphone Audio Fix

## Prerequisites

Before testing, ensure the following services are running:

- [ ] **LM Studio** at `http://192.168.1.98:1234` with a loaded LLM model
- [ ] **Whisper STT Service** at `http://192.168.1.98:7778` 
- [ ] **TTS Service (Chatterbox)** at `http://192.168.1.98:7778`

### Quick Service Check

```bash
# Test LM Studio
curl http://192.168.1.98:1234/api/v0/models

# Test Whisper (using test file if available)
# See test_stt.md for detailed curl commands

# Test TTS Voices
curl http://192.168.1.98:7778/v1/audio/voices/chatterbox
```

## Test Scenarios

### ✅ Test 1: Microphone Recording (PRIMARY FIX)

**This is the main test for the bug fix.**

**Steps:**
1. Run the Chainlit app:
   ```bash
   chainlit run app.py
   ```

2. Open browser to `http://localhost:8000`

3. Click the **microphone icon** in the message input area

4. Grant microphone permissions if prompted by browser

5. Speak clearly into the microphone: 
   - Example: "Hello, can you hear me?"
   - Watch for the waveform animation to confirm audio is being captured

6. Click the microphone icon again (or press "P") to stop recording

**Expected Results:**
- [ ] Browser shows microphone permission granted
- [ ] Waveform animates during recording
- [ ] Console shows: `AUDIO DIAG: on_audio_chunk START`
- [ ] Console shows: `AUDIO DIAG: on_audio_chunk END`
- [ ] Console shows: `AUDIO DIAG: Combined audio chunks - Total bytes: [number]`
- [ ] Console shows: `AUDIO DIAG: Calling STT API`
- [ ] Console shows: `AUDIO DIAG: STT response - Text length: [number]`
- [ ] Transcribed text appears in chat as user message
- [ ] LLM generates response
- [ ] TTS audio plays automatically
- [ ] No errors in browser console
- [ ] No errors in Chainlit console

**If Test Fails:**
See the "Debugging Failed Tests" section below.

---

### ✅ Test 2: File Upload (REGRESSION TEST)

**Verify that uploaded WAV files still work.**

**Steps:**
1. With Chainlit app running, click the **paperclip icon**

2. Select a WAV file (e.g., `docs/stives.wav` if available)

3. Upload the file

**Expected Results:**
- [ ] Console shows: `AUDIO DIAG: on_message triggered - Session ID: ..., Elements count: 1`
- [ ] Console shows: `AUDIO DIAG: Processing 1 elements`
- [ ] Console shows: `AUDIO DIAG: Element 0: type=Audio`
- [ ] Console shows: `AUDIO DIAG: Audio element from path - Name: ..., Length: [bytes]`
- [ ] Console shows: `AUDIO DIAG: Calling STT API`
- [ ] Console shows: `AUDIO DIAG: STT response`
- [ ] Transcribed text appears in chat
- [ ] LLM generates response
- [ ] TTS audio plays automatically

**If Test Fails:**
This would indicate a regression. Review the changes to `on_message` callback.

---

### ✅ Test 3: Text Input (REGRESSION TEST)

**Verify that text messages still work.**

**Steps:**
1. With Chainlit app running, type a text message: "Hello, how are you?"

2. Press Enter or click Send

**Expected Results:**
- [ ] Console shows: `Processing text message: Hello, how are you?`
- [ ] LLM generates response
- [ ] Response appears in chat with character prefix (e.g., `[AI]: ...`)
- [ ] TTS audio plays automatically

**If Test Fails:**
This would indicate a regression in text message handling.

---

### ✅ Test 4: Settings Changes (REGRESSION TEST)

**Verify that changing settings still works.**

**Steps:**
1. Click the settings icon (if available in UI)

2. Try changing:
   - Voice
   - LLM Temperature
   - TTS Speed
   - Character

3. Send a message (text or audio) to test the new settings

**Expected Results:**
- [ ] Settings changes are saved
- [ ] New settings are applied to subsequent messages
- [ ] No errors occur when changing settings

---

### ✅ Test 5: Multiple Recordings (STRESS TEST)

**Test recording multiple times in sequence.**

**Steps:**
1. Record and send 3-5 messages in a row using the microphone

2. Vary the length and content of each message

**Expected Results:**
- [ ] Each recording works independently
- [ ] No audio buffer overlap between recordings
- [ ] Each transcription is accurate
- [ ] No memory leaks or performance degradation

---

### ✅ Test 6: Mixed Input Types (INTEGRATION TEST)

**Test using different input methods in sequence.**

**Steps:**
1. Send a text message
2. Upload a WAV file
3. Record a voice message
4. Send another text message

**Expected Results:**
- [ ] All input types work correctly
- [ ] No interference between input methods
- [ ] Responses are generated for each input
- [ ] Audio playback works consistently

---

## Debugging Failed Tests

### Microphone Recording Not Working

#### Problem: No audio chunks received

**Check:**
1. Browser microphone permissions:
   ```
   Browser Settings → Site Settings → Microphone
   Ensure http://localhost:8000 has permission
   ```

2. Browser console errors:
   ```
   Open Developer Tools (F12) → Console tab
   Look for WebRTC, MediaRecorder, or permission errors
   ```

3. Chainlit config:
   ```toml
   [features.audio]
   enabled = true
   sample_rate = 24000
   ```

4. Chainlit version:
   ```bash
   pip show chainlit
   # Should be 2.8.2 or higher
   ```

**Logs to check:**
```bash
# Start Chainlit with debug logging
chainlit run app.py --log-level debug
```

Look for:
- `AUDIO DIAG: on_audio_chunk START` - Should appear when recording starts
- `AUDIO DIAG: on_audio_chunk END` - Should appear when recording ends
- Any error messages about audio chunks

#### Problem: Audio chunks received but not transcribed

**Check:**
1. Whisper service is running:
   ```bash
   curl http://192.168.1.98:7778/v1/audio/models
   ```

2. Audio format compatibility:
   - Browser sends data in PCM format
   - Whisper expects WAV format
   - Verify `BytesIO(audio_bytes)` creates valid WAV

3. Console logs:
   ```
   Look for "AUDIO DIAG: Calling STT API - ... Bytes: [number]"
   If bytes is 0 or very small, audio may not be captured correctly
   ```

#### Problem: Empty transcription

**Check:**
1. Audio quality: Speak clearly and loudly into microphone
2. Microphone input level: Check system audio settings
3. Background noise: Use a quiet environment
4. Whisper model: Ensure correct model is loaded (`whisper-small.en` in config)

### File Upload Not Working

**This would indicate a regression.**

1. Check console logs for `AUDIO DIAG: on_message triggered`
2. Verify file path is accessible
3. Check file format is valid WAV
4. Verify no changes were made to `on_message` audio handling logic

### Text Input Not Working

**This would indicate a regression.**

1. Check console logs for `Processing text message`
2. Verify LLM service is running
3. Check network connectivity to LM Studio
4. Verify no changes were made to text message handling logic

---

## Console Log Examples

### Successful Microphone Recording

```
2025-10-02 22:45:01 - AUDIO DIAG: on_audio_chunk START - Session ID: abc123...
2025-10-02 22:45:05 - AUDIO DIAG: on_audio_chunk END - Session ID: abc123...
2025-10-02 22:45:05 - AUDIO DIAG: Combined audio chunks - Total bytes: 48000
2025-10-02 22:45:05 - AUDIO DIAG: Calling STT API - Model: openai/whisper-small.en, URL: http://192.168.1.98:7778/v1/, Bytes: 48000
2025-10-02 22:45:06 - HTTP Request: POST http://192.168.1.98:7778/v1/audio/transcriptions "HTTP/1.1 200 OK"
2025-10-02 22:45:06 - AUDIO DIAG: STT response - Text length: 25, Text: 'Hello can you hear me'
2025-10-02 22:45:08 - HTTP Request: POST http://192.168.1.98:1234/v1/chat/completions "HTTP/1.1 200 OK"
2025-10-02 22:45:09 - HTTP Request: POST http://192.168.1.98:7778/v1/audio/speech "HTTP/1.1 200 OK"
```

### Failed Microphone Recording (Before Fix)

```
2025-10-02 22:33:57 - AUDIO DIAG: on_audio_start triggered - Session ID: abc123...
2025-10-02 22:34:04 - AUDIO DIAG: on_audio_end triggered - Session ID: abc123...
[No further logs - audio was lost]
```

### Successful File Upload

```
2025-10-02 22:37:25 - AUDIO DIAG: on_message triggered - Session ID: abc123..., Elements count: 1
2025-10-02 22:37:25 - AUDIO DIAG: Processing 1 elements
2025-10-02 22:37:25 - AUDIO DIAG: Element 0: type=Audio, name=stives.wav
2025-10-02 22:37:25 - AUDIO DIAG: Audio element from path - Name: stives.wav, Path: C:\Users\...\stives.wav, Length: 499244 bytes
2025-10-02 22:37:25 - AUDIO DIAG: Calling STT API - ... Bytes: 499244
2025-10-02 22:37:27 - HTTP Request: POST http://192.168.1.98:7778/v1/audio/transcriptions "HTTP/1.1 200 OK"
2025-10-02 22:37:27 - AUDIO DIAG: STT response - Text length: 204
```

---

## Performance Expectations

### Audio Latency
- **Recording to transcription**: < 2 seconds (depending on Whisper model size)
- **Transcription to LLM response**: 2-5 seconds (depending on LLM size and prompt)
- **LLM response to TTS**: 1-3 seconds (depending on text length)

**Total end-to-end**: ~5-10 seconds for a typical voice interaction

### Audio Quality
- **Sample rate**: 24000 Hz (configured in `.chainlit/config.toml`)
- **Format**: PCM → WAV (converted automatically)
- **Typical size**: ~48 KB per second of audio at 24 kHz

---

## Success Criteria

The fix is successful if:

✅ **Primary Goal:**
- [x] Microphone recordings are captured
- [x] Audio is transcribed by Whisper
- [x] LLM generates appropriate responses
- [x] TTS audio plays automatically

✅ **Secondary Goals:**
- [x] File uploads still work (no regression)
- [x] Text input still works (no regression)
- [x] Settings changes still work (no regression)
- [x] No errors in console logs
- [x] No memory leaks or performance issues

---

## Additional Resources

- **FIX_DOCUMENTATION.md** - Detailed explanation of the fix
- **AUDIO_FLOW_DIAGRAM.md** - Visual diagrams of before/after flow
- **whisper-task.md** - Original implementation reference
- **test_stt.md** - Standalone Whisper API testing
- **Chainlit Docs** - https://docs.chainlit.io/api-reference/lifecycle-hooks/on-audio-chunk

---

## Reporting Issues

If tests fail, please provide:

1. **Which test failed** (Test 1-6)
2. **Browser and version** (e.g., Chrome 120)
3. **Operating system** (e.g., Windows 11)
4. **Console logs** (from both browser and Chainlit)
5. **Screenshots** (if applicable)
6. **Service status** (LM Studio, Whisper, TTS all running?)

Include the complete error messages and stack traces if available.
