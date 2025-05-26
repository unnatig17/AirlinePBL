import streamlit as st
import sqlite3
import hashlib
from collections import deque
import streamlit_extras.switch_page_button as spb

class LoginPage: 
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
    
    def create_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def create_users_table(self):
        conn = self.create_connection()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     username TEXT PRIMARY KEY,
                     password TEXT)''')
        conn.commit()
        conn.close()

    def add_user(self, username, password):
        conn = self.create_connection()
        c = conn.cursor()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def authenticate_user(self, username, password):
        conn = self.create_connection()
        c = conn.cursor()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        result = c.fetchone()
        conn.close()
        return result is not None

lp = LoginPage()
lp.create_users_table()

st.title("Login Page")

menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if menu == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if lp.authenticate_user(username, password):
            st.success(f"Welcome {username}!")
            st.session_state["user"] = username
            st.switch_page("app_pages/main.py")
        else:
            st.error("Invalid username or password")

elif menu == "Register":
    st.subheader("Register")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Register"):
        if lp.add_user(new_user, new_pass):
            st.success("Account created successfully! Go to Login.")
        else:
            st.warning("Username already exists.")
