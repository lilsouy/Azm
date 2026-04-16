import streamlit as st
from engine import ask_azm

st.set_page_config(page_title="عزم", page_icon="✦", layout="centered")

st.markdown("""
<style>
* { direction: rtl; text-align: right; font-family: 'IBM Plex Sans Arabic', sans-serif; }
.stChatMessage { direction: rtl; }
.stChatMessage [data-testid="chatAvatarIcon-assistant"] { background-color: #534AB7; }
.emotion-tag {
    display: inline-block;
    border: 1px solid #AFA9EC;
    border-radius: 20px;
    padding: 4px 14px;
    margin: 4px;
    cursor: pointer;
    font-size: 14px;
}
</style>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


# ── حالة التطبيق ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "points" not in st.session_state:
    st.session_state.points = 0
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "tasks_generated" not in st.session_state:
    st.session_state.tasks_generated = False


# ── دالة توليد المهام الصغيرة ─────────────────────────────────
def generate_microtasks(task_text: str) -> list[str]:
    prompt = f"""قسّم هذه المهمة إلى 5 خطوات صغيرة جداً (كل خطوة أقل من 10 دقائق):
"{task_text}"

اكتب الخطوات فقط، كل خطوة في سطر واحد، بدون أرقام أو نقاط."""

    result = ask_azm(
        [{"role": "user", "content": prompt}],
        profile=st.session_state.profile
    )
    lines = [l.strip() for l in result.strip().splitlines() if l.strip()]
    return lines[:6]


# ── شاشة الاسم ────────────────────────────────────────────────
if "name" not in st.session_state.profile:
    st.markdown("<h1 style='color:#534AB7'>✦ مرحباً في عزم</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888'>أنا مدربك الذكي اللي يساعدك تبدأ</p>", unsafe_allow_html=True)
    name = st.text_input("ما اسمك؟", placeholder="اكتب اسمك هنا")
    if st.button("ابدأ ←", type="primary") and name.strip():
        st.session_state.profile["name"] = name.strip()
        st.rerun()


# ── شاشة الهدف الكبير ─────────────────────────────────────────
elif "big_goal" not in st.session_state.profile:
    st.markdown(f"<h2>أهلاً {st.session_state.profile['name']}! 👋</h2>", unsafe_allow_html=True)
    goal = st.text_input("إيش أكبر هدف تشتغل عليه هالفصل؟",
                         placeholder="مثلاً: أتخرج بتقدير ممتاز")
    if st.button("التالي ←", type="primary") and goal.strip():
        st.session_state.profile["big_goal"] = goal.strip()
        st.rerun()


# ── شاشة الهدف الأسبوعي ──────────────────────────────────────
elif "medium_goal" not in st.session_state.profile:
    st.markdown("<h2>هدفك الأسبوعي 🎯</h2>", unsafe_allow_html=True)
    goal = st.text_input("إيش أهم شيء تبغى تنجزه هالأسبوع؟",
                         placeholder="مهمة واضحة ومحددة")
    if st.button("التالي ←", type="primary") and goal.strip():
        st.session_state.profile["medium_goal"] = goal.strip()
        st.rerun()


# ── شاشة الحلم ───────────────────────────────────────────────
elif "dream" not in st.session_state.profile:
    st.markdown("<h2>حلمك ✦</h2>", unsafe_allow_html=True)
    dream = st.text_input("كيف تتخيل نفسك لما تحقق هدفك؟",
                          placeholder="صف الشعور أو المشهد")
    if st.button("هذا حلمي ✦", type="primary") and dream.strip():
        st.session_state.profile["dream"] = dream.strip()
        st.rerun()


# ── شاشة المحادثة الرئيسية ───────────────────────────────────
else:
    # الهيدر
    st.markdown(f"""
    <div style='background:#534AB7;padding:12px 18px;border-radius:12px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center'>
        <span style='color:white;font-size:18px;font-weight:600'>✦ عزم</span>
        <span style='color:rgba(255,255,255,0.75);font-size:13px'>{st.session_state.profile['name']}</span>
    </div>
    """, unsafe_allow_html=True)

    # شريط الحلم
    st.markdown(f"""
    <div style='background:#EEEDFE;padding:8px 14px;border-radius:8px;margin-bottom:12px;font-size:13px;color:#3C3489'>
        ✦ حلمك: {st.session_state.profile['dream']}
    </div>
    """, unsafe_allow_html=True)

    # النقاط
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown(f"""
        <div style='background:#FAEEDA;border:1px solid #FAC775;border-radius:20px;padding:5px 12px;font-size:12px;color:#854F0B;text-align:center'>
            ⚡ {st.session_state.points} نقطة
        </div>
        """, unsafe_allow_html=True)

    # رسالة ترحيب أول مرة
    if not st.session_state.messages:
        greeting = f"أهلاً {st.session_state.profile['name']}! 🌟\n\nأنا عزم، رفيقك في رحلة الإنجاز.\n\nهدفك الأسبوعي: \"{st.session_state.profile['medium_goal']}\"\n\nإيش المهمة اللي تحس إنك ما تقدر تبدأ فيها اليوم؟ وكيف تشعر تجاهها؟"
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    # عرض الرسائل
    for msg in st.session_state.messages:
        avatar = "✦" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    # اختيار المشاعر (تظهر لو ما اختار لحد الآن)
    if "pending_emotion" in st.session_state:
        st.markdown("**كيف تشعر تجاه هذه المهمة؟**")
        emotions = ["قلق", "خوف من الفشل", "كسل", "كمالية", "تشتت", "مرهق", "مو متحمس"]
        cols = st.columns(4)
        for i, emo in enumerate(emotions):
            with cols[i % 4]:
                if st.button(emo, key=f"emo_{emo}"):
                    task = st.session_state.pop("pending_emotion")
                    emotion_response = {
                        "قلق": "القلق يعني إنك تهتم، وهذا جميل. خل نحوله لطاقة.",
                        "خوف من الفشل": "الخوف من الفشل دليل إنك تهتم بالنتيجة. هذا يعني قادر تنجح.",
                        "كسل": "الكسل أحياناً رسالة إن المهمة تبدو كبيرة. نصغرها مع بعض.",
                        "كمالية": "الكمالية قوة وعبء. ابدأ ناقصاً وكمّل لاحقاً.",
                        "تشتت": "التشتت طبيعي. بس دقيقة واحدة تركيز كافية للبدء.",
                        "مرهق": "مرهق؟ إذن خطوة واحدة صغيرة كافية اليوم.",
                        "مو متحمس": "التحفيز يجي بعد البدء، مو قبله. جرّب دقيقتين بس.",
                    }.get(emo, "فاهم عليك. خل نبدأ بخطوة صغيرة.")

                    st.session_state.messages.append({"role": "user", "content": f"شعوري: {emo}"})
                    st.session_state.messages.append({"role": "assistant", "content": emotion_response})

                    # توليد المهام الصغيرة
                    with st.spinner("عزم يقسم المهمة..."):
                        steps = generate_microtasks(task)
                    st.session_state.tasks = [{"text": s, "done": False} for s in steps]
                    st.session_state.tasks_generated = True
                    st.session_state.points += 10
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "زين! قسّمت لك المهمة إلى خطوات صغيرة. ابدأ بأول خطوة وضغط على شرارة العزم! ⚡"
                    })
                    st.rerun()

    # قائمة المهام الصغيرة
    if st.session_state.tasks:
        st.markdown("---")
        st.markdown("**خطتك الصغيرة ✦**")
        for i, task in enumerate(st.session_state.tasks):
            checked = st.checkbox(
                task["text"],
                value=task["done"],
                key=f"task_{i}"
            )
            if checked and not task["done"]:
                st.session_state.tasks[i]["done"] = True
                st.session_state.points += 15
                st.rerun()

        done_count = sum(1 for t in st.session_state.tasks if t["done"])
        total = len(st.session_state.tasks)
        st.progress(done_count / total if total else 0,
                    text=f"{done_count}/{total} مكتملة")

        # شرارة العزم
        if "timer_active" not in st.session_state:
            st.session_state.timer_active = False

        if st.button("⚡ شرارة العزم — ابدأ 7 دقائق", type="primary"):
            st.session_state.timer_active = True
            st.session_state.points += 5
            first_undone = next((t["text"] for t in st.session_state.tasks if not t["done"]), "")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"الساعة بدت! ركّز 7 دقائق على: \"{first_undone}\"\nأغلق كل شيء ثاني وابدأ الآن. أنت قادر! 💪"
            })
            st.rerun()

    # صندوق الكتابة
    user_input = st.chat_input("أخبر عزم كيف تشعر وما هي مهمتك...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # كشف إذا في مهمة محددة
        task_keywords = ["مهمة", "مذاكر", "مشروع", "تقرير", "واجب", "اذاكر", "ابدأ", "كتاب", "بحث", "امتحان"]
        has_task = any(kw in user_input for kw in task_keywords)

        with st.spinner("عزم يفكر..."):
            response = ask_azm(
                st.session_state.messages,
                profile=st.session_state.profile
            )

        st.session_state.messages.append({"role": "assistant", "content": response})

        # لو في مهمة وما في tasks بعد، ابدأ اختيار المشاعر
        if has_task and not st.session_state.tasks:
            st.session_state.pending_emotion = user_input

        st.rerun()