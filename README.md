# 🤖 AutoFixer: The Log-to-PR Agent

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**AutoFixer** is an autonomous AI agent that watches your production server logs. When a crash occurs, it analyzes the stack trace, finds the exact bug in your codebase, writes a fix, and automatically opens a Pull Request on GitHub. 

Wake up to Pull Requests, not Production Crashes.

## 🚀 Features
- **Real-time Log Watching:** Instantly detects `Exceptions` and `Errors`.
- **AI-Powered Root Cause Analysis:** Extracts file paths, line numbers, and understands *why* it crashed.
- **Autonomous Fix Generation:** Uses LLMs to generate safe, contextual code fixes.
- **Auto Pull Request:** Creates a new branch, commits the fix, and opens a beautiful PR with explanation.

## 🚀 Quick Setup

1. **Clone & Install Dependencies**
   ```bash
   git clone https://github.com/your-username/autofixer-agent.git
   cd autofixer-agent
   pip install -r requirements.txt
   ```

2. **🔑 API Keys Setup (Crucial Step)**
   AutoFixer requires two API keys to function as a real AI:
   - **Gemini API Key:** For analyzing errors and generating code fixes.
   - **GitHub Personal Access Token:** For automatically creating branches and Pull Requests.
   
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY and GITHUB_TOKEN
   ```

3. **Start the Agent**
   ```bash
   python main.py
   ```

## 🧪 Try it out
While `main.py` is running, try simulating a crash by writing an error to `error.log`:
```bash
echo "Traceback (most recent call last):" >> error.log
echo "  File \"src/app.py\", line 42, in <module>" >> error.log
echo "    print(user['name'])" >> error.log
echo "KeyError: 'name'" >> error.log
```
Watch the terminal as AutoFixer analyzes the error and automatically generates the PR!

## 🤝 Contributing
We welcome contributions! Please see `CONTRIBUTING.md` for guidelines.

## 📝 License
MIT License
