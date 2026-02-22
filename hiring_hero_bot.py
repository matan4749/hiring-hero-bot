import telebot
from telebot import types
from groq import Groq
import requests
import os
import tempfile

# pip install pytelegrambotapi groq pymupdf python-docx

import os
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8426423526:AAFIDVhSUfY19bmrDuPiDe-aTb4-9TdCmvg')
GROQ_API_KEY   = os.environ.get('GROQ_API_KEY', '')

bot    = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# ═══════════════════════════════════════════════════════════
#  TEXTS
# ═══════════════════════════════════════════════════════════
TEXTS = {
    'he': {
        # UI
        'welcome': (
            "🎓 ברוך הבא ל-Hiring Hero!\n"
            "הבוט שיהפוך אותך למתכנת שכל חברה רוצה לגייס.\n\n"
            "בחר מה תרצה לעשות עכשיו:"
        ),
        'interview_btn':  "🎙️ ראיון דמה",
        'task_btn':       "💻 בדיקת קוד",
        'leetcode_btn':   "🧩 ליטקוד יומי",
        'cv_btn':         "📄 ניתוח קורות חיים",
        'jd_btn':         "🔍 מנתח משרות (JD)",
        'python_btn':     "🐍 לימוד Python",
        'sysdesign_btn':  "🏗️ System Design",
        'lang_btn':       "🌐 עבור לאנגלית",
        'menu_btn':       "🏠 תפריט ראשי",

        # interview
        'interview_start': "🏢 הראיון התחיל.\nשלום, אני המראיין שלך היום. ספר לי על פרויקט מעניין שעבדת עליו, או שנצלוח ישר לשאלות טכניות?",

        # task
        'task_prompt': "💻 שלח לי את הקוד של המטלה שלך ואני אבצע Code Review מקצועי.",

        # cv
        'cv_prompt':      "📄 שלח לי את קורות החיים שלך — טקסט חופשי, קובץ PDF, או קובץ Word (.docx)\nאני אנתח, אתן משוב מלא, ואציע שיפורים קונקרטיים.",
        'cv_processing':  "⏳ מעבד את הקובץ...",
        'cv_unsupported': "❌ פורמט לא נתמך. שלח PDF, DOCX, או טקסט.",
        'cv_error_file':  "❌ לא הצלחתי לקרוא את הקובץ. נסה שוב.",

        # jd analyzer
        'jd_prompt':     "🔍 הדבק את טקסט המשרה (Job Description) שאתה מעוניין בה.\nאני אחלץ את ה-Keywords החשובים ואגיד לך בדיוק מה להדגיש בקורות החיים שלך כדי לעבור ATS.",
        'jd_processing': "⏳ מנתח את המשרה...",

        # leetcode
        'leetcode_intro':        "🧩 מייצר שאלת LeetCode...",
        'leetcode_submit':       "שלח את הפתרון שלך בקוד, ואני אעבור עליו ואתן משוב מפורט.",
        'leetcode_solution_btn': "💡 הצג פתרון",
        'leetcode_thinking':     "⏳ בודק את הפתרון שלך...",

        # python
        'python_intro':       "🐍 בחר נושא ללמידה:",
        'python_topics': [
            ("Variables & Types", "py_vars"),
            ("Lists & Dicts",     "py_lists"),
            ("Functions",         "py_funcs"),
            ("OOP",               "py_oop"),
            ("Decorators",        "py_deco"),
            ("Async / Await",     "py_async"),
            ("Generators",        "py_gen"),
            ("Error Handling",    "py_errors"),
        ],
        'python_answer_prompt': "ענה על התרגיל בקוד Python:",
        'python_next_btn':      "➡️ נושא הבא",

        # system design
        'sysdesign_intro': "🏗️ בחר מערכת לתכנן:",
        'sysdesign_topics': [
            ("WhatsApp / Chat",        "sd_chat"),
            ("URL Shortener",          "sd_url"),
            ("Instagram / Image Feed", "sd_insta"),
            ("YouTube / Streaming",    "sd_video"),
            ("Uber / Ride Sharing",    "sd_uber"),
            ("Google Search",          "sd_search"),
        ],
        'sysdesign_thinking': "🏗️ מעבד את התשובה שלך...",

        # AI systems
        'interview_system': "You are a Senior Tech Interviewer at a Top-Tier company. Conduct the interview in Hebrew. Ask ONE question at a time, give a short critique, then ask the next.",
        'task_system':      "Perform a professional code review. Check complexity, clean code, and bugs. Answer in Hebrew.",
        'cv_system': (
            "You are an expert CV analyst and writer for software engineers. "
            "Do the following in Hebrew:\n"
            "1. ANALYSIS: Identify strengths and weaknesses in the CV (structure, content, impact).\n"
            "2. SCORE: Give an overall ATS score out of 10 with justification.\n"
            "3. IMPROVEMENTS: List 5-7 specific, actionable improvements.\n"
            "4. REWRITE: Rewrite the most important section (summary/experience) to be more impactful.\n"
            "Use clear headers for each section."
        ),
        'jd_system': (
            "You are an ATS and recruitment expert. Analyze the job description and do the following in Hebrew:\n"
            "1. TOP KEYWORDS: Extract the 10-15 most important technical and soft-skill keywords the ATS will scan for.\n"
            "2. MUST-HAVES: List required skills/experience the candidate must highlight.\n"
            "3. NICE-TO-HAVES: List preferred skills that give a competitive edge.\n"
            "4. CV TIPS: Give 4-5 specific tips on how to tailor a software engineer CV for this role.\n"
            "5. RED FLAGS: Mention anything in the JD that candidates should be aware of.\n"
            "Use clear headers for each section."
        ),
        'general_system':  "You are a professional software engineering career coach. Answer in Hebrew.",
        'leetcode_gen_system': (
            "You are a LeetCode coach. Generate ONE LeetCode Medium problem.\n"
            "Format EXACTLY:\nProblem: <name>\nDifficulty: Medium\nDescription: <desc>\nExamples:\n<ex>\nConstraints:\n<c>\n"
            "SOLUTION_PLACEHOLDER\n<full Python solution with explanation>\n"
            "Speak Hebrew for text, keep code in English."
        ),
        'leetcode_review_system': "You are a senior engineer reviewing a LeetCode solution. Check correctness, time/space complexity, edge cases, code quality. Be constructive. Answer in Hebrew.",
        'python_teach_system': (
            "You are a Python teacher. Teach the topic clearly with examples, then give ONE coding exercise. "
            "Format: explanation, code example, then 'תרגיל: <exercise>'. Answer in Hebrew."
        ),
        'python_review_system': "You are a Python teacher reviewing a student solution. Give feedback on correctness, style, and improvements. Answer in Hebrew.",
        'sysdesign_system': (
            "You are a Staff Engineer conducting a System Design interview in Hebrew. "
            "Do NOT give the answer. Ask ONE probing question at a time about: requirements, scale, "
            "components (Load Balancer, DB, Cache, CDN, Queue), trade-offs, bottlenecks. "
            "Give short feedback after each answer, then ask the next question. Conduct in Hebrew."
        ),
        'error': "❌ תקלה זמנית בשרת.",
    },

    'en': {
        # UI
        'welcome': (
            "🎓 Welcome to Hiring Hero!\n"
            "The bot that turns you into a developer every company wants to hire.\n\n"
            "Choose what you'd like to do:"
        ),
        'interview_btn':  "🎙️ Mock Interview",
        'task_btn':       "💻 Code Review",
        'leetcode_btn':   "🧩 Daily LeetCode",
        'cv_btn':         "📄 CV Analysis",
        'jd_btn':         "🔍 JD Analyzer",
        'python_btn':     "🐍 Learn Python",
        'sysdesign_btn':  "🏗️ System Design",
        'lang_btn':       "🌐 Switch to Hebrew",
        'menu_btn':       "🏠 Main Menu",

        # interview
        'interview_start': "🏢 Interview started.\nHi, I'm your interviewer. Tell me about an interesting project, or shall we jump to technical questions?",

        # task
        'task_prompt': "💻 Send me your code and I'll perform a professional Code Review.",

        # cv
        'cv_prompt':      "📄 Send me your CV — plain text, PDF, or Word (.docx) file.\nI'll analyze it fully, give detailed feedback, and suggest concrete improvements.",
        'cv_processing':  "⏳ Processing your file...",
        'cv_unsupported': "❌ Unsupported format. Please send PDF, DOCX, or plain text.",
        'cv_error_file':  "❌ Couldn't read the file. Please try again.",

        # jd analyzer
        'jd_prompt':     "🔍 Paste the Job Description text for the role you're targeting.\nI'll extract the most important keywords and tell you exactly what to highlight in your CV to pass the ATS scan.",
        'jd_processing': "⏳ Analyzing the job description...",

        # leetcode
        'leetcode_intro':        "🧩 Generating LeetCode question...",
        'leetcode_submit':       "Send me your solution in code and I'll review it with detailed feedback.",
        'leetcode_solution_btn': "💡 Show Solution",
        'leetcode_thinking':     "⏳ Reviewing your solution...",

        # python
        'python_intro':       "🐍 Choose a topic to learn:",
        'python_topics': [
            ("Variables & Types", "py_vars"),
            ("Lists & Dicts",     "py_lists"),
            ("Functions",         "py_funcs"),
            ("OOP",               "py_oop"),
            ("Decorators",        "py_deco"),
            ("Async / Await",     "py_async"),
            ("Generators",        "py_gen"),
            ("Error Handling",    "py_errors"),
        ],
        'python_answer_prompt': "Answer the exercise above in Python code:",
        'python_next_btn':      "➡️ Next Topic",

        # system design
        'sysdesign_intro': "🏗️ Choose a system to design:",
        'sysdesign_topics': [
            ("WhatsApp / Chat",        "sd_chat"),
            ("URL Shortener",          "sd_url"),
            ("Instagram / Image Feed", "sd_insta"),
            ("YouTube / Streaming",    "sd_video"),
            ("Uber / Ride Sharing",    "sd_uber"),
            ("Google Search",          "sd_search"),
        ],
        'sysdesign_thinking': "🏗️ Processing your answer...",

        # AI systems
        'interview_system': "You are a Senior Tech Interviewer at a Top-Tier company. Conduct the interview in English. Ask ONE question at a time, give a short critique, then ask the next.",
        'task_system':      "Perform a professional code review. Check complexity, clean code, and bugs. Answer in English.",
        'cv_system': (
            "You are an expert CV analyst and writer for software engineers. "
            "Do the following in English:\n"
            "1. ANALYSIS: Identify strengths and weaknesses in the CV (structure, content, impact).\n"
            "2. SCORE: Give an overall ATS score out of 10 with justification.\n"
            "3. IMPROVEMENTS: List 5-7 specific, actionable improvements.\n"
            "4. REWRITE: Rewrite the most important section (summary/experience) to be more impactful.\n"
            "Use clear headers for each section."
        ),
        'jd_system': (
            "You are an ATS and recruitment expert. Analyze the job description and do the following in English:\n"
            "1. TOP KEYWORDS: Extract the 10-15 most important technical and soft-skill keywords the ATS will scan for.\n"
            "2. MUST-HAVES: List required skills/experience the candidate must highlight.\n"
            "3. NICE-TO-HAVES: List preferred skills that give a competitive edge.\n"
            "4. CV TIPS: Give 4-5 specific tips on how to tailor a software engineer CV for this role.\n"
            "5. RED FLAGS: Mention anything in the JD that candidates should be aware of.\n"
            "Use clear headers for each section."
        ),
        'general_system':  "You are a professional software engineering career coach. Answer in English.",
        'leetcode_gen_system': (
            "You are a LeetCode coach. Generate ONE LeetCode Medium problem.\n"
            "Format EXACTLY:\nProblem: <name>\nDifficulty: Medium\nDescription: <desc>\nExamples:\n<ex>\nConstraints:\n<c>\n"
            "SOLUTION_PLACEHOLDER\n<full Python solution with explanation>\nSpeak English."
        ),
        'leetcode_review_system': "You are a senior engineer reviewing a LeetCode solution. Check correctness, time/space complexity, edge cases, code quality. Be constructive. Answer in English.",
        'python_teach_system': (
            "You are a Python teacher. Teach the topic clearly with examples, then give ONE coding exercise. "
            "Format: explanation, code example, then 'Exercise: <exercise>'. Answer in English."
        ),
        'python_review_system': "You are a Python teacher reviewing a student solution. Give feedback on correctness, style, and improvements. Answer in English.",
        'sysdesign_system': (
            "You are a Staff Engineer conducting a System Design interview in English. "
            "Do NOT give the answer. Ask ONE probing question at a time about: requirements, scale, "
            "components (Load Balancer, DB, Cache, CDN, Queue), trade-offs, bottlenecks. "
            "Give short feedback after each answer, then ask the next question. Conduct in English."
        ),
        'error': "❌ Temporary server error.",
    }
}

