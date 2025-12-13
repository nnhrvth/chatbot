import streamlit as st
from src import storage, rule_engine, suggestion_engine
from src.models import Medication
import uuid

st.set_page_config(page_title="MediMini", layout="wide")
st.title("MediMini — Smart Medication Assistant")

USER_ID = "u1"

# Daten laden
rules = storage.load_rules()
meds = storage.get_medications_for_user(USER_ID)

st.sidebar.header("Aktionen")

# Medikament hinzufügen
with st.sidebar.expander("Medikament hinzufügen"):
    with st.form("add_med"):
        name = st.text_input("Name")
        dose = st.text_input("Dosis")
        times = st.text_input("Einnahmezeiten (ISO, z.B. 2025-12-11T08:00:00)")
        submit = st.form_submit_button("Hinzufügen")

        if submit and name:
            med = Medication(
                id=str(uuid.uuid4()),
                user_id=USER_ID,
                name=name,
                dose=dose or None,
                times=[t.strip() for t in times.split(",")],
                start_date=None,
                end_date=None
            )
            data = storage.load_data()
            data["medications"].append(med.dict())
            storage.save_data(data)
            st.success("Medikament hinzugefügt")
            st.experimental_rerun()

# Interaktionen prüfen
if st.sidebar.button("Interaktionen prüfen"):
    conflicts = rule_engine.check_conflicts(meds, rules)
    st.session_state["conflicts"] = conflicts

st.header("Einnahmeplan")
for m in meds:
    st.write(f"**{m['name']}** ({m.get('dose','')}) → {m['times']}")

conflicts = st.session_state.get("conflicts")

if conflicts:
    st.error(f"{len(conflicts)} Konflikt(e) erkannt")
    for c in conflicts:
        st.write(c)
        if st.button("Vorschlag generieren", key=c["med_a_id"]):
            suggestions = suggestion_engine.generate_suggestions(meds, rules)
            st.session_state["suggestions"] = suggestions

suggestions = st.session_state.get("suggestions")
if suggestions:
    st.header("Vorschläge")
    for s in suggestions:
        for cand in s["candidates"]:
            if st.button(f"{cand['old_time']} → {cand['new_time']}"):
                suggestion_engine.apply_suggestion(
                    USER_ID,
                    {"candidates": [cand]},
                    meds,
                    storage
                )
                st.success("Vorschlag angewendet")
                st.experimental_rerun()
