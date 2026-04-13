import streamlit as st
from Nuha import ask_azm

st.set_page_config(page_title="عزم", page_icon="✦", layout="centered")

st.markdown("""
<style>
* { direction: rtl; text-align: right; }
.stChatMessage { direction: rtl; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {}

if "name" not in st.session_state.profile:
    st.title("✦ مرحباً في عزم")
    st.subheader("أنا مدربك الذكي اللي يساعدك تبدأ")
    name = st.text_input("ما اسمك؟")
    if st.button("ابدأ") and name:
        st.session_state.profile["name"] = name
        st.rerun()

elif "big_goal" not in st.session_state.profile:
    st.title(f"أهلاً {st.session_state.profile['name']}! 👋")
    goal = st.text_input("إيش أكبر هدف تشتغلين عليه هالفصل؟")
    if st.button("التالي") and goal:
        st.session_state.profile["big_goal"] = goal
        st.rerun()

elif "medium_goal" not in st.session_state.profile:
    st.title("هدفك الأسبوعي")
    goal = st.text_input("إيش أهم شيء تبغين تنجزيه هالأسبوع؟")
    if st.button("التالي") and goal:
        st.session_state.profile["medium_goal"] = goal
        st.rerun()

elif "dream" not in st.session_state.profile:
    st.title("حلمك ✦")
    dream = st.text_input("كيف تتخيلين نفسك لما تحققين هدفك؟")
    if st.button("هذا حلمي") and dream:
        st.session_state.profile["dream"] = dream
        st.rerun()

else:
    st.markdown(f"""
    <div style='background:#534AB7;padding:12px 16px;border-radius:10px;margin-bottom:16px;'>
        <span style='color:white;font-size:18px;font-weight:500'>✦ عزم</span>
        <span style='color:rgba(255,255,255,0.7);font-size:13px;margin-right:8px'>
            {st.session_state.profile['name']}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:#EEEDFE;padding:8px 12px;border-radius:8px;margin-bottom:16px;font-size:13px;color:#3C3489'>
        حلمك: {st.session_state.profile['dream']} ✦
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant", avatar="✦"):
                st.write(msg["content"])

    user_input = st.chat_input("أخبر عزم كيف تشعرين وما هي مهمتك...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant", avatar="✦"):
            with st.spinner("عزم يفكر..."):
                response = ask_azm(st.session_state.messages)
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})