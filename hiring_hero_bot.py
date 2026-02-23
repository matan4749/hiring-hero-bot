import telebot, os, requests, tempfile, random, string, time
from telebot import types
from groq import Groq

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
GROQ_API_KEY   = os.environ.get('GROQ_API_KEY', '')

bot    = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# ═══════════════════════════════════════════════════════════════════════════
#  PYTHON QUIZ BANK
# ═══════════════════════════════════════════════════════════════════════════
ALL_QUESTIONS = [
    # Variables & Types
    {'q':'🐍 What is the output of `type(3.0)`?',
     'options':["<class 'int'>","<class 'float'>","<class 'str'>","<class 'number'>"],'answer':1,
     'tip':'3.0 has a decimal point → float.','cat':'Variables & Types'},
    {'q':'🐍 Which is a valid variable name?',
     'options':['2name','my-var','_my_var','my var'],'answer':2,
     'tip':'Names can start with _ or a letter, not a digit or hyphen.','cat':'Variables & Types'},
    {'q':'🐍 What type is `True`?',
     'options':['str','int','bool','NoneType'],'answer':2,
     'tip':'True and False are Python booleans (bool).','cat':'Variables & Types'},
    {'q':'🐍 What does `int("7")` return?',
     'options':['Error','7 (int)','7 (str)','0.7'],'answer':1,
     'tip':'int() converts a string to an integer.','cat':'Variables & Types'},
    # Lists & Dicts
    {'q':'🐍 What does `[1,2,3][-1]` return?',
     'options':['1','2','3','Error'],'answer':2,
     'tip':'Negative index -1 returns the last element.','cat':'Lists & Dicts'},
    {'q':'🐍 How to add a key to a dict?',
     'options':['d.add("k",1)','d["k"]=1','d.insert("k",1)','d.put("k",1)'],'answer':1,
     'tip':'Use d["key"] = value to add or update.','cat':'Lists & Dicts'},
    {'q':'🐍 Which method removes the last list item?',
     'options':['remove()','delete()','pop()','discard()'],'answer':2,
     'tip':'list.pop() removes and returns the last item.','cat':'Lists & Dicts'},
    {'q':'🐍 How to get all dict keys?',
     'options':['d.values()','d.keys()','d.items()','d.all()'],'answer':1,
     'tip':'d.keys() returns a view of all keys.','cat':'Lists & Dicts'},
    # Functions
    {'q':'🐍 What does `*args` do?',
     'options':['Multiplies args','Keyword args only','Positional args (any number)','Makes args optional'],'answer':2,
     'tip':'*args collects extra positional arguments into a tuple.','cat':'Functions'},
    {'q':'🐍 What is a lambda?',
     'options':['A loop','An anonymous function','A class method','A module'],'answer':1,
     'tip':'lambda x: x+1 is a one-line anonymous function.','cat':'Functions'},
    {'q':'🐍 What does `return` do without a value?',
     'options':['Returns 0','Returns None','Raises error','Returns False'],'answer':1,
     'tip':'A bare return statement returns None.','cat':'Functions'},
    {'q':'🐍 What is a default argument?',
     'options':['An arg that\'s always required','A value used if arg is not passed','A global variable','A keyword-only arg'],'answer':1,
     'tip':'def greet(name="World") — name defaults to "World".','cat':'Functions'},
    # OOP
    {'q':'🐍 What is `self` in a class method?',
     'options':['The class itself','The current instance','A global variable','A built-in'],'answer':1,
     'tip':'self refers to the current object instance.','cat':'OOP'},
    {'q':'🐍 Which keyword is used for inheritance?',
     'options':['extends','inherits','class Child(Parent):','super'],'answer':2,
     'tip':'class Dog(Animal): — parent goes in parentheses.','cat':'OOP'},
    {'q':'🐍 What is `__init__`?',
     'options':['A destructor','A constructor method','A class variable','A static method'],'answer':1,
     'tip':'__init__ is called when a new object is created.','cat':'OOP'},
    {'q':'🐍 What does `@staticmethod` mean?',
     'options':['Method needs self','Method belongs to class, not instance','Method is private','Method is async'],'answer':1,
     'tip':'Static methods don\'t receive self — they\'re like regular functions inside a class.','cat':'OOP'},
    # Error Handling
    {'q':'🐍 Which block always runs?',
     'options':['try','except','else','finally'],'answer':3,
     'tip':'finally always executes, with or without an exception.','cat':'Error Handling'},
    {'q':'🐍 How to raise a custom error?',
     'options':['error("msg")','throw ValueError("msg")','raise ValueError("msg")','except ValueError("msg")'],'answer':2,
     'tip':'Use raise ExceptionType("message") to raise an exception.','cat':'Error Handling'},
    {'q':'🐍 What exception for wrong key in dict?',
     'options':['ValueError','IndexError','KeyError','TypeError'],'answer':2,
     'tip':'d["missing"] → KeyError if the key doesn\'t exist.','cat':'Error Handling'},
    {'q':'🐍 What exception for dividing by zero?',
     'options':['ValueError','ZeroDivisionError','MathError','OverflowError'],'answer':1,
     'tip':'1/0 raises ZeroDivisionError.','cat':'Error Handling'},
    # Decorators
    {'q':'🐍 What does a decorator do?',
     'options':['Adds CSS','Wraps a function to extend behavior','Creates a class','Imports a module'],'answer':1,
     'tip':'@decorator wraps a function, adding behavior before/after.','cat':'Decorators'},
    {'q':'🐍 `@property` lets you...',
     'options':['Define a static method','Access a method like an attribute','Create a class variable','Override __init__'],'answer':1,
     'tip':'@property lets you call obj.name instead of obj.name().','cat':'Decorators'},
]

