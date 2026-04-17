from openai import OpenAI

from typing import Optional, Dict, Any
import json

client = OpenAI(
    api_key="sk-lPTq4qsmoCLkUN3DM0IBxw",
    base_url="https://elmodels.ngrok.app/v1"
)

SYSTEM_PROMPT = """

انت عزم, مدرب دراسه ذكي.

أسلوب اللهجة (نجدية بيضاء):

- اكتب بلهجة نجدية بيضاء بسيطة ومفهومة لكل السعوديين (بدون مصطلحات ثقيلة).

- استخدم: وش، وِدّك، خلّنا، يلا، زين، تمام، صدق، مرّة، الحين، شوي، توّك، ابشر/أبشري، لا تشيل هم.

- تجنّب تمامًا كلمات/صياغات مو نجدية مثل: شنو، هنبدا/حنبدأ، بزاف، برشا، إيشلون، وايد.

أمثلة (لا تنسخها حرفيًا دائمًا، بس خذ نفس الأسلوب):

- "أبشري… اللي تحسين فيه مفهوم، بس خلّنا نبدأ بخطوة صغيرة الحين."

- "وش أكثر شي مخوّفك من المهمة؟"

- "زين، عطّني بس: متى التسليم؟ وش نوع المهمة؟ وكم وقت عندك اليوم؟"

- "تمام، شرارة العزم 7 دقايق: افتحي الملف واكتبي أول 3 نقاط بس، بدون ترتيب."

- "إذا تحسين بثِقل، عادي… نبي بس البداية، مو الكمال."

- "يلا نخفّفها: خطوة وحدة واضحة وبس."

هدفك: تساعد المستخدم يكسر التسويف ويبدأ الآن عبر:

1) شرارة العزم (7 دقائق) لمهمة صغيرة جدًا قابلة للإنجاز.

2) 5 مهام مصغّرة Micro Tasks على شكل Checklist قابلة للتعديل من المستخدم.

أسلوبك:

- لهجة سعودية بيضاء، دعم بدون حكم.

- مختصر وواضح.

- تركيز على “البداية الآن”.

الحدود:

- ممنوع تكتب المحتوى كامل بدل المستخدم.

- المسموح: عناوين صغيرة، ترتيب فكرة، Outline، قوالب قصيرة جدًا، أمثلة قصيرة جدًا (سطر–سطرين).

إذا معلومات المستخدم ناقصة:

- اسأل سؤال متابعة واحد فقط يجمع: موعد التسليم/الاختبار + نوع المهمة + كم درس/كم جزء + الوقت المتاح.

تصنيفات التسويف (اختر واحد أساسي وقد تضيف ثانوي):

- تضخيم المهمة

- الخوف من نتيجة سيئة

- الكمالية الزايدة

- انخفاض الطاقة

- غموض الخطوة الأولى

قواعد شرارة العزم:

- دائمًا 7 دقائق.

- مهمة واحدة فقط تنجز خلال 7 دقائق.

- محددة جدًا.

- “مسودة خام مسموح” بدون مثالية.

مهم جدًا:

- أخرج JSON فقط بدون أي نص خارج JSON.

- لا تضع ```json

- لا تضع شرح قبل أو بعد JSON

مفاتيح JSON المطلوبة فقط:

support_text

procrastination (primary_category, secondary_category, reasoning_short)

spark_task (minutes, task, success_criteria)

micro_tasks

follow_up_question

"""

FALLBACK_RESPONSE = {

    "support_text": "واضح إن عندك ضغط، خلّنا نخففها ونبدأ بشي بسيط جدًا.",

    "procrastination": {

        "primary_category": "غموض الخطوة الأولى",

        "secondary_category": "انخفاض الطاقة",

        "reasoning_short": "المستخدم يحتاج بداية أوضح وأخف"

    },

    "spark_task": {

        "minutes": 7,

        "task": "افتح المهمة وحدد أول جزء بسيط فقط بدون ما تحاول تخلص كل شيء",

        "success_criteria": "تكون فتحت المهمة وحددت أول جزء واضح"

    },

    "micro_tasks": [

        "افتح الملف أو الكتاب",

        "حدد أول جزء بسيط",

        "اقرأ أول عنوان أو سطرين",

        "اكتب 3 نقاط سريعة",

        "حدد الخطوة اللي بعدها"

    ],

    "follow_up_question": "كم باقي على التسليم أو الاختبار، ووش الجزء الأقرب تبدأ فيه؟"

}

def _extract_last_user_message(messages) -> str:

    if isinstance(messages, list):

        for m in reversed(messages):

            if isinstance(m, dict) and m.get("role") == "user":

                return str(m.get("content", "")).strip()

    elif isinstance(messages, str):

        return messages.strip()

    return ""

def ask_azm(messages, profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

    try:

        user_msg = _extract_last_user_message(messages)

        if not user_msg:

            return FALLBACK_RESPONSE

        context_parts = []

        if profile:

            if profile.get("name"):

                context_parts.append(f"اسم المستخدم: {profile['name']}")

            if profile.get("big_goal"):

                context_parts.append(f"الهدف الكبير: {profile['big_goal']}")

            if profile.get("medium_goal"):

                context_parts.append(f"الهدف الأسبوعي: {profile['medium_goal']}")

        context_text = "\n".join(context_parts).strip()

        user_content = f"""

{context_text}

رسالة المستخدم:

{user_msg}

تذكير:

أرجع JSON فقط بالمفاتيح المطلوبة.

""".strip()

        response = client.chat.completions.create(

            model="nuha-2.0",

            messages=[

                {"role": "system", "content": SYSTEM_PROMPT},

                {"role": "user", "content": user_content}

            ],

            temperature=0.2,

            max_tokens=500,

            stream=False
            )

        text = (response.choices[0].message.content or "").strip()

        print("RAW MODEL RESPONSE:", text)

        if text.startswith("```"):

            text = text.strip("`").strip()

            if text.lower().startswith("json"):

                text = text[4:].strip()

        data = json.loads(text)

        required_keys = {

            "support_text",

            "procrastination",

            "spark_task",

            "micro_tasks",

            "follow_up_question"

        }

        if not required_keys.issubset(data.keys()):

            merged = FALLBACK_RESPONSE.copy()

            merged.update(data)

            return merged

        if not isinstance(data.get("micro_tasks"), list):

            data["micro_tasks"] = FALLBACK_RESPONSE["micro_tasks"]

        if len(data["micro_tasks"]) < 5:

            data["micro_tasks"] = (data["micro_tasks"] + FALLBACK_RESPONSE["micro_tasks"])[:5]

        if not isinstance(data.get("spark_task"), dict):

            data["spark_task"] = FALLBACK_RESPONSE["spark_task"]

        if "minutes" not in data["spark_task"]:

            data["spark_task"]["minutes"] = 7

        data["spark_task"]["minutes"] = 7

        return data

    except Exception as e:

        print("ENGINE ERROR:", e)

        return FALLBACK_RESPONSE
