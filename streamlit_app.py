import streamlit as st
from datetime import datetime, timedelta
from dateutil import parser
import json
import os
import uuid

# ==================================================
# KONFIGURATION
# ==================================================

st.set_page_config(
    page_title="MediMini",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("MediMini")
st.subheader("Smart Medication Assistant")

DATA_FILE = "data.json"
USER_ID = "u1"

# ==================================================
# DEFAULT DATEN
# ==================================================

DEFAULT_DATA = {
    "users": [{"id": "u1", "email": "demo@example.com"}],
    "medications": [],
    "rules": [
        {
            "id": "R-001",
            "med_a": "MedA",
            "med_b": "MedB",
            "min_time_diff_minutes": 120
        }
    ],
    "changes_log": []
}

# ==================================================
# DATENHALTUNG
# ==================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ==================================================
# BUSINESS LOGIC
# ==================================================

def get_medications_for_user(data, user_id):
    return [m for m in data["medications"] if m["user_id"] == user_id]

def check_conflicts(medications, rules):
    conflicts = []
    for r in rules:
        meds_a = [m for m in medications if m["name"] == r["med_a"]]
        meds_b = [m for m in medications if m["name"] == r["med_b"]]

        for ma in meds_a:
            for mb in meds_b:
                for ta in ma["times"]:
                    for tb in mb["times"]:
                        diff = abs(
                            (parser.isoparse(ta) - parser.isoparse(tb)).total_seconds()
                        ) / 60
                        if diff < r["min_time_diff_minutes"]:
                            conflicts.append({
                                "rule_id": r["id"],
                                "med_a": ma["name"],
                                "med_b": mb["name"],
                                "time_a": ta,
                                "time_b": tb
                            })
    return conflicts

def generate_new_time(old_time):
    return (parser.isoparse(old_time) + timedelta(minutes=120)).isoformat()

# ==================================================
# DATEN LADEN
# ==================================================

data = load_data()
medications = get_medications_for_user(data, USER_ID)
rules = data["rules"]

# ==================================================
# SIDEBAR - MEDIKAMENT HINZUFUEGEN
# ==================================================

st.sidebar.header("Medikament hinzufuegen")

with st.sidebar.form("add_med_form", clear_on_submit=True):
    name = st.text_input("Name")
    dose = st.text_input("Dosis (optional)")
    time = st.text_input(
        "Einnahmezeit (ISO-Format)",
        placeholder="2025-12-11T08:00:00"
    )

    submitted = st.form_submit_button("Hinzufuegen")

    if submitted:
        if not name or not time:
            st.sidebar.error("Name und Einnahmezeit sind Pflichtfelder.")
        else:
            try:
                parser.isoparse(time)
                data["medications"].append({
                    "id": str(uuid.uuid4()),
                    "user_id": USER_ID,
                    "name": name,
                    "dose": dose,
                    "times": [time]
                })
                save_data(data)
                st.experimental_rerun()
            except Exception:
                st.sidebar.error("Ungueltiges Zeitformat.")

# ==================================================
# HAUPTBEREICH - EINNAHMEPLAN
# ==================================================

st.markdown("## Einnahmeplan")

if not medications:
    st.info("Noch keine Medikamente eingetragen.")
else:
    for m in medications:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 3, 1])

            with col1:
                st.markdown(f"**{m['name']}**")
                st.write(f"Dosis: {m.get('dose','-')}")

            with col2:
                st.write("Einnahmezeiten:")
                for t in m["times"]:
                    st.code(t, language="text")

            with col3:
                if st.button("Loeschen", key=f"del_{m['id']}"):
                    data["medications"] = [
                        med for med in data["medications"]
                        if med["id"] != m["id"]
                    ]
                    save_data(data)
                    st.experimental_rerun()

# ==================================================
# INTERAKTIONEN
# ==================================================

st.markdown("## Interaktionen")

if st.button("Interaktionen pruefen"):
    st.session_state["conflicts"] = check_conflicts(medications, rules)

conflicts = st.session_state.get("conflicts")

if conflicts is not None:
    if not conflicts:
        st.success("Keine Konflikte gefunden.")
    else:
        st.error(f"{len(conflicts)} Konflikt(e) erkannt")

        for idx, c in enumerate(conflicts):
            with st.container(border=True):
                st.write(
                    f"{c['med_a']} und {c['med_b']} "
                    f"({c['time_a']} / {c['time_b']})"
                )

                if st.button("Vorschlag anwenden", key=f"apply_{idx}"):
                    new_time = generate_new_time(c["time_b"])

                    for m in data["medications"]:
                        if m["name"] == c["med_b"]:
                            m["times"] = [new_time]

                    data["changes_log"].append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "conflict": c,
                        "new_time": new_time
                    })

                    save_data(data)
                    st.experimental_rerun()

# ==================================================
# FOOTER
# ==================================================

st.caption(
    "MediMini ist ein Demonstrationsprojekt im Rahmen einer "
    "Software-Engineering-Lehrveranstaltung. "
    "Keine medizinische Beratung."
)


