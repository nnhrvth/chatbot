import streamlit as st
from openai import OpenAI
import time

st.title("💬 Custom Assistant Chatbot")
st.write(
    "Dieser Chatbot nutzt einen OpenAI Assistant über die Assistants API. "
    "Gib unten deinen OpenAI API Key ein, um loszulegen."
)

# Eingabe des API-Keys
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Bitte füge deinen OpenAI API Key ein, um fortzufahren.", icon="🗝️")
else:
    # Client erzeugen
    client = OpenAI(api_key=openai_api_key)

    # Session-States
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Vorherige Nachrichten anzeigen
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat-Eingabe
    if prompt := st.chat_input("Nachricht an deinen Assistant..."):

        # Nutzer-Eingabe speichern und anzeigen
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Nachricht an Thread senden
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Assistant-Run starten
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id="asst_HsHMJirBzfDZymplBlXKqFmQ"
        )

        # Warten bis die Antwort fertig ist
        with st.chat_message("assistant"):
            placeholder = st.empty()
            while True:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status in ["failed", "cancelled", "expired"]:
                    placeholder.error("Fehler beim Ausführen des Assistant-Runs.")
                    st.stop()
                time.sleep(1)

            # Antworten abrufen
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Letzte Assistant-Antwort anzeigen
            last_message = messages.data[0].content[0].text.value
            placeholder.markdown(last_message)
            st.session_state.messages.append({"role": "assistant", "content": last_message})
