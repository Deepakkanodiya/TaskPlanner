import streamlit as st
import json
import os
import time
from datetime import datetime, date
from google import genai

st.set_page_config(
    page_title="Deepak's Workspace & Energy Dashboard",
    layout="wide",
    page_icon="🎯"
)

# 1. API Key लोड करना
api_key = ""
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

# 2. स्टोरेज फाइल्स
DATA_FILE = "priority_data.json"
JOURNAL_FILE = "journal_vault.json"
AUDIT_FILE = "energy_audit.json"

def load_data():
    default_data = {"tasks": [], "horizon": [], "wins": [], "ai_schedule": ""}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_data
    return default_data

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def load_journal():
    if os.path.exists(JOURNAL_FILE):
        try:
            with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_journal(entries):
    with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def load_audit():
    if os.path.exists(AUDIT_FILE):
        try:
            with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_audit(audit_data):
    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, ensure_ascii=False, indent=2)

data = load_data()
journal_entries = load_journal()
audit_history = load_audit()

today_date = datetime.now()
day_name = today_date.strftime("%A")
formatted_date = today_date.strftime("%d %B %Y")
today_str = today_date.strftime("%Y-%m-%d")

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title("🎯 दीपक जी का वर्कस्पेस")
    st.caption("NDPS • Life Coaching • Personal Vault")
    st.markdown(f"📅 **{day_name}**, {formatted_date}")
    
    st.divider()
    is_ptm_or_early = st.checkbox("PTM / अर्ली डे? (7:15 AM)", value=(day_name in ["Wednesday", "Thursday"]), key="sb_ptm_chk")
    is_holiday = st.checkbox("स्कूल छुट्टी / रविवार?", value=(day_name == "Sunday"), key="sb_hol_chk")
    
    st.divider()
    if api_key:
        st.success("🟢 AI Connected")
    else:
        api_key = st.text_input("Gemini API Key:", type="password", key="sb_api_key")
        
    st.divider()
    st.subheader("💡 त्वरित नया काम")
    quick_t = st.text_input("टास्क का नाम:", key="sb_quick_t")
    quick_cat = st.selectbox("कहाँ जोड़ें?", ["आज के टास्क्स", "Horizon (बाद के लिए)"], key="sb_quick_cat")
    if st.button("टास्क शामिल करें", use_container_width=True, key="sb_add_quick_btn"):
        if quick_t.strip():
            new_item = {
                "id": int(time.time()),
                "text": quick_t.strip(),
                "created_at": datetime.now().strftime("%d-%b %H:%M")
            }
            if quick_cat == "आज के टास्क्स":
                data["tasks"].append(new_item)
            else:
                data["horizon"].append(new_item)
            save_data(data)
            st.success("टास्क जुड़ गया!")
            st.rerun()

    # --- 🛡️ बैकअप और रिस्टोर टूल ---
    st.divider()
    st.subheader("🛡️ डेटा सुरक्षा व बैकअप")
    
    # 1. पूरा डेटा एक साथ JSON में पैक करना
    all_vault_data = {
        "priority_data": data,
        "journal_vault": journal_entries,
        "energy_audit": audit_history,
        "backup_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    json_bytes = json.dumps(all_vault_data, ensure_ascii=False, indent=2).encode('utf-8')
    
    st.download_button(
        label="⬇️ पूरा डेटा बैकअप डाउनलोड करें",
        data=json_bytes,
        file_name=f"Deepak_Workspace_Backup_{today_str}.json",
        mime="application/json",
        use_container_width=True
    )
    
    with st.expander("♻️ पुराना बैकअप रिस्टोर करें"):
        uploaded_backup = st.file_uploader("बैकअप JSON चुनें:", type=["json"])
        if uploaded_backup is not None:
            if st.button("डेटा रिस्टोर करें (Confirm)", type="primary", use_container_width=True):
                try:
                    loaded = json.load(uploaded_backup)
                    if "priority_data" in loaded:
                        save_data(loaded["priority_data"])
                    if "journal_vault" in loaded:
                        save_journal(loaded["journal_vault"])
                    if "energy_audit" in loaded:
                        save_audit(loaded["energy_audit"])
                    st.success("डेटा सफलतापूर्वक रिस्टोर हो गया!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"फ़ाइल पढ़ने में त्रुटि: {str(e)}")

# ----------------- TOP HORIZONTAL TABS -----------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Brain Dump & Plan",
    "🕒 My Daily Routine",
    "📖 Journal & Vault",
    "⚡ Energy Audit (60s)",
    "🎯 Focus Mode",
    "🔭 Horizon & Wins"
])

