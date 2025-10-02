import os
from dotenv import load_dotenv
import requests
import json
from openai import AsyncOpenAI
import asyncio
import chainlit as cl
from fastapi import Request
from fastapi.responses import JSONResponse
from chainlit.server import app
from chainlit.user_session import user_sessions
from io import BytesIO
from chainlit.input_widget import Select, Slider, Switch
import sys

load_dotenv()

# Load config.json
config_path = 'config.json'

try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    print(f"Error: Failed to load {config_path}. Exiting.")
    sys.exit(1)

LM_STUDIO_URL = config["lm_studio_base_url"].rstrip('/v1')
CHATTERBOX_URL = config["tts_base_url"]
TTS_WEBUI_URL = config["tts_webui_url"]

# Fetch available voices for Chatterbox dynamically from API
try:
    voices_response = requests.get(f"{CHATTERBOX_URL}/v1/audio/voices/chatterbox")
    voices_response.raise_for_status()
    voices_data = voices_response.json()
    #print(f"Fetched voices data: {voices_data}")  # Debug log
    available_voices = [v["value"] for v in voices_data["voices"]]
    if config["tts_voice"] not in available_voices:
        print(f"Warning: Config voice {config['tts_voice']} not in available voices. Using first available.")
        config["tts_voice"] = available_voices[0] if available_voices else config["tts_voice"]
except Exception as e:
    voices_data = [{"value": config["tts_voice"], "label": config["tts_voice"]}]
    available_voices = [config["tts_voice"]]
    print(f"Warning: Could not fetch voices from API: {e}. Using config voice.")

tts_model = config["tts_model_name"]
tts_voice = config["tts_voice"]
print(f"Using TTS voice: {tts_voice}")

# Fetch available LLM models dynamically
def fetch_available_models():
    try:
        response = requests.get(f"{LM_STUDIO_URL}/api/v0/models")
        response.raise_for_status()
        models_data = response.json()["data"]
        return [m["id"] for m in models_data if m["type"] == "llm"]
    except Exception as e:
        raise Exception(f"Could not fetch models from LM Studio: {e}")


available_models = fetch_available_models()


api_key = os.getenv("LM_API_KEY", config["api_key"])
client = AsyncOpenAI(base_url=f"{LM_STUDIO_URL}/v1", api_key=api_key)
tts_client = AsyncOpenAI(base_url=f"{CHATTERBOX_URL}/v1", api_key=api_key)
# Instrument the OpenAI client
cl.instrument_openai()

# Defaults from config
default_llm_temp = 0.0
default_max_tokens = 1000
default_tts_speed = config["tts_speed"]
default_tts_exaggeration = config["tts_exaggeration"]
default_tts_voice = config["tts_voice"]
default_tts_model = config["tts_model_name"]
default_tts_response_format = config["tts_response_format"]
default_tts_stream = config["tts_stream"]

# Prompt catalog
prompt_catalog = {
    "AI": "You are a 3-P-O, a helpful AI assistant. Your responses are concise and brief. No more than 2 sentences per message.",
    "Yoda": "You are Yoda, wise Jedi Master. Reply in Yoda-speak. No more than 2 sentences per message.",
    "Stark": "You are a helpful but snarky AI assistant. Your name is Tony. No more than 2 sentences per message."
}

# Character profiles for chat participants
character_options = ["AI", "Yoda", "Stark"]

settings = {
    "temperature": default_llm_temp,
    "max_tokens": default_max_tokens,
}



