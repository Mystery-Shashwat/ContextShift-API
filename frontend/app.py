import os
import streamlit as st
import requests

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="ContextShift", page_icon="🧠", layout="centered")

if "token" not in st.session_state:
    st.session_state.token = None

def login(username, password):
    response = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
    if response.status_code == 200:
        st.session_state.token = response.json()["access_token"]
        st.success("Logged in successfully!")
        st.rerun()
    else:
        st.error("Invalid credentials")

def register(username, password):
    response = requests.post(f"{API_URL}/auth/register", json={"username": username, "password": password})
    if response.status_code == 200:
        st.success("Registered successfully! You can now log in.")
    else:
        st.error(response.json().get("detail", "Registration failed"))

def logout():
    st.session_state.token = None
    st.rerun()

if not st.session_state.token:
    st.title("Welcome to ContextShift 🧠")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            l_username = st.text_input("Username")
            l_password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                login(l_username, l_password)
                
    with tab2:
        with st.form("register_form"):
            r_username = st.text_input("Username")
            r_password = st.text_input("Password", type="password")
            if st.form_submit_button("Register"):
                register(r_username, r_password)
else:
    st.sidebar.title("ContextShift")
    if st.sidebar.button("Logout"):
        logout()
        
    st.title("Dashboard")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    tab1, tab2 = st.tabs(["Save Context", "Resume Context"])
    
    with tab1:
        st.header("Save New Context")
        raw_context = st.text_area("What are you working on?", height=150)
        if st.button("Save Context"):
            with st.spinner("Analyzing with Groq LLM..."):
                resp = requests.post(f"{API_URL}/save", json={"raw_context": raw_context}, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"Context saved! ID: `{data['id']}`")
                    with st.expander("View Structured Data", expanded=True):
                        st.json(data)
                else:
                    st.error("Failed to save context")
                    
    with tab2:
        st.header("Resume Previous Context")
        
        # Fetch user's contexts
        resp = requests.get(f"{API_URL}/contexts", headers=headers)
        if resp.status_code == 200:
            contexts = resp.json()
            if not contexts:
                st.info("You don't have any saved contexts yet.")
            else:
                context_id = st.selectbox("Select Context ID to resume", [c["id"] for c in contexts])
                if st.button("Resume"):
                    r_resp = requests.get(f"{API_URL}/resume/{context_id}", headers=headers)
                    if r_resp.status_code == 200:
                        r_data = r_resp.json()
                        st.write("### Summary")
                        st.info(r_data.get("summary", ""))
                        st.write("### Next Step")
                        st.success(r_data.get("next_step", ""))
                        if r_data.get("questions"):
                            st.write("### Open Questions")
                            for q in r_data["questions"]:
                                st.warning(q)
                    else:
                        st.error("Failed to load context")
