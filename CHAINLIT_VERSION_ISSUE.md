# Chainlit Version Compatibility Issue

## Problem

The initial fix attempted to use `@cl.on_audio_chunk`, which doesn't exist in Chainlit 2.8.1/2.8.2. This caused the application to fail at startup with:

```
File "<frozen importlib._bootstrap_external>", line 995, in exec_module
AttributeError: module 'chainlit' has no attribute 'on_audio_chunk'
```

## Chainlit Version Information

- **Installed Version**: 2.8.1 (per `.chainlit/config.toml`)
- **Issue States**: Version 2.8.2
- **`on_audio_chunk`**: Added in Chainlit 2.9.0 or later (estimate)

## Solutions

### Option 1: Upgrade Chainlit (Recommended)

Upgrade to Chainlit 2.9.0+ which supports the `@cl.on_audio_chunk` decorator:

```bash
pip install --upgrade chainlit
```

Then restore the `on_audio_chunk` implementation that was reverted.

**Pros:**
- Uses the modern, documented API
- Clean, straightforward implementation
- Well-supported approach

**Cons:**
- Requires upgrading dependencies
- May introduce breaking changes in other areas

### Option 2: Use Chainlit's Built-in STT with Custom Provider

Configure Chainlit's built-in STT to use the local Whisper API. This requires:

1. Keeping `speech_to_text.enabled = true` in config
2. Implementing a custom STT provider that Chainlit can use
3. Configuring the provider to point to `http://192.168.1.98:7778/v1/audio/transcriptions`

**Status**: Needs research on Chainlit 2.8.x STT provider API.

### Option 3: Workaround with Available Hooks

Use only the hooks available in 2.8.x (`on_audio_start`, `on_audio_end`, `on_message`):

1. Disable built-in STT (`speech_to_text.enabled = false`)
2. When mic recording finishes, it should send audio as a message element
3. Handle the audio element in `on_message` (like file uploads)

**Issue**: Based on user's logs, mic audio doesn't trigger `on_message` even though file uploads do. This suggests the mic button may not work properly with `speech_to_text.enabled = false`.

### Option 4: Custom Frontend Integration

Implement custom JavaScript to:
1. Capture microphone audio in the browser
2. Send it as a file upload via the existing upload mechanism
3. Process it in `on_message` like other uploaded files

**Reference**: config.toml has commented line: `#custom_js = "/public/react-stt.js"`

This suggests custom JS integration was considered before.

## Current Status

- [x] Reverted `on_audio_chunk` implementation to fix startup crash
- [x] Disabled `speech_to_text.enabled` as first troubleshooting step
- [ ] Waiting for user to test if mic audio now comes through `on_message`
- [ ] Need to determine which solution to implement

## Recommendation

**Best path forward:**

1. **Immediate**: Ask user to upgrade Chainlit to latest version
2. **If upgrade not possible**: Research Chainlit 2.8.x custom STT provider API
3. **Fallback**: Implement custom frontend solution

## Testing Needed

With current changes (`speech_to_text.enabled = false`, no `on_audio_chunk`):

1. Start the app: `chainlit run app.py`
2. Click microphone icon and speak
3. Check if `on_message` is triggered with audio element
4. Check logs for any error messages

## Questions for User

1. Can you upgrade to Chainlit 2.9.0 or later?
2. With the current changes, does the app start successfully?
3. Does clicking the microphone icon still work?
4. Are there any console errors when using the mic?
