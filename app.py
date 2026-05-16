import streamlit as st
import time

# Set up Streamlit Page FIRST
st.set_page_config(page_title="Support Copilot", page_icon="🤖", layout="wide")

import database
from chatbot import SupportCopilot
from feedback import render_feedback_ui

# Initialize Database and Seed it
database.init_db()

@st.cache_resource
def get_chatbot():
    return SupportCopilot()

bot = get_chatbot()

def stream_text(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.05)

# --- AUTHENTICATION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- AUTHENTICATION UI ---
if not st.session_state.logged_in:
    st.title("🔐 Welcome to Support Copilot")
    st.markdown("Please select your module to continue:")
    
    module_selection = st.radio("Select Module:", ["User Module", "Admin Module"], horizontal=True)
    
    if module_selection == "User Module":
        st.subheader("👤 User Portal")
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
        
        with tab_login:
            with st.form("user_login_form"):
                l_username = st.text_input("Username")
                l_password = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Log In")
                
                if submit_login:
                    is_auth, role = database.authenticate_user(l_username, l_password)
                    if is_auth:
                        if role == 'admin':
                            st.error("You are an admin. Please select the 'Admin Module' to log in.")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.username = l_username
                            st.session_state.role = role
                            st.success("Logged in successfully!")
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        st.error("Invalid username or password.")
                        
        with tab_signup:
            with st.form("signup_form"):
                s_username = st.text_input("Choose a Username")
                s_password = st.text_input("Choose a Password", type="password")
                submit_signup = st.form_submit_button("Sign Up")
                
                if submit_signup:
                    if len(s_username) < 3 or len(s_password) < 3:
                        st.error("Username and password must be at least 3 characters.")
                    else:
                        success = database.create_user(s_username, s_password, role='user')
                        if success:
                            st.success("Account created successfully! Logging you in...")
                            st.session_state.logged_in = True
                            st.session_state.username = s_username
                            st.session_state.role = 'user'
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Username already exists. Please choose another one.")
                            
    elif module_selection == "Admin Module":
        st.subheader("🛡️ Admin Portal")
        
        with st.form("admin_login_form"):
            a_username = st.text_input("Admin Username")
            a_password = st.text_input("Admin Password", type="password")
            submit_admin_login = st.form_submit_button("Admin Log In")
            
            if submit_admin_login:
                is_auth, role = database.authenticate_user(a_username, a_password)
                if is_auth:
                    if role != 'admin':
                        st.error("Access Denied. You do not have admin privileges.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.username = a_username
                        st.session_state.role = role
                        st.success("Logged in successfully as Admin!")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    st.error("Invalid admin credentials.")

else:
    # --- LOGGED IN UI ---
    st.sidebar.title(f"👤 Welcome, {st.session_state.username}")
    st.sidebar.markdown(f"**Role:** {st.session_state.role.capitalize()}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    # --- ADMIN MODULE ---
    if st.session_state.role == 'admin':
        st.title("🛡️ Admin Control Panel")
        
        tab_pending, tab_resolved, tab_users, tab_all_queries = st.tabs([
            "Pending Tickets", "Resolved Tickets", "User Database", "All User Queries"
        ])
        
        with tab_pending:
            st.header("Escalated Tickets (Requires Action)")
            pending_df = database.get_pending_tickets()
            
            if pending_df.empty:
                st.success("No pending tickets! You are all caught up.")
            else:
                for index, row in pending_df.iterrows():
                    with st.expander(f"Ticket #{row['id']} from {row['username']} - {row['timestamp']}"):
                        st.write(f"**User Question:** {row['user_query']}")
                        st.write(f"**AI Response:** {row['chatbot_response']}")
                        
                        with st.form(f"reply_form_{row['id']}"):
                            admin_reply = st.text_area("Your Reply:")
                            if st.form_submit_button("Send Reply"):
                                database.reply_to_ticket(row['id'], admin_reply)
                                st.success("Reply sent successfully!")
                                st.rerun()
                                
        with tab_resolved:
            st.header("Resolved Tickets")
            resolved_df = database.get_resolved_tickets()
            if resolved_df.empty:
                st.info("No resolved tickets yet.")
            else:
                st.dataframe(resolved_df[['id', 'username', 'user_query', 'admin_response', 'timestamp']], use_container_width=True)
            
        with tab_users:
            st.header("Registered Users")
            users_df = database.get_all_users()
            st.dataframe(users_df, use_container_width=True)
            
        with tab_all_queries:
            st.header("Global Chat Logs")
            queries_df = database.get_all_interactions()
            st.dataframe(queries_df[['id', 'username', 'user_query', 'predicted_intent', 'chatbot_response', 'escalated']], use_container_width=True)

    # --- USER MODULE ---
    else:
        st.title("🤖 Autonomous Customer Support Copilot")
        st.markdown("I am your smart AI assistant. I can answer FAQs, do math, check the time, and search general knowledge!")

        tab1, tab_tickets, tab2 = st.tabs(["💬 Chat", "🎫 My Tickets", "📊 Analytics Dashboard"])

        with tab1:
            if "messages" not in st.session_state:
                st.session_state.messages = []
                
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg["role"] == "assistant" and "interaction_id" in msg:
                        render_feedback_ui(msg["interaction_id"])

            st.write("---")
            st.write("**Suggested Queries:**")
            cols = st.columns(4)
            suggestions = ["I need to speak to a manager", "What is 15 * 8?", "What is the time?", "Places to visit in Paris"]
            
            selected_prompt = None
            for i, suggestion in enumerate(suggestions):
                if cols[i].button(suggestion):
                    selected_prompt = suggestion

            prompt = st.chat_input("Type your message here...")
            final_prompt = selected_prompt if selected_prompt else prompt

            if final_prompt:
                st.session_state.messages.append({"role": "user", "content": final_prompt})
                with st.chat_message("user"):
                    st.markdown(final_prompt)
                    
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response, escalated, intent = bot.process_query(final_prompt)
                        interaction_id = database.log_interaction(
                            username=st.session_state.username,
                            query=final_prompt, 
                            intent=intent, 
                            response=response, 
                            escalated=escalated
                        )
                        st.write_stream(stream_text(response))
                        render_feedback_ui(interaction_id)
                        
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "interaction_id": interaction_id
                })
                
        with tab_tickets:
            st.header("My Support Tickets")
            st.markdown("If your question was too complex, it was sent to our human experts. Check responses here.")
            
            user_tickets = database.get_user_tickets(st.session_state.username)
            if user_tickets.empty:
                st.info("You don't have any escalated tickets.")
            else:
                for index, row in user_tickets.iterrows():
                    status_emoji = "✅ Resolved" if row['admin_response'] else "⏳ Pending Review"
                    with st.expander(f"Ticket #{row['id']} - {row['timestamp']} | {status_emoji}"):
                        st.write(f"**Your Question:** {row['user_query']}")
                        if row['admin_response']:
                            st.success(f"**Expert Reply:** {row['admin_response']}")
                        else:
                            st.warning("An expert is currently reviewing this ticket. Please check back later.")

        with tab2:
            st.header("Analytics Dashboard")
            st.markdown("Real-time metrics for your customer support bot.")
            if st.button("Refresh Metrics"):
                st.rerun()
            metrics = database.get_metrics()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Queries", metrics["total_queries"])
            col2.metric("Resolved Tickets", metrics["resolved"])
            col3.metric("Escalated Tickets", metrics["escalated"])
            col4.metric("Helpful Rate", metrics["helpful_rate"])
