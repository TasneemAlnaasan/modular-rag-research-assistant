import streamlit as st
import requests

API_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="Multi-Source Research Assistant", page_icon="🔍")

st.title("🔍 Multi-Source Research Assistant")
st.caption("Ask about AI companies — vision, funding, or latest news.")

question = st.text_input("Your question:")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        try:
            response = requests.post(API_URL, json={"question": question})
            response.raise_for_status()
            answer = response.json()["answer"]
            st.markdown(f"**Answer:** {answer}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the API: {e}")
import streamlit as st
import requests

API_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="Multi-Source Research Assistant", page_icon="🔍")

st.title("🔍 Multi-Source Research Assistant")
st.caption("Ask about AI companies — vision, funding, or latest news.")

with st.form(key="question_form"):
    question = st.text_input("Your question:")
    submitted = st.form_submit_button("Ask")

if submitted and question:
    with st.spinner("Thinking..."):
        try:
            response = requests.post(API_URL, json={"question": question})
            response.raise_for_status()
            answer = response.json()["answer"]
            st.markdown(f"**Answer:** {answer}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the API: {e}")