# ═══════════════════════════════════════════════════════════════════════════
#  SYSTEM DESIGN BANK
# ═══════════════════════════════════════════════════════════════════════════
SD_QUESTIONS = {
    'WhatsApp / Chat': [
        {'q':'🏗️ 10M messages/sec — what handles the load?',
         'options':['Single DB','Message Queue (Kafka)','More RAM','Bigger server'],'answer':1,
         'tip':'✅ Message Queue decouples producers from consumers and handles massive throughput.'},
        {'q':'🏗️ Store chat history for 2B users?',
         'options':['One MySQL','NoSQL + sharding (Cassandra)','Files on disk','Redis only'],'answer':1,
         'tip':'✅ Cassandra scales horizontally, optimized for time-series message data.'},
        {'q':'🏗️ How to detect if a user is online?',
         'options':['Poll DB every second','WebSocket heartbeat + Redis TTL','SMS ping','Email check'],'answer':1,
         'tip':'✅ WebSocket keeps persistent connection; Redis TTL expires if heartbeat stops.'},
    ],
    'URL Shortener': [
        {'q':'🏗️ How to generate a unique short code?',
         'options':['Random number','Base62 of auto-increment ID','MD5 hash','UUID'],'answer':1,
         'tip':'✅ Base62 gives 56B combos from a 6-char code.'},
        {'q':'🏗️ 100M redirects/day — where to cache?',
         'options':['MySQL','Redis (in-memory)','Hard disk','CDN only'],'answer':1,
         'tip':'✅ Redis stores key-value pairs in memory — sub-millisecond lookups.'},
        {'q':'🏗️ Same URL submitted twice?',
         'options':['Two short URLs','Return same short URL','Return error','Ask the user'],'answer':1,
         'tip':'✅ Check if URL exists first — return existing short code (idempotent).'},
    ],
    'Instagram / Feed': [
        {'q':'🏗️ User uploads photo — what processes it?',
         'options':['Sync API call','Async worker + S3','Store in MySQL','Email it'],'answer':1,
         'tip':'✅ Async workers (SQS + Lambda) process/resize; S3 stores originals.'},
        {'q':'🏗️ Generate feed for 500M users?',
         'options':['Query DB on every load','Pre-compute in Redis (fan-out)','Send emails','GraphQL only'],'answer':1,
         'tip':'✅ Fan-out on write: push new posts to followers\' caches when posted.'},
        {'q':'🏗️ Images load slowly in Brazil — what do you add?',
         'options':['Bigger US server','CDN (CloudFront)','Compress to 1px','Nothing'],'answer':1,
         'tip':'✅ CDN caches static content at edge locations near users globally.'},
    ],
    'YouTube / Video': [
        {'q':'🏗️ Serve 4K video at multiple qualities?',
         'options':['Send original to all','Transcode async (360p/720p/1080p)','Compress to 240p','Stream raw bytes'],'answer':1,
         'tip':'✅ Async transcoding creates multiple resolutions; client picks based on bandwidth.'},
        {'q':'🏗️ Video has 1B views — store count efficiently?',
         'options':['UPDATE in MySQL per view','Redis counter + batch flush','Count from logs','Ignore'],'answer':1,
         'tip':'✅ Redis INCR is atomic and fast; batch-flush to DB periodically.'},
    ],
    'Uber / Ride': [
        {'q':'🏗️ Match rider to nearest driver?',
         'options':['Loop all drivers','Geospatial index (Redis GEO)','Call each driver','Random pick'],'answer':1,
         'tip':'✅ Redis GEO stores coordinates and finds nearest in O(log n).'},
        {'q':'🏗️ 1M drivers updating location every 5 sec?',
         'options':['Write to MySQL each update','Write to Redis, async flush','Ignore old locations','Use cookies'],'answer':1,
         'tip':'✅ Redis handles millions of writes/sec; async workers persist to DB in batches.'},
    ],
}