@cl.on_chat_start
async def on_chat_start():
    selected_model = available_models[0]
    cl.user_session.set("selected_model", selected_model)
    
    # Set initial settings in session
    selected_voice = default_tts_voice
    cl.user_session.set("selected_voice", selected_voice)
    cl.user_session.set("system_prompt", prompt_catalog["AI"])
    cl.user_session.set("character", character_options[0])
    cl.user_session.set("llm_temp", default_llm_temp)
    cl.user_session.set("max_tokens", default_max_tokens)
    cl.user_session.set("tts_speed", default_tts_speed)
    cl.user_session.set("tts_exaggeration", default_tts_exaggeration)
    cl.user_session.set("reasoning_enabled", False)
    
    # Send dynamic chat settings form for voice and other options
    voice_index = available_voices.index(selected_voice) if selected_voice in available_voices else 0
    settings_form = await cl.ChatSettings(
        [
            Select(
                id="voice",
                label="TTS Voice",
                values=available_voices,
                initial_index=voice_index
            ),
            Select(
                id="model",
                label="LLM Model",
                values=available_models,
                initial_index=0
            ),
            Select(
                id="model_refresh",
                label="Model Refresh",
                values=["No Action", "Refresh Now"],
                initial_index=0
            ),
            Select(
                id="system_prompt",
                label="System Prompt",
                values=list(prompt_catalog.keys()),
                initial_index=0
            ),
            Select(
                id="character",
                label="Character",
                values=character_options,
                initial_index=0
            ),
            Slider(
                id="llm_temp",
                label="LLM Temperature",
                initial=default_llm_temp,
                min=0.0,
                max=2.0,
                step=0.1
            ),
            Slider(
                id="max_tokens",
                label="Max Tokens",
                initial=default_max_tokens,
                min=100,
                max=2000,
                step=50
            ),
            Slider(
                id="tts_speed",
                label="TTS Speed",
                initial=default_tts_speed,
                min=0.25,
                max=4.0,
                step=0.05
            ),
            Slider(
                id="tts_exaggeration",
                label="TTS Exaggeration",
                initial=default_tts_exaggeration,
                min=0.0,
                max=1.0,
                step=0.1
            ),
            Switch(
                id="reasoning_enabled",
                label="Enable Reasoning",
                initial=False
            )
        ]
    ).send()

    await cl.Message(content=f"Model: {selected_model}  Voice: {selected_voice}").send()

    # Settings are now managed via user_session; UI actions removed due to API incompatibility

@cl.on_settings_update
async def on_settings_update(settings):
    cl.user_session.set("selected_model", settings["model"])
    cl.user_session.set("selected_voice", settings["voice"])
    cl.user_session.set("system_prompt", prompt_catalog[settings["system_prompt"]])
    cl.user_session.set("character", settings["character"])
    cl.user_session.set("llm_temp", settings["llm_temp"])
    cl.user_session.set("max_tokens", int(settings["max_tokens"]))
    cl.user_session.set("tts_speed", settings["tts_speed"])
    cl.user_session.set("tts_exaggeration", settings["tts_exaggeration"])
    cl.user_session.set("reasoning_enabled", settings["reasoning_enabled"])

    if settings["model_refresh"] == "Refresh Now":
        try:
            updated_models = fetch_available_models()
            old_models = cl.user_session.get("available_models", available_models)
            new_models = [m for m in updated_models if m not in old_models]
            cl.user_session.set("available_models", updated_models)
            
            if new_models:
                notification = f"Models refreshed! New models added: {', '.join(new_models)}"
            else:
                notification = "Models refreshed. No new models detected."
            
            # Update selected_model if it was removed
            selected_model = cl.user_session.get("selected_model")
            if selected_model not in updated_models:
                new_selected = updated_models[0] if updated_models else available_models[0]
                cl.user_session.set("selected_model", new_selected)
                notification += f" Switched to {new_selected}."
            
            await cl.Message(content=notification).send()
        except Exception as e:
            await cl.Message(content=f"Failed to refresh models: {str(e)}").send()
        # Note: User can select "No Action" to stop further refreshes

@app.post("/voice-input")
async def handle_voice_input(request: Request):
    """
    This endpoint receives the transcribed text and sessionId from the frontend,
    finds the correct user session, and processes the message.
    """
    data = await request.json()
    transcript = data.get("transcript")
    session_id = data.get("sessionId")

    if not transcript or not session_id:
        return JSONResponse(content={"status": "error", "message": "Missing transcript or sessionId"}, status_code=400)

    # Check if the session ID is valid
    if session_id in user_sessions:
        # Get the user's message processing function (the one decorated with @cl.on_message)
        on_message_coro = on_message

        # Create the message object
        msg = cl.Message(author="User", content=transcript)

        # Run the message processing function within the correct user session context
        await cl.run_sync(
            cl.context.with_session(
                user_sessions[session_id].id,
                lambda: on_message_coro(msg),
            )
        )
        return JSONResponse(content={"status": "ok"}, status_code=200)

    return JSONResponse(content={"status": "error", "message": "Session not found"}, status_code=404)