PYTHON_TOPICS = {
    'py_vars': "Variables & Types", 'py_lists': "Lists & Dicts",
    'py_funcs': "Functions",        'py_oop':   "OOP",
    'py_deco':  "Decorators",       'py_async': "Async / Await",
    'py_gen':   "Generators",       'py_errors':"Error Handling",
}
SYSDESIGN_TOPICS = {
    'sd_chat':  "WhatsApp / Chat App",       'sd_url':    "URL Shortener",
    'sd_insta': "Instagram / Image Feed",    'sd_video':  "YouTube / Video Streaming",
    'sd_uber':  "Uber / Ride Sharing",       'sd_search': "Google Search",
}

# ═══════════════════════════════════════════════════════════
#  STATE
# ═══════════════════════════════════════════════════════════
user_states        = {}
user_histories     = {}
user_langs         = {}
user_leet_question = {}
user_leet_solution = {}
user_python_topic  = {}

def get_lang(c): return user_langs.get(c, 'en')
def txt(c, k):   return TEXTS[get_lang(c)][k]

# ═══════════════════════════════════════════════════════════
#  MENUS
# ═══════════════════════════════════════════════════════════
def main_menu(c):
    L = TEXTS[get_lang(c)]
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton(L['interview_btn'],  callback_data='start_interview'),
        types.InlineKeyboardButton(L['task_btn'],       callback_data='check_task'),
        types.InlineKeyboardButton(L['leetcode_btn'],   callback_data='leetcode'),
        types.InlineKeyboardButton(L['cv_btn'],         callback_data='fix_cv'),
        types.InlineKeyboardButton(L['jd_btn'],         callback_data='jd_analyze'),
        types.InlineKeyboardButton(L['python_btn'],     callback_data='python'),
        types.InlineKeyboardButton(L['sysdesign_btn'],  callback_data='sysdesign'),
        types.InlineKeyboardButton(L['lang_btn'],       callback_data='toggle_lang'),
    )
    return m

