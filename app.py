import streamlit as st
import time
import base64
import streamlit.components.v1 as components
from engine import ask_azm, generate_steps_with_ai

st.set_page_config(page_title="عزم", page_icon="✨", layout="centered")

st.markdown("""
<style>
* {
    direction: rtl;
    text-align: right;
    font-family: 'IBM Plex Sans Arabic', sans-serif;
}
.stChatMessage {
    direction: rtl;
}
.stChatMessage [data-testid="chatAvatarIcon-assistant"] {
    background-color: #534AB7;
}
.timer-card {
    background: linear-gradient(135deg, #F6F3FF, #EEEDFE);
    border: 1px solid #D9D4FF;
    border-radius: 18px;
    padding: 14px;
    margin: 14px 0;
}
</style>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;700&display=swap" rel="stylesheet">
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
if "timer_active" not in st.session_state:
    st.session_state.timer_active = False
if "timer_end" not in st.session_state:
    st.session_state.timer_end = None
if "timer_duration" not in st.session_state:
    st.session_state.timer_duration = 420
if "played_finish_sound" not in st.session_state:
    st.session_state.played_finish_sound = False


# ── أدوات مساعدة ─────────────────────────────────────────────
def has_real_tasks():
    return bool(st.session_state.tasks) and any(
        isinstance(t, dict) and t.get("text", "").strip()
        for t in st.session_state.tasks
    )


def generate_microtasks(task_text: str) -> list[str]:
    return generate_steps_with_ai(
        task_text,
        profile=st.session_state.profile
    )


def get_level(points: int):
    if points < 50:
        return "مبتدئة", 0, 50
    elif points < 120:
        return "منطلقة", 50, 120
    elif points < 220:
        return "مثابرة", 120, 220
    elif points < 350:
        return "منجزة", 220, 350
    else:
        return "أسطورية", 350, 500


def render_points_and_level():
    level_name, min_points, max_points = get_level(st.session_state.points)

    progress = 0.0
    if max_points > min_points:
        progress = (st.session_state.points - min_points) / (max_points - min_points)
        progress = max(0.0, min(progress, 1.0))

    st.markdown(f"""
    <div style='background:#FFF7E8;border:1px solid #F6D28B;padding:12px 14px;border-radius:14px;margin-bottom:12px'>
        <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>
            <span style='font-weight:700;color:#7A4B00'>⚡ {st.session_state.points} نقطة</span>
            <span style='font-size:13px;color:#6B5E2E'>المستوى: {level_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress, text=f"تقدمك في مستوى {level_name}")


def render_circular_timer(total_seconds: int, remaining_seconds: int):
    progress = 0
    if total_seconds > 0:
        progress = (total_seconds - remaining_seconds) / total_seconds
        progress = max(0, min(progress, 1))

    mins = remaining_seconds // 60
    secs = remaining_seconds % 60
    dash_offset = 565.48 * (1 - progress)

    components.html(
        f"""
        <div style="display:flex;justify-content:center;margin:18px 0;">
          <div style="position:relative;width:220px;height:220px;">
            <svg width="220" height="220" viewBox="0 0 220 220">
              <circle cx="110" cy="110" r="90"
                      stroke="#E9E7FB" stroke-width="14" fill="none" />
              <circle cx="110" cy="110" r="90"
                      stroke="#534AB7" stroke-width="14" fill="none"
                      stroke-linecap="round"
                      stroke-dasharray="565.48"
                      stroke-dashoffset="{dash_offset}"
                      transform="rotate(-90 110 110)" />
            </svg>
            <div style="
                position:absolute;top:50%;left:50%;
                transform:translate(-50%,-50%);
                text-align:center;
                font-family:Arial,sans-serif;">
              <div style="font-size:18px;color:#534AB7;font-weight:700;">⚡ شرارة العزم</div>
              <div style="font-size:38px;font-weight:800;color:#222;margin-top:8px;">
                {mins:02d}:{secs:02d}
              </div>
              <div style="font-size:13px;color:#777;margin-top:8px;">ركزي على خطوة واحدة فقط</div>
            </div>
          </div>
        </div>
        """,
        height=250,
    )


def play_finish_sound():
    beep_base64 = (
        "UklGRlQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YTAAAAAAAP//AAD//wAA//8AAP//"
        "AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA"
    )
    st.audio(base64.b64decode(beep_base64), format="audio/wav", autoplay=True)


# ── شاشة الاسم ───────────────────────────────────────────────
if "name" not in st.session_state.profile:
    st.markdown("<h1 style='color:#534AB7'>✨ مرحباً في عزم</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888'>أنا مدربك الذكي اللي يساعدك تبدأ</p>", unsafe_allow_html=True)

    name = st.text_input("ما اسمك؟", placeholder="اكتب اسمك هنا")
    if st.button("ابدأ ←", type="primary") and name.strip():
        st.session_state.profile["name"] = name.strip()
        st.rerun()


# ── شاشة الهدف الكبير ────────────────────────────────────────
elif "big_goal" not in st.session_state.profile:
    st.markdown(f"<h2>أهلاً {st.session_state.profile['name']}! 👋</h2>", unsafe_allow_html=True)

    goal = st.text_input(
        "إيش أكبر هدف تشتغل عليه هالفصل؟",
        placeholder="مثلاً: أتخرج بتقدير ممتاز"
    )
    if st.button("التالي ←", type="primary") and goal.strip():
        st.session_state.profile["big_goal"] = goal.strip()
        st.rerun()


# ── شاشة الهدف الأسبوعي ─────────────────────────────────────
elif "medium_goal" not in st.session_state.profile:
    st.markdown("<h2>هدفك الأسبوعي 🎯</h2>", unsafe_allow_html=True)

    goal = st.text_input(
        "إيش أهم شيء تبغى تنجزه هالأسبوع؟",
        placeholder="مهمة واضحة ومحددة"
    )
    if st.button("التالي ←", type="primary") and goal.strip():
        st.session_state.profile["medium_goal"] = goal.strip()
        st.rerun()


# ── شاشة الحلم ──────────────────────────────────────────────
elif "dream" not in st.session_state.profile:
    st.markdown("<h2>حلمك ✨</h2>", unsafe_allow_html=True)

    dream = st.text_input(
        "كيف تتخيل نفسك لما تحقق هدفك؟",
        placeholder="صف الشعور أو المشهد"
    )
    if st.button("هذا حلمي ✨", type="primary") and dream.strip():
        st.session_state.profile["dream"] = dream.strip()
        st.rerun()


# ── الشاشة الرئيسية ──────────────────────────────────────────
else:
    st.markdown(f"""
    <div style='background:#534AB7;padding:12px 18px;border-radius:12px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center'>
        <span style='color:white;font-size:18px;font-weight:600'>✨ عزم</span>
        <span style='color:rgba(255,255,255,0.75);font-size:13px'>{st.session_state.profile['name']}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:#EEEDFE;padding:8px 14px;border-radius:8px;margin-bottom:12px;font-size:13px;color:#3C3489'>
        ✨ حلمك: {st.session_state.profile['dream']}
    </div>
    """, unsafe_allow_html=True)

    render_points_and_level()

    if not st.session_state.messages:
        greeting = f"""أهلاً {st.session_state.profile['name']}! 🌟

أنا عزم، رفيقك في رحلة الإنجاز.

هدفك الأسبوعي: "{st.session_state.profile['medium_goal']}"

وش المهمة اللي موقفك اليوم؟"""
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    # الشات فقط
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg["content"])
        else:
            with st.chat_message("user"):
                st.write(msg["content"])

    # اختيار الشعور
    if "pending_emotion" in st.session_state:
        st.markdown("### كيف تشعر تجاه هذه المهمة؟")
        emotions = ["قلق", "خوف من الفشل", "كسل", "كمالية", "تشتت", "مرهق", "مو متحمس"]
        cols = st.columns(4)

        for i, emo in enumerate(emotions):
            with cols[i % 4]:
                if st.button(emo, key=f"emo_{emo}"):
                    task = st.session_state.pop("pending_emotion")

                    emotion_response = {
                        "قلق": "واضح إنك مهتم بالمهمة، وخلنا نبسطها سوا.",
                        "خوف من الفشل": "مو لازم تنجزها كاملة الآن، يكفي تبدأ بداية بسيطة.",
                        "كسل": "يمكن مو كسل، يمكن المهمة طالعة أكبر من حجمها الحقيقي.",
                        "كمالية": "ما نحتاج نسخة مثالية، نحتاج بداية فقط.",
                        "تشتت": "خلنا نمسك أول خطوة فقط ونترك الباقي بعدين.",
                        "مرهق": "بناخذ أصغر خطوة ممكنة، شيء خفيف عليك.",
                        "مو متحمس": "مو لازم الحماس يسبق البداية، أحيانًا البداية هي اللي تجيب الحماس."
                    }.get(emo, "خلنا نبدأ بخطوة صغيرة.")

                    st.session_state.messages.append({"role": "user", "content": f"شعوري: {emo}"})
                    st.session_state.messages.append({"role": "assistant", "content": emotion_response})

                    with st.spinner("عزم يقسم المهمة..."):
                        steps = generate_microtasks(task)

                    st.session_state.tasks = [{"text": s, "done": False} for s in steps if s.strip()]
                    st.session_state.tasks_generated = True
                    st.session_state.points += 10

                    if st.session_state.tasks:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "جهزت لك خطوات تنفيذ واضحة ✨ تلقينها تحت، ابدئي بأول خطوة فقط."
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "ما قدرت أطلع خطوات واضحة من المهمة هذي، جرّبي تكتبينها بشكل أوضح شوي."
                        })

                    st.rerun()

    # خطوات التنفيذ فقط
    if has_real_tasks():
        st.markdown("---")
        st.markdown("## ✨ خطوات التنفيذ")
        st.caption("ركزي فقط على أول خطوة، ولا تشيلين هم الباقي.")

        for i, task in enumerate(st.session_state.tasks):
            checked = st.checkbox(
                task["text"],
                value=task["done"],
                key=f"task_{i}"
            )

            if checked and not task["done"]:
                st.session_state.tasks[i]["done"] = True
                st.session_state.points += 15

                done_count = sum(1 for t in st.session_state.tasks if t["done"])
                total = len(st.session_state.tasks)

                if done_count < total:
                    next_task = next((t["text"] for t in st.session_state.tasks if not t["done"]), "")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"أحسنت! خلصت خطوة وحصلت على 15 نقطة ✨\n\nالخطوة الجاية: {next_task}"
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"أبدعت! خلصت كل الخطوات 🎉\n\nاقتربت من هدفك. {st.session_state.profile.get('big_goal', '')} صار أقرب اليوم."
                    })

                st.rerun()

        done_count = sum(1 for t in st.session_state.tasks if t["done"])
        total = len(st.session_state.tasks)
        progress_value = done_count / total if total else 0
        st.progress(progress_value, text=f"{done_count}/{total} مكتملة")

        if done_count < total:
            if st.button("⚡ شرارة العزم — ابدأ 7 دقائق", type="primary"):
                st.session_state.timer_active = True
                st.session_state.timer_duration = 420
                st.session_state.timer_end = time.time() + 420
                st.session_state.played_finish_sound = False
                st.session_state.points += 5

                first_undone = next((t["text"] for t in st.session_state.tasks if not t["done"]), "")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"""اشتغلت شرارة العزم ⚡

ركزي 7 دقائق فقط على:
**{first_undone}**

اقفلي أي شيء يشتتك وابدئي الآن."""
                })
                st.rerun()

        if st.session_state.timer_active and st.session_state.timer_end:
            remaining = max(0, int(st.session_state.timer_end - time.time()))
            render_circular_timer(st.session_state.timer_duration, remaining)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("⏹ إيقاف التايمر"):
                    st.session_state.timer_active = False
                    st.session_state.timer_end = None
                    st.rerun()

            with col_b:
                st.markdown(
                    "<div style='padding-top:8px;color:#666;font-size:14px'>خذي نفسًا... خطوة واحدة فقط ✨</div>",
                    unsafe_allow_html=True
                )

            if remaining > 0:
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.timer_active = False
                st.session_state.timer_end = None

                if not st.session_state.played_finish_sound:
                    play_finish_sound()
                    st.session_state.played_finish_sound = True

                st.balloons()
                st.session_state.points += 20
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "خلصت 7 دقائق! 🔔🔥 ممتاز جدًا. علّمي الخطوة اللي خلصتيها وخذي نقاطك."
                })
                st.rerun()

    # إدخال المستخدم
    user_input = st.chat_input("أخبر عزم كيف تشعر وما هي مهمتك...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        task_keywords = [
            "مهمة", "مذاكر", "مشروع", "تقرير", "واجب", "اذاكر", "أذاكر",
            "ابدأ", "كتاب", "بحث", "امتحان", "برمجة", "كود"
        ]
        has_task = any(kw in user_input for kw in task_keywords)

        with st.spinner("عزم يفكر..."):
            response = ask_azm(
                st.session_state.messages,
                profile=st.session_state.profile
            )

        st.session_state.messages.append({"role": "assistant", "content": response})

        if has_task:
            st.session_state.pending_emotion = user_input

        st.rerun()