from openai import AsyncOpenAI
from openai import OpenAI
import chainlit as cl
client = AsyncOpenAI(base_url="http://192.168.1.98:1234/v1", api_key="lm-studio")
# Instrument the OpenAI client
cl.instrument_openai()

settings = {
    "model": "qwen/qwen3-8b",
    "temperature": 0,
    # ... more settings
}

import chainlit as cl


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="qwen3-4b-instruct-2507",
            markdown_description="The underlying LLM model is **qwen3-4b-instruct-2507**.",
            icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="qwen/qwen3-8b",
            markdown_description="The underlying LLM model is **qwen/qwen3-8b**.",
            icon="https://picsum.photos/250",
        ),
        cl.ChatProfile(
            name="phi-4-mini-instruct",
            markdown_description="The underlying LLM model is **phi-4-mini-instruct**.",
            icon="https://picsum.photos/250",
        ),
        cl.ChatProfile(
            name="qwen/qwen3-14b",
            markdown_description="The underlying LLM model is **qwen/qwen3-14b**.",
            icon="https://picsum.photos/250",
        ),        
    ]

@cl.on_chat_start
async def on_chat_start():
    chat_profile = cl.user_session.get("chat_profile")
    await cl.Message(
        content=f"starting chat using the {chat_profile} chat profile"
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    response = await client.chat.completions.create(
        messages=[
            {
                "content": "You are a helpful bot, you always reply in Object/Subject/Verb format. If asked, you will always give your name as Yoda.",
                "role": "system"
            },
            {
                "content": message.content,
                "role": "user"
            }
        ],
        **settings
    )
    await cl.Message(content=response.choices[0].message.content).send()