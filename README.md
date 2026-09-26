# EduGenie: Google Gemini Powered Educational Assistant

EduGenie is a lightweight AI-powered educational assistant that simplifies learning through generative AI. Designed for students of all academic levels, EduGenie enables users to:

- 💬 **Ask questions and receive smart, concise answers** or simplified explanations with analogies.
- 📝 **Generate interactive quizzes** from topics or text with instant grading, score breakdown, and explanations.
- 🗺️ **Receive personalized learning recommendations** & structured roadmaps with timelines, topics, and exercises.
- 📄 **Summarize large educational passages**, extracting key takeaways and core terminology.

Built with **FastAPI** for the backend and a responsive **HTML+CSS+JS frontend**, EduGenie leverages lightweight and cloud-based AI models for local efficiency and cloud power.

---

## 🌟 Core Features & Demonstration Scenarios

- **Scenario 1 (Q&A)**: A student asking *"Which is the largest ocean?"* gets structured facts, area, depth, and origin details about the Pacific Ocean.
- **Scenario 2 (Quiz)**: A student testing understanding of *"The Pythagoras Theorem"* clicks **Generate Quiz** to receive multiple-choice questions with real-time grading.
- **Scenario 3 (Learning Path)**: A learner exploring *"SQL"* receives a multi-week structured roadmap with stage objectives, key topics, and practical exercise ideas.
- **Passage Summarizer**: Convert long lecture notes or articles into structured summaries, key bullet points, and defined terms.

---

## 🛠️ Tech Stack & Required Skills

- **Backend**: FastAPI, Uvicorn, Python 3.14
- **Generative AI Engine**: Google Gemini API (`google-genai` / `google-generativeai`)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6), Marked.js, FontAwesome
- **Database**: SQLite (`edugenie.db`)

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Installation & Setup
Clone the repository and install requirements:

```bash
git clone https://github.com/siva240905/EduGenie.git
cd EduGenie
pip install -r requirements.txt
```

### 3. Environment Configuration (Optional)
Copy `.env.example` to `.env` and set your Google Gemini API Key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

*(Note: You can also enter your Gemini API Key directly in the UI header input, or use Demonstration Mode without an API Key.)*

---

## 🏃 Running the Application

Launch the server using any of the following commands:

```bash
python app.py
```
or
```bash
python -m uvicorn app:app --reload --port 8000
```
or double click `start.bat` on Windows.

Open your browser at **`http://localhost:8000`**.

---

## 🧪 Running Automated Tests

Run the test suite to verify all API endpoints:

```bash
python test_app.py
```

---

## 📜 License
MIT License
