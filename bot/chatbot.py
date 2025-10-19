"""
Core logic for a conversational medical chatbot using Google Gemini via LangChain.
No RAG, purely conversational. 

Flask backend teams can import and use:
    - initialize_chat_session(session_id)
    - get_bot_reply(session_id, user_message)

Dependencies:
    pip install langchain google-generative-ai python-dotenv
"""

import os
from dotenv import load_dotenv
from threading import Lock

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Load environment
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise EnvironmentError("Please set the GOOGLE_API_KEY in your environment or .env file.")

# Global in-memory session map (simple approach)
_sessions = {}
_session_lock = Lock()

# System prompt to guide safe, responsible conversation
SYSTEM_PROMPT = (
    """
    You are a helpful medical assistant named MedPal who can answer questions on various medical and 
    health related issues. Give clear and understandable answers to the patient with detailed explanation
    for his question. Draw your knowledge from the public websites given below.
    1. https://www.aiims.edu/index.php/en
    2. https://www.medscape.com/
    3. https://www.plannedparenthood.org/
    4. https://www.who.int/

    Always state the referances for your answer in the end. If you cant state the referances,
    reply with "I cant find any good referances" instead of making up some answer.  

    ALWAYS give your answer IN BULLET FORMAT.
    """
)


def _create_chain():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite", 
        temperature=0.7,
        max_output_tokens=500
    )

    memory = ConversationBufferMemory(memory_key="history", return_messages=True)
    chain = ConversationChain(llm=llm, memory=memory, verbose=False)
    return chain



def initialize_chat_session(session_id: str) -> None:
    """
    Initializes a new chat session (if not already created).
    This should be called when a new user session starts.
    """
    with _session_lock:
        if session_id not in _sessions:
            _sessions[session_id] = _create_chain()


def get_bot_reply(session_id: str, user_message: str) -> str:
    """
    Given a session_id and user input, returns the chatbot's reply.
    Automatically maintains conversation context.

    Args:
        session_id (str): Unique user session identifier.
        user_message (str): Text input from user.

    Returns:
        str: Model-generated reply.
    """
    if not user_message.strip():
        return "Please enter a valid question."

    with _session_lock:
        # Ensure session exists
        if session_id not in _sessions:
            initialize_chat_session(session_id)

        chain = _sessions[session_id]

    # Generate model reply
    try:
        response = chain.predict(input=f"{SYSTEM_PROMPT}\nUser: {user_message}")
        return response.strip()
    except Exception as e:
        return f"An error occurred while generating a response: {e}"


def clear_chat_session(session_id: str) -> None:
    """
    Optional: Clears a user's chat memory (resets the conversation).
    """
    with _session_lock:
        if session_id in _sessions:
            del _sessions[session_id]
