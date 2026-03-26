```
---
title: Ai Resume Optimizer
emoji: 🚀
colorFrom: blue
colorTo: cyan
sdk: docker
pinned: false
app_port: 7860
---

# 🤖 ResumeAI Optimizer — ATS Scoring & AI Optimization
An AI-powered platform to help job seekers optimize their resumes against specific job descriptions. Features a web dashboard for point-and-click scoring and a Telegram bot for on-the-go optimization and PDF delivery.

## 🌟 Key Features

- **ATS Scoring**: Powered by HuggingFace/Gemini models to score resumes against job descriptions.
- **Detailed Feedback**: Provides actionable tips to improve your resume's impact, keywords, and formatting.
- **PDF Generation**: Generates optimized versions of your resume in PDF format.
- **Telegram Bot Integration**: Use `@YourBotName` to upload your resume and get instant scores and feedback.
- **Responsive Dashboard**: Beautiful dark-themed dashboard for managing your resume optimizations.

## 🛠️ Tech Stack

- **Backend**: Django 4.2+, Django Rest Framework
- **AI/ML**: HuggingFace Transformers (Llama/Gemini)
- **Frontend**: Vanilla CSS, Semantic HTML5
- **Telegram Bot**: `python-telegram-bot`
- **PDF Processing**: `pdfplumber`, `reportlab`

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/RATNESH2121/Ai_Resume_toptimizer.git
cd Ai_Resume_toptimizer
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (refer to `.env.example`):
```env
HF_API_TOKEN=your_huggingface_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DJANGO_SECRET_KEY=your_django_secret_key
DEBUG=True
```

### 5. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```

### 6. Start Telegram Bot
```bash
python bot/main.py
```

## 📜 Repository Structure

- `core/`: Core Django application (models, views, logic).
- `resume_optimizer/`: Project configuration (settings, urls).
- `bot/`: Telegram bot implementation.
- `requirements.txt`: Project dependencies.
- `.env.example`: Example environment configuration.

## 🤝 Contributing

Feel free to fork the project, open issues, and submit pull requests. Let's build a tool that helps everyone land their dream job!

---
Developed by **Ratnesh**