# ----------------- TAB 1: BRAIN DUMP & PLAN -----------------
with tab1:
    col_dump, col_sched = st.columns([1, 1.2])
    
    with col_dump:
        st.subheader("🧠 Brain Dump")
        st.caption("अपने सभी विचार या काम एक साथ यहाँ लिखें:")
        dump_text = st.text_area(
            "काम यहाँ लिखें (एक लाइन में एक):",
            height=120,
            placeholder="जैसे:\n- IEP वर्कशीट तैयार करना\n- शाम 7:30 बजे काउंसलिंग सेशन\n- भैया से ज़रूरी चर्चा",
            key="tab1_dump_area"
        )
        
        c_b1, c_b2 = st.columns(2)
        with c_b1:
            if st.button("📥 आज के टास्क्स में जोड़ें", use_container_width=True, key="t1_add_today"):
                if dump_text.strip():
                    lines = [line.strip().lstrip("-•*1234567890. ") for line in dump_text.split("\n") if line.strip()]
                    for l in lines:
                        data["tasks"].append({
                            "id": int(time.time() * 1000) + len(data["tasks"]),
                            "text": l,
                            "created_at": datetime.now().strftime("%d-%b %H:%M")
                        })
                    save_data(data)
                    st.success(f"{len(lines)} काम जुड़ गए!")
                    st.rerun()
        with c_b2:
            if st.button("🔭 सीधे Horizon में डालें", use_container_width=True, key="t1_add_hor"):
                if dump_text.strip():
                    lines = [line.strip().lstrip("-•*1234567890. ") for line in dump_text.split("\n") if line.strip()]
                    for l in lines:
                        data["horizon"].append({
                            "id": int(time.time() * 1000) + len(data["horizon"]),
                            "text": l,
                            "created_at": datetime.now().strftime("%d-%b %H:%M")
                        })
                    save_data(data)
                    st.success(f"{len(lines)} काम Horizon में सुरक्षित!")
                    st.rerun()

        st.divider()
        st.subheader(f"📋 आज के कुल टास्क्स ({len(data['tasks'])})")
        if not data["tasks"]:
            st.info("आज के लिए कोई टास्क नहीं है। ऊपर बॉक्स से जोड़ें।")
        else:
            for idx, item in enumerate(data["tasks"]):
                c1, c2, c3 = st.columns([0.7, 0.15, 0.15])
                with c1:
                    st.markdown(f"**{idx + 1}.** {item['text']}")
                with c2:
                    if st.button("✅", key=f"t1_done_{item['id']}", help="Mark Done"):
                        data["wins"].append({
                            "text": item["text"],
                            "completed_at": datetime.now().strftime("%d-%b %H:%M")
                        })
                        data["tasks"].pop(idx)
                        save_data(data)
                        st.rerun()
                with c3:
                    if st.button("🔭", key=f"t1_later_{item['id']}", help="Move to Horizon"):
                        data["horizon"].append(item)
                        data["tasks"].pop(idx)
                        save_data(data)
                        st.rerun()

    with col_sched:
        st.subheader(f"⚡ AI Time-Blocked Schedule ({day_name})")
        if st.button("✨ आज का कस्टमाइज़्ड शेड्यूल बनाएँ", type="primary", use_container_width=True, key="t1_make_plan_btn"):
            if not api_key:
                st.error("API Key नहीं मिली!")
            elif not data["tasks"]:
                st.warning("कम से कम 1-2 टास्क जोड़ें।")
            else:
                with st.spinner("AI टाइम-ब्लॉक्स तैयार कर रहा है..."):
                    tasks_str = "\n".join([f"- {t['text']}" for t in data["tasks"]])
                    status_txt = "Holiday" if is_holiday else ("PTM Early (7:15 AM)" if is_ptm_or_early else "Normal (School 9:15 to 3:00)")
                    
                    prompt_lines = [
                        "तुम दीपक जी के पर्सनल AI एग्जीक्यूटिव शेड्यूलर हो।",
                        "दीपक जी का शेड्यूल: Special Educator at NDPS, Life Coach & Counsellor (Evening office).",
                        f"आज: {day_name}, {formatted_date}",
                        f"स्थिति: {status_txt}",
                        "नियम: स्कूल वापसी 4:30 PM, 5:00 PM भोजन (Strict Protected), 6:00 PM - 10:00 PM काउंसलिंग ऑफिस डीप वर्क।",
                        "टास्क्स:",
                        tasks_str,
                        "कृपया हिंदी/हिंग्लिश में एक सटीक, ऊर्जावान टाइम-ब्लॉक्ड शेड्यूल बनाओ।"
                    ]
                    prompt = "\n".join(prompt_lines)
                    
                    try:
                        client = genai.Client(api_key=api_key.strip())
                        res = client.models.generate_content(
                            model="gemini-3.8-flash",
                            contents=prompt,
                        )
                        data["ai_schedule"] = res.text
                        save_data(data)
                        st.rerun()
                    except Exception as e:
                        st.error(f"एरर आया: {str(e)}")

        if data.get("ai_schedule"):
            st.markdown(data["ai_schedule"])
            if st.button("🔄 शेड्यूल रीसेट करें", key="t1_reset_plan_btn"):
                data["ai_schedule"] = ""
                save_data(data)
                st.rerun()