# ═══════════════════════════════════════════════════════════════════════════
#  INTERVIEW QUESTIONS
# ═══════════════════════════════════════════════════════════════════════════
INTERVIEW_QUESTIONS = [
    {'q':'🎙️ Difference between `==` and `===` in JavaScript?',
     'options':['== value only (loose)','=== value AND type (strict)','Same thing','== for strings only'],'correct':[0,1],
     'tip':'✅ == coerces types (1=="1" true), === does not. Always prefer ===.'},
    {'q':'🎙️ What is Big O notation?',
     'options':['Code quality grade','Algorithm time/space complexity','A sorting algorithm','A DB query language'],'correct':[1],
     'tip':'✅ Big O describes how runtime/memory grows with input size.'},
    {'q':'🎙️ Difference between process and thread?',
     'options':['Process has own memory; threads share','Threads are slower','Process is part of thread','Identical'],'correct':[0],
     'tip':'✅ Processes are isolated; threads share memory and are lighter.'},
    {'q':'🎙️ What is REST?',
     'options':['A language','HTTP-based API architecture','A DB type','A JS framework'],'correct':[1],
     'tip':'✅ REST uses HTTP verbs (GET/POST/PUT/DELETE) and stateless requests.'},
    {'q':'🎙️ What is a deadlock?',
     'options':['Server crash','Two processes waiting for each other forever','A sorting bug','Memory full'],'correct':[1],
     'tip':'✅ Process A waits for B, B waits for A — neither can proceed.'},
    {'q':'🎙️ SQL vs NoSQL?',
     'options':['SQL is newer','SQL structured/relational; NoSQL flexible/scalable','NoSQL uses tables','Same thing'],'correct':[1],
     'tip':'✅ SQL: strict schema, ACID. NoSQL: flexible schema, horizontal scale.'},
    {'q':'🎙️ What is a closure?',
     'options':['Closes a file','Function that remembers outer scope','A type of loop','Class destructor'],'correct':[1],
     'tip':'✅ A closure keeps outer variables alive after the outer function returns.'},
    {'q':'🎙️ What is the CAP theorem?',
     'options':['CPU, API, Partition','Consistency, Availability, Partition — pick 2','Cache, Auth, Performance','A Python lib'],'correct':[1],
     'tip':'✅ Distributed systems can guarantee only 2 of 3: C, A, P.'},
]

# ═══════════════════════════════════════════════════════════════════════════
#  MULTIPLAYER GAME ROOMS
# ═══════════════════════════════════════════════════════════════════════════
# rooms[code] = {
#   'host': chat_id,
#   'players': {chat_id: {'name': str, 'score': int, 'answered': int}},
#   'questions': [...],
#   'q_idx': int,
#   'active': bool,
#   'answered_this_round': set(),
# }
game_rooms   = {}
player_rooms = {}  # chat_id -> room_code

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def get_display_name(chat_id):
    try:
        info = bot.get_chat(chat_id)
        name = info.first_name or ''
        if info.last_name: name += f' {info.last_name}'
        return name or f'Player_{str(chat_id)[-4:]}'
    except Exception:
        return f'Player_{str(chat_id)[-4:]}'

def rank_emoji(i):
    return ['🥇','🥈','🥉','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟'][i] if i < 10 else f'{i+1}.'

