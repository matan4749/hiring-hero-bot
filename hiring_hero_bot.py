import telebot, os, requests, tempfile, random, string, time, threading
from telebot import types
from groq import Groq

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
GROQ_API_KEY   = os.environ.get('GROQ_API_KEY', '')

bot    = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# ═══════════════════════════════════════════════════════════════════════════
#  DESIGN CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════
COLORS  = ["🟥", "🟦", "🟩", "🟨"]
SHAPES  = ["▲",  "●",  "■",  "★"]
DIV     = "━━━━━━━━━━━━━━━━━━━"

# ═══════════════════════════════════════════════════════════════════════════
#  PYTHON QUIZ BANK
# ═══════════════════════════════════════════════════════════════════════════
ALL_QUESTIONS = [
    {'q':'🐍 What is the output of `type(3.0)`?',
     'options':["<class 'int'>","<class 'float'>","<class 'str'>","<class 'number'>"],'answer':1,
     'tip':'3.0 has a decimal point → float.'},
    {'q':'🐍 Which is a valid variable name?',
     'options':['2name','my-var','_my_var','my var'],'answer':2,
     'tip':'Names can start with _ or a letter, not a digit or hyphen.'},
    {'q':'🐍 What type is `True`?',
     'options':['str','int','bool','NoneType'],'answer':2,
     'tip':'True and False are Python booleans (bool).'},
    {'q':'🐍 What does `int("7")` return?',
     'options':['Error','7 (int)','7 (str)','0.7'],'answer':1,
     'tip':'int() converts a string to an integer.'},
    {'q':'🐍 What does `[1,2,3][-1]` return?',
     'options':['1','2','3','Error'],'answer':2,
     'tip':'Negative index -1 returns the last element.'},
    {'q':'🐍 How to add a key to a dict?',
     'options':['d.add("k",1)','d["k"]=1','d.insert("k",1)','d.put("k",1)'],'answer':1,
     'tip':'Use d["key"] = value to add or update.'},
    {'q':'🐍 Which method removes the last list item?',
     'options':['remove()','delete()','pop()','discard()'],'answer':2,
     'tip':'list.pop() removes and returns the last item.'},
    {'q':'🐍 How to get all dict keys?',
     'options':['d.values()','d.keys()','d.items()','d.all()'],'answer':1,
     'tip':'d.keys() returns a view of all keys.'},
    {'q':'🐍 What does `*args` do?',
     'options':['Multiplies args','Keyword args only','Positional args (any number)','Makes args optional'],'answer':2,
     'tip':'*args collects extra positional arguments into a tuple.'},
    {'q':'🐍 What is a lambda?',
     'options':['A loop','An anonymous function','A class method','A module'],'answer':1,
     'tip':'lambda x: x+1 is a one-line anonymous function.'},
    {'q':'🐍 What does `return` do without a value?',
     'options':['Returns 0','Returns None','Raises error','Returns False'],'answer':1,
     'tip':'A bare return statement returns None.'},
    {'q':'🐍 What is a default argument?',
     'options':["Always required","Value used if arg not passed","A global var","Keyword-only arg"],'answer':1,
     'tip':'def greet(name="World") — name defaults to "World".'},
    {'q':'🐍 What is `self` in a class method?',
     'options':['The class itself','The current instance','A global variable','A built-in'],'answer':1,
     'tip':'self refers to the current object instance.'},
    {'q':'🐍 Which keyword is used for inheritance?',
     'options':['extends','inherits','class Child(Parent):','super'],'answer':2,
     'tip':'class Dog(Animal): — parent goes in parentheses.'},
    {'q':'🐍 What is `__init__`?',
     'options':['A destructor','A constructor','A class variable','A static method'],'answer':1,
     'tip':'__init__ is called when a new object is created.'},
    {'q':'🐍 What does `@staticmethod` mean?',
     'options':["Needs self","Belongs to class, not instance","Method is private","Method is async"],'answer':1,
     'tip':"Static methods don't receive self."},
    {'q':'🐍 Which block always runs?',
     'options':['try','except','else','finally'],'answer':3,
     'tip':'finally always executes, with or without an exception.'},
    {'q':'🐍 How to raise a custom error?',
     'options':['error("msg")','throw Error("msg")','raise ValueError("msg")','except Error("msg")'],'answer':2,
     'tip':'Use raise ExceptionType("message") to raise an exception.'},
    {'q':'🐍 What exception for wrong dict key?',
     'options':['ValueError','IndexError','KeyError','TypeError'],'answer':2,
     'tip':'d["missing"] → KeyError if the key does not exist.'},
    {'q':'🐍 What exception for dividing by zero?',
     'options':['ValueError','ZeroDivisionError','MathError','OverflowError'],'answer':1,
     'tip':'1/0 raises ZeroDivisionError.'},
    {'q':'🐍 What does a decorator do?',
     'options':['Adds CSS','Wraps function to extend behavior','Creates a class','Imports a module'],'answer':1,
     'tip':'@decorator wraps a function, adding behavior before/after.'},
    {'q':'🐍 `@property` lets you...',
     'options':['Define a static method','Access method like attribute','Create class variable','Override __init__'],'answer':1,
     'tip':'@property lets you call obj.name instead of obj.name().'},
]

