import os
from dotenv import load_dotenv
import requests
import json
from openai import AsyncOpenAI
import chainlit as cl
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
try:
    response = requests.get(f"{LM_STUDIO_URL}/api/v0/models")
    response.raise_for_status()
    models_data = response.json()["data"]
    available_models = [m["id"] for m in models_data if m["type"] == "llm"]
except Exception as e:
    print(f"Error: Could not fetch models from LM Studio: {e}. Exiting.")
    sys.exit(1)


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
    "yoda": "You are Yoda, wise Jedi Master. Reply in Yoda-speak",
    "roleplay": "You are a roleplaying character. Engage in immersive dialogue."
}

# Character profiles for chat participants
character_options = ["User", "Yoda", "Jedi Apprentice"]

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
    
    # Prompt for voice selection before starting
    actions = [cl.Action(name=f"voice_select", label=v["label"], payload={"voice": v["value"]}) for v in voices_data["voices"]]
    res = await cl.AskActionMessage(
        content="Select a TTS voice to start the chat:",
        actions=actions
    ).send()
    selected_voice = res.get("payload", {}).get("voice") if res else config["tts_voice"]
    cl.user_session.set("selected_voice", selected_voice)
    
    # Set defaults for new session
    cl.user_session.set("system_prompt", prompt_catalog["default"])
    cl.user_session.set("character", character_options[0])
    cl.user_session.set("llm_temp", default_llm_temp)
    cl.user_session.set("max_tokens", default_max_tokens)
    cl.user_session.set("tts_speed", default_tts_speed)
    cl.user_session.set("tts_exaggeration", default_tts_exaggeration)
    
    await cl.Message(
        content=f"Starting chat using the {selected_model} model and voice: {selected_voice}."
    ).send()
    
    # Settings are now managed via user_session; UI actions removed due to API incompatibility

@cl.on_message
async def on_message(message: cl.Message):
    if not message.content:
        return
    
    selected_model = cl.user_session.get("selected_model")
    if not selected_model:
        selected_model = available_models[0]
    
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
            autoplay=True
        )
        await audio.send(for_id=text_msg.id)
    except Exception as e:
        print(f"TTS Exception: {str(e)}")
        await cl.Message(content=f"TTS generation failed: {str(e)}").send()

async def chat_settings():
    return {
        "model": available_models[0],
        "voice": default_tts_voice,
        "system_prompt": "default",
        "character": character_options[0],
        "llm_temp": default_llm_temp,
        "max_tokens": default_max_tokens,
        "tts_speed": default_tts_speed,
        "tts_exaggeration": default_tts_exaggeration,
        "reasoning_enabled": False,
        "schema": {
            "type": "object",
            "properties": {
                "voice": {
                    "type": "string",
                    "title": "Voice",
                    "enum": available_voices,
                    "description": "Select voice for TTS"
                },
                "system_prompt": {
                    "type": "string",
                    "title": "Prompt Role",
                    "enum": list(prompt_catalog.keys()),
                    "description": "Select system prompt"
                },
                "character": {
                    "type": "string",
                    "title": "Character",
                    "enum": character_options,
                    "description": "Select character"
                },
                "llm_temp": {
                    "type": "number",
                    "title": "LLM Temperature",
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "description": "Adjust creativity"
                },
                "max_tokens": {
                    "type": "integer",
                    "title": "Max Tokens",
                    "minimum": 100,
                    "maximum": 2000,
                    "description": "Max response length"
                },
                "tts_speed": {
                    "type": "number",
                    "title": "TTS Speed",
                    "minimum": 0.25,
                    "maximum": 4.0,
                    "description": "Speech speed"
                },
                "tts_exaggeration": {
                    "type": "number",
                    "title": "TTS Exaggeration",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Voice expressiveness"
                },
                "reasoning_enabled": {
                    "type": "boolean",
                    "title": "Enable Reasoning",
                    "description": "Toggle step-by-step reasoning"
                }
            }
        }
    }