def title_for_score(score, total):
    pct = score / total if total else 0
    if pct == 1.0: return '🏆 Legend!'
    if pct >= 0.8: return '🔥 Pro!'
    if pct >= 0.5: return '💪 Rising Star!'
    return '📚 Keep Learning!'

def broadcast_room(code, text, markup=None, exclude=None):
    room = game_rooms.get(code)
    if not room: return
    for cid in list(room['players']):
        if exclude and cid == exclude: continue
        try:
            if markup:
                bot.send_message(cid, text, reply_markup=markup)
            else:
                bot.send_message(cid, text)
        except Exception:
            pass

def send_leaderboard(code):
    """Send leaderboard after each question."""
    room = game_rooms.get(code)
    if not room: return
    players = sorted(room['players'].items(), key=lambda x: -x[1]['score'])
    total_q = room['q_idx']  # questions done so far
    lines = [f"📊 *Leaderboard — after Q{total_q}:*\n"]
    for i, (cid, p) in enumerate(players):
        lines.append(f"{rank_emoji(i)} {p['name']} — {p['score']} pts")
    broadcast_room(code, '\n'.join(lines))

def send_game_question(code):
    room = game_rooms.get(code)
    if not room: return
    idx       = room['q_idx']
    questions = room['questions']
    if idx >= len(questions):
        end_game(code)
        return
    q = questions[idx]
    total = len(questions)
    room['answered_this_round'] = set()
    room['timer_active'] = True
    m = abcd_btn(q['options'], f'game_ans:{code}')
    broadcast_room(code, f"*Q{idx+1}/{total}*\n\n{q['q']}\n\n⏱️ 30 seconds!", markup=m)

    # 30-second timer in background thread
    import threading
    def timer_end():
        time.sleep(30)
        r = game_rooms.get(code)
        if not r or not r.get('timer_active'): return
        if r['q_idx'] != idx: return  # already moved on
        # Time's up — show who didn't answer
        missed = [p['name'] for cid, p in r['players'].items()
                  if cid not in r['answered_this_round']]
        if missed:
            broadcast_room(code, f"⏰ Time's up! No answer from: {', '.join(missed)}")
        r['q_idx'] += 1
        r['timer_active'] = False
        send_leaderboard(code)
        time.sleep(2)
        send_game_question(code)
    threading.Thread(target=timer_end, daemon=True).start()

def end_game(code):
    room = game_rooms.get(code)
    if not room: return
    room['active'] = False
    players = sorted(room['players'].items(), key=lambda x: -x[1]['score'])
    total   = len(room['questions'])
    lines   = ["🏁 *Game Over! Final Scores:*\n"]
    for i, (cid, p) in enumerate(players):
        lines.append(f"{rank_emoji(i)} {p['name']} — {p['score']}/{total} {title_for_score(p['score'], total)}")
    result = '\n'.join(lines)
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🏠 Menu", callback_data='menu'))
    broadcast_room(code, result, markup=m)
    # cleanup
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
        clean = text.replace("*","").replace("_","").replace("`","").replace("~","")
        bot.send_message(c, clean, reply_markup=reply_markup)

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
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("🎙️ Mock Interview", callback_data='interview'),
        types.InlineKeyboardButton("🐍 Python Trivia",  callback_data='python_menu'),
        types.InlineKeyboardButton("🏗️ System Design",  callback_data='sysdesign'),
        types.InlineKeyboardButton("🧩 LeetCode",       callback_data='leetcode'),
        types.InlineKeyboardButton("📄 CV Analysis",    callback_data='cv'),
        types.InlineKeyboardButton("🔍 JD Analyzer",    callback_data='jd'),
    )
    return m

def back_btn(c=None):
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🏠 Menu", callback_data='menu'))
    return m

def abcd_btn(options, prefix):
    labels = ["🅐","🅑","🅒","🅓"]
    m = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(f"{labels[i]} {opt[:28]}", callback_data=f"{prefix}:{i}") for i, opt in enumerate(options)]
    m.add(*btns)
    return m

def sd_topic_menu():
    m = types.InlineKeyboardMarkup(row_width=2)
    for name in SD_QUESTIONS:
        m.add(types.InlineKeyboardButton(name, callback_data=f"sd_topic:{name}"))
    m.add(types.InlineKeyboardButton("🏠 Menu", callback_data='menu'))
    return m

