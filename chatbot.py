from langchain_openai import AzureOpenAI, AzureChatOpenAI
from langchain.chains import ConversationChain
from vector_db import search_vector_db
from utils import clean_response
import os
from dotenv import load_dotenv
from tools import use_tool
import re
# Load environment variables from .env file
load_dotenv()

# Initialize the Azure OpenAI client
azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_version = "2024-02-15-preview"
azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

llm = AzureChatOpenAI(
    api_key=azure_openai_api_key,
    azure_endpoint=azure_openai_endpoint,
    api_version=azure_openai_api_version,
    deployment_name=azure_openai_deployment_name
)

conversation_chain = ConversationChain(llm=llm)

# State to remember if an email should be sent and awaiting email address
email_request_state = {
    "awaiting_email": False,
    "email_subject": "",
    "email_body": ""
}

# List to store chat history
chat_history = []

def get_chatbot_response(user_input, prompt=None):
    # Check if the chatbot is awaiting an email address
    if email_request_state["awaiting_email"]:
        email_address = user_input.strip()
        chat_history_str = "\n\n".join(chat_history)
        use_tool("send_email", email_request_state["email_subject"], email_request_state["email_body"], email_address)
        email_request_state["awaiting_email"] = False
        return f"Email sent to {email_address}"

    # Retrieve relevant information from vector store
    relevant_texts = search_vector_db(user_input)

    # Combine retrieved texts, prompt, and user input to provide context for answering the question
    combined_input = ""
    if prompt:
        combined_input += f"{prompt}\n\n"

    if relevant_texts:
        # Combine retrieved texts and user input to provide context for answering the question
        context = " ".join(relevant_texts)
        combined_input = f"Based on the following information, answer the question concisely:\n\n{context}\n\nQuestion: {user_input}"
    else:
        combined_input += user_input

    # Generate response using LLM
    raw_response = conversation_chain.invoke(combined_input)

    # Assume the response is a dictionary with 'response' key
    if isinstance(raw_response, dict) and 'response' in raw_response:
        response_content = raw_response['response']
    else:
        response_content = raw_response

    # Clean and format the response
    formatted_response = clean_response(response_content)

    # Add the user input and response to the chat history
    chat_history.append(f"You: {user_input}")
    chat_history.append(f"Bot: {formatted_response}")

    # Check if the user requested to send an email
    email_phrases = ["send email", "email me the chat", "email this to me"]
    if any(phrase in user_input.lower() for phrase in email_phrases):
        # Extract email address if provided in the input
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', user_input)
        if email_match:
            email_address = email_match.group(0)
            chat_history_str = "\n\n".join(chat_history)
            use_tool("send_email", "Your Chat Information", chat_history_str, email_address)
            return f"Email sent to {email_address}"
        email_request_state["awaiting_email"] = True
        email_request_state["email_subject"] = "Your Chat Information"
        email_request_state["email_body"] = formatted_response
        return "Please provide the email address to send the information to."

    return formatted_response
