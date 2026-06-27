import streamlit as st
import os
import json
from dotenv import load_dotenv
import base64
from datetime import datetime
import google.generativeai as genai

try:
    import requests
    from html.parser import HTMLParser
    _HAS_REQUESTS = True
except Exception:
    _HAS_REQUESTS = False

try:
    import PyPDF2
    _HAS_PYPDF2 = True
except Exception:
    _HAS_PYPDF2 = False

try:
    import docx
    _HAS_DOCX = True
except Exception:
    _HAS_DOCX = False

load_dotenv()

st.set_page_config(
    page_title="IntellectAI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

MEMORY_FILE = "chat_memory.json"
PROFILE_FILE = "profile.json"
ROBOT_FILE = "robot.png"
PROFILE_PIC_FILE = "profile_pic.png"

# Robot image URL (updated with the correct copy image address)
ROBOT_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRBWrVbKZGdXiQ4iDQu-amwsD7Vy8e1q8ng_MuTpsneIw&s=10"

# User-provided profile picture (base64 data URI)
PROFILE_PIC_B64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAJQAsgMBIgACEQEDEQH/xAAbAAEAAwEBAQEAAAAAAAAAAAAABAUGAwECB//EADgQAAIBAgIIBAIIBwEAAAAAAAABAgMEBRESFCExQVRxoRNRUmEiMkJDU4GRscHRIzNygpLw8RX/xAAVAQEBAAAAAAAAAAAAAAAAAAAAAf/EABYRAQEBAAAAAAAAAAAAAAAAAAABEf/aAAwDAQACEQMRAD8A/WwAVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPNnED08lJRjnNqMfNkK/xGNt/DgtKr5cI9Sjr16teWlVm5P3ZcF/PErSD21VL+lNnysVs3vqSX9jM8Bg1NKvSrfyqsZ9GdTJJuLzi2nwaeRZ2WKyhlC6znH18V1JgugeRakh4tOLWaae89AAAAAAAAAAAAAAAAAAAAQ8Su9VpfDl4k9kfb3JhmsQr6xd1JL5U9GPRCFR22229re9ngBUAAAABRZYReOlUVCo/gnsjnwZeGSNLYV9YtKdR/NllLqiUSAARQAAAAAAAAAAAAAAAHO4n4dCpPjGLZleBp75Z2VfL0MzBYlAAAAAAAAC5wGedOrT8mn/AL+BTFtgC+Ks/aP6gXAAIoAAAAAAAAAAAAAAAD5qQ06coPisjKSi4ycXvWxmtKHGLfwrjxF8tTb9/EQV4AKgAAAAAF5gdNxtpzf05fkimpU5VakYQWcpPI09CkqFGFKO6MUl7jVdAAQAAAAAAAAAAAAAAAADlc0I3NGVKo8k9z8vc6gDLXFvUtqjhUWW3Y+DRyNTcUKVxDQqxzjw80U9zhNaDboPxF6dzKK4HSdGrTeU6cov3iz5UJN5KMn0QR8nq25LiyVQw65rPZDQj6p7C3s8PpWzU38dT1NbF0CuWF2PgLxaqfiS3L0osQCAAAAAAAAAAAAAAAAAAQ7zEaVs3HLTqL6MXu6sCYR617b0M1Oom1wjtZR3N9cXGanNxh6YPYRS4mrmpjUE8qVGUveTyI0sYuJP4VTj0WZXgCY8UvH9al0igsSu08/FX+C/YhgKnwxa6jv0H1id6eNS+so5rzjL9yqARoKOKWtXfN035TWRMi1KOcWmvNPYZI60a9WhLSozlF+WewYa1IKu0xeMso3K0X647n+xZpqSTi8092RFegAAAAAAAAAAPvBUYvevN21J7PrGvyA+cQxNycqNtLKO5zXHoVQBQAAQAAAAAAAAAAAl2V7UtZb9Om98H+hEAVqqNWFamp0nnF9joZuwu5WtXPa6cvnX6mji1KKlF5prNPzIPQAAAAAAAcbyvq1vOrxS+Fe/AzDbbbbzb3suMem1GjTXFuX4f9KYsKAAIAAAAAAAAAAAAAAAAF1glfTpyoSe2G1dGUpLwuo6d9TyfzPRfvmKsaMAEAAAAABwuLajXadampNbE2c//PtPsI9wCwNQtOXh3GoWn2Ee4ADULTl49xqFpy8e4ADULTl49xqFpy8e4ADULTl49xqFpy8e4ADULTl49xqFpy8e4ADULTl49z6p2NrGcZRoRTi809u9AASfMAEAAAf/2Q=="

# Load API key from .env (local) or Streamlit Cloud secrets
_env_key = os.getenv("GEMINI_API_KEY", "")
try:
    _secrets_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    _secrets_key = ""
API_KEY = (_secrets_key or _env_key or "").strip()

# Model fallback chain
MODELS = ["gemini-1.5-pro", "gemini-pro"]


def image_data_uri(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    except Exception:
        pass
    return None


ROBOT_URI = image_data_uri(ROBOT_FILE) or ROBOT_URL
PROFILE_PIC_URI = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQrvqMr_iJ5proxfjDhFMCRPVIBwUyZXvdHN68lgwo0gA&s=10"

SYSTEM_PROMPT = """You are "IntellectAI", a dedicated personalized Education & Career advisor.
Your one and only purpose is to guide students toward a better academic life, career, and future.

============================
LANGUAGE RULES (VERY IMPORTANT)
============================
- Detect the language of the user's message and ALWAYS reply in the SAME language:
  - If the user writes in English  -> reply in English.
  - If the user writes in Urdu (Urdu script) -> reply in Urdu (Urdu script).
  - If the user writes in Roman Urdu / Roman English -> reply in Roman Urdu.
- Never switch the language unless the user switches first.

============================
SCOPE (STRICT)
============================
- You ONLY answer questions related to EDUCATION, study, academics, careers, fields,
  domains, university subjects, exams, interviews, tests, notes, roadmaps, future
  guidance, and dictionary/word meanings.
- If a question is OUTSIDE the education/career context (e.g. politics, gossip, jokes,
  cooking, random chit-chat, anything unrelated to learning or careers), politely REFUSE
  in the user's language.
- Keep the refusal short and respectful.

============================
WHAT YOU CAN DO
============================
- Career guidance, future planning, roadmaps, phases, steps, and field/domain guides.
- Dictionary feature: give meaning/definition of any word in English, Urdu, or Roman Urdu.
- Help with university notes, summaries, assignment understanding, and study help.
- Interview preparation and test/exam preparation.
- Generate quizzes, model answers, and study plans.

Always be encouraging, supportive, and focused on the student's growth and future success."""


def load_profile():
    default_profile = {
        "name": "Samiya Asghar",
        "first_name": "",
        "last_name": "",
        "program": "BS",
        "department": "Computer Science and Software Engineering",
        "year": "2025-2029",
        "status": "Undergraduate Student",
        "university": "Jinnah University for Women",
        "matriculation": "",
        "intermediate": "",
        "certifications": "",
        "contact": "",
        "address": "",
        "skills": "",
        "experience": "",
    }
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_profile.update(data)
                return default_profile
        except Exception:
            return default_profile
    return default_profile


def save_profile(profile_data):
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            return []
    return []


def save_memory(data):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_memory()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_id" not in st.session_state:
    st.session_state.current_id = None
if "file_context" not in st.session_state:
    st.session_state.file_context = ""
if "view_state" not in st.session_state:
    st.session_state.view_state = "chat"
if "sources" not in st.session_state:
    st.session_state.sources = []
if "profile_editing" not in st.session_state:
    st.session_state.profile_editing = False


def new_chat():
    st.session_state.messages = []
    st.session_state.current_id = None
    st.session_state.file_context = ""
    st.session_state.sources = []
    st.session_state.view_state = "chat"


def persist_current():
    if not st.session_state.messages:
        return
    first_user_msg = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "New Chat")
    title = (first_user_msg[:30] + "...") if len(first_user_msg) > 30 else first_user_msg
    entry_id = st.session_state.current_id or datetime.now().isoformat()
    entry = {
        "id": entry_id,
        "title": title,
        "messages": st.session_state.messages,
        "ts": datetime.now().strftime("%I:%M %p"),
    }
    st.session_state.current_id = entry_id
    updated_chats = [c for c in st.session_state.all_chats if c["id"] != entry_id]
    updated_chats.insert(0, entry)
    st.session_state.all_chats = updated_chats
    save_memory(updated_chats)


def load_chat(cid):
    for c in st.session_state.all_chats:
        if c["id"] == cid:
            st.session_state.messages = c["messages"]
            st.session_state.current_id = cid
            st.session_state.view_state = "chat"
            return


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.parts.append(text)


def fetch_url_text(url):
    if not _HAS_REQUESTS:
        return f"[Link saved: {url}] (install 'requests' to import page text)"
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        parser = _TextExtractor()
        parser.feed(resp.text)
        text = " ".join(parser.parts)
        return text[:8000]
    except Exception as e:
        return f"[Could not load {url}: {e}]"


def extract_file_text(file_path=None, uploaded_file=None, file_name=""):
    name = file_name or (os.path.basename(file_path) if file_path else "file")
    lower = name.lower()
    try:
        if lower.endswith(".pdf") and _HAS_PYPDF2:
            reader = PyPDF2.PdfReader(file_path if file_path else uploaded_file)
            return "\n".join((p.extract_text() or "") for p in reader.pages)[:8000]
        if lower.endswith(".docx") and _HAS_DOCX:
            d = docx.Document(file_path if file_path else uploaded_file)
            return "\n".join(p.text for p in d.paragraphs)[:8000]
        if file_path:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()[:8000]
        if uploaded_file is not None:
            return uploaded_file.read().decode("utf-8", errors="ignore")[:8000]
    except Exception as e:
        return f"[Could not read {name}: {e}]"
    return f"[Saved source: {name}]"


def ask_gemini(user_text):
    if not API_KEY or API_KEY in ("your_new_api_key_here", ""):
        return (
            "⚠️ **API key missing or expired.**\n\n"
            "**Local (your PC):** Open the `.env` file and set:\n"
            "```\nGEMINI_API_KEY=apni_nayi_key_yahan_paste_karo\n```\n\n"
            "**Streamlit Cloud:** App Settings → Secrets mein yeh add karo:\n"
            "```\nGEMINI_API_KEY = \"apni_nayi_key_yahan_paste_karo\"\n```\n\n"
            "Nayi key banao: https://aistudio.google.com/apikey"
        )
    try:
        client = genai.Client(api_key=API_KEY)
        history = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))

        payload_text = user_text
        active_context = ""
        if st.session_state.sources:
            active_context = "\n\n".join(s.get("content", "") for s in st.session_state.sources if s.get("content"))
        if active_context:
            payload_text = (
                f"[ATTACHED SOURCE CONTEXT]\n{active_context}\n\n"
                f"[USER INQUIRY]\n{user_text}"
            )

        history.append(types.Content(role="user", parts=[types.Part(text=payload_text)]))

        last_error = None
        for model_name in MODELS:
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=history,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                return resp.text or "(Empty response)"
            except Exception as model_err:
                err_str = str(model_err)
                if any(x in err_str for x in ["503", "UNAVAILABLE", "overloaded", "high demand"]):
                    last_error = model_err
                    continue
                raise model_err

        msg = str(last_error)
        return (
            "⚠️ **All Gemini models are currently overloaded.** This is a temporary "
            "issue on Google's side. Please wait 1-2 minutes and try again.\n\n"
            f"_(Technical detail: {msg})_"
        )

    except Exception as e:
        msg = str(e)
        if "RESOURCE_EXHAUSTED" in msg or "429" in msg or "quota" in msg.lower():
            return (
                "🚦 **Daily free-tier limit reached.**\n\n"
                "Your Gemini API key has used up its free quota for now.\n\n"
                "1. Wait for the quota to reset (usually after 24 hours), **or**\n"
                "2. Create a fresh key at https://aistudio.google.com/apikey and paste it "
                "into your `.env` file:\n\n"
                "```\nGEMINI_API_KEY=your_new_key_here\n```"
            )
        return f"❌ **Error:** {msg}"


