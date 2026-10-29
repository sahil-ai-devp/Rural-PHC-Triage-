# Generated with Claude, reviewed and modified by the team
import sqlite3, datetime
import streamlit as st, pandas as pd

db = sqlite3.connect("triage.db", check_same_thread=False)
db.execute("""CREATE TABLE IF NOT EXISTS patients(id INTEGER PRIMARY KEY,
 name TEXT, age INT, symptoms TEXT, sbp INT, spo2 INT, temp REAL, pulse INT,
 priority TEXT, rank INT, reasons TEXT, created TEXT, synced INT DEFAULT 0)""")

SYMPTOMS = ["Chest pain", "Breathlessness", "Unconscious/seizure",
            "Heavy bleeding", "Fever", "Vomiting", "Headache", "Cough"]

def triage(sym, sbp, spo2, temp, pulse):
    em, ur = [], []
    if spo2 < 90: em.append(f"SpO2 {spo2}% critically low")
    elif spo2 < 94: ur.append(f"SpO2 {spo2}% low")
    if "Chest pain" in sym and spo2 < 94: em.append("RED FLAG: chest pain + low SpO2")
    if "Breathlessness" in sym and spo2 < 94: em.append("RED FLAG: breathlessness + low SpO2")
    if "Unconscious/seizure" in sym: em.append("Unconscious/seizure")
    if "Heavy bleeding" in sym: em.append("Heavy bleeding")
    if sbp >= 180 or sbp < 90: em.append(f"BP {sbp} dangerous")
    elif sbp >= 160: ur.append(f"BP {sbp} high")
    if temp >= 40: em.append(f"Temp {temp} very high")
    elif temp >= 38.5: ur.append(f"Temp {temp} high")
    if pulse > 130 or pulse < 40: em.append(f"Pulse {pulse} abnormal")
    elif pulse > 110: ur.append(f"Pulse {pulse} fast")
    if "Chest pain" in sym and not em: ur.append("Chest pain")
    if em: return "Emergency", 0, em
    if ur: return "Urgent", 1, ur
    return "Routine", 2, ["No danger signs found"]

st.title("Rural PHC Triage Assistant")
st.caption("Assists the nurse/ASHA worker. It never replaces the doctor.")
t1, t2 = st.tabs(["Register patient", "Live queue"])

with t1:
    name = st.text_input("Name"); age = st.number_input("Age", 0, 120, 30)
    sym = st.multiselect("Symptoms", SYMPTOMS)
    c = st.columns(4)
    sbp = c[0].number_input("BP (systolic)", 50, 250, 120)
    spo2 = c[1].number_input("SpO2 %", 50, 100, 98)
    temp = c[2].number_input("Temp °C", 34.0, 43.0, 37.0)
    pulse = c[3].number_input("Pulse", 20, 220, 80)
    if st.button("Assess") and name:
        p, r, why = triage(sym, sbp, spo2, temp, pulse)
        db.execute("INSERT INTO patients(name,age,symptoms,sbp,spo2,temp,pulse,priority,rank,reasons,created) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                   (name, age, ", ".join(sym), sbp, spo2, temp, pulse, p, r, "; ".join(why), datetime.datetime.now().isoformat(timespec="seconds")))
        db.commit()
        {"Emergency": st.error, "Urgent": st.warning, "Routine": st.success}[p](f"{p}: " + "; ".join(why))

with t2:
    df = pd.read_sql("SELECT name,age,priority,reasons,created,synced FROM patients ORDER BY rank, created", db)
    st.dataframe(df, use_container_width=True)
    if st.button("Sync to server (mock)"):
        db.execute("UPDATE patients SET synced=1"); db.commit(); st.success("Synced"); st.rerun()