# 🤖 Autonomous Customer Support Copilot

An AI-powered customer support application with role-based access (User/Admin), a custom knowledge base (RAG), and a dynamic AI engine capable of handling real-time math, Wikipedia searches, and time lookup.

## ✨ Features
*   **Dual Modules**: Role-based access control with separate User and Admin portals.
*   **Dynamic AI Engine**: Automatically intercepts specific queries (Math, Time, Wikipedia, Places).
*   **Smart Escalation**: Classifies complex intents and escalates them to human experts.
*   **Learning Memory**: If an Admin answers a complex query, the AI learns it and instantly regurgitates that exact answer for future users asking the same question.
*   **Streaming UI**: ChatGPT-like text generation effect.
*   **Analytics Dashboard**: Real-time tracking of query resolution and escalation metrics.

## 🚀 How to Run Locally

1. **Install Dependencies**:
   Open your terminal in this folder and run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Application**:
   ```bash
   streamlit run app.py
   ```

## 🔐 Accounts & Roles
*   **Users**: Create a new account via the 'Sign Up' tab in the User Module.
*   **Admins**: 5 fixed admins are pre-registered in the database.
    *   **Usernames**: `admin1`, `admin2`, `admin3`, `admin4`, `admin5`
    *   **Password**: `admin123`

## ☁️ How to Deploy (Streamlit Community Cloud)
1. Upload this entire folder to a **GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub account.
4. Click **New App**, select your repository, and set `app.py` as the Main file path.
5. Click **Deploy**. Your app will be live and free on the internet!
