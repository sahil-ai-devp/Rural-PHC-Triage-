# Generated with Claude, reviewed and modified by the team
import sqlite3, datetime
import streamlit as st, pandas as pd

db = sqlite3.connect("triage.db", check_same_thread=False)
db.execute("""CREATE TABLE IF NOT EXISTS patients(id INTEGER PRIMARY KEY,
 name TEXT, age INT, symptoms TEXT, sbp INT, spo2 INT, temp REAL, pulse INT,
 priority TEXT, rank INT, reasons TEXT, created TEXT, synced INT DEFAULT 0)""")

# Order in every list: English, Hindi, Punjabi
T = {
 "title": ["Rural PHC Triage Assistant", "ग्रामीण PHC ट्राइएज सहायक", "ਪੇਂਡੂ PHC ਟ੍ਰਾਇਏਜ ਸਹਾਇਕ"],
 "caption": ["Assists the nurse/ASHA worker. It never replaces the doctor.",
             "यह नर्स/आशा कार्यकर्ता की सहायता करता है। यह डॉक्टर का स्थान नहीं लेता।",
             "ਇਹ ਨਰਸ/ਆਸ਼ਾ ਵਰਕਰ ਦੀ ਮਦਦ ਕਰਦਾ ਹੈ। ਇਹ ਡਾਕਟਰ ਦੀ ਥਾਂ ਨਹੀਂ ਲੈਂਦਾ।"],
 "tab1": ["Register patient", "मरीज़ पंजीकरण", "ਮਰੀਜ਼ ਰਜਿਸਟਰ"],
 "tab2": ["Live queue", "लाइव कतार", "ਲਾਈਵ ਕਤਾਰ"],
 "name": ["Name", "नाम", "ਨਾਂ"],
 "age": ["Age", "उम्र", "ਉਮਰ"],
 "sym": ["Symptoms", "लक्षण", "ਲੱਛਣ"],
 "bp": ["BP (systolic)", "BP (ऊपरी)", "BP (ਉਪਰਲਾ)"],
 "spo2": ["SpO2 %", "SpO2 %", "SpO2 %"],
 "temp": ["Temp °C", "तापमान °C", "ਤਾਪਮਾਨ °C"],
 "pulse": ["Pulse", "नाड़ी", "ਨਬਜ਼"],
 "assess": ["Assess", "जाँच करें", "ਜਾਂਚ ਕਰੋ"],
 "sync": ["Sync to server (mock)", "सर्वर से सिंक करें (डेमो)", "ਸਰਵਰ ਨਾਲ ਸਿੰਕ ਕਰੋ (ਡੈਮੋ)"],
 "synced": ["Synced", "सिंक हो गया", "ਸਿੰਕ ਹੋ ਗਿਆ"],
}
COLS = [["Name", "Age", "Priority", "Reasons", "Time", "Synced"],
        ["नाम", "उम्र", "प्राथमिकता", "कारण", "समय", "सिंक"],
        ["ਨਾਂ", "ਉਮਰ", "ਤਰਜੀਹ", "ਕਾਰਨ", "ਸਮਾਂ", "ਸਿੰਕ"]]
PRI = {"Emergency": ["Emergency", "आपातकाल", "ਐਮਰਜੈਂਸੀ"],
       "Urgent": ["Urgent", "जल्दी", "ਜ਼ਰੂਰੀ"],
       "Routine": ["Routine", "सामान्य", "ਆਮ"]}
SYM = {"Chest pain": ["Chest pain", "सीने में दर्द", "ਛਾਤੀ ਵਿੱਚ ਦਰਦ"],
       "Breathlessness": ["Breathlessness", "साँस फूलना", "ਸਾਹ ਚੜ੍ਹਨਾ"],
       "Unconscious/seizure": ["Unconscious/seizure", "बेहोशी/दौरा", "ਬੇਹੋਸ਼ੀ/ਦੌਰਾ"],
       "Heavy bleeding": ["Heavy bleeding", "भारी रक्तस्राव", "ਭਾਰੀ ਖੂਨ ਵਗਣਾ"],
       "Fever": ["Fever", "बुखार", "ਬੁਖ਼ਾਰ"],
       "Vomiting": ["Vomiting", "उल्टी", "ਉਲਟੀ"],
       "Headache": ["Headache", "सिरदर्द", "ਸਿਰ ਦਰਦ"],
       "Cough": ["Cough", "खाँसी", "ਖੰਘ"]}
