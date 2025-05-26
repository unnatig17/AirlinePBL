import streamlit as st

pages = [
    st.Page("app_pages/login.py", title="Login"),
    st.Page("app_pages/main.py", title="Main")
]

pg = st.navigation(pages, position="hidden", expanded=False)

pg.run()