# ═══════════════════════════════════════════════════════════════════════════
#  SYSTEM DESIGN BANK
# ═══════════════════════════════════════════════════════════════════════════
SD_QUESTIONS = {
    'WhatsApp / Chat': [
        {'q':'🏗️ 10M messages/sec — what handles the load?',
         'options':['Single DB','Message Queue (Kafka)','More RAM','Bigger server'],'answer':1,
         'tip':'Message Queue decouples producers/consumers and handles massive throughput.'},
        {'q':'🏗️ Store chat history for 2B users?',
         'options':['One MySQL','NoSQL + sharding (Cassandra)','Files on disk','Redis only'],'answer':1,
         'tip':'Cassandra scales horizontally, optimized for time-series message data.'},
        {'q':'🏗️ How to detect if a user is online?',
         'options':['Poll DB every second','WebSocket heartbeat + Redis TTL','SMS ping','Email check'],'answer':1,
         'tip':'WebSocket keeps persistent connection; Redis TTL expires if heartbeat stops.'},
    ],
    'URL Shortener': [
        {'q':'🏗️ How to generate a unique short code?',
         'options':['Random number','Base62 of auto-increment ID','MD5 hash','UUID'],'answer':1,
         'tip':'Base62 gives 56B combos from a 6-char code.'},
        {'q':'🏗️ 100M redirects/day — where to cache?',
         'options':['MySQL','Redis (in-memory)','Hard disk','CDN only'],'answer':1,
         'tip':'Redis stores key-value pairs in memory — sub-millisecond lookups.'},
        {'q':'🏗️ Same URL submitted twice?',
         'options':['Two short URLs','Return same short URL','Return error','Ask the user'],'answer':1,
         'tip':'Check if URL exists first — return existing short code (idempotent).'},
    ],
    'Instagram / Feed': [
        {'q':'🏗️ User uploads photo — what processes it?',
         'options':['Sync API call','Async worker + S3','Store in MySQL','Email it'],'answer':1,
         'tip':'Async workers process/resize; S3 stores originals.'},
        {'q':'🏗️ Generate feed for 500M users?',
         'options':['Query DB on every load','Pre-compute in Redis (fan-out)','Send emails','GraphQL only'],'answer':1,
         'tip':'Fan-out on write: push new posts to followers caches when posted.'},
        {'q':'🏗️ Images load slowly in Brazil — what to add?',
         'options':['Bigger US server','CDN (CloudFront)','Compress to 1px','Nothing'],'answer':1,
         'tip':'CDN caches static content at edge locations near users globally.'},
    ],
    'YouTube / Video': [
        {'q':'🏗️ Serve 4K video at multiple qualities?',
         'options':['Send original to all','Transcode async (360p/720p/1080p)','Compress to 240p','Stream raw bytes'],'answer':1,
         'tip':'Async transcoding creates multiple resolutions; client picks by bandwidth.'},
        {'q':'🏗️ Video has 1B views — store count efficiently?',
         'options':['UPDATE in MySQL per view','Redis counter + batch flush','Count from logs','Ignore'],'answer':1,
         'tip':'Redis INCR is atomic and fast; batch-flush to DB periodically.'},
    ],
    'Uber / Ride': [
        {'q':'🏗️ Match rider to nearest driver?',
         'options':['Loop all drivers','Geospatial index (Redis GEO)','Call each driver','Random pick'],'answer':1,
         'tip':'Redis GEO stores coordinates and finds nearest in O(log n).'},
        {'q':'🏗️ 1M drivers updating location every 5 sec?',
         'options':['Write to MySQL each update','Write to Redis, async flush','Ignore old locations','Use cookies'],'answer':1,
         'tip':'Redis handles millions of writes/sec; async workers persist to DB in batches.'},
    ],
}

# ═══════════════════════════════════════════════════════════════════════════
#  INTERVIEW QUESTIONS
# ═══════════════════════════════════════════════════════════════════════════
INTERVIEW_QUESTIONS = [
    {'q':'🎙️ Difference between `==` and `===` in JavaScript?',
     'options':['== value only (loose)','=== value AND type (strict)','Same thing','== strings only'],'correct':[0,1],
     'tip':'== coerces types (1=="1" true); === does not. Always prefer ===.'},
    {'q':'🎙️ What is Big O notation?',
     'options':['Code quality grade','Algorithm time/space complexity','A sorting algorithm','A DB query language'],'correct':[1],
     'tip':'Big O describes how runtime/memory grows with input size.'},
    {'q':'🎙️ Difference between process and thread?',
     'options':['Process has own memory; threads share','Threads are slower','Process is part of thread','Identical'],'correct':[0],
     'tip':'Processes are isolated; threads share memory and are lighter.'},
    {'q':'🎙️ What is REST?',
     'options':['A language','HTTP-based API architecture','A DB type','A JS framework'],'correct':[1],
     'tip':'REST uses HTTP verbs (GET/POST/PUT/DELETE) and stateless requests.'},
    {'q':'🎙️ What is a deadlock?',
     'options':['Server crash','Two processes waiting for each other forever','A sorting bug','Memory full'],'correct':[1],
     'tip':'Process A waits for B, B waits for A — neither can proceed.'},
    {'q':'🎙️ SQL vs NoSQL?',
     'options':['SQL is newer','SQL relational; NoSQL flexible/scalable','NoSQL uses tables','Same thing'],'correct':[1],
     'tip':'SQL: strict schema, ACID. NoSQL: flexible schema, horizontal scale.'},
    {'q':'🎙️ What is a closure?',
     'options':['Closes a file','Function remembering outer scope','A type of loop','Class destructor'],'correct':[1],
     'tip':'A closure keeps outer variables alive after the outer function returns.'},
    {'q':'🎙️ What is the CAP theorem?',
     'options':['CPU, API, Partition','Consistency, Availability, Partition — pick 2','Cache, Auth, Perf','A Python lib'],'correct':[1],
     'tip':'Distributed systems can guarantee only 2 of 3: C, A, P.'},
]

# ═══════════════════════════════════════════════════════════════════════════
#  MULTIPLAYER ROOMS
# ═══════════════════════════════════════════════════════════════════════════
game_rooms   = {}
player_rooms = {}

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def get_display_name(chat_id):
    try:
        info = bot.get_chat(chat_id)
        name = (info.first_name or '') + (' ' + info.last_name if info.last_name else '')
        return name.strip() or f'Player_{str(chat_id)[-4:]}'
    except Exception:
        return f'Player_{str(chat_id)[-4:]}'