def back_btn(c):
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(txt(c, 'menu_btn'), callback_data='go_menu'))
    return m

def leetcode_btns(c):
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton(txt(c, 'leetcode_solution_btn'), callback_data='leet_show_solution'),
        types.InlineKeyboardButton(txt(c, 'menu_btn'),              callback_data='go_menu'),
    )
    return m

def python_topics_menu(c):
    m = types.InlineKeyboardMarkup(row_width=2)
    for label, cb in txt(c, 'python_topics'):
        m.add(types.InlineKeyboardButton(label, callback_data=cb))
    m.add(types.InlineKeyboardButton(txt(c, 'menu_btn'), callback_data='go_menu'))
    return m

def python_after_btns(c):
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton(txt(c, 'python_next_btn'), callback_data='python'),
        types.InlineKeyboardButton(txt(c, 'menu_btn'),        callback_data='go_menu'),
    )
    return m

def sysdesign_topics_menu(c):
    m = types.InlineKeyboardMarkup(row_width=2)
    for label, cb in txt(c, 'sysdesign_topics'):
        m.add(types.InlineKeyboardButton(label, callback_data=cb))
    m.add(types.InlineKeyboardButton(txt(c, 'menu_btn'), callback_data='go_menu'))
    return m

# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════
def safe_send(c, text, reply_markup=None):
    try:
        bot.send_message(c, text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception:
        clean = text.replace("*","").replace("_","").replace("`","").replace("~","")
        bot.send_message(c, clean, reply_markup=reply_markup)

def call_ai(system, user, temp=0.6):
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=temp,
    )
    return r.choices[0].message.content