def transcribe_audio(audio_bytes, mime_type="audio/wav"):
    if not API_KEY or API_KEY in ("your_new_api_key_here", ""):
        return ""
    try:
        client = genai.Client(api_key=API_KEY)
        for model_name in MODELS:
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part(text=(
                                    "Transcribe this audio to plain text exactly as spoken. "
                                    "Keep the same language the speaker used (English, Urdu, or Roman Urdu). "
                                    "Return only the transcription, no extra words."
                                )),
                                types.Part(inline_data=types.Blob(mime_type=mime_type, data=audio_bytes)),
                            ],
                        )
                    ],
                )
                return (resp.text or "").strip()
            except Exception as model_err:
                err_str = str(model_err)
                if any(x in err_str for x in ["503", "UNAVAILABLE", "overloaded", "high demand"]):
                    continue
                break
        return ""
    except Exception:
        return ""


# PREMIUM COHESIVE STYLES (RE-ENGINEERED) 
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #f8f9fc !important;
    }

    /* ===== GLOBAL WIDTH LIMITATION & PERFECT CENTER ALIGNMENT ===== */
    .main .block-container, div[data-testid="stAppViewBlockContainer"] {
        max-width: 820px !important;
        margin: 0 auto !important;
        padding-top: 4rem !important;
        padding-bottom: 6rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* ===== SIDEBAR PREMIUM STYLES (WIDER & SUBSTANTIAL) ===== */
    section[data-testid="stSidebar"] {
        background: #1c1c2e !important;
        min-width: 320px !important;
        max-width: 320px !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 24px 16px !important;
        display: flex;
        flex-direction: column;
        height: 100vh;
        gap: 0;
    }

    /* Brand row */
    .sb-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 0 20px 4px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 16px;
    }
    .sb-logo {
        width: 38px; height: 38px;
        border-radius: 10px;
        object-fit: cover;
        flex-shrink: 0;
    }
    .sb-title {
        font-size: 20px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.3px;
        line-height: 1.1;
    }
    .sb-tagline {
        font-size: 11px !important;
        color: #8b8fa8 !important;
        font-weight: 400;
        letter-spacing: 0.2px;
    }

    /* Profile row in sidebar */
    .sb-profile {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 16px;
        background: rgba(255,255,255,0.05);
    }
    .sb-avatar {
        width: 40px; height: 40px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid rgba(139,92,246,0.6);
        flex-shrink: 0;
    }
    .sb-uname {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #f3f4f6 !important;
        line-height: 1.2;
    }
    .sb-ustatus {
        font-size: 11px !important;
        color: #8b8fa8 !important;
        font-weight: 400;
    }

    /* Sidebar buttons styling (UNIFORM SIZE & PROFESSIONAL SPACING) */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
        text-align: left !important;
        padding: 12px 16px !important;
        width: 100% !important;
        min-height: 48px !important;
        transition: all 0.2s ease !important;
        margin-bottom: 10px !important;
        display: flex !important;
        align-items: center !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button p,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button span {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: rgba(255,255,255,0.1) !important;
        border-color: rgba(255,255,255,0.2) !important;
        color: #ffffff !important;
        transform: translateX(2px);
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover p,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover span {
        color: #ffffff !important;
    }

    /* Caption styling */
    section[data-testid="stSidebar"] p {
        color: #a0aec0 !important;
    }

    /* ===== HERO SECTION & CENTERED TYPOGRAPHY ===== */
    .hero-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center !important;
        width: 100%;
        margin: 0 auto;
    }

    .hero-robot-img {
        width: 150px !important;
        height: 150px !important;
        object-fit: contain !important;
        margin: 20px auto 24px auto !important;
        display: block !important;
        border: none !important;
        background: transparent !important;
        filter: drop-shadow(0 10px 25px rgba(28,28,46,0.12));
    }

    .hero-title-main {
        font-size: 48px !important;
        font-weight: 800 !important;
        letter-spacing: -1.5px !important;
        line-height: 1.2 !important;
        color: #1e293b !important;
        text-align: center !important;
        margin: 24px auto 16px auto !important;
        display: block !important;
    }

    .hero-sub-main {
        font-size: 18px !important;
        color: #475569 !important;
        background: transparent !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
        max-width: 650px !important;
        margin: 0 auto 36px auto !important;
        text-align: center !important;
        display: block !important;
    }

    /* ===== DISCLAIMER STYLING (PERFECT PLACEMENT) ===== */
    .disclaimer-text {
        font-family: 'Inter', sans-serif;
        font-size: clamp(12px, 1vw, 13.5px) !important;
        color: #7b8494 !important;
        text-align: center !important;
        max-width: 600px !important;
        margin: 0 auto 24px auto !important;
        line-height: 1.5 !important;
        display: block !important;
    }

    /* ===== HORIZONTAL BUTTON ROW & PILLS ===== */
    div[data-testid="stHorizontalBlock"] {
        max-width: 650px !important;
        margin: 0 auto !important;
        display: flex !important;
        justify-content: center !important;
        gap: 12px !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0% !important;
        min-width: 0 !important;
    }

    /* Clean professional button styling */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button {
        background-color: #f1f3f6 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 24px !important;
        color: #4a5568 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 10px 14px !important; /* Slightly narrower padding to prevent word wrap */
        width: 100% !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        transition: all 0.2s ease-in-out !important;
        white-space: nowrap !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
        background-color: #e2e8f0 !important;
        border-color: #cbd5e1 !important;
        color: #1a202c !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06) !important;
    }

    /* ===== BOTTOM CHAT INPUT (PERFECTLY CENTERED, CLEAN) ===== */
    div[data-testid="stBottomBlockContainer"] {
        background: transparent !important;
        padding-bottom: 24px !important;
    }
    div[data-testid="stBottomBlockContainer"] > div {
        max-width: 760px !important;
        margin: 0 auto !important;
        padding: 0 12px !important;
    }

    /* Style the main input box container */
    div[data-testid="stChatInput"] {
        background: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 28px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06) !important;
        padding: 6px 12px 6px 20px !important;
        outline: none !important;
    }

    /* CRITICAL: Completely remove harsh default active/focused/clicked blue outline */
    div[data-testid="stChatInput"]:focus-within,
    div[data-testid="stChatInput"]:active,
    div[data-testid="stChatInput"]:focus {
        border-color: #cbd5e1 !important;
        box-shadow: 0 6px 24px rgba(0,0,0,0.08) !important;
        outline: none !important;
    }
    div[data-testid="stChatInput"] textarea {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
        color: #1a1a2e !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 15.5px !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* Premium Styled Submit Arrow Button */
    button[data-testid="stChatInputSubmitButton"] {
        background-color: #1c1c2e !important;
        color: #ffffff !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: background-color 0.15s ease !important;
    }
    button[data-testid="stChatInputSubmitButton"]:hover {
        background-color: #2e2e4a !important;
    }
    button[data-testid="stChatInputSubmitButton"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    /* ===== CHAT MESSAGES ===== */
    div[data-testid="stChatMessage"] {
        background: #ffffff !important;
        border-radius: 16px !important;
        padding: 18px 22px !important;
        margin: 12px 0 !important;
        border: 1px solid #eaecf0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
        font-size: 15px !important;
        line-height: 1.7 !important;
    }

    /* ===== SOURCE CONTAINER & PILLS WITH 'X' ===== */
    div.sources-container {
        margin: 12px 0 !important;
        width: 100% !important;
    }
    div.sources-container div[data-testid="stColumn"] div[data-testid="stButton"] > button {
        background-color: #eef2ff !important;
        border: 1px solid #c7d2fe !important;
        border-radius: 16px !important;
        color: #4338ca !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 6px 12px !important;
        width: 100% !important;
        min-height: 32px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
        transition: all 0.15s ease-in-out !important;
        white-space: nowrap !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div.sources-container div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
        background-color: #e0e7ff !important;
        border-color: #a5b4fc !important;
        color: #3730a3 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 5px rgba(67,56,202,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

current_profile = load_profile()


@st.dialog("Paste website & YouTube URLs to add as a source in IntellectAI")
def websites_dialog():
    st.caption("Paste any links below to import as study sources.")
    links = st.text_area("Paste any links", height=180, placeholder="https://example.com\nhttps://youtube.com/watch?v=...")
    st.markdown(
        "- To add multiple URLs, separate them with a space or a new line.\n"
        "- Only the visible text on the website will be imported.\n"
        "- Only public YouTube videos / pages are supported."
    )
    if st.button("Insert", type="primary", key="ins_links"):
        urls = [u.strip() for u in links.replace("\n", " ").split(" ") if u.strip()]
        added = 0
        for u in urls:
            text = fetch_url_text(u)
            st.session_state.sources.append({
                "type": "🌐",
                "name": u,
                "content": f"[WEBSITE SOURCE: {u}]\n{text}"
            })
            added += 1
        st.session_state.view_state = "chat"
        st.success(f"Inserted {added} link(s) as sources.")
        st.rerun()


@st.dialog("Upload files from your folder")
def upload_dialog():
    st.caption("Choose files from your computer folder to add as study sources.")
    files = st.file_uploader(
        "Upload files",
        type=["pdf", "docx", "txt", "md", "py", "csv", "json"],
        accept_multiple_files=True,
        key="uploader_main",
    )
    if st.button("Add as sources", type="primary", key="add_uploads"):
        added = 0
        for f in files or []:
            text = extract_file_text(uploaded_file=f, file_name=f.name)
            st.session_state.sources.append({
                "type": "📄",
                "name": f.name,
                "content": f"[UPLOADED FILE: {f.name}]\n{text}"
            })
            added += 1
        st.session_state.view_state = "chat"
        st.success(f"Added {added} file(s) as sources.")
        st.rerun()


@st.dialog("Select items")
def drive_dialog():
    st.markdown(
        "<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>"
        "<span style='font-size:20px;'>🟢🔵🟡</span>"
        "<b style='font-size:18px;'>Search in Drive or paste URL</b></div>",
        unsafe_allow_html=True,
    )
    tabs = st.tabs(["Recent", "My Drive", "Shared with me", "Starred", "Computers"])
    with tabs[0]:
        st.caption("Recent")
        drive_url = st.text_input(
            "Paste a Google Drive / Docs / Slides / Sheets link",
            placeholder="https://drive.google.com/file/d/.../view",
            key="drive_url_in",
        )
        st.markdown(
            "- Paste a **public / shared** Google Drive link to import its text.\n"
            "- Make sure link sharing is set to *Anyone with the link*."
        )
        if st.button("Insert", type="primary", key="ins_drive"):
            url = (drive_url or "").strip()
            if url:
                text = fetch_url_text(url)
                st.session_state.sources.append({
                    "type": "📁",
                    "name": url,
                    "content": f"[DRIVE SOURCE: {url}]\n{text}"
                })
                st.session_state.view_state = "chat"
                st.success("Inserted Drive item as a source.")
                st.rerun()
            else:
                st.warning("Please paste a Drive URL first.")
    for t in tabs[1:]:
        with t:
            st.info("Sign-in based browsing is not available here. Paste a Drive share URL in the **Recent** tab to import.")


# SIDEBAR RENDER 
with st.sidebar:
    _robot_html = (
        f"<img src='{ROBOT_URI}' class='sb-logo' alt='IntellectAI robot'/>"
        if ROBOT_URI else "<span style='font-size:28px;'>🤖</span>"
    )
    st.markdown(f"""
    <div class="sb-brand">
        {_robot_html}
        <div>
            <div class="sb-title">IntellectAI</div>
            <div class="sb-tagline">Education &amp; Career Advisor</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if PROFILE_PIC_URI:
        st.markdown(
            f"""
            <div class="sb-profile">
                <img src="{PROFILE_PIC_URI}" class="sb-avatar" alt="Profile picture"/>
                <div>
                    <div class="sb-uname">{current_profile['name']}</div>
                    <div class="sb-ustatus">{current_profile['status']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("👤  My Profile", key="profile_btn_trigger", use_container_width=True):
        st.session_state.view_state = "profile"
        st.rerun()

    if st.button("💬  New Chat", use_container_width=True):
        persist_current()
        new_chat()
        st.rerun()

    # Toggled interactive Recents History button with clock icon
    show_hist = st.session_state.get('show_history', True)
    if st.button("🕒  Recents History", key="recents_history_header_btn", use_container_width=True):
        st.session_state.show_history = not show_hist
        st.rerun()

    if show_hist:
        if st.session_state.all_chats:
            for c in st.session_state.all_chats:
                label_text = f"💬 {c['ts']} - {c['title']}"
                if st.button(label_text, key=f"log_{c['id']}", use_container_width=True):
                    load_chat(c["id"])
                    st.rerun()
        else:
            st.caption("No history items yet.")

    st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)

    if st.button("⚙️  Settings", use_container_width=True, key="settings_btn"):
        st.session_state.view_state = "settings"
        st.rerun()


# MAIN WORKSPACE 
if st.session_state.view_state == "profile":
    if PROFILE_PIC_URI:
        st.markdown(
            f"""
            <div class="profile-row">
                <img src="{PROFILE_PIC_URI}" class="profile-pic-lg" alt="Profile picture"/>
                <div>
                    <h2 style="margin:0;color:#111827;">{current_profile['name']}</h2>
                    <p style="margin:0;color:#6b7280;">{current_profile['status']} · {current_profile['university']}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("## 👤 My Profile")

    if st.session_state.profile_editing:
        with st.form("profile_edit_form"):
            p_name = st.text_input("Name", value=current_profile["name"])
            p_fname = st.text_input("First Name", value=current_profile.get("first_name", ""))
            p_lname = st.text_input("Last Name", value=current_profile.get("last_name", ""))
            p_program = st.text_input("Program", value=current_profile["program"])
            p_dept = st.text_input("Department", value=current_profile["department"])
            p_year = st.text_input("Year", value=current_profile["year"])
            p_status = st.text_input("Status", value=current_profile["status"])
            p_univ = st.text_input("University", value=current_profile["university"])
            p_matric = st.text_input("Matriculation", value=current_profile.get("matriculation", ""), placeholder="e.g. 90% - ABC Board")
            p_inter = st.text_input("Intermediate", value=current_profile.get("intermediate", ""), placeholder="e.g. 85% - XYZ College")
            p_certs = st.text_area("Certifications", value=current_profile.get("certifications", ""), placeholder="e.g. Coursera Python, Google IT Support")
            p_contact = st.text_input("Contact", value=current_profile.get("contact", ""), placeholder="e.g. email or phone")
            p_address = st.text_input("Address", value=current_profile.get("address", ""))
            p_skills = st.text_area(
                "Skills (add what you learn over time)",
                value=current_profile.get("skills", ""),
                placeholder="e.g. Python, HTML/CSS, Data Structures, Public Speaking",
            )
            p_exp = st.text_area(
                "Experience",
                value=current_profile.get("experience", ""),
                placeholder="e.g. Built a portfolio website, Completed an AI bootcamp",
            )
            col_psave, col_pcancel = st.columns([1, 4])
            with col_psave:
                if st.form_submit_button("Save", type="primary"):
                    save_profile({
                        "name": p_name, "first_name": p_fname, "last_name": p_lname,
                        "program": p_program, "department": p_dept,
                        "year": p_year, "status": p_status, "university": p_univ,
                        "matriculation": p_matric, "intermediate": p_inter,
                        "certifications": p_certs, "contact": p_contact, "address": p_address,
                        "skills": p_skills, "experience": p_exp,
                    })
                    st.session_state.profile_editing = False
                    st.success("Profile updated!")
                    st.rerun()
            with col_pcancel:
                if st.form_submit_button("Cancel"):
                    st.session_state.profile_editing = False
                    st.rerun()
    else:
        col_edit, col_back = st.columns([1, 4])
        with col_edit:
            if st.button("✏️ Edit Profile", type="primary", key="edit_profile_btn"):
                st.session_state.profile_editing = True
                st.rerun()
        with col_back:
            if st.button("← Back to Chat", key="profile_back_btn"):
                st.session_state.view_state = "chat"
                st.rerun()

        st.markdown("### Saved Details")
        st.markdown(f"""
        - **Name:** {current_profile['name']}
        - **First Name:** {current_profile.get('first_name', '') or '_not set_'}
        - **Last Name:** {current_profile.get('last_name', '') or '_not set_'}
        - **Program:** {current_profile['program']}
        - **Department:** {current_profile['department']}
        - **Year:** {current_profile['year']}
        - **Status:** {current_profile['status']}
        - **University:** {current_profile['university']}
        - **Matriculation:** {current_profile.get('matriculation', '') or '_not set_'}
        - **Intermediate:** {current_profile.get('intermediate', '') or '_not set_'}
        - **Certifications:** {current_profile.get('certifications', '') or '_not set_'}
        - **Contact:** {current_profile.get('contact', '') or '_not set_'}
        - **Address:** {current_profile.get('address', '') or '_not set_'}
        """)
        st.markdown("### 🛠️ Skills")
        st.markdown(current_profile.get("skills") or "_No skills added yet. Click **Edit Profile** to add what you learn._")
        st.markdown("### 💼 Experience")
        st.markdown(current_profile.get("experience") or "_No experience added yet. Click **Edit Profile** to add._")

elif st.session_state.view_state == "settings":
    st.markdown("## ⚙️ Settings")
    if st.button("Clear All Chat History", type="primary"):
        st.session_state.all_chats = []
        save_memory([])
        new_chat()
        st.success("Cleared!")
        st.rerun()
    if st.button("← Back to Chat"):
        st.session_state.view_state = "chat"
        st.rerun()

else:
    #CHAT VIEW
    if not st.session_state.messages:
        # Centered spacious landing page elements
        if ROBOT_URI:
            st.markdown(
                f"<div class='hero-wrapper'><img src='{ROBOT_URI}' class='hero-robot-img' alt='IntellectAI robot'/>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div class='hero-wrapper'><h1 style='text-align:center;font-size:80px;margin-bottom:24px;'>🤖</h1>", unsafe_allow_html=True)

        st.markdown(f"""
            <div class="hero-title-main">What's on your mind, {current_profile["name"]}?</div>
            <div class="hero-sub-main">I'm IntellectAI, your personalized education &amp; career advisor. Ask me anything about study, careers, or your future.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for m in st.session_state.messages:
            avatar_icon = "🧑‍💻" if m["role"] == "user" else (ROBOT_URI if ROBOT_URI else "🤖")
            with st.chat_message(m["role"], avatar=avatar_icon):
                st.markdown(m["content"])

    if st.session_state.sources:
        st.markdown("<div class='sources-container'>", unsafe_allow_html=True)
        # Render horizontal capsule columns for interactive 'X' close deletions
        num_sources = len(st.session_state.sources)
        cols = st.columns(num_sources)
        for idx, s in enumerate(st.session_state.sources):
            with cols[idx]:
                display_name = s['name']
                # Clean URL parsing for display in website capsule names
                if display_name.startswith("http"):
                    display_name = display_name.replace("https://", "").replace("http://", "").split("/")[0]
                if len(display_name) > 15:
                    display_name = display_name[:12] + "..."
                if st.button(f"{s['type']} {display_name} ✕", key=f"src_pill_{idx}", use_container_width=True):
                    st.session_state.sources.pop(idx)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # DISCLAIMER (Clearly underneath the description/messages)
    st.markdown(
        '<div class="disclaimer-text">IntellectAI can make mistakes. Consider verifying important academic information.</div>',
        unsafe_allow_html=True,
    )

    # 3 ACTION BUTTONS (Perfect horizontal row below the disclaimer)
    _, col_b1, col_b2, col_b3, _ = st.columns([1.2, 1.3, 1.3, 1.3, 1.2])
    with col_b1:
        if st.button("📤  Upload files", key="btn_upload"):
            upload_dialog()
    with col_b2:
        if st.button("🌐  Websites", key="btn_web"):
            websites_dialog()
    with col_b3:
        if st.button("📁  Drive", key="btn_drive"):
            drive_dialog()

    # CHAT INPUT
    try:
        submission = st.chat_input(
            "Ask about careers, academics, notes, interview prep, word meanings...",
            accept_file=True,
            file_type=["pdf", "docx", "txt", "md", "py", "csv", "json"],
        )
    except TypeError:
        submission = st.chat_input("Ask about careers, academics, notes, interview prep, word meanings...")

    # PROCESS INPUT
    input_text = None
    attached_files = []
    if submission:
        if isinstance(submission, str):
            input_text = submission
        else:
            input_text = getattr(submission, "text", "") or ""
            attached_files = list(getattr(submission, "files", []) or [])

    if attached_files:
        for f in attached_files:
            text = extract_file_text(uploaded_file=f, file_name=f.name)
            st.session_state.sources.append({
                "type": "📄",
                "name": f.name,
                "content": f"[UPLOADED FILE: {f.name}]\n{text}"
            })

    if input_text:
        st.session_state.messages.append({"role": "user", "content": input_text})
        with st.spinner("Thinking..."):
            ai_response = ask_gemini(input_text)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        persist_current()
        st.rerun()
    elif attached_files:
        st.rerun()
