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

            Generate the output in a concise format of 2-4 short paragraphs.Ensure that all important points are clearly highlighted in your output.
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

def set_custom_css():
    st.markdown("""
        <style>
        /* Dark theme styles */
        .stApp {
            background-color: #1a1a1a;
            color: white;
        }
        
        /* Header styles */
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
        }
        
        /* Logo styles */
        .logo-container {
            width: 150px;
        }
        
        /* Title styles */
        .title-container {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .co-pilot-title {
            color: white;
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        .subtitle {
            color: #9ca3af;
            font-size: 1.2rem;
        }
        
        .highlight {
            color: #2dd4bf;
        }
        
        /* Upload container styles */
        .upload-container {
            border: 2px dashed #4b5563;
            border-radius: 0.5rem;
            padding: 2rem;
            text-align: center;
            margin: 2rem auto;
            max-width: 600px;
        }
        
        .upload-icon {
            color: #6b7280;
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        
        .upload-text {
            color: #9ca3af;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Custom button styles */
        .stButton>button {
            background-color: #2dd4bf;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
        }
        </style>
    """, unsafe_allow_html=True)


# Main function to handle the Streamlit app logic
def main():
    st.set_page_config(page_title="LineCraft Co-pilot", layout="wide")
    set_custom_css()

    # Sidebar for chat summary
    st.sidebar.header("Chat Summary")
    
    # Initialize session states for messages and analysis flag if not already done
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    if 'initial_analysis_done' not in st.session_state:
        st.session_state['initial_analysis_done'] = False

    # Display the conversation summary in the sidebar
    def update_sidebar_summary():
        with st.sidebar:
            if st.session_state['messages']:
                st.write("Conversation so far:")
                for i, message in enumerate(st.session_state['messages']):
                    # Only display messages from the Co-pilot (assistant)
                    if message["role"] == "assistant":
                        # Truncate assistant's message in the summary (set to 100 characters, for example)
                        truncated_content = message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"]
                        
                        st.write(f"{truncated_content}")

    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        st.image("https://raw.githubusercontent.com/nikhils0035/co-pilot/refs/heads/main/1.svg", width=150)

    with col3:
        st.markdown(
        '''
        <div style="display: flex; align-items: center; justify-content: center; height: 100%; text-align: center;">
            <br><br><br><br> <!-- Added multiple line breaks to increase space -->
            <a href="https://linecraft.ai" target="_blank" style="color: white; text-decoration: none;">Visit Our Website &#x2197;</a>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(""" 
    <div class="title-container" style="text-align: center; display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 0;">
        <img src="https://raw.githubusercontent.com/nikhils0035/co-pilot/refs/heads/main/CoPilot%20Icon.svg" alt="icon" style="width: 40px; height: 40px; margin-right: 10px;">
        <h1 class="co-pilot-title" style="margin: 0; font-size: 28px;">Co-Pilot</h1>
    </div>
    <p class="subtitle" style="text-align: center; margin-top: 0;">
        Your data is smarter than you think. Turn 
        <span class="highlight">charts into chats</span> 
        with the Linecraft AI Co-Pilot.
    </p>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload a graph", type=["jpg", "jpeg", "png", "bmp", "tiff"], label_visibility="hidden")

    if uploaded_file is not None and not st.session_state['initial_analysis_done']:
        base64_image = encode_image(uploaded_file)
        openai_analysis = analyze_image_openai(base64_image)

        st.session_state['messages'].append({
            "role": "user",
            "content": "Uploaded an image for analysis.",
            "image": uploaded_file
        })
        
        st.session_state['messages'].append({
            "role": "assistant",
            "content": openai_analysis
        })

        st.session_state['initial_analysis_done'] = True
        update_sidebar_summary()  # Update the sidebar immediately after response

    # Display the conversation
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            if "image" in message:
                st.image(message["image"], width=400)
            st.write(message["content"])

    # Show the follow-up question input only after the first assistant response
    if st.session_state['initial_analysis_done']:
        user_query = st.chat_input("Ask a follow-up question about the graph...")

        if user_query:
            st.session_state['messages'].append({
                "role": "user",
                "content": user_query
            })

            with st.chat_message("user"):
                st.write(user_query)

            assistant_placeholder = st.empty()

            with assistant_placeholder.chat_message("assistant"):
                typing_placeholder = st.empty()
                typing_placeholder.write("Linecraft co-pilot is typing...")

            context_messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state['messages']]

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

            time.sleep(2)

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            ai_response = response.json()['choices'][0]['message']['content']

            assistant_placeholder.empty()

            st.session_state['messages'].append({
                "role": "assistant",
                "content": ai_response
            })

            with st.chat_message("assistant"):
                st.write(ai_response)

            update_sidebar_summary()  # Update the sidebar immediately after assistant's response

if __name__ == "__main__":
    main()
