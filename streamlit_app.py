import streamlit as st
from datetime import datetime, timedelta
from dateutil import parser
import json
import os
import uuid

# --------------------------------------------------
# Konfiguration
# --------------------------------------------------

st.set_page_config(page_title="MediMini", layout="wide")
st.title("MediMini - Smart Medication Assistant")

DATA_FILE = "data.json"
USER_ID = "u1"

# --------------------------------------------------
# Initiale Daten (Fallback)
# --------------------------------------------------

DEFAULT_DATA = {
    "users": [{"id": "u1", "email": "demo@example.com"}],
    "medications": [
        {
            "id": "m1",
            "user_id": "u1",
            "name": "MedA",
            "dose": "10mg",
            "times": ["2025-12-11T08:00:00"]
        },
        {
            "id": "m2",
            "user_id": "u1",
            "name": "MedB",
            "dose": "5mg",
            "times": ["2025-12-11T09:00:00"]
        }
    ],
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

# --------------------------------------------------
# Persistence Layer
# --------------------------------------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --------------------------------------------------
# Business Logic
# --------------------------------------------------

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
                            (parser.isoparse(ta) - parser.isoparse(tb))
                            .total_seconds()
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

def generate_suggestion(conflict):
    new_time = parser.isoparse(conflict["time_b"]) + timedelta(minutes=120)
    return new_time.isoformat()

# --------------------------------------------------
# UI
# --------------------------------------------------

data = load_data()
medications = get_medications_for_user(data, USER_ID)
rules = data["rules"]

# Sidebar: Medikament hinzufuegen
st.sidebar.header("Medikament hinzufuegen")

with st.sidebar.form("add_med"):
    name = st.text_input("Name")
    dose = st.text_input("Dosis")
    time = st.text_input("Einnahmezeit (ISO, z.B. 2025-12-11T08:00:00)")
    submit = st.form_submit_button("Hinzufuegen")

    if submit and name and time:
        data["medications"].append({
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": name,
            "dose": dose,
            "times": [time]
        })
        save_data(data)
        st.experimental_rerun()

# Anzeige Einnahmeplan
st.header("Einnahmeplan")

for m in medications:
    st.write(f"{m['name']} ({m.get('dose','')}) - {m['times']}")

# Konflikte pruefen
if st.button("Interaktionen pruefen"):
    conflicts = check_conflicts(medications, rules)
    st.session_state["conflicts"] = conflicts

conflicts = st.session_state.get("conflicts")

if conflicts:
    st.error(f"{len(conflicts)} Konflikt(e) erkannt")

    for c in conflicts:
        st.write(c)

        if st.button("Vorschlag anwenden", key=c["time_b"]):
            new_time = generate_suggestion(c)

            for m in data["medications"]:
                if m["name"] == c["med_b"]:
                    m["times"] = [new_time]

            data["changes_log"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "conflict": c,
                "new_time": new_time
            })

            save_data(data)
            st.success("Vorschlag angewendet")
            st.experimental_rerun()
elif conflicts == []:
    st.success("Keine Konflikte gefunden")

st.caption("Demo-App. Keine medizinische Beratung.")