def python_mode_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("👤 Solo — Practice alone", callback_data='python_solo'),
        types.InlineKeyboardButton("🎮 Create Multiplayer Game", callback_data='python_create'),
        types.InlineKeyboardButton("🔗 Join a Game", callback_data='python_join'),
        types.InlineKeyboardButton("🏠 Menu", callback_data='menu'),
    )
    return m

# ═══════════════════════════════════════════════════════════════════════════
#  QUIZ SENDERS
# ═══════════════════════════════════════════════════════════════════════════
def send_solo_question(c):
    s     = user_sessions[c]
    idx   = s['q_idx']
    qs    = s['questions']
    if idx >= len(qs):
        score = s['score']
        total = len(qs)
        bot.send_message(c,
            f"✅ Done! {score}/{total} — {title_for_score(score, total)}",
            reply_markup=back_btn())
        user_states[c] = None
        return
    q = qs[idx]
    bot.send_message(c, f"*Q{idx+1}/{len(qs)}*\n\n{q['q']}",
                     parse_mode="Markdown",
                     reply_markup=abcd_btn(q['options'], 'solo_ans'))

def send_sd_question(c):
    s     = user_sessions[c]
    topic = s['topic']
    idx   = s['q_idx']
    qs    = SD_QUESTIONS.get(topic, [])
    if idx >= len(qs):
        score = s['score']
        total = len(qs)
        msg = f"🏗️ Done! {score}/{total} — {title_for_score(score, total)}"
        bot.send_message(c, msg, reply_markup=back_btn())
        user_states[c] = None
        return
    q = qs[idx]
    bot.send_message(c, f"*Q{idx+1}/{len(qs)}*\n\n{q['q']}",
                     parse_mode="Markdown",
                     reply_markup=abcd_btn(q['options'], 'sd_ans'))

def send_interview_question(c):
    s   = user_sessions[c]
    idx = s['q_idx']
    if idx >= len(INTERVIEW_QUESTIONS):
        score = s['score']
        total = len(INTERVIEW_QUESTIONS)
        bot.send_message(c,
            f"🎙️ Interview done! {score}/{total} — {title_for_score(score, total)}",
            reply_markup=back_btn())
        user_states[c] = None
        return
    q = INTERVIEW_QUESTIONS[idx]
    bot.send_message(c, f"*Q{idx+1}/{len(INTERVIEW_QUESTIONS)}*\n\n{q['q']}",
                     parse_mode="Markdown",
                     reply_markup=abcd_btn(q['options'], 'iv_ans'))