def call_ai_history(messages, temp=0.6):
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=temp,
    )
    return r.choices[0].message.content

def extract_pdf(path):
    import fitz
    doc  = fitz.open(path)
    text = "".join(p.get_text() for p in doc)
    doc.close()
    return text.strip()

def extract_docx(path):
    from docx import Document
    return "\n".join(p.text for p in Document(path).paragraphs if p.text.strip())

def download_file(file_id):
    info   = bot.get_file(file_id)
    url    = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{info.file_path}"
    suffix = os.path.splitext(info.file_path)[1]
    tmp    = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(requests.get(url).content)
    tmp.close()
    return tmp.name, suffix.lower()

# ═══════════════════════════════════════════════════════════
#  HANDLERS
# ═══════════════════════════════════════════════════════════
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    c = message.chat.id
    user_states[c] = None; user_histories[c] = []
    bot.send_message(c, txt(c, 'welcome'), reply_markup=main_menu(c))

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    c    = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    # ── menu / lang ──
    if data == 'go_menu':
        user_states[c] = None; user_histories[c] = []
        bot.send_message(c, txt(c, 'welcome'), reply_markup=main_menu(c))
        return
    if data == 'toggle_lang':
        user_langs[c]  = 'en' if get_lang(c) == 'he' else 'he'
        user_states[c] = None; user_histories[c] = []
        bot.send_message(c, txt(c, 'welcome'), reply_markup=main_menu(c))
        return

    # ── interview ──
    if data == 'start_interview':
        user_states[c]    = 'INTERVIEW'
        user_histories[c] = [{"role":"system","content":txt(c,'interview_system')}]
        safe_send(c, txt(c, 'interview_start'), reply_markup=back_btn(c))

    # ── code review ──
    elif data == 'check_task':
        user_states[c] = 'TASK'
        bot.send_message(c, txt(c, 'task_prompt'), reply_markup=back_btn(c))

    # ── cv ──
    elif data == 'fix_cv':
        user_states[c] = 'CV'
        bot.send_message(c, txt(c, 'cv_prompt'), reply_markup=back_btn(c))

    # ── jd analyzer ──
    elif data == 'jd_analyze':
        user_states[c] = 'JD'
        bot.send_message(c, txt(c, 'jd_prompt'), reply_markup=back_btn(c))

    # ── leetcode ──
    elif data == 'leetcode':
        user_states[c] = 'LEET_WAIT'
        bot.send_message(c, txt(c, 'leetcode_intro'))
        bot.send_chat_action(c, 'typing')
        try:
            full = call_ai(txt(c,'leetcode_gen_system'), "Generate a problem now.")
            if 'SOLUTION_PLACEHOLDER' in full:
                parts = full.split('SOLUTION_PLACEHOLDER')
                q, s  = parts[0].strip(), parts[1].strip() if len(parts)>1 else ""
            else:
                q, s = full, ""
            user_leet_question[c] = q
            user_leet_solution[c] = s
            user_states[c]        = 'LEET_SOLVING'
            safe_send(c, q)
            bot.send_message(c, txt(c,'leetcode_submit'), reply_markup=leetcode_btns(c))
        except Exception as e:
            print(f"LeetCode error: {e}")
            bot.send_message(c, txt(c,'error'), reply_markup=back_btn(c))
            user_states[c] = None

    elif data == 'leet_show_solution':
        s   = user_leet_solution.get(c, "")
        msg = f"Solution:\n\n{s}" if s else "No solution saved."
        safe_send(c, msg, reply_markup=back_btn(c))
        user_states[c] = None

    # ── python ──
    elif data == 'python':
        bot.send_message(c, txt(c,'python_intro'), reply_markup=python_topics_menu(c))

    elif data in PYTHON_TOPICS:
        topic = PYTHON_TOPICS[data]
        user_python_topic[c] = topic
        user_states[c]       = 'PYTHON_EXERCISE'
        bot.send_chat_action(c, 'typing')
        try:
            lesson = call_ai(txt(c,'python_teach_system'), f"Teach me about: {topic}")
            safe_send(c, lesson)
            bot.send_message(c, txt(c,'python_answer_prompt'), reply_markup=back_btn(c))
        except Exception as e:
            print(f"Python error: {e}")
            bot.send_message(c, txt(c,'error'), reply_markup=back_btn(c))

    # ── system design ──
    elif data == 'sysdesign':
        bot.send_message(c, txt(c,'sysdesign_intro'), reply_markup=sysdesign_topics_menu(c))

    elif data in SYSDESIGN_TOPICS:
        system_name = SYSDESIGN_TOPICS[data]
        user_states[c]    = 'SYSDESIGN'
        user_histories[c] = [
            {"role":"system","content":txt(c,'sysdesign_system')},
            {"role":"user",  "content":f"I want to design: {system_name}"},
        ]
        bot.send_chat_action(c, 'typing')
        try:
            resp = call_ai_history(user_histories[c])
            user_histories[c].append({"role":"assistant","content":resp})
            safe_send(c, resp, reply_markup=back_btn(c))
        except Exception as e:
            print(f"SysDesign error: {e}")
            bot.send_message(c, txt(c,'error'), reply_markup=back_btn(c))

