# Onexa Assistant

AI-powered chatbot for Onexa ed-tech platform.

## Features

- Answers questions about Onexa courses and programs
- Provides enrollment information
- Suggests courses based on student background
- Works with or without Gemini API key

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   ```

### Environment Variables

- **GEMINI_API_KEY**: Get from https://aistudio.google.com/app/apikey
- **SECRET_KEY**: Any random string for Flask sessions (e.g., `my-secret-key-123`)

## Running Locally

```bash
python app.py
```

Visit http://localhost:5000

## Deployment on Render

1. Push to GitHub (don't commit .env!)
2. Create new Web Service on Render
3. Connect your GitHub repo
4. Set environment variables in Render dashboard:
   - `GEMINI_API_KEY`
   - `SECRET_KEY`
5. Deploy!

## Project Structure

```
onexa-assistant/
├── app.py              # Flask application
├── knowledge.py        # Knowledge base
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Chat interface
├── .env.example       # Environment variables template
└── .gitignore         # Git ignore rules
```