# ----------------- TAB 2: DAILY ROUTINE -----------------
with tab2:
    st.subheader("🕒 आपकी मास्टर दिनचर्या (Deepak's Master Schedule)")
    st.info("यह टाइम-टेबल आपके पूरे दिन के आधारभूत नियम तय करता है और AI इसी के आधार पर टास्क शेड्यूल करता है।")
    
    routine_data = [
        {"समय (Time Slot)": "06:30 AM (बुध: 05:00 AM)", "गतिविधि / फोकस": "🌅 वेकअप & मॉर्निंग रूटीन", "विवरण": "फ्रेश होना, मॉर्निंग प्रेप"},
        {"समय (Time Slot)": "08:00 AM / 08:30 AM", "गतिविधि / फोकस": "🚌 बस बोर्डिंग", "विवरण": "Scheme 54 (8:00 AM) या LIG (8:30 AM)"},
        {"समय (Time Slot)": "09:15 AM - 03:00 PM (बुध/गुरु/PTM: 7:15)", "गतिविधि / फोकस": "🏫 NDPS School", "विवरण": "Special Education, सेशंस, कक्षाएं"},
        {"समय (Time Slot)": "03:15 PM - 04:30 PM", "गतिविधि / फोकस": "🚍 रिटर्न बस", "विवरण": "घर या भैया के घर वापसी"},
        {"समय (Time Slot)": "05:00 PM", "गतिविधि / फोकस": "🥗 डिनर (Dinner Time)", "विवरण": "पौष्टिक भोजन, विश्राम (Strictly Protected)"},
        {"समय (Time Slot)": "06:00 PM - 10:00 PM", "गतिविधि / फोकस": "💼 Counselling Office", "विवरण": "लाइफ कोचिंग, थेरेपी सेशंस, मेंटल वर्क, क्लाइंट्स"},
        {"समय (Time Slot)": "10:00 PM Onwards", "गतिविधि / फोकस": "🌙 फैमिली & स्वाध्याय", "विवरण": "रिलैक्स, परिवार के साथ समय, शांतिपूर्ण नींद"}
    ]
    st.table(routine_data)