@cl.on_message
async def on_message(message: cl.Message):
    if not message.content:
        return
    
    # Use latest models from session if available, else global
    session_models = cl.user_session.get("available_models")
    current_models = session_models if session_models else available_models
    selected_model = cl.user_session.get("selected_model")
    if not selected_model:
        selected_model = current_models[0]
    
    system_prompt = cl.user_session.get("system_prompt", prompt_catalog["AI"])
    reasoning_enabled = cl.user_session.get("reasoning_enabled", False)
    if reasoning_enabled:
        system_prompt += " Think step by step before responding."
    
    llm_temp = cl.user_session.get("llm_temp", default_llm_temp)
    max_tokens = cl.user_session.get("max_tokens", default_max_tokens)
    
    response = await client.chat.completions.create(
        model=selected_model,
        messages=[
            {
                "content": system_prompt,
                "role": "system"
            },
            {
                "content": message.content,
                "role": "user"
            }
        ],
        temperature=llm_temp,
        max_tokens=max_tokens,
    )
    text_content = response.choices[0].message.content
    
    character = cl.user_session.get("character", character_options[0])
    # Send text response with character context if needed
    text_msg = await cl.Message(content=f"[{character}]: {text_content}").send()
    
    # Generate TTS audio streaming
    selected_voice = cl.user_session.get("selected_voice", default_tts_voice)
    tts_speed = cl.user_session.get("tts_speed", default_tts_speed)
    tts_exaggeration = cl.user_session.get("tts_exaggeration", default_tts_exaggeration)

    params_dict = {
        "exaggeration": tts_exaggeration,
        "cfg_weight": config["tts_cfg_weight"],
        "temperature": config["tts_temperature"],
        "device": config["tts_device"],
        "dtype": config["tts_dtype"],
        "seed": config["tts_seed"],
        "chunked": config["tts_chunked"],
        "use_compilation": config["tts_use_compilation"],
        "max_new_tokens": config["tts_max_new_tokens"],
        "max_cache_len": config["tts_max_cache_len"],
        "desired_length": config["tts_desired_length"],
        "max_length": config["tts_max_length"],
        "halve_first_chunk": True,
        "cpu_offload": False,
        "cache_voice": False,
        "tokens_per_slice": None,
        "remove_milliseconds": None,
        "remove_milliseconds_start": None,
        "chunk_overlap_method": "undefined"
    }

    track_id = f"{cl.context.session.id}_tts_{hash(text_content) % 10000}"

    buffer = b""
    async with tts_client.audio.speech.with_streaming_response.create(
        model=default_tts_model,
        input=text_content,
        voice=selected_voice,
        response_format=default_tts_response_format,
        speed=tts_speed,
        extra_body={"params": params_dict}
    ) as response:
        async for chunk in response.iter_bytes():
            buffer += chunk

    audio = cl.Audio(
        name="response_audio.wav",
        content=buffer,
        mime="audio/wav",
        auto_play=True
    )
    await audio.send(for_id=text_msg.id)

# This is required as of Chainlit >=2.0
# https://github.com/Chainlit/chainlit/releases/tag/2.0rc0
# Set to "return True" in the Github example
@cl.on_audio_start
async def on_audio_start():
    return True

# This is required as of Chainlit >=2.0
# https://github.com/Chainlit/chainlit/releases/tag/2.0rc0
# Set to "pass" in the GitHub example
@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):
    pass

# This is required as of Chainlit >=2.0
# https://github.com/Chainlit/chainlit/releases/tag/2.0rc0
# set to "pass" in the github example
@cl.on_audio_end
async def on_audio_end():
    pass

@cl.action_callback("refresh_models")
async def on_refresh_models(action: cl.Action):
    try:
        updated_models = fetch_available_models()
        old_models = cl.user_session.get("available_models", available_models)
        new_models = [m for m in updated_models if m not in old_models]
        cl.user_session.set("available_models", updated_models)
        
        if new_models:
            notification = f"Models refreshed! New models added: {', '.join(new_models)}"
        else:
            notification = "Models refreshed. No new models detected."
        
        # Update selected_model if it was removed
        selected_model = cl.user_session.get("selected_model")
        if selected_model not in updated_models:
            new_selected = updated_models[0] if updated_models else available_models[0]
            cl.user_session.set("selected_model", new_selected)
            notification += f" Switched to {new_selected}."
        
        await cl.Message(content=notification).send()
    except Exception as e:
        await cl.Message(content=f"Failed to refresh models: {str(e)}").send()

