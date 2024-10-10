import base64
import requests
import streamlit as st
import streamlit.components.v1 as components
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from io import BytesIO
from PIL import Image
import io
import os

# Initialize FastAPI app
app = FastAPI()

# OpenAI API key
openai_key = os.environ["OPENAI_API_KEY"]

def analyze_image_openai(base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key}"
    }
    message_list = [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        },
        {
            "type": "text",
            "text": f"""
            You are an expert graph interpreter with deep expertise in the manufacturing domain, including machines, processes, production systems, control systems (PLCs), 
            firmware, and part types (both discrete and continuous production).

            1. **Overview:**
            - Summarize the brief overview of the graph image from the data visualized in this graph along with the type of graph. Provide a summary that would make sense to
              someone with no technical or domain knowledge, explaining what the graph represents and any important conclusions.

            2. **Insights:**
            - Thinking from the people working in the manufacturing line, include necessary information for them based on the type of graph.
            - Analyze whether the trend in the data shows a general increase, decrease, or stability.
            - Identify any outliers and explain how they differ from the rest of the data.
            - If the graph is a scatter plot, describe the relationship between the two variables, noting any correlation and its implications.
            - Feel free to use variance, outliers, similarities, trends, comparisons to better understand the context.
            - Feel free to provide supporting numbers, etc.
            - Strictly do not include any recommendations and/or implications based on the data.

            Generate the output in a concise format of 2-4 short paragraphs.
            """
        }
    ]

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": message_list
            }
        ],
        "max_tokens": 1024
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

# Function to convert any image format to JPEG
def convert_to_jpeg(image_file):
    image = Image.open(image_file)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    
    jpeg_image = io.BytesIO()
    image.save(jpeg_image, format="JPEG")
    jpeg_image.seek(0)
    return jpeg_image

# Encode the image to base64
def encode_image(image_file):
    jpeg_image = convert_to_jpeg(image_file)
    return base64.b64encode(jpeg_image.read()).decode('utf-8')

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    contents = await file.read()
    base64_image = base64.b64encode(contents).decode('utf-8')
    
    openai_analysis = analyze_image_openai(base64_image)
    return {"openai_analysis": openai_analysis}

import streamlit as st
import time
import requests

def main():
    st.set_page_config(page_title="LineCraft Co-pilot", layout="wide")

    col1, col2 = st.columns([1, 6])

    with col1:
        st.image("https://cdn.prod.website-files.com/6667f48b2cd0ba5f5cdd53f3/666809c74e0bdb84a7b0f02a_linecraft-logo.svg", width=150)

    with col2:
        st.title("LineCraft Co-pilot")

    # Clear conversation button
    if st.button("Clear Conversation"):
        st.session_state['messages'] = []
        st.session_state['initial_analysis_done'] = False  # Reset analysis state
        st.rerun()  # Rerun the script to refresh the UI

    # Initialize session states for messages and analysis flag if not already done
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    if 'initial_analysis_done' not in st.session_state:
        st.session_state['initial_analysis_done'] = False

    # File uploader
    uploaded_file = st.file_uploader("Upload a graph", type=["jpg", "jpeg", "png", "bmp", "tiff"], label_visibility="collapsed")

    if uploaded_file is not None and not st.session_state['initial_analysis_done']:
        base64_image = encode_image(uploaded_file)
        openai_analysis = analyze_image_openai(base64_image)

        # Append user message for image upload and assistant message for analysis
        st.session_state['messages'].append({
            "role": "user",
            "content": "Uploaded an image for analysis.",
            "image": uploaded_file
        })
        
        st.session_state['messages'].append({
            "role": "assistant",
            "content": openai_analysis
        })

        # Set flag to avoid repeating initial analysis
        st.session_state['initial_analysis_done'] = True

    # Display the entire conversation history
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            if "image" in message:
                st.image(message["image"], width=400)
            st.write(message["content"])

    # User query input for follow-up question
    user_query = st.chat_input("Ask a follow-up question about the graph...")

    if user_query:
        # Add the user query to the session state for conversation history
        st.session_state['messages'].append({
            "role": "user",
            "content": user_query
        })

        # Display user query immediately
        with st.chat_message("user"):
            st.write(user_query)

        # Create a placeholder for the assistant response
        assistant_placeholder = st.empty()

        # Display typing indicator while waiting for response
        with assistant_placeholder.chat_message("assistant"):
            typing_placeholder = st.empty()
            typing_placeholder.write("Linecraft co-pilot is typing...")

        # Prepare context for OpenAI analysis including previous messages
        context_messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state['messages']]

        # Modify the prompt to check for relevance
        relevance_check_prompt = f""" 
        {user_query}
        """

        payload = {
            "model": "gpt-4o",
            "messages": context_messages + [{"role": "user", "content": relevance_check_prompt}],
            "max_tokens": 1024
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_key}"
        }

        # Simulate typing delay (optional)
        time.sleep(2)

        # Make the API call
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        ai_response = response.json()['choices'][0]['message']['content']

        # Replace typing placeholder with the actual response (no fading away of the old response)
        assistant_placeholder.empty()  # Clear the placeholder

        # Add the AI response to the session state for conversation history
        st.session_state['messages'].append({
            "role": "assistant",
            "content": ai_response
        })

        # Display the AI response in a new message
        with st.chat_message("assistant"):
            st.write(ai_response)

if __name__ == "__main__":
    main()