# ----------------- TAB 3: JOURNAL & VAULT -----------------
with tab3:
    st.subheader("📖 Personal Journal & Secure Vault")
    st.caption("भावनात्मक अभिव्यक्ति, सोमैटिक ट्रैकिंग और साक्ष्य-आधारित वस्तुनिष्ठ लॉगिंग।")
    
    col_j_form, col_j_view = st.columns([1, 1.1])
    
    with col_j_form:
        st.markdown("#### ✍️ नई प्रविष्टि दर्ज करें")
        
        c_dt1, c_dt2 = st.columns(2)
        with c_dt1:
            e_date = st.date_input("तारीख:", value=date.today(), key="j_dt_picker")
        with c_dt2:
            e_time_str = st.text_input("समय:", value=datetime.now().strftime("%H:%M"), key="j_tm_str")
        
        j_cat = st.selectbox(
            "श्रेणी (Category):",
            [
                "🌱 Mindset & Catharsis (कृतज्ञता व भाव-निकासी)",
                "⚖️ Factual Evidence Log (वस्तुनिष्ठ साक्ष्य)",
                "🖋️ Creative Studio (#poetry, #स्वर_साधना)",
                "⚡ Spark & Vision (आइडिया व ब्लूप्रिंट)"
            ],
            key="j_cat_picker"
        )
        
        j_tit = st.text_input("शीर्षक (Title):", placeholder="संक्षिप्त शीर्षक...", key="j_tit_in")
        
        ev_trig = ""
        ev_quo = ""
        ev_ch_pres = False
        ev_ch_not = ""
        ev_wit = ""
        cr_tag = ""
        sp_stat = "Idea"
        is_vlt = False
        
        if "Evidence" in j_cat:
            st.warning("⚠️ वस्तुनिष्ठ साक्ष्य: केवल प्रत्यक्ष शब्द (In Quotes) व शारीरिक क्रियाएं दर्ज करें।")
            ev_trig = st.text_area("संदर्भ / ट्रिगर (Context):", height=60, placeholder="स्थान, परिस्थिति या पहले की स्थिति...", key="ev_trig_in")
            ev_quo = st.text_area("प्रत्यक्ष शब्द व क्रियाएं (Quotes/Actions):", height=70, placeholder="जो शब्द हूबहू बोले गए...", key="ev_quo_in")
            
            c_ch1, c_ch2 = st.columns([0.45, 0.55])
            with c_ch1:
                ev_ch_pres = st.checkbox("क्या बच्चे उपस्थित थे?", key="ev_ch_p_chk")
            with c_ch2:
                if ev_ch_pres:
                    ev_ch_not = st.text_input("बच्चों की स्थिति/नोट्स:", placeholder="कहाँ थे? क्या देखा/सुना?", key="ev_ch_not_in")
            ev_wit = st.text_input("गवाह (Witnesses):", placeholder="मौजूद व्यक्तियों के नाम...", key="ev_wit_in")
            
        elif "Creative" in j_cat:
            cr_tag = st.text_input("टैग्स:", value="#poetry #swar_sadhana", key="cr_tag_in")
        elif "Spark" in j_cat:
            sp_stat = st.selectbox("प्रगति स्थिति:", ["Idea", "In-Progress", "Done"], key="sp_stat_in")
        elif "Mindset" in j_cat:
            is_vlt = st.checkbox("🔒 Auto-Hide / Vault Entry (पुनः पढ़ने व ओवरथिंकिंग से बचाने हेतु लॉक करें)", key="ms_vlt_chk")
            
        j_txt = st.text_area(
            "मुख्य विवरण / नोट्स (Main Content):",
            height=130,
            placeholder="अपनी बात, विचार, डायरी प्रविष्टि या विवरण यहाँ लिखें...",
            key="j_txt_in"
        )
        
        with st.expander("🩺 सोमैटिक लॉग (वैकल्पिक - BP & Sleep)"):
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                bp_v = st.text_input("Blood Pressure (BP):", placeholder="उदा. 120/80", key="bp_v_in")
            with c_s2:
                sleep_v = st.slider("Sleep Quality (1-10):", 1, 10, 7, key="sleep_v_in")
        
        if st.button("💾 जर्नल में सुरक्षित करें (Save Entry)", type="primary", use_container_width=True, key="save_j_btn"):
            if j_txt.strip() or ev_quo.strip() or j_tit.strip():
                new_e = {
                    "id": int(time.time() * 1000),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "entry_time": f"{e_date} {e_time_str}",
                    "category": j_cat,
                    "title": j_tit.strip() if j_tit.strip() else "बिना शीर्षक",
                    "body": j_txt.strip(),
                    "is_vaulted": is_vlt,
                    "trigger": ev_trig.strip(),
                    "quotes": ev_quo.strip(),
                    "children_present": ev_ch_pres,
                    "children_notes": ev_ch_not.strip(),
                    "witnesses": ev_wit.strip(),
                    "tags": cr_tag.strip(),
                    "status": sp_stat,
                    "bp": bp_v.strip() if bp_v else "",
                    "sleep": sleep_v
                }
                journal_entries.insert(0, new_e)
                save_journal(journal_entries)
                st.success("✅ प्रविष्टि सुरक्षित रूप से दर्ज कर ली गई!")
                st.rerun()
            else:
                st.error("कृपया शीर्षक या विवरण में कुछ लिखें।")

    with col_j_view:
        st.markdown("#### 🗄️ दर्ज रिकॉर्ड्स (Vault Ledger)")
        f_choice = st.radio(
            "फ़िल्टर:", 
            ["सभी (All)", "Evidence Log", "Mindset", "Creative", "Spark"],
            horizontal=True,
            key="j_view_filt"
        )
        
        filtered = journal_entries
        if f_choice == "Evidence Log":
            filtered = [e for e in journal_entries if "Evidence" in e.get("category", "")]
        elif f_choice == "Mindset":
            filtered = [e for e in journal_entries if "Mindset" in e.get("category", "")]
        elif f_choice == "Creative":
            filtered = [e for e in journal_entries if "Creative" in e.get("category", "")]
        elif f_choice == "Spark":
            filtered = [e for e in journal_entries if "Spark" in e.get("category", "")]

        if not filtered:
            st.info("इस श्रेणी में अभी कोई प्रविष्टि नहीं है।")
        else:
            for idx, e in enumerate(filtered):
                is_ev = "Evidence" in e.get("category", "")
                header_title = f"{e.get('category', 'Log')} • {e.get('title')}"
                
                with st.expander(header_title, expanded=(idx == 0)):
                    st.caption(f"📅 दिनांक व समय: **{e.get('entry_time', e.get('created_at'))}** | सिस्टम लॉग: `{e.get('created_at')}`")
                    
                    if e.get("is_vaulted"):
                        st.info("🔒 यह प्रविष्टि वॉल्टेड (छिपी हुई) है।")
                        if st.checkbox("नोट देखें (Reveal Note)", key=f"rev_{e['id']}"):
                            st.write(e.get("body"))
                    else:
                        if e.get("body"):
                            st.markdown(e.get("body"))

                    if is_ev:
                        st.markdown("---")
                        if e.get("trigger"):
                            st.markdown(f"**ट्रिगर / संदर्भ:** {e.get('trigger')}")
                        if e.get("quotes"):
                            st.markdown("**प्रत्यक्ष वाक्य व क्रियाएं:**")
                            st.code(e.get("quotes"), language="text")
                        
                        child_status = "🔴 हाँ" if e.get("children_present") else "🟢 नहीं"
                        notes = e.get("children_notes")
                        if notes:
                            st.markdown(f"**बच्चे मौजूद थे:** {child_status} ({notes})")
                        else:
                            st.markdown(f"**बच्चे मौजूद थे:** {child_status}")
                            
                        if e.get("witnesses"):
                            st.markdown(f"**गवाह:** {e.get('witnesses')}")

                    meta_items = []
                    if e.get("tags"):
                        meta_items.append(f"🏷️ `{e.get('tags')}`")
                    if e.get("status"):
                        meta_items.append(f"📌 स्थिति: **{e.get('status')}**")
                    if e.get("bp"):
                        meta_items.append(f"❤️ BP: `{e.get('bp')}`")
                    if e.get("sleep"):
                        meta_items.append(f"🌙 Sleep: `{e.get('sleep')}/10`")
                    
                    if meta_items:
                        st.caption(" | ".join(meta_items))

