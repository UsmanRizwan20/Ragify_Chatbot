import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from PIL import Image
import pandas as pd
from tenacity import retry, wait_exponential, stop_after_attempt
# Set page configuration for a premium look
st.set_page_config(
    page_title="RAGify",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a beautiful design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    /* Base Styles */
    p, h1, h2, h3, h4, h5, h6, li, ul, label, input, textarea, .stMarkdown {
        font-family: 'Outfit', sans-serif !important;
    }

    .stApp {
        background: radial-gradient(circle at 15% 50%, #1a1025, #0a0a0a 50%);
        background-attachment: fixed;
        color: #f8fafc;
    }
    
    /* Headers */
    h1, h2, h3 {
        background: linear-gradient(to right, #c4b5fd, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Sidebar styling with glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(15, 15, 20, 0.6) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Chat container and bubbles */
    .stChatMessage {
        background: rgba(30, 30, 40, 0.6) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease-in-out;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
    }
    
    /* Assistant Message specific styling */
    [data-testid="stChatMessage"]:nth-child(odd) {
        border-bottom-left-radius: 4px;
    }
    
    /* User message specific styling */
    [data-testid="stChatMessage"]:nth-child(even) {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.8) 0%, rgba(139, 92, 246, 0.8) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom-right-radius: 4px;
    }
    
    /* File uploader */
    [data-testid="stFileUploadDropzone"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 2px dashed rgba(139, 92, 246, 0.5) !important;
        border-radius: 16px;
        transition: all 0.3s ease;
    }

    [data-testid="stFileUploadDropzone"]:hover {
        background: rgba(139, 92, 246, 0.1) !important;
        border-color: rgba(139, 92, 246, 1) !important;
    }
    
    /* Chat Input styling */
    [data-testid="stChatInput"] {
        background: rgba(20, 20, 25, 0.8) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px;
    }
    
    /* Hide standard top padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 10rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv(override=True)

# Check for API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 Gemini API Key not found! Please create a `.env` file and add `GEMINI_API_KEY=your_key`.")
    st.stop()

# Initialize the GenAI client
client = genai.Client(api_key=api_key)

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True
)
def call_gemini(model_name, contents):
    return client.models.generate_content(
        model=model_name,
        contents=contents,
    )

def generate_with_retry(contents):
    try:
        # Try the primary model first
        return call_gemini('gemini-2.5-flash', contents)
    except Exception as e:
        # If it's a server/availability error, try the fallback model
        if '503' in str(e) or 'UNAVAILABLE' in str(e) or '500' in str(e):
            st.warning("⚠️ Primary model is experiencing high demand. Automatically switching to fallback model (gemini-1.5-flash)...")
            return call_gemini('gemini-1.5-flash', contents)
        raise e

# Header
st.title("✨ RAGify")
st.markdown("A premium multimodal AI assistant powered by Google's **Gemini 2.5 Flash** model.")
st.divider()

# Sidebar for Image Upload (Multimodal)
with st.sidebar:
    st.header("📎 Attach File")
    st.markdown("Upload an image or spreadsheet to chat about it with Gemini.")
    uploaded_file = st.file_uploader("Choose a file...", type=["jpg", "jpeg", "png", "xlsx", "csv"])
    
    image_to_process = None
    data_context = None
    if uploaded_file is not None:
        # Reset the file pointer to the beginning before reading
        uploaded_file.seek(0)
        
        if uploaded_file.name.endswith(('.jpg', '.jpeg', '.png')):
            image_to_process = Image.open(uploaded_file)
            st.image(image_to_process, caption="Uploaded Image", use_container_width=True)
            st.success("Image ready for analysis!")
        elif uploaded_file.name.endswith(('.xlsx', '.csv')):
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Show preview and limit size if needed
                st.dataframe(df.head(5))
                st.success(f"Data ready for analysis! ({len(df)} rows)")
                data_context = f"Here is the uploaded data from {uploaded_file.name}:\n\n" + df.head(100).to_markdown()
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
    st.divider()
    if st.button("Clear Chat History", type="primary"):
        st.session_state.messages = []
        st.rerun()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display welcome message if chat is empty
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style="background: rgba(30, 30, 40, 0.4); border: 1px solid rgba(255,255,255,0.05); padding: 2rem; border-radius: 16px; margin-top: 2rem;">
        <h3 style="margin-top: 0;">Welcome to RAGify! 👋</h3>
        <p style="color: #cbd5e1; font-size: 1.1rem;">Your intelligent, multimodal AI assistant designed for seamless data interaction.</p>
        <ul style="color: #94a3b8; line-height: 1.8;">
            <li><strong style="color: #e2e8f0;">💬 Chat:</strong> Ask questions, brainstorm ideas, or generate text in the chat box below.</li>
            <li><strong style="color: #e2e8f0;">🖼️ Analyze Images:</strong> Upload an image via the sidebar and ask Gemini to describe it or extract text.</li>
            <li><strong style="color: #e2e8f0;">📊 Explore Data:</strong> Upload Excel or CSV files to easily chat with your datasets.</li>
        </ul>
        <p style="color: #a78bfa; margin-bottom: 0; margin-top: 1.5rem; font-weight: 500;">
            ✨ Simply type your first message below to get started!
        </p>
    </div>
    """, unsafe_allow_html=True)

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask Gemini anything..."):
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Gemini is thinking..."):
            try:
                # Prepare contents list
                contents = [prompt]
                
                # If an image is uploaded, append it to the prompt
                if image_to_process:
                    contents.append(image_to_process)
                
                # If data was uploaded, append it as text context
                if data_context:
                    contents.append(data_context)
                
                # Call Gemini API
                response = generate_with_retry(contents)
                
                result_text = response.text
                st.markdown(result_text)
                
                # Save assistant response to state
                st.session_state.messages.append({"role": "assistant", "content": result_text})
            
            except Exception as e:
                st.error(f"Error generating response: {e}")
