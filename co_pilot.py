# app.py

import base64
import requests
import streamlit as st
import streamlit.components.v1 as components
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from io import BytesIO

# Initialize FastAPI app
app = FastAPI()

# OpenAI and Anthropic API keys
import os
# os.environ['REQUESTS_CA_BUNDLE'] = r"C:\Users\nikhils\Downloads\Zscaler Root CA.crt"
# os.environ["OPENAI_API_KEY"] = openai_key
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
            "text":f"""
            You are an expert graph interpreter with deep expertise in the manufacturing domain, including machines, processes, production systems, control systems (PLCs), firmware, and part types (both discrete and continuous production).

    1. **Overview:**
    - Summarize the brief overview of the graph image from the data visualized in this graph along with the type of graph.

    2. **Insights:**
    - Thinking from the people working in the manufacturing line, include necessary information for them based on the type of graph.
    - Analyze whether the trend in the data shows a general increase, decrease, or stability.
    - Identify any outliers and explain how they differ from the rest of the data.
    - If the graph is a scatter plot, describe the relationship between the two variables, noting any correlation and its implications.
    - Feel free to use variance,outliers, similarities, trends, comparisions to better understand the context.
    - Feel free to provide supporting numbers ,etc
    - Strictly do not include any recommendations and/or implications based on the data.
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

from PIL import Image
import io

# Function to convert any image format to JPEG
def convert_to_jpeg(image_file):
    from PIL import Image
    import io
    image = Image.open(image_file)
    # Convert to RGB in case the image has an alpha channel (like PNGs)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    
    # Save the image to a BytesIO object as a JPEG
    jpeg_image = io.BytesIO()
    image.save(jpeg_image, format="JPEG")
    jpeg_image.seek(0)  # Reset pointer to the start of the file
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
from PIL import Image
import base64
import io



def main():
    st.set_page_config(page_title="LineCraft Co-pilot")

    # Create two columns: one for the logo and title, one for the file uploader
    col1, col2 = st.columns([1, 3])

    with col1:
        # Add company logo
        st.image("https://cdn.prod.website-files.com/6667f48b2cd0ba5f5cdd53f3/666809c74e0bdb84a7b0f02a_linecraft-logo.svg", width=150)  # Replace with your actual logo

    with col2:
        st.title("LineCraft Co-pilot")



    uploaded_file = st.file_uploader("Upload a graph", type=["jpg", "jpeg", "png", "bmp", "tiff"], label_visibility="collapsed")

    # Create a list to store conversation history
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    if uploaded_file is not None:
        # Encode the image
        base64_image = encode_image(uploaded_file)

        # Simulate the AI analysis call
        openai_analysis = analyze_image_openai(base64_image)

        # Add user message (uploaded image) to conversation history
        st.session_state['messages'].append({
            "role": "user",
            "content": "Uploaded an image for analysis.",
            "image": uploaded_file
        })
        
        # Add system message (AI analysis) to conversation history
        st.session_state['messages'].append({
            "role": "assistant",
            "content": openai_analysis
        })

    # Display the conversation history as a chatbot UI
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            if "image" in message:
                st.image(message["image"], width=400)
            st.write(message["content"])

    # Add a text input for user queries
    # while True:
    user_query = st.chat_input("Ask a question about the graph...")

    if user_query:
        # Add user query to conversation history
        st.session_state['messages'].append({
            "role": "user",
            "content": user_query
        })
        
        # Simulate AI response (replace with actual AI call in production)
        ai_response = f"This is a simulated response to: {user_query}"
        
        # Add AI response to conversation history
        st.session_state['messages'].append({
            "role": "assistant",
            "content": ai_response
        })
    
        # Rerun the app to display the new messages
        # st.rerun()




if __name__ == "__main__":
    main()

   