# ----------------- TAB 4: ENERGY AUDIT (12 DIMENSIONS) -----------------
with tab4:
    st.subheader("⚡ 60-Second Daily Energy Deposit Ledger")
    st.caption("संज्ञानात्मक थकान (Cognitive Burnout) और अति-विचार को रोकने हेतु दैनिक ऊर्जा ऑडिट।")
    
    today_audit = audit_history.get(today_str, {
        "active_deposits": [],
        "energy_score": 4,
        "bp_systolic": 120,
        "bp_diastolic": 80,
        "creator_win": ""
    })
    saved_checked = set(today_audit.get("active_deposits", []))
    
    DIMENSIONS = {
        "1. Relationship": [
            ("rel_wife", "Wife Boundary (स्पष्ट सीमा व सम्मान)"),
            ("rel_parents", "Parents (माता-पिता से संवाद/सेवा)"),
            ("rel_circle", "Close Circle (मित्र व शुभचिंतक)"),
            ("rel_others", "Others (अन्य सामाजिक दायित्व)")
        ],
        "2. Body": [
            ("body_exercise", "Exercise / Walk (नियमित पैदल चलना)"),
            ("body_nutrition", "Clean Nutrition (पौष्टिक व सात्विक आहार)"),
            ("body_healing", "Healing (विश्राम व रिकवरी)"),
            ("body_medicine", "Natural Medicine (प्राकृतिक चिकित्सा/नेचुरोपैथी)")
        ],
        "3. Professional": [
            ("prof_job", "Job / School (NDPS Special Education)"),
            ("prof_digital", "Digital Assets Creation (सामग्री/प्लेटफ़ॉर्म)"),
            ("prof_altbiz", "Alternate Business (काउंसलिंग व कोचिंग)")
        ],
        "4. Mind": [
            ("mind_meditation", "Meditation (ध्यान व एकाग्रता)"),
            ("mind_healing", "Emotional Healing (भावनात्मक संतुलन)"),
            ("mind_journal", "Micro-Journaling (लघु-डायरी)"),
            ("mind_catharsis", "Catharsis (भाव-निकासी)"),
            ("mind_sleep", "Sound Sleep (गहरी व शांत नींद)")
        ],
        "5. Social": [
            ("soc_kids", "Teaching Kids (बच्चों को मार्गदर्शन)"),
            ("soc_webinar", "Free Webinar / Masterclass"),
            ("soc_meeting", "Energizing Meetings (सकारात्मक संवाद)")
        ],
        "6. Team": [
            ("team_interns", "Interns Guidance (इंटर्न्स/सहकर्मी)"),
            ("team_referrals", "Referrals Network"),
            ("team_mission", "Mission-mode Work (संकल्प आधारित कार्य)")
        ],
        "7. Spiritual": [
            ("spir_anasakti", "☸️ अनासक्ति भाव (Non-Attachment Toggle)"),
            ("spir_dhyan", "Dhyan (गहन आत्म-चिंतन)"),
            ("spir_satsang", "Satsang (सत्संग व स्वाध्याय)")
        ],
        "8. Learning": [
            ("learn_courses", "Courses (अध्ययन व पाठ्य सामग्री)"),
            ("learn_doing", "Learn by Doing (करके सीखना)")
        ],
        "9. Conserving": [
            ("cons_boundary", "Energy Boundary Kept (ऊर्जा की सुरक्षा)"),
            ("cons_vibes", "Good Vibration Transformation (सकारात्मक तरंगें)")
        ],
        "10. Money": [
            ("mon_invest", "Smart Investment (सजग निवेश)"),
            ("mon_spend", "Conscious Spending (जागरूक व्यय)")
        ],
        "11. Legacy": [
            ("leg_creator", "Creator Win (कंटेंट बनाया, रील्स का उपभोग नहीं किया)"),
            ("leg_longterm", "Long-term Blueprinting (दीर्घकालिक निर्माण)")
        ],
        "12. Entertainment": [
            ("ent_music", "Bhajan / Music Practice (स्वर साधना व संगीत)"),
            ("ent_ground", "Outdoor Ground Activity (घास पर चलना/प्रकृति)"),
            ("ent_play", "Play with Kids (बच्चों के साथ खेल)")
        ]
    }
    
    CLUSTERS = [
        {"name": "🌿 Vitality & Mind", "dims": ["2. Body", "4. Mind", "9. Conserving"]},
        {"name": "💼 Enterprise & Craft", "dims": ["3. Professional", "6. Team", "10. Money", "8. Learning"]},
        {"name": "🤝 Connection & Roots", "dims": ["1. Relationship", "5. Social", "11. Legacy", "12. Entertainment"]},
        {"name": "🕉️ Spiritual Anchor", "dims": ["7. Spiritual"]}
    ]
    
    active_cnt = 0
    for d_title, items in DIMENSIONS.items():
        if any(item_key in saved_checked for item_key, _ in items):
            active_cnt += 1
            
    st.markdown(f"### 🎯 आज का एनर्जी स्कोर: **{active_cnt} / 12 Dimensions Invested**")
    st.progress(active_cnt / 12)
    st.divider()

    c_grid_1, c_grid_2 = st.columns(2)
    new_checked_keys = []
    
    for i, cluster in enumerate(CLUSTERS):
        target_col = c_grid_1 if i % 2 == 0 else c_grid_2
        with target_col:
            cluster_box = st.container(border=True)
            with cluster_box:
                st.markdown(f"#### {cluster['name']}")
                for d_title in cluster["dims"]:
                    st.markdown(f"**{d_title}**")
                    for k, lbl in DIMENSIONS[d_title]:
                        is_checked = st.checkbox(lbl, value=(k in saved_checked), key=f"t4_aud_{k}")
                        if is_checked:
                            new_checked_keys.append(k)
                    st.write("")

    st.markdown("---")
    st.markdown("#### 🩺 सोमैटिक व क्रिएटर मेट्रिक्स")
    m_c1, m_c2, m_c3, m_c4 = st.columns([1, 1, 1, 2])
    with m_c1:
        ea_score = st.slider("समग्र ऊर्जा स्तर (1-5):", 1, 5, value=int(today_audit.get("energy_score", 4)), key="t4_ea_score")
    with m_c2:
        ea_sys = st.number_input("BP Systolic (ऊपर):", min_value=80, max_value=200, value=int(today_audit.get("bp_systolic", 120)), key="t4_ea_sys")
    with m_c3:
        ea_dia = st.number_input("BP Diastolic (नीचे):", min_value=50, max_value=130, value=int(today_audit.get("bp_diastolic", 80)), key="t4_ea_dia")
    with m_c4:
        ea_win = st.text_input("🎨 क्रिएटर जीत (Creator Win):", value=str(today_audit.get("creator_win", "")), key="t4_ea_win")

    if st.button("💾 आज का एनर्जी ऑडिट सुरक्षित करें", type="primary", use_container_width=True, key="t4_save_audit_btn"):
        audit_history[today_str] = {
            "date": today_str,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "active_deposits": new_checked_keys,
            "energy_score": ea_score,
            "bp_systolic": ea_sys,
            "bp_diastolic": ea_dia,
            "creator_win": ea_win.strip()
        }
        save_audit(audit_history)
        st.success("✅ एनर्जी ऑडिट सफलतापूर्वक दर्ज हो गया!")
        st.rerun()

