# 🌟 ClauseEase: Contract Simplifier & Auth Portal

> A secure authentication web application and contract simplifying tool built using **Python (FastAPI) & MySQL**.  
> Analyze legal documents, get readability scores, and simplify complex clauses with a modern dark-themed UI.

---

## 🔥 Preview

![Dashboard UI](./image1.png)

---

## 🧠 Project Overview

ClauseEase is a comprehensive tool designed to help users manage and simplify legal contracts. It combines a robust authentication system with advanced NLP services to provide insights into document complexity.

### Key Features
- **User Authentication**: Secure registration and login with password hashing.
- **Contract Analysis**: Upload or paste text to get readability scores.
- **NLP metrics**: Flesch-Kincaid Grade Level and Gunning Fog Index.
- **Modern UI**: Sleek dark-mode dashboard with glassmorphism effects.
- **Document Management**: Securely store and manage uploaded PDF documents.

---

## 🏗 Tech Stack

**Frontend**
- HTML5 & Vanilla CSS (Custom Design System)
- JavaScript (Fetch API, DOM Manipulation)

**Backend**
- Python 3.x
- FastAPI
- MySQL Connector

**NLP & ML**
- NLTK
- TextStat / spaCy (Readability analysis)

**Security**
- Passlib (bcrypt) for password hashing
- Environment variables for sensitive configuration

---

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/aryanmish96-cloud/login-auth-app.git
   ```

2. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Set up Environment Variables**
   Create a `.env` file in the `backend/` directory:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=auth_db
   ```

4. **Run the application**
   ```bash
   cd backend
   python app.py
   ```

---

## ⚙️ System Flow

1. **Login/Register**: Users sign up or sign in to access the dashboard.
2. **Upload/Paste**: Users provide contract text or upload a PDF.
3. **Analyze**: The backend processes the text using NLP services.
4. **Insights**: Readability scores and simplified insights are displayed on the UI.
