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









from typing import List, Optional
from pydantic import BaseModel

class Medication(BaseModel):
    id: str
    user_id: str
    name: str
    dose: Optional[str]
    times: List[str]
    start_date: Optional[str]
    end_date: Optional[str]


import json
from pathlib import Path
from threading import Lock
from datetime import datetime

DATA_FILE = Path("data/sample_data.json")
RULES_FILE = Path("data/rules.json")
LOCK = Lock()

def load_data():
    with LOCK:
        return json.loads(DATA_FILE.read_text())

def save_data(data):
    with LOCK:
        DATA_FILE.write_text(json.dumps(data, indent=2))

def load_rules():
    return json.loads(RULES_FILE.read_text())

def get_medications_for_user(user_id):
    data = load_data()
    return [m for m in data["medications"] if m["user_id"] == user_id]

def update_medication_times(user_id, med_id, new_times):
    data = load_data()
    for m in data["medications"]:
        if m["id"] == med_id and m["user_id"] == user_id:
            m["times"] = new_times
            data.setdefault("changes_log", []).append({
                "timestamp": datetime.utcnow().isoformat(),
                "med_id": med_id,
                "new_times": new_times
            })
            save_data(data)
            return True
    return False



from dateutil import parser

def check_conflicts(medications, rules):
    conflicts = []
    for r in rules:
        a = [m for m in medications if m["name"] == r["med_a"]]
        b = [m for m in medications if m["name"] == r["med_b"]]
        for ma in a:
            for mb in b:
                for ta in ma["times"]:
                    for tb in mb["times"]:
                        diff = abs((parser.isoparse(ta) - parser.isoparse(tb)).total_seconds()) / 60
                        if diff < r["min_time_diff_minutes"]:
                            conflicts.append({
                                "rule_id": r["id"],
                                "med_a_id": ma["id"],
                                "med_b_id": mb["id"],
                                "med_a_time": ta,
                                "med_b_time": tb
                            })
    return conflicts



from datetime import timedelta
from dateutil import parser
from .rule_engine import check_conflicts

def generate_suggestions(medications, rules):
    suggestions = []
    conflicts = check_conflicts(medications, rules)

    for c in conflicts:
        new_time = parser.isoparse(c["med_b_time"]) + timedelta(hours=2)
        suggestions.append({
            "candidates": [{
                "med_id": c["med_b_id"],
                "old_time": c["med_b_time"],
                "new_time": new_time.isoformat()
            }]
        })
    return suggestions

def apply_suggestion(user_id, suggestion, medications, storage):
    cand = suggestion["candidates"][0]
    for m in medications:
        if m["id"] == cand["med_id"]:
            new_times = [
                cand["new_time"] if t == cand["old_time"] else t
                for t in m["times"]
            ]
            return storage.update_medication_times(user_id, m["id"], new_times), "OK"
    return False, "Fehler"



{
  "users": [{ "id": "u1", "email": "demo@example.com" }],
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
  "changes_log": []
}



[
  {
    "id": "R-001",
    "med_a": "MedA",
    "med_b": "MedB",
    "min_time_diff_minutes": 120
  }
]


streamlit
pydantic
python-dateutil
pytest


from src import storage, rule_engine

def test_conflict_detection():
    meds = storage.get_medications_for_user("u1")
    rules = storage.load_rules()
    conflicts = rule_engine.check_conflicts(meds, rules)
    assert len(conflicts) == 1