def rank_emoji(i):
    medals = ['🥇','🥈','🥉','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
    return medals[i] if i < len(medals) else f'{i+1}.'

def title_for_score(score, total):
    pct = score / total if total else 0
    if pct == 1.0: return '🏆 LEGEND'
    if pct >= 0.8: return '🔥 PRO'
    if pct >= 0.6: return '💪 Rising Star'
    if pct >= 0.4: return '📈 Getting There'
    return '📚 Keep Learning'

def score_bar(score, total):
    filled = round((score / total) * 10) if total else 0
    return '█' * filled + '░' * (10 - filled)

def broadcast_room(code, text, markup=None, exclude=None):
    room = game_rooms.get(code)
    if not room: return
    for cid in list(room['players']):
        if exclude and cid == exclude: continue
        try:
            bot.send_message(cid, text, parse_mode="Markdown", reply_markup=markup)
        except Exception:
            pass

def question_markup(options, prefix, code=None, solo=False):
    """Colored A/B/C/D buttons + optional quit/leave."""
    m = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton(
            f"{COLORS[i]} {SHAPES[i]}  {opt[:22]}",
            callback_data=f"{prefix}:{i}"
        ) for i, opt in enumerate(options)
    ]
    m.add(*btns)
    if solo:
        m.add(types.InlineKeyboardButton("🚪 Quit", callback_data='solo_quit'))
    elif code:
        m.add(types.InlineKeyboardButton("🚪 Leave Game", callback_data=f'game_leave:{code}'))
    return m

def send_leaderboard_msg(code):
    room = game_rooms.get(code)
    if not room: return
    players = sorted(room['players'].items(), key=lambda x: -x[1]['score'])
    q_done  = room['q_idx']
    lines   = [f"📊 *{DIV}*\n*Leaderboard — Q{q_done}*\n*{DIV}*\n"]
    for i, (cid, p) in enumerate(players):
        lines.append(f"{rank_emoji(i)} *{p['name']}*\n`{score_bar(p['score'], q_done)}` {p['score']} pts\n")
    broadcast_room(code, '\n'.join(lines))

def timer_bar(secs, total=30):
    """Color progress bar: green → yellow → red."""
    filled = round((secs / total) * 15)
    empty  = 15 - filled
    if secs > 20:   color = "🟩"
    elif secs > 8:  color = "🟨"
    else:           color = "🟥"
    bar = color * filled + "⬜" * empty
    return f"{bar} *{secs}s*"

def send_game_question(code):
    room = game_rooms.get(code)
    if not room: return
    idx  = room['q_idx']
    qs   = room['questions']
    if idx >= len(qs):
        end_game(code)
        return
    q     = qs[idx]
    total = len(qs)
    room['answered_this_round'] = set()
    room['timer_active']        = True
    room['timer_msg_ids']       = {}  # cid -> msg_id

    m = question_markup(q['options'], f'game_ans:{code}', code=code)
    broadcast_room(code,
        f"*{DIV}*\n"
        f"🎮 *Q{idx+1} / {total}*\n"
        f"*{DIV}*\n\n"
        f"{q['q']}",
        markup=m)

    # Send timer message separately (so we can edit it)
    time.sleep(0.3)
    for cid in list(room['players']):
        try:
            msg = bot.send_message(cid, timer_bar(30), parse_mode="Markdown")
            room['timer_msg_ids'][cid] = msg.message_id
        except Exception:
            pass

    def live_timer():
        for secs in range(29, 0, -1):
            time.sleep(1)
            r = game_rooms.get(code)
            if not r or not r.get('timer_active') or r['q_idx'] != idx: return
            bar_text = timer_bar(secs)
            for cid, mid in list(r.get('timer_msg_ids', {}).items()):
                try:
                    bot.edit_message_text(bar_text, cid, mid, parse_mode="Markdown")
                except Exception:
                    pass

        # Time's up
        r = game_rooms.get(code)
        if not r or not r.get('timer_active') or r['q_idx'] != idx: return
        for cid, mid in list(r.get('timer_msg_ids', {}).items()):
            try:
                bot.edit_message_text("🔴 *TIME'S UP!*", cid, mid, parse_mode="Markdown")
            except Exception:
                pass
        missed = [p['name'] for cid, p in r['players'].items() if cid not in r['answered_this_round']]
        if missed:
            broadcast_room(code, f"⏰ No answer from: _{', '.join(missed)}_")
        r['q_idx']       += 1
        r['timer_active']  = False
        time.sleep(1)
        send_leaderboard_msg(code)
        time.sleep(2)
        send_game_question(code)

    threading.Thread(target=live_timer, daemon=True).start()

def end_game(code):
    room = game_rooms.get(code)
    if not room: return
    room['active'] = False
    players = sorted(room['players'].items(), key=lambda x: -x[1]['score'])
    total   = len(room['questions'])

    lines = [
        f"🏁 *{DIV}*",
        f"*      🎊 GAME OVER 🎊*",
        f"*{DIV}*\n",
    ]

    # Podium top 3
    podium_icons = ['🥇', '🥈', '🥉']
    lines.append("*🏆 Podium:*")
    for i, (cid, p) in enumerate(players[:3]):
        lines.append(f"{podium_icons[i]} *{p['name']}* — {p['score']} pts")
    lines.append("")

    # Full standings
    lines.append(f"*📋 Full Rankings:*\n")
    for i, (cid, p) in enumerate(players):
        t = title_for_score(p['score'], total)
        lines.append(
            f"{rank_emoji(i)} *{p['name']}*  _{t}_\n"
            f"`{score_bar(p['score'], total)}` {p['score']}/{total}\n"
        )

    if players:
        lines.append(f"🎊 *Congrats {players[0][1]['name']}!* 🎊")

    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("🔄 Play Again", callback_data='python_create'),
        types.InlineKeyboardButton("🏠 Menu",       callback_data='menu'),
    )
    broadcast_room(code, '\n'.join(lines), markup=m)
    for cid in list(room['players']):
        player_rooms.pop(cid, None)
        user_states.pop(cid, None)
    game_rooms.pop(code, None)

