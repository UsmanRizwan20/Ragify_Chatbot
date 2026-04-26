# RAGify

RAGify is a premium multimodal AI assistant powered by Google's **Gemini 2.5 Flash** model, built using Streamlit. It allows users to:
- Chat with an intelligent AI.
- Upload images to analyze them or extract text.
- Upload datasets (Excel/CSV) and interactively explore or query them.

## Features
- **Multimodal capabilities:** Support for text, images, and data (CSV/XLSX).
- **Beautiful UI:** Custom premium dark-themed design with glassmorphism effects.
- **Easy Deployment:** Built entirely with Python and Streamlit.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "capstone 2 (RAG)"
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Folder Structure

- `app.py`: Main Streamlit application file.
- `requirements.txt`: Python dependencies required to run the app.
- `.env`: Environment variables (not tracked by git, must be created manually).
- `src/`: Directory for any additional source code modules.
- `notebooks/`: Directory for Jupyter Notebooks or exploratory data analysis.

## Technologies Used
- **Streamlit**
- **Google GenAI SDK**
- **Pandas**
- **Pillow**
- **Python Dotenv**
