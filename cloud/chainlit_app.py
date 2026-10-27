"""Archived teaching UI with mandatory password authentication."""
import hashlib
import hmac
import os
from uuid import uuid4
import chainlit as cl
from cloud.client import ask


@cl.password_auth_callback
def authenticate(username: str, password: str):
    candidate = hashlib.pbkdf2_hmac('sha256',password.encode(),
        os.environ['CHAINLIT_PASSWORD_SALT'].encode(),600000).hex()
    if (hmac.compare_digest(username,os.environ.get('CHAINLIT_USERNAME','operator'))
            and hmac.compare_digest(candidate,os.environ['CHAINLIT_PASSWORD_HASH'])):
        return cl.User(identifier='operator')
    return None


@cl.on_chat_start
async def start(): cl.user_session.set('agent_session','chainlit-'+uuid4().hex)


@cl.on_message
async def message(value: cl.Message):
    if not cl.user_session.get('user'): return
    try:
        answer = await ask(value.content,cl.user_session.get('agent_session'))
        await cl.Message(content=answer['response']).send()
    except Exception:
        await cl.Message(content='No se pudo completar la consulta. No se reintentó automáticamente.').send()