# ═══════════════════════════════════════════════════════════════════════════
#  STATE
# ═══════════════════════════════════════════════════════════════════════════
user_states   = {}
user_langs    = {}
user_sessions = {}

def get_lang(c): return user_langs.get(c, 'en')

def call_ai(system, user, temp=0.6):
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=temp,
    )
    return r.choices[0].message.content

def safe_send(c, text, reply_markup=None):
    try:
        bot.send_message(c, text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception:
        bot.send_message(c,
            text.replace("*","").replace("_","").replace("`",""),
            reply_markup=reply_markup)

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

# ═══════════════════════════════════════════════════════════════════════════
#  MENUS
# ═══════════════════════════════════════════════════════════════════════════
def main_menu(c):
    lang = get_lang(c)
    m = types.InlineKeyboardMarkup(row_width=2)
    if lang == 'he':
        m.add(
            types.InlineKeyboardButton("🎙️ ראיון דמה",    callback_data='interview'),
            types.InlineKeyboardButton("🐍 Python Trivia", callback_data='python_menu'),
            types.InlineKeyboardButton("🏗️ System Design", callback_data='sysdesign'),
            types.InlineKeyboardButton("🧩 LeetCode",      callback_data='leetcode'),
            types.InlineKeyboardButton("📄 ניתוח CV",      callback_data='cv'),
            types.InlineKeyboardButton("🔍 מנתח JD",       callback_data='jd'),
        )
        m.row(
            types.InlineKeyboardButton("🌐 English", callback_data='lang'),
            types.InlineKeyboardButton("ℹ️ אודות",   callback_data='about'),
        )
    else:
        m.add(
            types.InlineKeyboardButton("🎙️ Mock Interview", callback_data='interview'),
            types.InlineKeyboardButton("🐍 Python Trivia",  callback_data='python_menu'),
            types.InlineKeyboardButton("🏗️ System Design",  callback_data='sysdesign'),
            types.InlineKeyboardButton("🧩 LeetCode",       callback_data='leetcode'),
            types.InlineKeyboardButton("📄 CV Analysis",    callback_data='cv'),
            types.InlineKeyboardButton("🔍 JD Analyzer",    callback_data='jd'),
        )
        m.row(
            types.InlineKeyboardButton("🌐 עברית",  callback_data='lang'),
            types.InlineKeyboardButton("ℹ️ About",  callback_data='about'),
        )
    return m

def back_btn():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🏠 Menu", callback_data='menu'))
    return m

def python_mode_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("👤 Solo — Practice alone",   callback_data='python_solo'),
        types.InlineKeyboardButton("🎮 Create Multiplayer Game", callback_data='python_create'),
        types.InlineKeyboardButton("🔗 Join a Game",             callback_data='python_join'),
        types.InlineKeyboardButton("◀️ Back",                    callback_data='menu'),
    )
    return m

def player_count_menu():
    m = types.InlineKeyboardMarkup(row_width=5)
    btns = [types.InlineKeyboardButton(str(i), callback_data=f'game_setplayers:{i}') for i in range(2, 11)]
    m.add(*btns)
    m.add(types.InlineKeyboardButton("◀️ Back", callback_data='python_menu'))
    return m

def sd_topic_menu():
    m = types.InlineKeyboardMarkup(row_width=2)
    for name in SD_QUESTIONS:
        m.add(types.InlineKeyboardButton(name, callback_data=f"sd_topic:{name}"))
    m.add(types.InlineKeyboardButton("◀️ Back", callback_data='menu'))
    return m

# ═══════════════════════════════════════════════════════════════════════════
#  SOLO QUESTION SENDERS (with timer)
# ═══════════════════════════════════════════════════════════════════════════
def send_solo_question(c):
    s   = user_sessions.get(c)
    if not s: return
    idx = s['q_idx']
    qs  = s['questions']
    if idx >= len(qs):
        score = s['score']
        total = len(qs)
        t     = title_for_score(score, total)
        bot.send_message(c,
            f"*{DIV}*\n"
            f"✅ *Quiz Complete!*\n"
            f"*{DIV}*\n\n"
            f"Score: *{score} / {total}*\n"
            f"`{score_bar(score, total)}`\n\n"
            f"*{t}* 🎓",
            parse_mode="Markdown", reply_markup=back_btn())
        user_states[c] = None
        return
    q = qs[idx]
    m = question_markup(q['options'], 'solo_ans', solo=True)
    bot.send_message(c,
        f"*{DIV}*\n"
        f"🐍 *Q{idx+1} / {len(qs)}*\n"
        f"*{DIV}*\n\n"
        f"{q['q']}",
        parse_mode="Markdown", reply_markup=m)

    # Live timer message
    try:
        timer_msg = bot.send_message(c, timer_bar(30), parse_mode="Markdown")
        timer_mid = timer_msg.message_id
    except Exception:
        timer_mid = None

    def solo_timer(q_idx):
        for secs in range(29, 0, -1):
            time.sleep(1)
            if user_states.get(c) != 'SOLO': return
            sess = user_sessions.get(c)
            if not sess or sess['q_idx'] != q_idx: return
            if timer_mid:
                try:
                    bot.edit_message_text(timer_bar(secs), c, timer_mid, parse_mode="Markdown")
                except Exception:
                    pass
        if user_states.get(c) != 'SOLO': return
        sess = user_sessions.get(c)
        if not sess or sess['q_idx'] != q_idx: return
        if timer_mid:
            try:
                bot.edit_message_text("🔴 *TIME'S UP!*", c, timer_mid, parse_mode="Markdown")
            except Exception:
                pass
        bot.send_message(c, "⏰ *Time's up!* Moving on...", parse_mode="Markdown")
        sess['q_idx'] += 1
        time.sleep(0.5)
        send_solo_question(c)
    threading.Thread(target=solo_timer, args=(idx,), daemon=True).start()