R = {"spo2_crit": ["SpO2 {v}% critically low", "SpO2 {v}% खतरनाक रूप से कम", "SpO2 {v}% ਖ਼ਤਰਨਾਕ ਤੌਰ 'ਤੇ ਘੱਟ"],
     "spo2_low": ["SpO2 {v}% low", "SpO2 {v}% कम", "SpO2 {v}% ਘੱਟ"],
     "rf_chest": ["RED FLAG: chest pain + low SpO2", "खतरे का संकेत: सीने में दर्द + कम SpO2", "ਖ਼ਤਰੇ ਦਾ ਸੰਕੇਤ: ਛਾਤੀ ਵਿੱਚ ਦਰਦ + ਘੱਟ SpO2"],
     "rf_breath": ["RED FLAG: breathlessness + low SpO2", "खतरे का संकेत: साँस फूलना + कम SpO2", "ਖ਼ਤਰੇ ਦਾ ਸੰਕੇਤ: ਸਾਹ ਚੜ੍ਹਨਾ + ਘੱਟ SpO2"],
     "unconscious": ["Unconscious/seizure", "बेहोशी/दौरा", "ਬੇਹੋਸ਼ੀ/ਦੌਰਾ"],
     "bleeding": ["Heavy bleeding", "भारी रक्तस्राव", "ਭਾਰੀ ਖੂਨ ਵਗਣਾ"],
     "bp_danger": ["BP {v} dangerous", "BP {v} खतरनाक", "BP {v} ਖ਼ਤਰਨਾਕ"],
     "bp_high": ["BP {v} high", "BP {v} अधिक", "BP {v} ਵੱਧ"],
     "temp_vhigh": ["Temp {v} very high", "तापमान {v} बहुत अधिक", "ਤਾਪਮਾਨ {v} ਬਹੁਤ ਵੱਧ"],
     "temp_high": ["Temp {v} high", "तापमान {v} अधिक", "ਤਾਪਮਾਨ {v} ਵੱਧ"],
     "pulse_abn": ["Pulse {v} abnormal", "नाड़ी {v} असामान्य", "ਨਬਜ਼ {v} ਗ਼ੈਰ-ਸਧਾਰਨ"],
     "pulse_fast": ["Pulse {v} fast", "नाड़ी {v} तेज़", "ਨਬਜ਼ {v} ਤੇਜ਼"],
     "chest": ["Chest pain", "सीने में दर्द", "ਛਾਤੀ ਵਿੱਚ ਦਰਦ"],
     "none": ["No danger signs found", "कोई खतरे का संकेत नहीं", "ਕੋਈ ਖ਼ਤਰੇ ਦਾ ਸੰਕੇਤ ਨਹੀਂ"]}

def triage(sym, sbp, spo2, temp, pulse):
    em, ur = [], []
    if spo2 < 90: em.append(("spo2_crit", spo2))
    elif spo2 < 94: ur.append(("spo2_low", spo2))
    if "Chest pain" in sym and spo2 < 94: em.append(("rf_chest", ""))
    if "Breathlessness" in sym and spo2 < 94: em.append(("rf_breath", ""))
    if "Unconscious/seizure" in sym: em.append(("unconscious", ""))
    if "Heavy bleeding" in sym: em.append(("bleeding", ""))
    if sbp >= 180 or sbp < 90: em.append(("bp_danger", sbp))
    elif sbp >= 160: ur.append(("bp_high", sbp))
    if temp >= 40: em.append(("temp_vhigh", temp))
    elif temp >= 38.5: ur.append(("temp_high", temp))
    if pulse > 130 or pulse < 40: em.append(("pulse_abn", pulse))
    elif pulse > 110: ur.append(("pulse_fast", pulse))
    if "Chest pain" in sym and not em: ur.append(("chest", ""))
    if em: return "Emergency", 0, em
    if ur: return "Urgent", 1, ur
    return "Routine", 2, [("none", "")]

def show(stored, i):
    out = []
    for item in stored.split(";"):
        if "|" in item:
            k, v = item.split("|", 1)
            out.append(R[k][i].format(v=v) if k in R else item)
        else:
            out.append(item)  # old English rows
    return "; ".join(out)

lang = st.radio("Language / भाषा / ਭਾਸ਼ਾ", ["English", "हिन्दी", "ਪੰਜਾਬੀ"], horizontal=True)
i = ["English", "हिन्दी", "ਪੰਜਾਬੀ"].index(lang)
t = lambda k: T[k][i]

st.title(t("title"))
st.caption(t("caption"))
t1, t2 = st.tabs([t("tab1"), t("tab2")])

with t1:
    name = st.text_input(t("name")); age = st.number_input(t("age"), 0, 120, 30)
    sym = st.multiselect(t("sym"), list(SYM), format_func=lambda s: SYM[s][i])
    c = st.columns(4)
    sbp = c[0].number_input(t("bp"), 50, 250, 120)
    spo2 = c[1].number_input(t("spo2"), 50, 100, 98)
    temp = c[2].number_input(t("temp"), 34.0, 43.0, 37.0)
    pulse = c[3].number_input(t("pulse"), 20, 220, 80)
    if st.button(t("assess")) and name:
        p, r, why = triage(sym, sbp, spo2, temp, pulse)
        stored = ";".join(f"{k}|{v}" for k, v in why)
        db.execute("INSERT INTO patients(name,age,symptoms,sbp,spo2,temp,pulse,priority,rank,reasons,created) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                   (name, age, ", ".join(sym), sbp, spo2, temp, pulse, p, r, stored, datetime.datetime.now().isoformat(timespec="seconds")))
        db.commit()
        {"Emergency": st.error, "Urgent": st.warning, "Routine": st.success}[p](f"{PRI[p][i]}: " + show(stored, i))

with t2:
    df = pd.read_sql("SELECT name,age,priority,reasons,created,synced FROM patients ORDER BY rank, created", db)
    df["priority"] = df["priority"].map(lambda p: PRI[p][i])
    df["reasons"] = df["reasons"].map(lambda s: show(s, i))
    df.columns = COLS[i]
    st.dataframe(df, use_container_width=True)
    if st.button(t("sync")):
        db.execute("UPDATE patients SET synced=1"); db.commit(); st.success(t("synced")); st.rerun()