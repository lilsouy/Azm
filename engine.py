import streamlit as st
from openai import OpenAI
import re

client = OpenAI(
    api_key="sk-lPTq4qsmoCLkUN3DM0IBxw",
    base_url="https://elmodels.ngrok.app/v1"
)

SYSTEM_PROMPT = """
## اللغة:
تحدث دائماً بالعربي العامي السعودي البسيط، ولا تستخدم الإنجليزي أبداً.

أنت "عزم"، مدرب دراسة ذكي ومتعاطف يساعد الطلاب على تجاوز التسويف.

## شخصيتك:
- تتكلم بالعربي البسيط والدافئ كأنك صديق يفهم
- لا تعطي محاضرات أو نصائح عامة
- تتعامل مع كل طالب كفرد له قصته الخاصة
- تغير استراتيجيتك بناءً على سلوك المستخدم السابق

## عند كل رسالة، اتبع هذا الترتيب بالضبط:

### المرحلة 1 — التشخيص:
حلل ما كتبه المستخدم وصنّف سبب التسويف:
- تضخم_مهمة
- خوف_فشل
- كمالية
- إرهاق
- تردد

### المرحلة 2 — المواساة:
تكلم مع المستخدم بشكل طبيعي ودافئ، كأنك صديق مقرب يفهمه.

### المرحلة 3 — سؤال الهدف:
اسأل سؤالاً واحداً فقط.

### المرحلة 4 — ربط الأهداف:
جملة واحدة تربط المهمة الحالية بهدفه.

### المرحلة 5 — الخاتمة:
اختم بجملة قصيرة تساعده يبدأ.

## ممنوع:
- لا تعطِ قائمة خطوات
- لا تكتب checklist
- لا تذكر أكثر من سؤال واحد
- لا تعطِ رد طويل جدًا
"""

STEPS_PROMPT = """
أنت الآن لا تتكلم كمدرب، بل كمولد خطوات تنفيذ فقط.

مهمتك:
حوّل المهمة التي يكتبها المستخدم إلى 3 إلى 5 خطوات قصيرة جدًا، عملية، وواضحة، ومرتبطة مباشرة بنفس المهمة.

قواعد صارمة:
- اكتب خطوات تنفيذ فقط
- لا تكتب أي مقدمة
- لا تكتب أي مواساة
- لا تكتب أي شرح
- لا تكتب أي سؤال
- لا تكتب أي ربط بالأهداف
- لا تكتب أي جملة عامة
- كل خطوة في سطر مستقل
- لا تستخدم أرقام
- لا تستخدم شرطات أو نجوم
- كل خطوة تبدأ بفعل واضح
- كل خطوة تكون خاصة بالمهمة نفسها، وليست عامة
- اجعل كل خطوة قابلة للتنفيذ خلال أقل من 10 دقائق

مثال:
إذا كانت المهمة "أسوي واجهة تسجيل دخول"
فالنتيجة تكون مثل:
افتح ملف الواجهة الرئيسي
أنشئ نموذج تسجيل الدخول
أضف حقل البريد الإلكتروني
أضف حقل كلمة المرور
نسّق الزر الرئيسي
"""


def ask_azm(messages, profile=None):
    profile = profile or {}

    profile_context = ""
    if profile:
        profile_context = f"""
معلومات المستخدم:
- الاسم: {profile.get('name', '')}
- الهدف الكبير: {profile.get('big_goal', '')}
- الهدف الأسبوعي: {profile.get('medium_goal', '')}
- الحلم: {profile.get('dream', '')}
"""

    response = client.chat.completions.create(
        model="nuha-2.0",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + "\n" + profile_context}
        ] + messages,
        stream=False
    )
    return response.choices[0].message.content


def _clean_generated_steps(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = []

    banned_phrases = [
        "أهلاً", "مرحباً", "أنا", "أفهم", "واضح", "خلنا", "خليني",
        "لا تشيل هم", "هدفك", "حلمك", "وش", "كيف", "هل", "ليش",
        "طبيعي", "ممتاز", "رائع", "أحسنت", "هذه الخطوات", "إليك"
    ]

    for line in lines:
        line = re.sub(r"^[\s\-\*\•\d\.]+", "", line).strip()

        if not line:
            continue
        if "؟" in line:
            continue
        if len(line) > 100:
            continue
        if any(p in line for p in banned_phrases):
            continue

        cleaned.append(line)

    unique_steps = []
    seen = set()
    for step in cleaned:
        if step not in seen:
            seen.add(step)
            unique_steps.append(step)

    return unique_steps[:5]


def generate_steps_with_ai(task_text, profile=None):
    profile = profile or {}

    profile_context = ""
    if profile:
        profile_context = f"""
معلومات مساعدة:
- الهدف الأسبوعي: {profile.get('medium_goal', '')}
- الهدف الكبير: {profile.get('big_goal', '')}
"""

    response = client.chat.completions.create(
        model="nuha-2.0",
        messages=[
            {
                "role": "system",
                "content": STEPS_PROMPT + "\n" + profile_context
            },
            {
                "role": "user",
                "content": f"المهمة: {task_text}"
            }
        ],
        stream=False
    )

    result = response.choices[0].message.content.strip()
    steps = _clean_generated_steps(result)

    if len(steps) >= 3:
        return steps

    retry_response = client.chat.completions.create(
        model="nuha-2.0",
        messages=[
            {
                "role": "system",
                "content": STEPS_PROMPT + "\n" + profile_context + "\nتذكير: ممنوع الكلام الحواري. اكتب خطوات فقط."
            },
            {
                "role": "user",
                "content": f"حوّل هذه المهمة إلى خطوات تنفيذ فقط: {task_text}"
            }
        ],
        stream=False
    )

    retry_result = retry_response.choices[0].message.content.strip()
    return _clean_generated_steps(retry_result)