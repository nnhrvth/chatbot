import streamlit as st
from datetime import datetime, timedelta
from dateutil import parser
import json
import os
import uuid

# ==================================================
# KONFIGURATION
# ==================================================

st.set_page_config(page_title="MediMini", layout="wide")
st.title("MediMini - Smart Medication Assistant")

DATA_FILE = "data.json"
USER_ID = "u1"

# ==================================================
# DEFAULT DATEN
# ==================================================

DEFAULT_DATA = {
    "users": [
        {"id": "u1", "email": "demo@example.com"}
    ],
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
# UI - MEDIKAMENT HINZUFUEGEN
# ==================================================

data = load_data()
medications = get_medications_for_user(data, USER_ID)
rules = data["rules"]

st.sidebar.header("Medikament hinzufuegen")

with st.sidebar.form("add_med_form", clear_on_submit=True):
    name = st.text_input("Name des Medikaments")
    dose = st.text_input("Dosis (z.B. 10mg)")
    time = st.text_input(
        "Einnahmezeit (ISO-Format)",
        placeholder="2025-12-11T08:00:00"
    )

    submitted = st.form_submit_button("Hinzufuegen")

    if submitted:
        if not name or not time:
            st.error("Name und Einnahmezeit sind Pflichtfelder.")
        else:
            try:
                parser.isoparse(time)  # Validierung
                data["medications"].append({
                    "id": str(uuid.uuid4()),
                    "user_id": USER_ID,
                    "name": name,
                    "dose": dose,
                    "times": [time]
                })
                save_data(data)
                st.success("Medikament erfolgreich hinzugefuegt")
                st.experimental_rerun()
            except Exception:
                st.error("Ungueltiges Zeitformat.")

# ==================================================
# UI - EINNAHMEPLAN
# ==================================================

st.header("Einnahmeplan")

if not medications:
    st.info("Noch keine Medikamente hinterlegt.")
else:
    for m in medications:
        st.write(
            f"{m['name']} | Dosis: {m.get('dose','-')} | Zeiten: {m['times']}"
        )

# ==================================================
# UI - INTERAKTIONEN
# ==================================================

if st.button("Interaktionen pruefen"):
    st.session_state["conflicts"] = check_conflicts(medications, rules)

conflicts = st.session_state.get("conflicts")

if conflicts is not None:
    if not conflicts:
        st.success("Keine Konflikte gefunden.")
    else:
        st.error(f"{len(conflicts)} Konflikt(e) erkannt")

        for idx, c in enumerate(conflicts):
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
                st.success("Vorschlag angewendet")
                st.experimental_rerun()

# ==================================================
# FOOTER
# ==================================================

st.caption("MediMini ist ein Demonstrationsprojekt. Keine medizinische Beratung.")