def send_sd_question(c):
    s   = user_sessions.get(c)
    if not s: return
    idx = s['q_idx']
    qs  = SD_QUESTIONS.get(s['topic'], [])
    if idx >= len(qs):
        score = s['score']
        total = len(qs)
        bot.send_message(c,
            f"🏗️ *Done!* {score}/{total} — {title_for_score(score, total)}",
            parse_mode="Markdown", reply_markup=back_btn())
        user_states[c] = None
        return
    q = qs[idx]
    m = question_markup(q['options'], 'sd_ans', solo=True)
    bot.send_message(c,
        f"*{DIV}*\n🏗️ *Q{idx+1} / {len(qs)}*\n*{DIV}*\n\n{q['q']}",
        parse_mode="Markdown", reply_markup=m)

def send_interview_question(c):
    s   = user_sessions.get(c)
    if not s: return
    idx = s['q_idx']
    if idx >= len(INTERVIEW_QUESTIONS):
        score = s['score']
        total = len(INTERVIEW_QUESTIONS)
        bot.send_message(c,
            f"🎙️ *Interview Done!* {score}/{total} — {title_for_score(score, total)}",
            parse_mode="Markdown", reply_markup=back_btn())
        user_states[c] = None
        return
    q = INTERVIEW_QUESTIONS[idx]
    m = question_markup(q['options'], 'iv_ans', solo=True)
    bot.send_message(c,
        f"*{DIV}*\n🎙️ *Q{idx+1} / {len(INTERVIEW_QUESTIONS)}*\n*{DIV}*\n\n{q['q']}",
        parse_mode="Markdown", reply_markup=m)

# ═══════════════════════════════════════════════════════════════════════════
#  COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    c = message.chat.id
    user_states[c] = None
    player_rooms.pop(c, None)
    lang = get_lang(c)
    txt = (
        f"⚡ *ברוך הבא ל-DevBoost Career Coach!*\n\n"
        f"הבוט שיהפוך אותך למפתח שכל חברה רוצה לגייס 🚀\n\n"
        f"_בחר מה תרצה לעשות:_"
        if lang == 'he' else
        f"⚡ *Welcome to DevBoost Career Coach!*\n\n"
        f"The AI bot that turns you into a developer every company wants to hire 🚀\n\n"
        f"_Choose what you'd like to do:_"
    )
    bot.send_message(c, txt, parse_mode="Markdown", reply_markup=main_menu(c))