# ----------------- TAB 5: FOCUS MODE -----------------
with tab5:
    st.subheader("🎯 Focus Mode: Single Task Flow")
    if not data["tasks"]:
        st.info("फ़ोकस करने के लिए अभी कोई टास्क नहीं है। पहले टैब ('Brain Dump & Plan') से टास्क जोड़ें।")
    else:
        current_focus = data["tasks"][0]
        focus_box = st.container(border=True)
        with focus_box:
            st.caption("अभी का एकमात्र लक्ष्य (#1 Priority):")
            st.header(f"🔥 {current_focus['text']}")
            st.caption(f"दर्ज समय: {current_focus['created_at']}")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if st.button("🎉 यह काम पूरा हुआ! (Done)", type="primary", use_container_width=True, key="t5_focus_done"):
                data["wins"].append({
                    "text": current_focus["text"],
                    "completed_at": datetime.now().strftime("%d-%b %H:%M")
                })
                data["tasks"].pop(0)
                save_data(data)
                st.balloons()
                st.rerun()
        with col_f2:
            if st.button("⏭️ अगले काम पर जाएँ (Skip)", use_container_width=True, key="t5_focus_skip"):
                item = data["tasks"].pop(0)
                data["tasks"].append(item)
                save_data(data)
                st.rerun()