# ── documents ──
@bot.message_handler(content_types=['document'])
def handle_document(message):
    c     = message.chat.id
    state = user_states.get(c)

    if state not in ('CV', 'JD'):
        user_states[c] = 'CV'
        bot.send_message(c, txt(c,'cv_prompt'), reply_markup=back_btn(c))
        return

    bot.send_message(c, txt(c,'cv_processing'))
    try:
        path, suffix = download_file(message.document.file_id)
        if suffix == '.pdf':
            content = extract_pdf(path)
        elif suffix in ('.docx', '.doc'):
            content = extract_docx(path)
        else:
            bot.send_message(c, txt(c,'cv_unsupported'), reply_markup=back_btn(c))
            return
        os.unlink(path)
        if not content.strip():
            bot.send_message(c, txt(c,'cv_error_file'), reply_markup=back_btn(c))
            return
        bot.send_chat_action(c, 'typing')
        system_key = 'cv_system' if state == 'CV' else 'jd_system'
        resp = call_ai(txt(c, system_key), content)
        safe_send(c, resp, reply_markup=back_btn(c))
        user_states[c] = None
    except Exception as e:
        import traceback; traceback.print_exc()
        bot.send_message(c, f"Error: {e}", reply_markup=back_btn(c))

# ── text messages ──
@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    c     = message.chat.id
    state = user_states.get(c)
    try:
        bot.send_chat_action(c, 'typing')

        if state == 'INTERVIEW':
            user_histories[c].append({"role":"user","content":message.text})
            resp = call_ai_history(user_histories[c])
            user_histories[c].append({"role":"assistant","content":resp})
            safe_send(c, resp, reply_markup=back_btn(c))

        elif state == 'TASK':
            resp = call_ai(txt(c,'task_system'), message.text)
            safe_send(c, resp, reply_markup=back_btn(c))
            user_states[c] = None

        elif state == 'CV':
            resp = call_ai(txt(c,'cv_system'), message.text)
            safe_send(c, resp, reply_markup=back_btn(c))
            user_states[c] = None

        elif state == 'JD':
            bot.send_message(c, txt(c,'jd_processing'))
            resp = call_ai(txt(c,'jd_system'), message.text)
            safe_send(c, resp, reply_markup=back_btn(c))
            user_states[c] = None

        elif state == 'LEET_SOLVING':
            bot.send_message(c, txt(c,'leetcode_thinking'))
            q    = user_leet_question.get(c, "")
            resp = call_ai(txt(c,'leetcode_review_system'), f"Question:\n{q}\n\nSolution:\n{message.text}")
            safe_send(c, resp, reply_markup=leetcode_btns(c))

        elif state == 'PYTHON_EXERCISE':
            topic = user_python_topic.get(c, "Python")
            resp  = call_ai(txt(c,'python_review_system'), f"Topic: {topic}\n\nStudent solution:\n{message.text}")
            safe_send(c, resp, reply_markup=python_after_btns(c))
            user_states[c] = None

        elif state == 'SYSDESIGN':
            bot.send_message(c, txt(c,'sysdesign_thinking'))
            user_histories[c].append({"role":"user","content":message.text})
            resp = call_ai_history(user_histories[c])
            user_histories[c].append({"role":"assistant","content":resp})
            safe_send(c, resp, reply_markup=back_btn(c))

        else:
            resp = call_ai(txt(c,'general_system'), message.text)
            safe_send(c, resp, reply_markup=back_btn(c))

    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(c, f"Error: {e}", reply_markup=back_btn(c))

print("🤖 Hiring Hero Bot is running...")
bot.infinity_polling()
