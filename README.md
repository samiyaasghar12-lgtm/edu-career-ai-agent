# 🤖 IntellectAI — Our Personal Education & Career Advisor

**IntellectAI** is a personalized, AI-powered educational and career advisory agent built specifically as a daily study companion. The system is engineered to handle academic questions across **any educational domain or field of study**, offering expert guidance on general studies, conceptual explanations, career planning, interview prep, and text analysis, while maintaining strict guardrails against non-educational topics.

Built with: **Python · Streamlit · Gemini AI (Google GenAI SDK) · JSON**

---

## 📝 Project Overview

IntellectAI is designed for consistent, day-to-day academic assistance. Whether it is solving domain-agnostic academic questions, defining vocabulary, structuring notes, or outlining study paths, this agent ensures a focused learning environment. 

Leveraging Google’s latest Gemini API and an intuitive Streamlit interface, it natively processes multi-lingual inputs (English, Urdu, and Roman Urdu). The platform features an intelligent dual-layer storage system that manages user profiles and preserves conversation history across sessions to maintain context for future learning.

---

## 📁 Project File Structure
edu-career-py/
├── agent.py                        ← Main application script (UI and Core Guardrail Logic)
├── requirements.txt                ← Project dependencies (Streamlit, Google-GenAI, Dotenv)
├── .env                            ← Secret environment variables (Gemini API Key)
├── .gitignore                      ← Specifies untracked files to prevent uploading to GitHub
├── README.md                       ← Project documentation (This file)
├── robot.png                       ← Main UI robot avatar graphic
├── chat_memory.json                ← Frontend session UI conversation history (Auto-saved)
├── automated_agent_memory.json    ← Backend cognitive memory context cache (Auto-saved)
├── profile.json                    ← User metadata state and persistence layer
└── .streamlit/
└── config.toml                 ← Premium theme visual layouts and server port configurations
---

## 🚀 Step-by-Step Local Setup via VS Code

### Step 1 — Install Python & Git
1. Download and install Python (Version 3.9 or higher): **https://python.org/downloads**
2. Download and install Git for version control: **https://git-scm.com/downloads**

### Step 2 — Configure Virtual Environment
Open your VS Code terminal and initialize a clean environment space:
```bash
python -m venv venv
Activate the virtual environment:

Windows (CMD/PowerShell): venv\Scripts\activate

Mac/Linux: source venv/bin/activate

Note: Once activated, you will see (venv) at the beginning of your terminal line.

Step 3 — Navigate to Code Directory & Install Dependencies
Navigate into your proper project folder where requirements.txt is located:

Bash
cd edu-career-py
Install all required package versions (streamlit, google-genai, python-dotenv):

Bash
pip install -r requirements.txt
Step 4 — Setup Private Gemini API Key
Create a .env file in your root project folder and input your secure API key:

Code snippet
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
🔑 Generate a free development API key at: https://aistudio.google.com

Step 5 — Run the Application
Execute the Streamlit application runner from your active terminal:

Bash
streamlit run agent.py
✅ Your default web browser will automatically open up http://localhost:8501/!
✨ Core FeaturesFeatureTechnical & Functional Detail🎓 Universal Academic FocusProvides comprehensive support for any domain or educational field; effectively ignores out-of-scope requests.🤖 Advanced GuardrailsProgrammed to politely decline non-educational content (e.g., recipes, casual chat), keeping your study sessions fully distraction-free.🧠 Dual-Layer JSON MemoryFrontend conversational state and backend assistant contexts are tracked across separate auto-saved JSON cache engines.👤 Persistent Student ProfileStores persistent user metadata displayed continuously inside the premium sidebar panel.🌐 Multi-Lingual CapabilityFull natural language comprehension across English, Urdu, and Roman Urdu scripts.🔍 Deep Search ArchivingAllows searching through older, archived conversations directly from the sidebar interaction log.🎨 Premium InterfaceCustom Gemini-styled dark sidebar paired with an interactive, responsive central workspace.
🐙 Publishing to GitHub
git init
git add .
git commit -m "Initial Commit: IntellectAI Guardrailed Multi-Domain Study Agent"
git branch -M main
git remote add origin [https://github.com/SamiyaAsghar/edu-career-ai-agent.git](https://github.com/SamiyaAsghar/edu-career-ai-agent.git)
git push -u origin main
⚠️ Security Warning: The .env file containing secrets, along with JSON history files, are protected by .gitignore to prevent data leakage onto public repositories.❓ TroubleshootingCommon IssuesSolutionModuleNotFoundError / No such fileEnsure you have navigated to the correct folder using cd edu-career-py before running the pip command.API Error Status (404/503)Check your credentials inside the .env file and verify your codebase implements the new google-genai SDK formats.Local Port ConflictIf port 8501 is busy with another service, launch using an alternative port: streamlit run agent.py --server.port 8502