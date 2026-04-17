import os
import re
from typing import Any

from openai import OpenAI

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
""".strip()


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
""".strip()


def _get_env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"المتغير البيئي {name} غير موجود")
    return value or ""


def _build_client() -> OpenAI:
    api_key = _get_env("OPENAI_API_KEY", required=True)
    base_url = _get_env("OPENAI_BASE_URL", "https://elmodels.ngrok.app/v1")
    return OpenAI(api_key=api_key, base_url=base_url)


def _build_profile_context(profile: dict[str, Any] | None, mode: str = "chat") -> str:
    profile = profile or {}

    if not profile:
        return ""

    if mode == "steps":
        return f"""
معلومات مساعدة:
- الاسم: {profile.get('name', '')}
- الهدف الأسبوعي: {profile.get('medium_goal', '')}
- الهدف الكبير: {profile.get('big_goal', '')}
- الحلم: {profile.get('dream', '')}
""".strip()

    return f"""
معلومات المستخدم:
- الاسم: {profile.get('name', '')}
- الهدف الكبير: {profile.get('big_goal', '')}
- الهدف الأسبوعي: {profile.get('medium_goal', '')}
- الحلم: {profile.get('dream', '')}
""".strip()


def _normalize_messages(messages: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    if not messages:
        return []

    normalized: list[dict[str, str]] = []

    for msg in messages:
        role = (msg.get("role") or "").strip()
        content = str(msg.get("content") or "").strip()

        if not role or not content:
            continue

        if role == "bot":
            role = "assistant"
        elif role == "user":
            role = "user"
        elif role == "assistant":
            role = "assistant"
        elif role == "system":
            role = "system"
        else:
            continue

        normalized.append({"role": role, "content": content})

    return normalized


def _chat_completion(messages: list[dict[str, str]]) -> str:
    client = _build_client()
    model_name = _get_env("OPENAI_MODEL", "nuha-2.0")

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=False,
        temperature=0.7,
    )

    return (response.choices[0].message.content or "").strip()


def ask_azm(messages: list[dict[str, Any]], profile: dict[str, Any] | None = None) -> str:
    normalized_messages = _normalize_messages(messages)
    profile_context = _build_profile_context(profile, mode="chat")

    system_content = SYSTEM_PROMPT
    if profile_context:
        system_content += "\n\n" + profile_context

    payload = [{"role": "system", "content": system_content}] + normalized_messages

    try:
        result = _chat_completion(payload)
        return result or "أنا معك. قل لي وش أصعب شيء موقفك الآن؟"
    except Exception:
        return "صار عندي مشكلة بسيطة وأنا أحاول أرد عليك. جرّب أرسل رسالتك مرة ثانية."


def _looks_like_valid_step(line: str) -> bool:
    banned_phrases = [
        "أهلاً", "مرحباً", "أنا", "أفهم", "واضح", "خلنا", "خليني",
        "لا تشيل هم", "هدفك", "حلمك", "وش", "كيف", "هل", "ليش",
        "طبيعي", "ممتاز", "رائع", "أحسنت", "هذه الخطوات", "إليك",
        "بالتأكيد", "أكيد", "مقدمة", "شرح", "أولاً", "ثانياً"
    ]

    if not line:
        return False
    if "؟" in line:
        return False
    if len(line) < 4 or len(line) > 100:
        return False
    if any(p in line for p in banned_phrases):
        return False

    return True


def _clean_generated_steps(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned: list[str] = []

    for line in lines:
        line = re.sub(r"^[\s\-\*\•\d\.\)\(]+", "", line).strip()
        line = re.sub(r"\s+", " ", line)

        if not _looks_like_valid_step(line):
            continue

        cleaned.append(line)

    unique_steps: list[str] = []
    seen: set[str] = set()

    for step in cleaned:
        if step not in seen:
            seen.add(step)
            unique_steps.append(step)

    return unique_steps[:5]


def _fallback_steps(task_text: str) -> list[str]:
    task_text = (task_text or "").strip()

    if not task_text:
        return [
            "افتح الملف أو الصفحة المرتبطة بالمهمة",
            "حدد أصغر جزء ممكن تبدأ فيه",
            "نفذ أول جزء فقط الآن",
        ]

    return [
        "افتح الشيء المرتبط بالمهمة",
        "حدد أول جزء بسيط من المهمة",
        f"ابدأ بتنفيذ أول جزء من: {task_text[:40]}",
    ]


def generate_steps_with_ai(task_text: str, profile: dict[str, Any] | None = None) -> list[str]:
    task_text = (task_text or "").strip()
    if not task_text:
        return _fallback_steps(task_text)

    profile_context = _build_profile_context(profile, mode="steps")

    system_content = STEPS_PROMPT
    if profile_context:
        system_content += "\n\n" + profile_context

    first_payload = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": f"المهمة: {task_text}"},
    ]

    try:
        result = _chat_completion(first_payload)
        steps = _clean_generated_steps(result)

        if len(steps) >= 3:
            return steps
    except Exception:
        steps = []

    retry_payload = [
        {
            "role": "system",
            "content": system_content + "\n\nتذكير مهم جدًا: ممنوع الكلام الحواري. اكتب خطوات تنفيذ فقط، كل خطوة في سطر مستقل."
        },
        {
            "role": "user",
            "content": f"حوّل هذه المهمة إلى خطوات تنفيذ قصيرة جدًا وواضحة فقط: {task_text}"
        }
    ]

    try:
        retry_result = _chat_completion(retry_payload)
        retry_steps = _clean_generated_steps(retry_result)

        if retry_steps:
            return retry_steps
    except Exception:
        pass

    return _fallback_steps(task_text)