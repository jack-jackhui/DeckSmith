"""Chatbot module for DeckSmith with conversation and email capabilities."""

import logging
import os
import re
from typing import Any, Dict, List, Optional

import streamlit as st
from dotenv import load_dotenv
from langchain.chains import ConversationChain
from langchain_openai import AzureChatOpenAI

from tools import EmailSendError, EmailValidationError, use_tool
from utils import clean_response
from vector_db import search_vector_db

load_dotenv()

logger = logging.getLogger(__name__)

azure_openai_api_key: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_version: str = "2024-02-15-preview"
azure_openai_deployment_name: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

llm = AzureChatOpenAI(
    api_key=azure_openai_api_key,
    azure_endpoint=azure_openai_endpoint,
    api_version=azure_openai_api_version,
    deployment_name=azure_openai_deployment_name
)

conversation_chain = ConversationChain(llm=llm)


def get_or_init_chat_state() -> Dict[str, Any]:
    """Initialize and return the chat state from Streamlit session state.

    Returns:
        Dictionary containing email_request_state and chat_history.
    """
    if "email_request_state" not in st.session_state:
        st.session_state.email_request_state = {
            "awaiting_email": False,
            "email_subject": "",
            "email_body": ""
        }

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    return {
        "email_request_state": st.session_state.email_request_state,
        "chat_history": st.session_state.chat_history
    }


def get_chatbot_response(user_input: str, prompt: Optional[str] = None) -> str:
    """Process user input and return a chatbot response.

    Args:
        user_input: The user's input message.
        prompt: Optional system prompt to prepend to the conversation.

    Returns:
        The chatbot's response string.
    """
    chat_state = get_or_init_chat_state()
    email_request_state = chat_state["email_request_state"]
    chat_history: List[str] = chat_state["chat_history"]

    if email_request_state["awaiting_email"]:
        email_address = user_input.strip()
        try:
            use_tool(
                "send_email",
                email_request_state["email_subject"],
                email_request_state["email_body"],
                email_address
            )
            email_request_state["awaiting_email"] = False
            logger.info("Email sent to %s", email_address)
            return f"Email sent to {email_address}"
        except (EmailValidationError, EmailSendError) as e:
            logger.error("Failed to send email: %s", e)
            email_request_state["awaiting_email"] = False
            return f"Failed to send email: {e}"

    relevant_texts = search_vector_db(user_input)

    combined_input = ""
    if prompt:
        combined_input += f"{prompt}\n\n"

    if relevant_texts:
        context = " ".join(relevant_texts)
        combined_input = (
            f"Based on the following information, answer the question concisely:\n\n"
            f"{context}\n\nQuestion: {user_input}"
        )
    else:
        combined_input += user_input

    logger.debug("Invoking conversation chain with input length: %d", len(combined_input))
    raw_response = conversation_chain.invoke(combined_input)

    if isinstance(raw_response, dict) and 'response' in raw_response:
        response_content = raw_response['response']
    else:
        response_content = raw_response

    formatted_response = clean_response(response_content)

    chat_history.append(f"You: {user_input}")
    chat_history.append(f"Bot: {formatted_response}")

    email_phrases = ["send email", "email me the chat", "email this to me"]
    if any(phrase in user_input.lower() for phrase in email_phrases):
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', user_input)
        if email_match:
            email_address = email_match.group(0)
            chat_history_str = "\n\n".join(chat_history)
            try:
                use_tool("send_email", "Your Chat Information", chat_history_str, email_address)
                logger.info("Email sent to %s", email_address)
                return f"Email sent to {email_address}"
            except (EmailValidationError, EmailSendError) as e:
                logger.error("Failed to send email: %s", e)
                return f"Failed to send email: {e}"

        email_request_state["awaiting_email"] = True
        email_request_state["email_subject"] = "Your Chat Information"
        email_request_state["email_body"] = formatted_response
        return "Please provide the email address to send the information to."

    return formatted_response
