import os
from dotenv import load_dotenv
import requests
import json
from openai import AsyncOpenAI
import chainlit as cl
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
    print(f"Fetched voices data: {voices_data}")  # Debug log
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
    "default": "You are a helpful AI assistant. Your responses are concise and brief. No more than 2-3 sentences per message.",
    "yoda": "You are Yoda, wise Jedi Master. Reply in Yoda-speak.",
    "roleplay": "You are a roleplaying character. Engage in immersive dialogue."
}

# Character profiles for chat participants
character_options = ["AI", "Yoda", "Stark"]

settings = {
    "temperature": default_llm_temp,
    "max_tokens": default_max_tokens,
}


@cl.set_chat_profiles
async def chat_profile():
    profiles = []
    for model_id in available_models:
        profiles.append(
            cl.ChatProfile(
                name=model_id,
                markdown_description=f"The underlying LLM model is **{model_id}**.",
                icon="https://picsum.photos/250",
            )
        )
    return profiles

@cl.on_chat_start
async def on_chat_start():
    chat_profile = cl.user_session.get("chat_profile")
    if isinstance(chat_profile, str):
        selected_model = chat_profile
    else:
        selected_model = chat_profile.name if chat_profile else available_models[0]
    cl.user_session.set("selected_model", selected_model)
    
    # Set initial settings in session
    selected_voice = default_tts_voice
    cl.user_session.set("selected_voice", selected_voice)
    cl.user_session.set("system_prompt", prompt_catalog["default"])
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

    await cl.Message(
        content=f"Starting chat using the {selected_model} model and voice: {selected_voice}. Use the settings form above to adjust voice and other options."
    ).send()

    # Add refresh models button
    refresh_msg = await cl.Message(
        content="Click to refresh available models from LM Studio server.",
        actions=[
            cl.Action(name="refresh_models", payload={}, label="Refresh Models")
        ]
    ).send()
    
    # Settings are now managed via user_session; UI actions removed due to API incompatibility

@cl.on_settings_update
async def on_settings_update(settings):
    cl.user_session.set("selected_voice", settings["voice"])
    cl.user_session.set("system_prompt", prompt_catalog[settings["system_prompt"]])
    cl.user_session.set("character", settings["character"])
    cl.user_session.set("llm_temp", settings["llm_temp"])
    cl.user_session.set("max_tokens", int(settings["max_tokens"]))
    cl.user_session.set("tts_speed", settings["tts_speed"])
    cl.user_session.set("tts_exaggeration", settings["tts_exaggeration"])
    cl.user_session.set("reasoning_enabled", settings["reasoning_enabled"])

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
    
    system_prompt = cl.user_session.get("system_prompt", prompt_catalog["default"])
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
    
    # Generate TTS audio
    selected_voice = cl.user_session.get("selected_voice", default_tts_voice)
    tts_speed = cl.user_session.get("tts_speed", default_tts_speed)
    tts_exaggeration = cl.user_session.get("tts_exaggeration", default_tts_exaggeration)
    try:
        tts_payload = {
            "model": default_tts_model,
            "input": text_content,
            "voice": selected_voice,
            "response_format": default_tts_response_format,
            "speed": tts_speed,
            "stream": False,
            "params": {
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
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "Origin": "https://192.168.1.98:8443",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        tts_response = requests.post(
            f"{CHATTERBOX_URL}/v1/audio/speech",
            json=tts_payload,
            headers=headers
        )
        print(f"TTS Response status: {tts_response.status_code}")
        if not tts_response.ok:
            print(f"TTS Error response: {tts_response.text}")
        tts_response.raise_for_status()
        audio_bytes = tts_response.content
        
        # Send audio element
        audio = cl.Audio(
            name="response_audio.wav",
            content=audio_bytes,
            mime="audio/wav",
            auto_play=True
        )
        await audio.send(for_id=text_msg.id)
    except Exception as e:
        print(f"TTS Exception: {str(e)}")
        await cl.Message(content=f"TTS generation failed: {str(e)}").send()

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

