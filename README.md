# ⚖️ The Jury: The AI Courtroom (God Mode)

A single, production-grade Adversarial AI Consensus Engine. This tool empowers users to force Large Language Models (LLMs) to debate, cross-examine, and judge each other to produce hallucination-free, high-confidence answers. Built with **FastAPI, Streamlit, and MySQL**, it offers a "Glass Box" experience to watch AI reasoning in real-time.

<p align="center">
  <img src="https://i.ibb.co/Vp8p6X6/jury-cover.png" alt="The Jury Dashboard Screenshot" width="100%">
  <br>
  <i>(A glimpse of the God Mode UI: Proposer, Critic, and Judge in action)</i>
</p>

[![Repo Size](https://img.shields.io/github/repo-size/KING-OF-FLAME/the-jury-ai-courtroom?style=flat-square&color=orange)](https://github.com/KING-OF-FLAME/the-jury-ai-courtroom)
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/KING-OF-FLAME/the-jury-ai-courtroom)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/KING-OF-FLAME/the-jury-ai-courtroom/graphs/commit-activity)

-------------------------------------------------

## 🌟 About The Project 📍

"The Jury" addresses the critical need for accuracy in Generative AI. Instead of trusting a single model's output (which may hallucinate), this system orchestrates a legal proceeding between multiple AI agents.

This project showcases:
*   **Adversarial Architecture**: Implements a Proposer (Optimist), Critic (Skeptic), and Judge (Realist) workflow.
*   **God Mode Config**: Inject specific personas (e.g., *"NSA Security Auditor"* vs *"Ruthless Lawyer"*) to change the debate tone.
*   **Live Cost Auditing**: Tracks token usage and calculates the exact dollar cost ($) of every case execution.
*   **Persistent Memory**: Uses MySQL to store every verdict, creating a database of "Legal Precedents."
*   **Vanilla & Async Power**: Built with FastAPI (Backend) and Streamlit (Frontend) for high-performance, asynchronous execution.

-------------------------------------------------

## 🚀 Getting Started 📍

To get "The Jury" up and running on your local machine, you'll need a web server environment (like XAMPP) and Python.

## Project Structure
```
the-jury-ai/
│
├── backend/                # FastAPI Application
│   ├── __init__.py
│   ├── main.py             # API Routes & Workflow Orchestration
│   ├── agents.py           # LLM Interaction Logic (Proposer, Critic, Judge)
│   ├── database.py         # MySQL Connection & CRUD operations
│   └── models.py           # Pydantic & SQLAlchemy Models
│
├── frontend/               # Streamlit UI
│   ├── app.py              # Main UI Logic
│   └── styles.css          # Custom styling for "Glass Box" look
│
├── database/               # Database Initialization
│   └── jury_db.sql         # SQL script for table creation
│
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
```


1.  **Clone the repository**:
    *   Open your command line or terminal.
    *   Run the command: `git clone https://github.com/KING-OF-FLAME/the-jury-ai-courtroom.git`

2.  **Database Setup (XAMPP)**:
    *   Start **Apache** and **MySQL** in XAMPP.
    *   Go to `http://localhost/phpmyadmin`.
    *   Create a database named `jury_db`.
    *   Import the SQL script located at `database/jury_db.sql` (or let the app auto-create it).

3.  **Install Dependencies**:
    *   Navigate to the project folder.
    *   Run: `pip install -r requirements.txt`

4.  **Configure Secrets**:
    *   Create a `.env` file in the root directory:
    ```env
    OPENROUTER_API_KEY=your_key_here
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=
    DB_NAME=jury_db
    API_URL=http://localhost:8000
    ```

5.  **Run the Application**:
    *   **Terminal 1 (Backend)**: `uvicorn backend.main:app --reload`
    *   **Terminal 2 (Frontend)**: `streamlit run frontend/app.py`
    *   Access the dashboard at `http://localhost:8501`.

-------------------------------------------------

## ✨ Features 📍

*   **Chained Execution Engine**: Watch agents react to each other instantly (Proposer -> Critic -> Judge).
*   **"Khatarnak" Test Suite**: One-click execution of complex scenarios (e.g., Stuxnet Design, DeFi Arbitrage, Legal Loopholes).
*   **Confidence Scoring**: The Judge assigns a 0-100% confidence score to every verdict.
*   **Thinking Process Visualization**: Specialized parsing for "Chain of Thought" models like DeepSeek and Olmo.
*   **Responsive UI**: A modern "Glassmorphism" interface that works seamlessly on desktop.

-------------------------------------------------

## 💡 Usage 📍

1.  **Config**: Select your models (GPT-4o, Claude 3.5, etc.) and assign Personas via the Sidebar.
2.  **Submit Case**: Enter a query or select a Test Case (e.g., "Analyze this NDA clause").
3.  **Watch the Trial**: See the Proposer draft a solution and the Critic tear it apart.
4.  **Verdict**: Receive the final judgment and download the case report as Markdown.

-------------------------------------------------

## 🤝 Contributions 📍

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have suggestions for improving this project, please fork the repo and create a pull request. You can also open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

-------------------------------------------------

## 📧 Contact 📍

Github: [KING OF FLAME](https://github.com/KING-OF-FLAME) - Creator and Maintainer
Instagram: [yash.developer](https://instagram.com/yash.developer)

-------------------------------------------------

## 🙏 Acknowledgments 📍

*   Special thanks to **OpenRouter** for democratizing AI access.
*   To the open-source community for continuous inspiration and learning.