# ═══════════════════════════════════════════════════════════════════════════
#  COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    c = message.chat.id
    user_states[c] = None
    player_rooms.pop(c, None)
    bot.send_message(c, "🎓 Welcome to *DevBoost Career Coach*!\nChoose what you'd like to do:",
                     parse_mode="Markdown", reply_markup=main_menu(c))

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
        bot.send_message(c, "Choose what you'd like to do:", reply_markup=main_menu(c))
        return

    # ════════════════════════════════════════════════════
    #  PYTHON TRIVIA
    # ════════════════════════════════════════════════════
    if data == 'python_menu':
        bot.send_message(c, "🐍 *Python Trivia* — choose mode:", parse_mode="Markdown",
                         reply_markup=python_mode_menu())
        return

    # ── Solo ──
    if data == 'python_solo':
        qs = random.sample(ALL_QUESTIONS, min(10, len(ALL_QUESTIONS)))
        user_sessions[c] = {'questions': qs, 'q_idx': 0, 'score': 0}
        user_states[c]   = 'SOLO'
        bot.send_message(c, "🐍 Solo mode! 10 random questions. Let's go!")
        send_solo_question(c)
        return

    if data.startswith('solo_ans:'):
        if user_states.get(c) != 'SOLO': return
        chosen = int(data.split(':')[1])
        s  = user_sessions[c]
        q  = s['questions'][s['q_idx']]
        labels = ["🅐","🅑","🅒","🅓"]
        if chosen == q['answer']:
            s['score'] += 1
            bot.send_message(c, f"✅ Correct! {q['tip']}")
        else:
            bot.send_message(c, f"❌ Wrong! Answer: {labels[q['answer']]} {q['options'][q['answer']]}\n{q['tip']}")
        s['q_idx'] += 1
        time.sleep(0.4)
        send_solo_question(c)
        return

    # ── Create Multiplayer ──
    if data == 'python_create':
        code = gen_code()
        name = get_display_name(c)
        qs   = random.sample(ALL_QUESTIONS, min(10, len(ALL_QUESTIONS)))
        game_rooms[code] = {
            'host': c,
            'players': {c: {'name': name, 'score': 0, 'answered': 0}},
            'questions': qs,
            'q_idx': 0,
            'active': False,
            'answered_this_round': set(),
        }
        player_rooms[c] = code
        user_states[c]  = 'GAME_LOBBY'
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("🚀 Start Game!", callback_data=f'game_start:{code}'))
        m.add(types.InlineKeyboardButton("❌ Cancel",       callback_data='game_cancel'))
        bot.send_message(c,
            f"🎮 *Game created!*\n\n"
            f"Share this code with friends:\n"
            f"┌─────────────┐\n"
            f"│  *{code}*  │\n"
            f"└─────────────┘\n\n"
            f"Players joined: 1 (you)\n"
            f"Press *Start* when everyone is in!",
            parse_mode="Markdown", reply_markup=m)
        return

    if data.startswith('game_start:'):
        code = data.split(':')[1]
        room = game_rooms.get(code)
        if not room or room['host'] != c: return
        if len(room['players']) < 1:
            bot.send_message(c, "⚠️ Need at least 1 player!")
            return
        room['active'] = True
        n = len(room['players'])
        names = ', '.join(p['name'] for p in room['players'].values())
        broadcast_room(code, f"🚀 *Game starts!*\n👥 {n} players: {names}\n\n10 questions. Good luck! 🍀")
        time.sleep(1)
        send_game_question(code)
        return

    if data == 'game_cancel':
        code = player_rooms.get(c)
        if code and game_rooms.get(code, {}).get('host') == c:
            broadcast_room(code, "❌ Game cancelled by host.", exclude=c)
            for cid in list(game_rooms[code]['players']):
                player_rooms.pop(cid, None)
                user_states.pop(cid, None)
            game_rooms.pop(code, None)
        user_states[c] = None
        bot.send_message(c, "Cancelled.", reply_markup=back_btn())
        return

    # ── Join Multiplayer ──
    if data == 'python_join':
        user_states[c] = 'JOIN_WAIT'
        bot.send_message(c, "🔗 Type the 5-letter game code:")
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
        labels = ["🅐","🅑","🅒","🅓"]
        player = room['players'][c]
        player['answered'] += 1
        if chosen == q['answer']:
            player['score'] += 1
            bot.send_message(c, f"✅ Correct! +1 point 🎉\n{q['tip']}")
        else:
            bot.send_message(c, f"❌ Wrong! Correct: {labels[q['answer']]} {q['options'][q['answer']]}\n{q['tip']}")
        # All answered? Move on immediately (don't wait for timer)
        if len(room['answered_this_round']) >= len(room['players']):
            room['timer_active'] = False
            room['q_idx'] += 1
            time.sleep(1)
            send_leaderboard(code)
            time.sleep(2)
            send_game_question(code)
        return

    # ════════════════════════════════════════════════════
    #  SYSTEM DESIGN
    # ════════════════════════════════════════════════════
    if data == 'sysdesign':
        bot.send_message(c, "🏗️ Choose a system to design:", reply_markup=sd_topic_menu())
        return

    if data.startswith('sd_topic:'):
        topic = data.split(':', 1)[1]
        user_sessions[c] = {'topic': topic, 'q_idx': 0, 'score': 0}
        user_states[c]   = 'SYSDESIGN'
        send_sd_question(c)
        return

    if data.startswith('sd_ans:'):
        if user_states.get(c) != 'SYSDESIGN': return
        chosen  = int(data.split(':')[1])
        s       = user_sessions[c]
        q       = SD_QUESTIONS[s['topic']][s['q_idx']]
        labels  = ["🅐","🅑","🅒","🅓"]
        if chosen == q['answer']:
            s['score'] += 1
            bot.send_message(c, f"✅ Correct!\n{q['tip']}")
        else:
            bot.send_message(c, f"❌ Wrong! Answer: {labels[q['answer']]} {q['options'][q['answer']]}\n{q['tip']}")
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
        bot.send_message(c, "🎙️ Mock Interview — 8 questions. Tap your answer!")
        send_interview_question(c)
        return

    if data.startswith('iv_ans:'):
        if user_states.get(c) != 'INTERVIEW': return
        chosen  = int(data.split(':')[1])
        s       = user_sessions[c]
        q       = INTERVIEW_QUESTIONS[s['q_idx']]
        labels  = ["🅐","🅑","🅒","🅓"]
        if chosen in q['correct']:
            s['score'] += 1
            bot.send_message(c, f"✅ Correct!\n{q['tip']}")
        else:
            correct_txt = ' / '.join(f"{labels[i]} {q['options'][i]}" for i in q['correct'])
            bot.send_message(c, f"❌ Wrong! Answer: {correct_txt}\n{q['tip']}")
        s['q_idx'] += 1
        time.sleep(0.4)
        send_interview_question(c)
        return

    # ════════════════════════════════════════════════════
    #  LEETCODE (Easy, button-driven)
    # ════════════════════════════════════════════════════
    if data == 'leetcode':
        user_states[c] = 'LEET_WAIT'
        bot.send_message(c, "🧩 Generating an Easy LeetCode question...")
        bot.send_chat_action(c, 'typing')
        try:
            system = (
                "You are a LeetCode coach. Give ONE Easy problem. "
                "Mobile-friendly: max 5 lines description, 1 example. "
                "Format strictly:\nProblem: <name>\nDescription: <text>\nExample: Input: ... Output: ...\nSOLUTION_PLACEHOLDER\n<Python solution, max 10 lines>"
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
        bot.send_message(c,
            "📄 Send me your CV — paste as text, or upload a PDF/Word file.\n"
            "I'll give you an ATS score + quick improvements.",
            reply_markup=back_btn())
        return

    if data == 'jd':
        user_states[c] = 'JD'
        bot.send_message(c,
            "🔍 Paste the Job Description.\n"
            "I'll extract keywords + what to highlight in your CV.",
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
            bot.send_message(c, "❌ Couldn't read file.", reply_markup=back_btn())
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

        # Waiting for join code
        if state == 'JOIN_WAIT':
            code = text.upper()
            room = game_rooms.get(code)
            if not room:
                bot.send_message(c, "❌ Game not found. Check the code.", reply_markup=back_btn())
                return
            if room['active']:
                bot.send_message(c, "❌ Game already started.", reply_markup=back_btn())
                return
            name = get_display_name(c)
            room['players'][c] = {'name': name, 'score': 0, 'answered': 0}
            player_rooms[c]    = code
            user_states[c]     = 'GAME_LOBBY'
            n = len(room['players'])
            bot.send_message(c, f"✅ Joined game *{code}*!\nWaiting for host to start... ({n} players)", parse_mode="Markdown")
            # Notify host
            host = room['host']
            m = types.InlineKeyboardMarkup()
            m.add(types.InlineKeyboardButton("🚀 Start Game!", callback_data=f'game_start:{code}'))
            m.add(types.InlineKeyboardButton("❌ Cancel",       callback_data='game_cancel'))
            try:
                bot.send_message(host,
                    f"👋 *{name}* joined! ({n} players total)\nPress Start when ready!",
                    parse_mode="Markdown", reply_markup=m)
            except Exception:
                pass
            return

        if state == 'CV':
            _process_cv_or_jd(c, text, 'CV')
        elif state == 'JD':
            _process_cv_or_jd(c, text, 'JD')
        else:
            system = "You are a software engineering career coach. Answer concisely — max 5 lines."
            resp = call_ai(system, text)
            safe_send(c, resp, reply_markup=back_btn())
    except Exception as e:
        bot.send_message(c, f"❌ Error: {e}", reply_markup=back_btn())

def _process_cv_or_jd(c, content, mode):
    if mode == 'CV':
        system = (
            "You are a CV expert. Be concise and mobile-friendly.\n"
            "Give:\n1. ATS Score: X/10\n2. Top 3 strengths\n3. Top 3 improvements (one line each)\n4. One rewritten bullet example.\nMax 20 lines."
        )
    else:
        system = (
            "You are an ATS expert. Be concise and mobile-friendly.\n"
            "Give:\n1. Top 10 Keywords (comma separated)\n2. Must-haves (3 bullets)\n3. Top 3 CV tips for this role.\nMax 20 lines."
        )
    bot.send_chat_action(c, 'typing')
    resp = call_ai(system, content)
    safe_send(c, resp, reply_markup=back_btn())
    user_states[c] = None

print("🤖 DevBoost Career Coach is running...")
bot.infinity_polling()