# ═══════════════════════════════════════════════════════════════════════════
#  CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    c    = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    # ── Menu ──
    if data == 'menu':
        user_states[c] = None
        lang = get_lang(c)
        txt = "_בחר מה תרצה לעשות:_" if lang == 'he' else "_Choose what you'd like to do:_"
        bot.send_message(c, txt, parse_mode="Markdown", reply_markup=main_menu(c))
        return

    # ── Language ──
    if data == 'lang':
        user_langs[c] = 'he' if get_lang(c) == 'en' else 'en'
        lang = get_lang(c)
        txt = "🌐 *שפה שונתה לעברית* ✅" if lang == 'he' else "🌐 *Language set to English* ✅"
        bot.send_message(c, txt, parse_mode="Markdown", reply_markup=main_menu(c))
        return

    # ── About ──
    if data == 'about':
        lang = get_lang(c)
        if lang == 'he':
            txt = (
                f"⚡ *DevBoost Career Coach*\n"
                f"*{DIV}*\n\n"
                f"🎓 נבנה על ידי *מתן וחננאל*\n"
                f"במסגרת קורס *DevBoost*\n\n"
                f"*הפיצ'רים שלנו:*\n"
                f"🎙️ ראיון דמה עם AI\n"
                f"🐍 Python Trivia — Solo & Multiplayer\n"
                f"🏗️ System Design Quiz\n"
                f"🧩 LeetCode Daily (Easy)\n"
                f"📄 ניתוח CV + ניקוד ATS\n"
                f"🔍 מנתח משרות (JD)\n\n"
                f"_Built with ❤️ — Python · Telegram API · Groq AI_"
            )
        else:
            txt = (
                f"⚡ *DevBoost Career Coach*\n"
                f"*{DIV}*\n\n"
                f"🎓 Built by *Matan & Hananel*\n"
                f"as part of the *DevBoost Course*\n\n"
                f"*Features:*\n"
                f"🎙️ AI Mock Interviews\n"
                f"🐍 Python Trivia — Solo & Multiplayer\n"
                f"🏗️ System Design Quiz\n"
                f"🧩 LeetCode Daily (Easy)\n"
                f"📄 CV Analysis + ATS Score\n"
                f"🔍 Job Description Analyzer\n\n"
                f"_Built with ❤️ — Python · Telegram API · Groq AI_"
            )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(types.InlineKeyboardButton("◀️ Back", callback_data='menu'))
        bot.send_message(c, txt, parse_mode="Markdown", reply_markup=m)
        return

    # ════════════════════════════════════════════════════
    #  PYTHON TRIVIA
    # ════════════════════════════════════════════════════
    if data == 'python_menu':
        bot.send_message(c,
            f"*{DIV}*\n🐍 *Python Trivia*\n*{DIV}*\n\nChoose your mode:",
            parse_mode="Markdown", reply_markup=python_mode_menu())
        return
    # ── Solo ──
    if data == 'python_solo':
        qs = random.sample(ALL_QUESTIONS, min(10, len(ALL_QUESTIONS)))
        user_sessions[c] = {'questions': qs, 'q_idx': 0, 'score': 0}
        user_states[c]   = 'SOLO'
        bot.send_message(c,
            "🐍 *Solo Mode!* 10 random questions.\n⏱ 30 seconds per question.\n\nLet's go! 🚀",
            parse_mode="Markdown")
        send_solo_question(c)
        return

    if data == 'solo_quit':
        user_states[c] = None
        bot.send_message(c, "👋 *Quiz stopped.* See you next time!", parse_mode="Markdown",
                         reply_markup=back_btn())
        return

    if data.startswith('solo_ans:'):
        if user_states.get(c) != 'SOLO': return
        chosen = int(data.split(':')[1])
        s = user_sessions.get(c)
        if not s: return
        q = s['questions'][s['q_idx']]
        if chosen == q['answer']:
            s['score'] += 1
            bot.send_message(c,
                f"✅ *Correct!* +1 🎉\n_{q['tip']}_",
                parse_mode="Markdown")
        else:
            bot.send_message(c,
                f"❌ *Wrong!*\n"
                f"You chose: {COLORS[chosen]} {SHAPES[chosen]}\n"
                f"Correct: {COLORS[q['answer']]} {SHAPES[q['answer']]} _{q['options'][q['answer']]}_\n\n"
                f"_{q['tip']}_",
                parse_mode="Markdown")
        s['q_idx'] += 1
        time.sleep(0.4)
        send_solo_question(c)
        return

    # ── Create Multiplayer ──
    if data == 'python_create':
        existing = player_rooms.get(c)
        if existing and existing in game_rooms:
            m = types.InlineKeyboardMarkup()
            m.add(types.InlineKeyboardButton("🚪 Leave Current Game", callback_data=f'game_leave:{existing}'))
            bot.send_message(c, "⚠️ You're already in a game! Leave first.", reply_markup=m)
            return
        bot.send_message(c,
            f"*{DIV}*\n🎮 *Create a Game*\n*{DIV}*\n\n"
            f"How many players? _(including you)_\n"
            f"Game *auto-starts* when all join!",
            parse_mode="Markdown", reply_markup=player_count_menu())
        return

    if data.startswith('game_setplayers:'):
        max_p = int(data.split(':')[1])
        code  = gen_code()
        name  = get_display_name(c)
        qs    = random.sample(ALL_QUESTIONS, min(10, len(ALL_QUESTIONS)))
        game_rooms[code] = {
            'host': c,
            'players': {c: {'name': name, 'score': 0, 'answered': 0}},
            'questions': qs,
            'q_idx': 0,
            'active': False,
            'answered_this_round': set(),
            'max_players': max_p,
            'timer_active': False,
        }
        player_rooms[c] = code
        user_states[c]  = 'GAME_LOBBY'
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("🚀 Start Now!",  callback_data=f'game_start:{code}'))
        m.add(types.InlineKeyboardButton("🛑 Cancel Game", callback_data='game_cancel'))
        bot.send_message(c,
            f"🎮 *Game Created!*\n\n"
            f"┌─────────────────────┐\n"
            f"│   🎯 Code:  *{code}*    │\n"
            f"└─────────────────────┘\n\n"
            f"👥 Waiting for *{max_p}* players...\n"
            f"🟢 Joined: *1 / {max_p}* _(you)_\n\n"
            f"📲 Share the code!\n"
            f"Game auto-starts when {max_p} players join.",
            parse_mode="Markdown", reply_markup=m)
        return

    if data.startswith('game_start:'):
        code = data.split(':')[1]
        room = game_rooms.get(code)
        if not room or room['host'] != c: return
        room['active'] = True
        n     = len(room['players'])
        names = ', '.join(p['name'] for p in room['players'].values())
        broadcast_room(code,
            f"🚀 *Game Starts Now!*\n"
            f"👥 *{n} players:* _{names}_\n\n"
            f"10 questions — Good luck! 🍀")
        time.sleep(1)
        threading.Thread(target=send_game_question, args=(code,), daemon=True).start()
        return

    if data == 'game_cancel':
        code = player_rooms.get(c)
        if code and game_rooms.get(code, {}).get('host') == c:
            broadcast_room(code, "🛑 *Game cancelled by host.*", exclude=c)
            for cid in list(game_rooms[code]['players']):
                player_rooms.pop(cid, None)
                user_states.pop(cid, None)
            game_rooms.pop(code, None)
        user_states[c] = None
        bot.send_message(c, "Cancelled.", reply_markup=back_btn())
        return

    # ── Leave Game ──
    if data.startswith('game_leave:'):
        code = data.split(':')[1]
        room = game_rooms.get(code)
        if room and c in room['players']:
            name = room['players'][c]['name']
            del room['players'][c]
            player_rooms.pop(c, None)
            user_states[c] = None
            bot.send_message(c,
                "👋 *You left the game.*\nSee you next time!",
                parse_mode="Markdown", reply_markup=back_btn())
            if room['players']:
                broadcast_room(code,
                    f"⚠️ *{name}* left. ({len(room['players'])} players remaining)")
                if room['host'] == c:
                    new_host     = next(iter(room['players']))
                    room['host'] = new_host
                    bot.send_message(new_host, "👑 *You are now the host!*", parse_mode="Markdown")
            else:
                game_rooms.pop(code, None)
        else:
            user_states[c] = None
            bot.send_message(c, "🏠 Back to menu.", reply_markup=back_btn())
        return

    # ── Join Multiplayer ──
    if data == 'python_join':
        user_states[c] = 'JOIN_WAIT'
        bot.send_message(c,
            "🔗 *Enter the 5-character game code:*",
            parse_mode="Markdown")
        return

    # ── Game Answer ──
    if data.startswith('game_ans:'):
        parts  = data.split(':')
        code   = parts[1]
        chosen = int(parts[2])
        room   = game_rooms.get(code)
        if not room or not room['active']: return
        if c not in room['players']: return
        if c in room['answered_this_round']:
            bot.answer_callback_query(call.id, "⏳ Already answered!")
            return
        room['answered_this_round'].add(c)
        q      = room['questions'][room['q_idx']]
        player = room['players'][c]
        player['answered'] += 1
        if chosen == q['answer']:
            player['score'] += 1
            bot.send_message(c,
                f"✅ *Correct!* +1 🎉\n_{q['tip']}_",
                parse_mode="Markdown")
        else:
            bot.send_message(c,
                f"❌ *Wrong!*\n"
                f"You: {COLORS[chosen]} {SHAPES[chosen]}\n"
                f"Correct: {COLORS[q['answer']]} {SHAPES[q['answer']]} _{q['options'][q['answer']]}_\n\n"
                f"_{q['tip']}_",
                parse_mode="Markdown")
        if len(room['answered_this_round']) >= len(room['players']):
            room['timer_active'] = False
            room['q_idx']       += 1
            time.sleep(1)
            send_leaderboard_msg(code)
            time.sleep(2)
            threading.Thread(target=send_game_question, args=(code,), daemon=True).start()
        return

    # ════════════════════════════════════════════════════
    #  SYSTEM DESIGN
    # ════════════════════════════════════════════════════
    if data == 'sysdesign':
        bot.send_message(c,
            f"*{DIV}*\n🏗️ *System Design*\n*{DIV}*\n\nChoose a system:",
            parse_mode="Markdown", reply_markup=sd_topic_menu())
        return

    if data.startswith('sd_topic:'):
        topic = data.split(':', 1)[1]
        user_sessions[c] = {'topic': topic, 'q_idx': 0, 'score': 0}
        user_states[c]   = 'SYSDESIGN'
        send_sd_question(c)
        return

    if data.startswith('sd_ans:'):
        if user_states.get(c) != 'SYSDESIGN': return
        chosen = int(data.split(':')[1])
        s = user_sessions.get(c)
        if not s: return
        q = SD_QUESTIONS[s['topic']][s['q_idx']]
        if chosen == q['answer']:
            s['score'] += 1
            bot.send_message(c, f"✅ *Correct!*\n_{q['tip']}_", parse_mode="Markdown")
        else:
            bot.send_message(c,
                f"❌ *Wrong!*\nCorrect: {COLORS[q['answer']]} _{q['options'][q['answer']]}_\n\n_{q['tip']}_",
                parse_mode="Markdown")
        s['q_idx'] += 1
        time.sleep(0.4)
        send_sd_question(c)
        return

    # ════════════════════════════════════════════════════
    #  MOCK INTERVIEW
    # ════════════════════════════════════════════════════
    if data == 'interview':
        user_sessions[c] = {'q_idx': 0, 'score': 0}
        user_states[c]   = 'INTERVIEW'
        bot.send_message(c,
            f"*{DIV}*\n🎙️ *Mock Interview*\n*{DIV}*\n\n8 questions — Tap your answer! 💪",
            parse_mode="Markdown")
        send_interview_question(c)
        return

    if data.startswith('iv_ans:'):
        if user_states.get(c) != 'INTERVIEW': return
        chosen = int(data.split(':')[1])
        s = user_sessions.get(c)
        if not s: return
        q = INTERVIEW_QUESTIONS[s['q_idx']]
        if chosen in q['correct']:
            s['score'] += 1
            bot.send_message(c, f"✅ *Correct!*\n_{q['tip']}_", parse_mode="Markdown")
        else:
            correct_opts = ' / '.join(f"{COLORS[i]} {q['options'][i]}" for i in q['correct'])
            bot.send_message(c,
                f"❌ *Wrong!*\nCorrect: {correct_opts}\n\n_{q['tip']}_",
                parse_mode="Markdown")
        s['q_idx'] += 1
        time.sleep(0.4)
        send_interview_question(c)
        return

    # ════════════════════════════════════════════════════
    #  LEETCODE
    # ════════════════════════════════════════════════════
    if data == 'leetcode':
        bot.send_message(c, "🧩 Generating an Easy LeetCode question...")
        bot.send_chat_action(c, 'typing')
        try:
            system = (
                "You are a LeetCode coach. Give ONE Easy problem. "
                "Mobile-friendly: max 5 lines description, 1 example. "
                "Format:\nProblem: <n>\nDescription: <text>\n"
                "Example: Input: ... Output: ...\n"
                "SOLUTION_PLACEHOLDER\n<Python solution max 10 lines>"
            )
            full = call_ai(system, "Generate an Easy LeetCode problem now.")
            if 'SOLUTION_PLACEHOLDER' in full:
                q, sol = full.split('SOLUTION_PLACEHOLDER', 1)
            else:
                q, sol = full, ""
            user_sessions[c] = {'leet_q': q.strip(), 'leet_sol': sol.strip()}
            user_states[c]   = 'LEET_DONE'
            m = types.InlineKeyboardMarkup(row_width=2)
            m.add(
                types.InlineKeyboardButton("💡 Show Solution", callback_data='leet_sol'),
                types.InlineKeyboardButton("🔄 New Question",  callback_data='leetcode'),
                types.InlineKeyboardButton("🏠 Menu",          callback_data='menu'),
            )
            safe_send(c, q.strip(), reply_markup=m)
        except Exception as e:
            bot.send_message(c, f"❌ Error: {e}", reply_markup=back_btn())
        return

    if data == 'leet_sol':
        sol = user_sessions.get(c, {}).get('leet_sol', 'No solution saved.')
        safe_send(c, f"💡 *Solution:*\n\n{sol}", reply_markup=back_btn())
        user_states[c] = None
        return

    # ════════════════════════════════════════════════════
    #  CV & JD
    # ════════════════════════════════════════════════════
    if data == 'cv':
        user_states[c] = 'CV'
        lang = get_lang(c)
        bot.send_message(c,
            "📄 שלח קורות חיים — טקסט, PDF, או Word.\nאקח לך ניקוד ATS + שיפורים קצרים." if lang == 'he' else
            "📄 Send your CV — text, PDF, or Word.\nI'll give you an ATS score + quick improvements.",
            reply_markup=back_btn())
        return

    if data == 'jd':
        user_states[c] = 'JD'
        lang = get_lang(c)
        bot.send_message(c,
            "🔍 הדבק את תיאור המשרה.\nאחלץ Keywords + טיפים לקו\"ח." if lang == 'he' else
            "🔍 Paste the Job Description.\nI'll extract keywords + CV tips.",
            reply_markup=back_btn())
        return