# ----------------- TAB 6: HORIZON & WINS -----------------
with tab6:
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        st.subheader("🔭 The Horizon (Pending & Deferred Tasks)")
        st.caption("जो काम आज नहीं करने, उन्हें यहाँ सुरक्षित रखें:")
        if not data["horizon"]:
            st.info("The Horizon खाली है।")
        else:
            for idx, item in enumerate(data["horizon"]):
                c_a, c_b, c_c = st.columns([0.7, 0.15, 0.15])
                with c_a:
                    st.write(f"📌 {item['text']}")
                with c_b:
                    if st.button("⬆️", key=f"t6_up_{item['id']}", help="Move to Today"):
                        data["tasks"].append(item)
                        data["horizon"].pop(idx)
                        save_data(data)
                        st.rerun()
                with c_c:
                    if st.button("🗑️", key=f"t6_del_{item['id']}"):
                        data["horizon"].pop(idx)
                        save_data(data)
                        st.rerun()

    with col_h2:
        st.subheader("🏆 Daily Wins (पूरे किए गए कार्य)")
        st.caption("आपकी उपलब्धियों का रिकॉर्ड:")
        if not data["wins"]:
            st.info("अभी तक कोई काम पूरा नहीं हुआ है।")
        else:
            for w in reversed(data["wins"]):
                st.markdown(f"- ✅ **{w['text']}** *(पूरा हुआ: {w['completed_at']})*")
            
            if st.button("🧹 पुरानी Wins साफ़ करें", key="t6_clear_wins"):
                data["wins"] = []
                save_data(data)
                st.rerun()
