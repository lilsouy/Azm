from openai import OpenAI
import time
import os
os.system('chcp 65001 > nul')

client = OpenAI(
    api_key="sk-oAlqOh_ZKXokKIJ08lt9Pw",
    base_url="https://elmodels.ngrok.app/v1"
)

# نقاط العزم
azm_points = 0

def ask_nuha(prompt):
    """إرسال رسالة للنموذج واستقبال الرد"""
    response = client.chat.completions.create(
        model="nuha-2.0",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    full_response = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
            full_response += content
    print()
    return full_response

def sparks_timer(minutes=7):
    """شرارة العزم - مؤقت 7 دقائق"""
    print(f"\n⚡ شرارة العزم! عندك {minutes} دقائق للخطوة الأولى فقط!")
    print("اضغط Enter لتبدأ...")
    input()
    seconds = minutes * 60
    print(f"🔥 البدء الآن! ({minutes} دقائق)")
    # نحاكي المؤقت بشكل مبسط
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    print("  انطلق! 🚀\n")
    print(f"[المؤقت يعمل لمدة {minutes} دقيقة - في التطبيق الحقيقي سيكون مرئياً]")
    input("\nاضغط Enter بعد انتهاء الخطوة الأولى...")

def show_checklist(tasks):
    """عرض قائمة المهام مع Checkbox"""
    global azm_points
    print("\n📋 خطتك الكاملة:")
    completed = []
    for i, task in enumerate(tasks, 1):
        print(f"  {'✅' if task in completed else '⬜'} {i}. {task}")
    
    print("\nأدخل رقم المهمة لتحديدها كمنجزة (0 للخروج):")
    while True:
        choice = input(">> ").strip()
        if choice == "0":
            break
        if choice.isdigit() and 1 <= int(choice) <= len(tasks):
            task = tasks[int(choice) - 1]
            if task not in completed:
                completed.append(task)
                azm_points += 10
                print(f"✅ أحسنت! +10 نقاط عزم 🌟 | مجموعك: {azm_points} نقطة")
            else:
                print("✅ هذه المهمة منجزة مسبقاً")
        
        # عرض القائمة المحدثة
        print("\n📋 خطتك:")
        for i, task in enumerate(tasks, 1):
            print(f"  {'✅' if task in completed else '⬜'} {i}. {task}")

def main():
    global azm_points
    print("=" * 50)
    print("        مرحباً بك في تطبيق عَزْم 💪")
    print("=" * 50)
    
    # ── المرحلة 1: استقبال المهمة والشعور ──
    print("\n📝 ما المهمة التي تجد صعوبة في البدء بها؟")
    task = input(">> ").strip()
    
    print("\n💭 كيف تشعر تجاهها؟ (مثال: خايف، متردد، ما أعرف من وين أبدأ)")
    feeling = input(">> ").strip()
    
    # ── المرحلة 2: تحليل الحالة النفسية ──
    print("\n🔍 عزم يحللك...\n")
    analysis_prompt = f"""
    المستخدم عنده مهمة: "{task}"
    وشعوره: "{feeling}"
    
    قم بـ:
    1. تحديد سبب التسويف (خوف، كمالية، تردد، إلخ)
    2. تقديم دعم نفسي مناسب وقصير (3-4 جمل)
    3. اسأله: كيف ستشعر بعد إتمام هذه المهمة؟
    
    الرد بالعربية، بأسلوب محفز وودي.
    """
    ask_nuha(analysis_prompt)
    
    # ── المرحلة 3: سؤال عن الدافع ──
    print("\n✨ شاركنا:")
    motivation = input(">> ").strip()
    print(f"\n💾 [تم حفظ دوافعك في ملفك الشخصي]\n")
    
    # ── المرحلة 4: تقسيم المهمة لـ Micro-Tasks ──
    print("⚙️  عزم يقسّم مهمتك لخطوات صغيرة...\n")
    microtasks_prompt = f"""
    المهمة: "{task}"
    
    قسّمها إلى 5 خطوات صغيرة جداً وقابلة للتنفيذ الفوري.
    اكتبها كقائمة مرقمة فقط بدون أي مقدمة.
    مثال:
    1. افتح الملف
    2. اقرأ أول صفحة فقط
    ...
    """
    tasks_response = ask_nuha(microtasks_prompt)
    
    # استخراج الخطوات من الرد
    tasks_list = []
    for line in tasks_response.split('\n'):
        line = line.strip()
        if line and line[0].isdigit():
            # إزالة الرقم والنقطة من البداية
            task_text = line.split('.', 1)[-1].strip()
            if task_text:
                tasks_list.append(task_text)
    
    if not tasks_list:
        tasks_list = ["الخطوة الأولى", "الخطوة الثانية", "الخطوة الثالثة"]
    
    # ── المرحلة 5: عرض أول خطوة + شرارة العزم ──
    print(f"\n🎯 ركّز على هذه الخطوة الأولى فقط:")
    print(f"   ➡️  {tasks_list[0]}\n")
    
    sparks_timer(minutes=7)
    
    # ── المرحلة 6: عرض الخطة الكاملة مع Checklist ──
    show_checklist(tasks_list)
    
    # ── الختام ──
    print("\n" + "=" * 50)
    print(f"🏆 مؤشر العزم النهائي: {azm_points} نقطة")
    if azm_points >= 30:
        print("⭐ مستوى: محترف العزم!")
    elif azm_points >= 10:
        print("🌱 مستوى: بادئ العزم - استمر!")
    else:
        print("💪 ابدأ وستحصل على نقاطك!")
    print("=" * 50)
    print("\n[📊 في التطبيق الحقيقي: سيتم تحليل سلوكك وتحسين التوصيات]")

if __name__ == "__main__":
    main()