# ═══════════════════════════════════════════════════════════════════════════
#  DOCUMENT HANDLER
# ═══════════════════════════════════════════════════════════════════════════
@bot.message_handler(content_types=['document'])
def handle_document(message):
    c     = message.chat.id
    state = user_states.get(c)
    if state not in ('CV', 'JD'):
        user_states[c] = 'CV'
        bot.send_message(c, "📄 Send your CV file.", reply_markup=back_btn())
        return
    bot.send_message(c, "⏳ Processing...")
    try:
        path, suffix = download_file(message.document.file_id)
        if suffix == '.pdf':
            content = extract_pdf(path)
        elif suffix in ('.docx', '.doc'):
            content = extract_docx(path)
        else:
            bot.send_message(c, "❌ Send PDF, DOCX, or plain text.", reply_markup=back_btn())
            return
        os.unlink(path)
        if not content.strip():
            bot.send_message(c, "❌ Couldn't read the file.", reply_markup=back_btn())
            return
        _process_cv_or_jd(c, content, state)
    except Exception as e:
        bot.send_message(c, f"❌ Error: {e}", reply_markup=back_btn())

# ═══════════════════════════════════════════════════════════════════════════
#  TEXT HANDLER
# ═══════════════════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    c     = message.chat.id
    state = user_states.get(c)
    text  = message.text.strip()
    try:
        bot.send_chat_action(c, 'typing')

        if state == 'JOIN_WAIT':
            code = text.upper()
            room = game_rooms.get(code)
            if not room:
                bot.send_message(c, "❌ Game not found. Check the code.", reply_markup=back_btn())
                return
            if room['active']:
                bot.send_message(c, "❌ Game already started!", reply_markup=back_btn())
                return
            existing = player_rooms.get(c)
            if existing and existing != code:
                bot.send_message(c, "⚠️ Leave your current game first.")
                return
            name = get_display_name(c)
            room['players'][c] = {'name': name, 'score': 0, 'answered': 0}
            player_rooms[c]    = code
            user_states[c]     = 'GAME_LOBBY'
            n     = len(room['players'])
            max_p = room.get('max_players', 99)
            bot.send_message(c,
                f"✅ *Joined game {code}!*\n👥 {n}/{max_p} players\nWaiting for game to start...",
                parse_mode="Markdown")
            broadcast_room(code, f"👋 *{name}* joined! ({n}/{max_p})", exclude=c)
            if n >= max_p:
                room['active'] = True
                names = ', '.join(p['name'] for p in room['players'].values())
                broadcast_room(code,
                    f"🚀 *{max_p} players joined!*\n👥 _{names}_\n\n🎮 *Game starting NOW!* 🍀")
                time.sleep(1)
                threading.Thread(target=send_game_question, args=(code,), daemon=True).start()
            else:
                host = room['host']
                mu = types.InlineKeyboardMarkup()
                mu.add(types.InlineKeyboardButton("🚀 Start Now!", callback_data=f'game_start:{code}'))
                mu.add(types.InlineKeyboardButton("🛑 Cancel",     callback_data='game_cancel'))
                try:
                    bot.send_message(host,
                        f"👥 *{n}/{max_p}* players joined. {max_p-n} more needed, or start now!",
                        parse_mode="Markdown", reply_markup=mu)
                except Exception:
                    pass
            return

        if state == 'CV':
            _process_cv_or_jd(c, text, 'CV')
        elif state == 'JD':
            _process_cv_or_jd(c, text, 'JD')
        else:
            lang   = get_lang(c)
            system = (
                "אתה מאמן קריירה לתוכנה. ענה בעברית, קצר — מקסימום 5 שורות."
                if lang == 'he' else
                "You are a software engineering career coach. Answer concisely — max 5 lines."
            )
            resp = call_ai(system, text)
            safe_send(c, resp, reply_markup=back_btn())
    except Exception as e:
        bot.send_message(c, f"❌ Error: {e}", reply_markup=back_btn())

def _process_cv_or_jd(c, content, mode):
    lang = get_lang(c)
    if mode == 'CV':
        system = (
            f"You are a CV expert. Be concise and mobile-friendly.\n"
            f"Give:\n1. ATS Score: X/10\n2. Top 3 strengths\n"
            f"3. Top 3 improvements (one line each)\n4. One rewritten bullet example.\n"
            f"Max 20 lines. Answer in {'Hebrew' if lang=='he' else 'English'}."
        )
    else:
        system = (
            f"You are an ATS expert. Be concise and mobile-friendly.\n"
            f"Give:\n1. Top 10 Keywords (comma separated)\n2. Must-haves (3 bullets)\n"
            f"3. Top 3 CV tips for this role.\nMax 20 lines. Answer in {'Hebrew' if lang=='he' else 'English'}."
        )
    bot.send_chat_action(c, 'typing')
    resp = call_ai(system, content)
    safe_send(c, resp, reply_markup=back_btn())
    user_states[c] = None

print("⚡ DevBoost Career Coach is running...")
bot.infinity_polling()
