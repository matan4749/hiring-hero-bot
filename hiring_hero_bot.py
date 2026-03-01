import telebot, os, requests, tempfile, random, string, time, threading, datetime
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
#  PYTHON QUIZ BANK — bilingual
# ═══════════════════════════════════════════════════════════════════════════
ALL_QUESTIONS = [
    # ── EASY ──────────────────────────────────────────────────────────────────
    {'q_en':'What is the output of `type(3.0)`?',
     'q_he':'מה הפלט של `type(3.0)`?',
     'options_en':["<class 'int'>","<class 'float'>","<class 'str'>","<class 'number'>"],
     'options_he':["<class 'int'>","<class 'float'>","<class 'str'>","<class 'number'>"],
     'answer':1,'difficulty':'easy',
     'tip_en':'3.0 has a decimal point → float.','tip_he':'3.0 מכיל נקודה עשרונית → float.'},

    {'q_en':'Which is a valid variable name?',
     'q_he':'איזה שם משתנה תקין?',
     'options_en':['2name','my-var','_my_var','my var'],
     'options_he':['2name','my-var','_my_var','my var'],
     'answer':2,'difficulty':'easy',
     'tip_en':'Names can start with _ or a letter, not a digit or hyphen.',
     'tip_he':'שמות משתנים יכולים להתחיל ב-_ או אות, לא ספרה או מינוס.'},

    {'q_en':'What type is `True`?',
     'q_he':'מה הטיפוס של `True`?',
     'options_en':['str','int','bool','NoneType'],
     'options_he':['str','int','bool','NoneType'],
     'answer':2,'difficulty':'easy',
     'tip_en':'True and False are Python booleans.','tip_he':'True ו-False הם ערכים בוליאניים.'},

    {'q_en':'What does `int("7")` return?',
     'q_he':'מה מחזיר `int("7")`?',
     'options_en':['Error','7 (int)','7 (str)','0.7'],
     'options_he':['שגיאה','7 (int)','7 (str)','0.7'],
     'answer':1,'difficulty':'easy',
     'tip_en':'int() converts a string to integer.','tip_he':'int() ממיר מחרוזת למספר שלם.'},

    {'q_en':'What does `[1,2,3][-1]` return?',
     'q_he':'מה מחזיר `[1,2,3][-1]`?',
     'options_en':['1','2','3','Error'],
     'options_he':['1','2','3','שגיאה'],
     'answer':2,'difficulty':'easy',
     'tip_en':'Negative index -1 returns the last element.',
     'tip_he':'אינדקס שלילי -1 מחזיר את האיבר האחרון.'},

    {'q_en':'How do you add a key to a dict?',
     'q_he':'איך מוסיפים מפתח ל-dict?',
     'options_en':['d.add("k",1)','d["k"]=1','d.insert("k",1)','d.put("k",1)'],
     'options_he':['d.add("k",1)','d["k"]=1','d.insert("k",1)','d.put("k",1)'],
     'answer':1,'difficulty':'easy',
     'tip_en':'Use d["key"] = value.','tip_he':'השתמש ב-d["מפתח"] = ערך.'},

    {'q_en':'Which method removes the last list item?',
     'q_he':'איזו מתודה מסירה את האיבר האחרון ברשימה?',
     'options_en':['remove()','delete()','pop()','discard()'],
     'options_he':['remove()','delete()','pop()','discard()'],
     'answer':2,'difficulty':'easy',
     'tip_en':'list.pop() removes and returns the last item.',
     'tip_he':'list.pop() מסיר ומחזיר את האיבר האחרון.'},

    {'q_en':'How do you get the length of a list?',
     'q_he':'איך מקבלים את אורך הרשימה?',
     'options_en':['list.length()','len(list)','list.size()','count(list)'],
     'options_he':['list.length()','len(list)','list.size()','count(list)'],
     'answer':1,'difficulty':'easy',
     'tip_en':'len() is a built-in function.','tip_he':'len() היא פונקציה מובנית.'},

    {'q_en':'What is the result of `2 ** 3`?',
     'q_he':'מה התוצאה של `2 ** 3`?',
     'options_en':['5','6','8','9'],
     'options_he':['5','6','8','9'],
     'answer':2,'difficulty':'easy',
     'tip_en':'** is the power operator.','tip_he':'** הוא אופרטור חזקה.'},

    {'q_en':'What does `print("Hi")` do?',
     'q_he':'מה עושה `print("Hi")`?',
     'options_en':['Returns "Hi"','Stores "Hi"','Displays "Hi" to console','Creates a variable'],
     'options_he':['מחזיר "Hi"','שומר "Hi"','מציג "Hi" בקונסול','יוצר משתנה'],
     'answer':2,'difficulty':'easy',
     'tip_en':'print() outputs text to the console.',
     'tip_he':'print() מציג טקסט בקונסול.'},

    {'q_en':'Which keyword starts a function definition?',
     'q_he':'איזו מילת מפתח מתחילה הגדרת פונקציה?',
     'options_en':['function','fun','def','func'],
     'options_he':['function','fun','def','func'],
     'answer':2,'difficulty':'easy',
     'tip_en':'def my_func(): is how you define a function.',
     'tip_he':'def my_func(): כך מגדירים פונקציה.'},

    {'q_en':'What is `None` in Python?',
     'q_he':'מה זה `None` בפייתון?',
     'options_en':['0','False','Empty string','The absence of a value'],
     'options_he':['0','False','מחרוזת ריקה','היעדר ערך'],
     'answer':3,'difficulty':'easy',
     'tip_en':'None represents no value / null.',
     'tip_he':'None מייצג אין ערך / null.'},

    {'q_en':'How do you create a comment in Python?',
     'q_he':'איך יוצרים הערה בפייתון?',
     'options_en':['// comment','/* comment */','# comment','-- comment'],
     'options_he':['// comment','/* comment */','# comment','-- comment'],
     'answer':2,'difficulty':'easy',
     'tip_en':'# starts a comment in Python.',
     'tip_he':'# מתחיל הערה בפייתון.'},

    {'q_en':'What does `range(3)` produce?',
     'q_he':'מה מייצר `range(3)`?',
     'options_en':['[1,2,3]','[0,1,2]','[0,1,2,3]','(1,2,3)'],
     'options_he':['[1,2,3]','[0,1,2]','[0,1,2,3]','(1,2,3)'],
     'answer':1,'difficulty':'easy',
     'tip_en':'range(n) generates 0 to n-1.',
     'tip_he':'range(n) מייצר 0 עד n-1.'},

    {'q_en':'What symbol is used for string concatenation?',
     'q_he':'איזה סמל משמש לחיבור מחרוזות?',
     'options_en':['&','+','*','|'],
     'options_he':['&','+','*','|'],
     'answer':1,'difficulty':'easy',
     'tip_en':'"Hello" + " World" = "Hello World".',
     'tip_he':'"Hello" + " World" = "Hello World".'},

    # ── MEDIUM ────────────────────────────────────────────────────────────────
    {'q_en':'What does `*args` do in a function?',
     'q_he':'מה עושה `*args` בפונקציה?',
     'options_en':['Multiplies args','Keyword args only','Any number of positional args','Makes args optional'],
     'options_he':['מכפיל ארגומנטים','ארגומנטים לפי שם','ארגומנטים פוזיציוניים (כל מספר)','הופך לאופציונליים'],
     'answer':2,'difficulty':'medium',
     'tip_en':'*args collects extra positional arguments into a tuple.',
     'tip_he':'*args אוסף ארגומנטים פוזיציוניים ל-tuple.'},

    {'q_en':'What is a lambda in Python?',
     'q_he':'מה זה lambda בפייתון?',
     'options_en':['A loop','An anonymous function','A class method','A module'],
     'options_he':['לולאה','פונקציה אנונימית','מתודת מחלקה','מודול'],
     'answer':1,'difficulty':'medium',
     'tip_en':'lambda x: x+1 is a one-line anonymous function.',
     'tip_he':'lambda x: x+1 היא פונקציה אנונימית.'},

    {'q_en':'What does `return` without a value return?',
     'q_he':'מה מחזיר `return` ללא ערך?',
     'options_en':['0','None','False','Error'],
     'options_he':['0','None','False','שגיאה'],
     'answer':1,'difficulty':'medium',
     'tip_en':'A bare return returns None.',
     'tip_he':'return ללא ערך מחזיר None.'},

    {'q_en':'Which block always executes in try/except?',
     'q_he':'איזה בלוק תמיד מתבצע ב-try/except?',
     'options_en':['try','except','else','finally'],
     'options_he':['try','except','else','finally'],
     'answer':3,'difficulty':'medium',
     'tip_en':'finally always runs, exception or not.',
     'tip_he':'finally תמיד רץ, עם חריגה או בלי.'},

    {'q_en':'What exception is raised for a missing dict key?',
     'q_he':'איזו חריגה עולה למפתח חסר ב-dict?',
     'options_en':['ValueError','IndexError','KeyError','TypeError'],
     'options_he':['ValueError','IndexError','KeyError','TypeError'],
     'answer':2,'difficulty':'medium',
     'tip_en':'d["missing"] raises KeyError.',
     'tip_he':'d["missing"] מעלה KeyError.'},

    {'q_en':'What does a decorator do?',
     'q_he':'מה עושה decorator?',
     'options_en':['Adds CSS','Wraps a function to extend behavior','Creates a class','Imports a module'],
     'options_he':['מוסיף CSS','עוטף פונקציה להרחבת התנהגות','יוצר מחלקה','מייבא מודול'],
     'answer':1,'difficulty':'medium',
     'tip_en':'@decorator wraps a function, adding behavior before/after.',
     'tip_he':'@decorator עוטף פונקציה ומוסיף התנהגות.'},

    {'q_en':'What is `self` in a class method?',
     'q_he':'מה זה `self` במתודת מחלקה?',
     'options_en':['The class itself','The current instance','A global variable','A built-in'],
     'options_he':['המחלקה עצמה','האובייקט הנוכחי','משתנה גלובלי','מובנה'],
     'answer':1,'difficulty':'medium',
     'tip_en':'self refers to the current object instance.',
     'tip_he':'self מתייחס לאובייקט הנוכחי.'},

    {'q_en':'What does `list comprehension` look like?',
     'q_he':'איך נראה list comprehension?',
     'options_en':['(x for x in l)','[x for x in l]','{x for x in l}','<x for x in l>'],
     'options_he':['(x for x in l)','[x for x in l]','{x for x in l}','<x for x in l>'],
     'answer':1,'difficulty':'medium',
     'tip_en':'[expr for item in iterable] is a list comprehension.',
     'tip_he':'[expr for item in iterable] הוא list comprehension.'},

    {'q_en':'What does `dict.get("k", 0)` do if "k" is missing?',
     'q_he':'מה עושה `dict.get("k", 0)` אם "k" לא קיים?',
     'options_en':['Raises KeyError','Returns None','Returns 0','Returns False'],
     'options_he':['מעלה KeyError','מחזיר None','מחזיר 0','מחזיר False'],
     'answer':2,'difficulty':'medium',
     'tip_en':'get() returns the default value if key is missing.',
     'tip_he':'get() מחזיר ברירת מחדל אם המפתח חסר.'},

    {'q_en':'What is the difference between `is` and `==`?',
     'q_he':'מה ההבדל בין `is` ל-`==`?',
     'options_en':['No difference','is checks identity, == checks equality','== checks identity','is checks type'],
     'options_he':['אין הבדל','is בודק זהות, == בודק שוויון','== בודק זהות','is בודק טיפוס'],
     'answer':1,'difficulty':'medium',
     'tip_en':'is checks if two variables point to the same object.',
     'tip_he':'is בודק אם שני משתנים מצביעים לאותו אובייקט.'},

    {'q_en':'What does `enumerate()` return?',
     'q_he':'מה מחזיר `enumerate()`?',
     'options_en':['A list of values','Index-value pairs','Only indices','A dict'],
     'options_he':['רשימת ערכים','זוגות אינדקס-ערך','רק אינדקסים','מילון'],
     'answer':1,'difficulty':'medium',
     'tip_en':'enumerate() yields (index, value) tuples.',
     'tip_he':'enumerate() מייצר זוגות (אינדקס, ערך).'},

    {'q_en':'What does `zip([1,2],[3,4])` produce?',
     'q_he':'מה מייצר `zip([1,2],[3,4])`?',
     'options_en':['[1,2,3,4]','[(1,3),(2,4)]','[[1,3],[2,4]]','{1:3, 2:4}'],
     'options_he':['[1,2,3,4]','[(1,3),(2,4)]','[[1,3],[2,4]]','{1:3, 2:4}'],
     'answer':1,'difficulty':'medium',
     'tip_en':'zip() pairs elements from multiple iterables.',
     'tip_he':'zip() משלב אלמנטים ממספר רשימות.'},

    {'q_en':'What is a set in Python?',
     'q_he':'מה זה set בפייתון?',
     'options_en':['Ordered list','Unordered collection of unique values','Key-value pairs','Immutable list'],
     'options_he':['רשימה מסודרת','אוסף לא מסודר של ערכים ייחודיים','זוגות מפתח-ערך','רשימה קבועה'],
     'answer':1,'difficulty':'medium',
     'tip_en':'A set stores unique elements with no guaranteed order.',
     'tip_he':'set מאחסן ערכים ייחודיים ללא סדר מובטח.'},

    {'q_en':'What does `map(func, list)` do?',
     'q_he':'מה עושה `map(func, list)`?',
     'options_en':['Filters items','Applies func to each item','Sorts the list','Counts items'],
     'options_he':['מסנן פריטים','מפעיל func על כל פריט','ממיין הרשימה','סופר פריטים'],
     'answer':1,'difficulty':'medium',
     'tip_en':'map() applies a function to every element.',
     'tip_he':'map() מפעיל פונקציה על כל אלמנט.'},

    {'q_en':'What is the output of `bool("")`?',
     'q_he':'מה הפלט של `bool("")`?',
     'options_en':['True','False','None','Error'],
     'options_he':['True','False','None','שגיאה'],
     'answer':1,'difficulty':'medium',
     'tip_en':'Empty string is falsy in Python.',
     'tip_he':'מחרוזת ריקה היא falsy בפייתון.'},

    # ── HARD ──────────────────────────────────────────────────────────────────
    {'q_en':'What is the output of `[x*2 for x in range(3) if x>0]`?',
     'q_he':'מה הפלט של `[x*2 for x in range(3) if x>0]`?',
     'options_en':['[0,2,4]','[2,4]','[1,2]','[0,1,2]'],
     'options_he':['[0,2,4]','[2,4]','[1,2]','[0,1,2]'],
     'answer':1,'difficulty':'hard',
     'tip_en':'range(3) gives 0,1,2. Filter x>0 gives 1,2. *2 gives [2,4].',
     'tip_he':'range(3) נותן 0,1,2. סינון x>0 נותן 1,2. *2 נותן [2,4].'},

    {'q_en':'What does `@staticmethod` mean?',
     'q_he':'מה אומר `@staticmethod`?',
     'options_en':['Method that modifies class','Method with no self/cls','Abstract method','Class-level variable'],
     'options_he':['מתודה שמשנה מחלקה','מתודה ללא self/cls','מתודה אבסטרקטית','משתנה ברמת מחלקה'],
     'answer':1,'difficulty':'hard',
     'tip_en':'@staticmethod does not receive self or cls.',
     'tip_he':'@staticmethod לא מקבלת self או cls.'},

    {'q_en':'What is a generator in Python?',
     'q_he':'מה זה generator בפייתון?',
     'options_en':['A list factory','A function that yields values lazily','A type of decorator','A class pattern'],
     'options_he':['מפעל רשימות','פונקציה שמייצרת ערכים בצורה עצלה','סוג של decorator','תבנית מחלקה'],
     'answer':1,'difficulty':'hard',
     'tip_en':'Generators use yield to produce values one at a time.',
     'tip_he':'generators משתמשים ב-yield לייצור ערכים אחד אחד.'},

    {'q_en':'What does `__slots__` do in a class?',
     'q_he':'מה עושה `__slots__` במחלקה?',
     'options_en':['Adds abstract methods','Restricts attributes, saves memory','Hides attributes','Enables inheritance'],
     'options_he':['מוסיף מתודות אבסטרקטיות','מגביל מאפיינים וחוסך זיכרון','מסתיר מאפיינים','מאפשר ירושה'],
     'answer':1,'difficulty':'hard',
     'tip_en':'__slots__ prevents __dict__ creation, saving memory.',
     'tip_he':'__slots__ מונע יצירת __dict__, חוסך זיכרון.'},

    {'q_en':'What is the GIL in Python?',
     'q_he':'מה זה GIL בפייתון?',
     'options_en':['A memory manager','A lock allowing only one thread to run at a time','A garbage collector','A type checker'],
     'options_he':['מנהל זיכרון','מנעול שמאפשר רק thread אחד בכל פעם','אוסף אשפה','בודק טיפוסים'],
     'answer':1,'difficulty':'hard',
     'tip_en':'GIL = Global Interpreter Lock, limits true parallelism in CPython.',
     'tip_he':'GIL = Global Interpreter Lock, מגביל מקביליות ב-CPython.'},

    {'q_en':'What does `functools.lru_cache` do?',
     'q_he':'מה עושה `functools.lru_cache`?',
     'options_en':['Logs function calls','Caches function results','Limits recursion','Sorts arguments'],
     'options_he':['מתעד קריאות','שומר תוצאות פונקציה ב-cache','מגביל רקורסיה','ממיין ארגומנטים'],
     'answer':1,'difficulty':'hard',
     'tip_en':'lru_cache memoizes results to avoid recomputation.',
     'tip_he':'lru_cache שומר תוצאות כדי למנוע חישוב חוזר.'},

    {'q_en':'What is the result of `0.1 + 0.2 == 0.3` in Python?',
     'q_he':'מה התוצאה של `0.1 + 0.2 == 0.3` בפייתון?',
     'options_en':['True','False','None','Error'],
     'options_he':['True','False','None','שגיאה'],
     'answer':1,'difficulty':'hard',
     'tip_en':'Floating point precision: 0.1+0.2 = 0.30000000000000004.',
     'tip_he':'דיוק נקודה צפה: 0.1+0.2 = 0.30000000000000004.'},

    {'q_en':'What does `__enter__` and `__exit__` enable?',
     'q_he':'מה מאפשרים `__enter__` ו-`__exit__`?',
     'options_en':['Iteration','Context managers (with statement)','Comparison','Serialization'],
     'options_he':['איטרציה','context managers (with statement)','השוואה','סריאליזציה'],
     'answer':1,'difficulty':'hard',
     'tip_en':'These dunder methods enable the "with" statement.',
     'tip_he':'מתודות אלו מאפשרות שימוש ב-"with" statement.'},

    {'q_en':'What is `*args` vs `**kwargs`?',
     'q_he':'מה ההבדל בין `*args` ל-`**kwargs`?',
     'options_en':['Both are the same','*args=positional tuple, **kwargs=keyword dict','*args=keyword, **kwargs=positional','Neither stores arguments'],
     'options_he':['שניהם זהים','*args=tuple פוזיציוני, **kwargs=dict עם שמות','*args=עם שמות, **kwargs=פוזיציוני','אף אחד לא שומר ארגומנטים'],
     'answer':1,'difficulty':'hard',
     'tip_en':'*args → tuple of extra positional args. **kwargs → dict of keyword args.',
     'tip_he':'*args → tuple של ארגומנטים פוזיציוניים. **kwargs → dict של ארגומנטים עם שם.'},

    {'q_en':'What does `collections.defaultdict` do?',
     'q_he':'מה עושה `collections.defaultdict`?',
     'options_en':['Sorts dict automatically','Returns default value for missing keys','Merges two dicts','Limits dict size'],
     'options_he':['ממיין dict אוטומטית','מחזיר ערך ברירת מחדל למפתחות חסרים','ממזג שני dicts','מגביל גודל dict'],
     'answer':1,'difficulty':'hard',
     'tip_en':'defaultdict(int) returns 0 for missing keys instead of KeyError.',
     'tip_he':'defaultdict(int) מחזיר 0 למפתחות חסרים במקום KeyError.'},

    {'q_en':'What is the complexity of Python dict lookup?',
     'q_he':'מה מורכבות חיפוש ב-dict בפייתון?',
     'options_en':['O(n)','O(log n)','O(1) average','O(n²)'],
     'options_he':['O(n)','O(log n)','O(1) ממוצע','O(n²)'],
     'answer':2,'difficulty':'hard',
     'tip_en':'Hash tables give O(1) average lookup.',
     'tip_he':'טבלאות hash נותנות O(1) ממוצע לחיפוש.'},

    {'q_en':'What is a metaclass in Python?',
     'q_he':'מה זה metaclass בפייתון?',
     'options_en':['A parent class','A class that creates classes','An abstract base class','A decorator'],
     'options_he':['מחלקת אב','מחלקה שיוצרת מחלקות','מחלקת בסיס אבסטרקטית','decorator'],
     'answer':1,'difficulty':'hard',
     'tip_en':'A metaclass is the class of a class — type is the default metaclass.',
     'tip_he':'metaclass היא המחלקה של מחלקה — type היא ברירת המחדל.'},

    {'q_en':'What does `__repr__` vs `__str__` do?',
     'q_he':'מה ההבדל בין `__repr__` ל-`__str__`?',
     'options_en':['Both are identical','__repr__=debug string, __str__=user string','__str__=debug, __repr__=user','Neither affects printing'],
     'options_he':['שניהם זהים','__repr__=מחרוזת debug, __str__=מחרוזת משתמש','__str__=debug, __repr__=משתמש','אף אחד לא משפיע על הדפסה'],
     'answer':1,'difficulty':'hard',
     'tip_en':'__repr__ for developers, __str__ for end users.',
     'tip_he':'__repr__ למפתחים, __str__ למשתמשי קצה.'},

    {'q_en':'What does `asyncio.gather()` do?',
     'q_he':'מה עושה `asyncio.gather()`?',
     'options_en':['Runs coroutines sequentially','Runs coroutines concurrently','Creates threads','Cancels tasks'],
     'options_he':['מריץ coroutines ברצף','מריץ coroutines במקביל','יוצר threads','מבטל tasks'],
     'answer':1,'difficulty':'hard',
     'tip_en':'gather() runs multiple coroutines concurrently.',
     'tip_he':'gather() מריץ מספר coroutines בו-זמנית.'},

    {'q_en':'What is a closure in Python?',
     'q_he':'מה זה closure בפייתון?',
     'options_en':['A sealed class','A function that captures variables from its enclosing scope','A context manager','A type of iterator'],
     'options_he':['מחלקה אטומה','פונקציה שלוכדת משתנים מהסביבה שלה','context manager','סוג של iterator'],
     'answer':1,'difficulty':'hard',
     'tip_en':'Closures "remember" variables from the scope where they were created.',
     'tip_he':'closures "זוכרות" משתנים מהסביבה שבה נוצרו.'},
]

EASY_Q   = [q for q in ALL_QUESTIONS if q.get('difficulty') == 'easy']
MEDIUM_Q = [q for q in ALL_QUESTIONS if q.get('difficulty') == 'medium']
HARD_Q   = [q for q in ALL_QUESTIONS if q.get('difficulty') == 'hard']

def get_q(q_dict, lang):
    """Return question fields in the right language."""
    return {
        'q':       q_dict.get(f'q_{lang}',       q_dict.get('q_en', '')),
        'options': q_dict.get(f'options_{lang}',  q_dict.get('options_en', [])),
        'answer':  q_dict['answer'],
        'tip':     q_dict.get(f'tip_{lang}',      q_dict.get('tip_en', '')),
    }

# ═══════════════════════════════════════════════════════════════════════════
#  SYSTEM DESIGN BANK — bilingual
# ═══════════════════════════════════════════════════════════════════════════
SD_QUESTIONS = {
    'WhatsApp / צ\'אט': {
        'en': 'WhatsApp / Chat',
        'he': 'WhatsApp / צ\'אט',
        'questions': [
            {'q_en':'🏗️ 10M messages/sec — what handles the load?',
             'q_he':'🏗️ 10M הודעות/שניה — מה מטפל בעומס?',
             'options_en':['Single DB','Message Queue (Kafka)','More RAM','Bigger server'],
             'options_he':['DB יחיד','תור הודעות (Kafka)','יותר RAM','שרת גדול יותר'],
             'answer':1,
             'tip_en':'Message Queue decouples producers/consumers and handles massive throughput.',
             'tip_he':'תור הודעות מפריד בין יצרנים לצרכנים ומטפל בנפח עצום.'},
            {'q_en':'🏗️ Store chat history for 2B users?',
             'q_he':'🏗️ איך שומרים היסטוריית צ\'אט ל-2B משתמשים?',
             'options_en':['One MySQL','NoSQL + sharding (Cassandra)','Files on disk','Redis only'],
             'options_he':['MySQL יחיד','NoSQL + sharding (Cassandra)','קבצים','רק Redis'],
             'answer':1,
             'tip_en':'Cassandra scales horizontally, optimized for time-series message data.',
             'tip_he':'Cassandra מתרחב אופקית, מותאם לנתוני הודעות.'},
            {'q_en':'🏗️ How to detect if a user is online?',
             'q_he':'🏗️ איך מזהים שמשתמש מחובר?',
             'options_en':['Poll DB every second','WebSocket heartbeat + Redis TTL','SMS ping','Email check'],
             'options_he':['סקירת DB כל שניה','WebSocket heartbeat + Redis TTL','SMS ping','בדיקת אימייל'],
             'answer':1,
             'tip_en':'WebSocket keeps persistent connection; Redis TTL expires if heartbeat stops.',
             'tip_he':'WebSocket שומר חיבור מתמיד; Redis TTL פג אם ה-heartbeat עוצר.'},
        ]
    },
    'URL Shortener': {
        'en': 'URL Shortener',
        'he': 'קיצור קישורים',
        'questions': [
            {'q_en':'🏗️ How to generate a unique short code?',
             'q_he':'🏗️ איך מייצרים קוד קצר ייחודי?',
             'options_en':['Random number','Base62 of auto-increment ID','MD5 hash','UUID'],
             'options_he':['מספר אקראי','Base62 של ID אוטומטי','MD5 hash','UUID'],
             'answer':1,
             'tip_en':'Base62 gives 56B combos from a 6-char code.',
             'tip_he':'Base62 נותן 56B צירופים מקוד של 6 תווים.'},
            {'q_en':'🏗️ 100M redirects/day — where to cache?',
             'q_he':'🏗️ 100M הפניות/יום — איפה לעשות cache?',
             'options_en':['MySQL','Redis (in-memory)','Hard disk','CDN only'],
             'options_he':['MySQL','Redis (בזיכרון)','דיסק קשיח','CDN בלבד'],
             'answer':1,
             'tip_en':'Redis stores key-value in memory — sub-millisecond lookups.',
             'tip_he':'Redis שומר key-value בזיכרון — חיפוש תת-מילישנייתי.'},
            {'q_en':'🏗️ Same URL submitted twice?',
             'q_he':'🏗️ אותו URL נשלח פעמיים?',
             'options_en':['Two short URLs','Return same short URL','Return error','Ask user'],
             'options_he':['שני קישורים קצרים','החזר אותו קישור קצר','החזר שגיאה','שאל משתמש'],
             'answer':1,
             'tip_en':'Check if URL exists first — return existing short code (idempotent).',
             'tip_he':'בדוק אם ה-URL קיים — החזר קוד קיים (idempotent).'},
        ]
    },
    'Instagram / Feed': {
        'en': 'Instagram / Feed',
        'he': 'Instagram / פיד',
        'questions': [
            {'q_en':'🏗️ User uploads photo — what processes it?',
             'q_he':'🏗️ משתמש מעלה תמונה — מה מעבד אותה?',
             'options_en':['Sync API call','Async worker + S3','Store in MySQL','Email it'],
             'options_he':['קריאת API סינכרונית','Worker אסינכרוני + S3','שמירה ב-MySQL','שלח באימייל'],
             'answer':1,
             'tip_en':'Async workers process/resize; S3 stores originals.',
             'tip_he':'Workers אסינכרוניים מעבדים/משנים גודל; S3 שומר מקור.'},
            {'q_en':'🏗️ Generate feed for 500M users?',
             'q_he':'🏗️ יצירת פיד ל-500M משתמשים?',
             'options_en':['Query DB every load','Pre-compute in Redis (fan-out)','Send emails','GraphQL only'],
             'options_he':['שאילתת DB בכל טעינה','חישוב מראש ב-Redis (fan-out)','שלח אימיילים','רק GraphQL'],
             'answer':1,
             'tip_en':'Fan-out on write: push new posts to followers caches.',
             'tip_he':'Fan-out on write: דחיפת פוסטים חדשים ל-cache של עוקבים.'},
            {'q_en':'🏗️ Images load slowly in Brazil?',
             'q_he':'🏗️ תמונות נטענות לאט בברזיל?',
             'options_en':['Bigger US server','CDN (CloudFront)','Compress to 1px','Nothing'],
             'options_he':['שרת US גדול יותר','CDN (CloudFront)','דחיסה ל-1px','כלום'],
             'answer':1,
             'tip_en':'CDN caches content at edge locations near users globally.',
             'tip_he':'CDN שומר תוכן בנקודות קרובות למשתמשים ברחבי העולם.'},
        ]
    },
    'YouTube / Video': {
        'en': 'YouTube / Video',
        'he': 'YouTube / וידאו',
        'questions': [
            {'q_en':'🏗️ Serve 4K video at multiple qualities?',
             'q_he':'🏗️ שידור וידאו 4K במספר רזולוציות?',
             'options_en':['Send original to all','Transcode async (360p/720p/1080p)','Compress to 240p','Stream raw bytes'],
             'options_he':['שלח מקור לכולם','Transcode אסינכרוני (360p/720p/1080p)','דחוס ל-240p','שדר bytes גולמיים'],
             'answer':1,
             'tip_en':'Async transcoding creates multiple resolutions; client picks by bandwidth.',
             'tip_he':'Transcoding אסינכרוני יוצר רזולוציות שונות; הלקוח בוחר לפי bandwidth.'},
            {'q_en':'🏗️ Video has 1B views — store count efficiently?',
             'q_he':'🏗️ לוידאו יש 1B צפיות — איך שומרים ספירה?',
             'options_en':['UPDATE in MySQL per view','Redis counter + batch flush','Count from logs','Ignore'],
             'options_he':['UPDATE ב-MySQL לכל צפייה','מונה Redis + שמירה בקבוצות','ספירה מ-logs','התעלם'],
             'answer':1,
             'tip_en':'Redis INCR is atomic and fast; batch-flush to DB periodically.',
             'tip_he':'Redis INCR אטומי ומהיר; שמירה ב-DB בקבוצות מדי פעם.'},
        ]
    },
    'Uber / נסיעה': {
        'en': 'Uber / Ride',
        'he': 'Uber / נסיעה',
        'questions': [
            {'q_en':'🏗️ Match rider to nearest driver?',
             'q_he':'🏗️ התאמת נוסע לנהג הקרוב ביותר?',
             'options_en':['Loop all drivers','Geospatial index (Redis GEO)','Call each driver','Random pick'],
             'options_he':['לולאה על כל הנהגים','אינדקס גיאוגרפי (Redis GEO)','התקשר לכל נהג','בחירה אקראית'],
             'answer':1,
             'tip_en':'Redis GEO stores coordinates and finds nearest in O(log n).',
             'tip_he':'Redis GEO שומר קואורדינטות ומוצא הקרוב ביותר ב-O(log n).'},
            {'q_en':'🏗️ 1M drivers updating location every 5 sec?',
             'q_he':'🏗️ 1M נהגים מעדכנים מיקום כל 5 שניות?',
             'options_en':['Write to MySQL each update','Write to Redis, async flush','Ignore old','Use cookies'],
             'options_he':['כתיבה ל-MySQL בכל עדכון','כתיבה ל-Redis, שמירה אסינכרונית','התעלם מישן','השתמש ב-cookies'],
             'answer':1,
             'tip_en':'Redis handles millions of writes/sec; async workers persist to DB.',
             'tip_he':'Redis מטפל במיליוני כתיבות/שניה; workers שומרים ל-DB אסינכרונית.'},
        ]
    },
}

# ═══════════════════════════════════════════════════════════════════════════
#  INTERVIEW QUESTIONS — bilingual, free chat
# ═══════════════════════════════════════════════════════════════════════════
INTERVIEW_QUESTIONS = [
    {'en': 'What is the difference between `==` and `===` in JavaScript?',
     'he': 'מה ההבדל בין `==` ל-`===` ב-JavaScript?'},
    {'en': 'Explain Big O notation and give an example.',
     'he': 'הסבר מה זה Big O notation ותן דוגמה.'},
    {'en': 'What is the difference between a process and a thread?',
     'he': 'מה ההבדל בין process ל-thread?'},
    {'en': 'What is REST and how does it work?',
     'he': 'מה זה REST ואיך זה עובד?'},
    {'en': 'What is a deadlock? How do you prevent it?',
     'he': 'מה זה deadlock? איך מונעים אותו?'},
    {'en': 'What are the differences between SQL and NoSQL databases?',
     'he': 'מה ההבדלים בין SQL ל-NoSQL?'},
    {'en': 'What is a closure in programming? Give an example.',
     'he': 'מה זה closure בתכנות? תן דוגמה.'},
    {'en': 'Explain the CAP theorem in distributed systems.',
     'he': 'הסבר את משפט CAP במערכות מבוזרות.'},
    {'en': 'What is the difference between synchronous and asynchronous programming?',
     'he': 'מה ההבדל בין תכנות סינכרוני לאסינכרוני?'},
    {'en': 'How does garbage collection work in modern languages?',
     'he': 'איך עובד garbage collection בשפות מודרניות?'},
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

TIMER_TOTAL = 10

def timer_bar(secs, total=TIMER_TOTAL):
    """Emoji clock + colored bar."""
    filled = round((secs / total) * 10)
    empty  = 10 - filled
    if secs > 10:  color = "🟢"; clock = "🕐"
    elif secs > 5: color = "🟡"; clock = "🕙"
    else:          color = "🔴"; clock = "🕛"
    bar = "▓" * filled + "░" * empty
    return f"{clock} `{bar}` *{secs}s*"

def send_game_question(code):
    room = game_rooms.get(code)
    if not room: return
    idx  = room['q_idx']
    qs   = room['questions']
    if idx >= len(qs):
        end_game(code)
        return
    qraw  = qs[idx]
    total = len(qs)
    room['answered_this_round'] = set()
    room['timer_active']        = True
    room['timer_msg_ids']       = {}

    # Send question per-player in their language
    for cid in list(room['players']):
        lang = get_lang(cid)
        q    = get_q(qraw, lang)
        qlbl = "שאלה" if lang == 'he' else "Q"
        m    = question_markup(q['options'], f'game_ans:{code}', code=code)
        # Truncate long questions for mobile
        q_text = q['q']
        if len(q_text) > 180:
            q_text = q_text[:177] + "..."
        try:
            bot.send_message(cid,
                f"⚡ *{qlbl} {idx+1}/{total}*\n\n{q_text}",
                parse_mode="Markdown", reply_markup=m)
        except Exception:
            pass

    # Send timer message separately
    time.sleep(0.3)
    for cid in list(room['players']):
        try:
            msg = bot.send_message(cid, timer_bar(TIMER_TOTAL), parse_mode="Markdown")
            room['timer_msg_ids'][cid] = msg.message_id
        except Exception:
            pass

    def live_timer():
        for secs in range(TIMER_TOTAL - 1, 0, -1):
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
            broadcast_room(code, f"⏰ _{', '.join(missed)}_")
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
user_progress = {}  # persistent stats per user

def get_lang(c): return user_langs.get(c, 'he')

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
MENU_PHOTO = "https://raw.githubusercontent.com/matan4749/hiring-hero-bot/main/Photo_Bot.jpg"

MENU_PHOTO_URL = "https://raw.githubusercontent.com/matan4749/hiring-hero-bot/main/Photo_Bot.jpg"
_MENU_PHOTO_CACHE = None

def send_main_menu(c, text):
    global _MENU_PHOTO_CACHE
    try:
        if _MENU_PHOTO_CACHE is None:
            r = requests.get(MENU_PHOTO_URL, timeout=10)
            if r.status_code == 200:
                _MENU_PHOTO_CACHE = r.content
        if _MENU_PHOTO_CACHE:
            import io
            bot.send_photo(c, io.BytesIO(_MENU_PHOTO_CACHE), caption=text,
                           parse_mode="Markdown", reply_markup=main_menu(c))
            return
    except Exception:
        pass
    bot.send_message(c, text, parse_mode="Markdown", reply_markup=main_menu(c))

def main_menu(c):
    lang = get_lang(c)
    m = types.InlineKeyboardMarkup(row_width=2)
    if lang == 'he':
        m.add(
            types.InlineKeyboardButton("🎙️ ראיון דמה",      callback_data='interview'),
            types.InlineKeyboardButton("⚡ DevDuel",   callback_data='python_menu'),
            types.InlineKeyboardButton("🏗️ System Design",  callback_data='sysdesign'),
            types.InlineKeyboardButton("🧩 LeetCode",        callback_data='leetcode'),
            types.InlineKeyboardButton("📄 ניתוח CV",        callback_data='cv'),
            types.InlineKeyboardButton("🔍 מנתח JD",         callback_data='jd'),
        )
        m.add(types.InlineKeyboardButton("⚡ פיצ'רים מיוחדים 🔥", callback_data='extras_menu'))
        m.row(
            types.InlineKeyboardButton("🌐 English", callback_data='lang'),
            types.InlineKeyboardButton("ℹ️ אודות",   callback_data='about'),
        )
    else:
        m.add(
            types.InlineKeyboardButton("🎙️ Mock Interview", callback_data='interview'),
            types.InlineKeyboardButton("⚡ DevDuel",   callback_data='python_menu'),
            types.InlineKeyboardButton("🏗️ System Design",  callback_data='sysdesign'),
            types.InlineKeyboardButton("🧩 LeetCode",       callback_data='leetcode'),
            types.InlineKeyboardButton("📄 CV Analysis",    callback_data='cv'),
            types.InlineKeyboardButton("🔍 JD Analyzer",    callback_data='jd'),
        )
        m.add(types.InlineKeyboardButton("⚡ Special Features 🔥", callback_data='extras_menu'))
        m.row(
            types.InlineKeyboardButton("🌐 עברית",  callback_data='lang'),
            types.InlineKeyboardButton("ℹ️ About",  callback_data='about'),
        )
    return m

def extras_menu(lang='he'):
    m = types.InlineKeyboardMarkup(row_width=1)
    if lang == 'he':
        m.add(
            types.InlineKeyboardButton("📊 הפרופיל שלי — מעקב התקדמות",             callback_data='my_profile'),
            types.InlineKeyboardButton("🎯 אתגר יומי — Python + LeetCode + ראיון",  callback_data='daily_challenge'),
            types.InlineKeyboardButton("⚡ Speed Round — כמה שאלות ב-60 שניות",     callback_data='speed_round'),
            types.InlineKeyboardButton("◀️ חזרה לתפריט",                             callback_data='menu'),
        )
    else:
        m.add(
            types.InlineKeyboardButton("📊 My Profile — progress tracking",              callback_data='my_profile'),
            types.InlineKeyboardButton("🎯 Daily Challenge — Python+LeetCode+Interview", callback_data='daily_challenge'),
            types.InlineKeyboardButton("⚡ Speed Round — max questions in 60 seconds",   callback_data='speed_round'),
            types.InlineKeyboardButton("◀️ Back to menu",                                callback_data='menu'),
        )
    return m

def back_btn(help_key=None):
    m = types.InlineKeyboardMarkup(row_width=2)
    if help_key:
        m.add(
            types.InlineKeyboardButton("❓ עזרה", callback_data=f'help:{help_key}'),
            types.InlineKeyboardButton("🏠 תפריט", callback_data='menu'),
        )
    else:
        m.add(types.InlineKeyboardButton("🏠 תפריט", callback_data='menu'))
    return m

HELP_TEXTS = {
    'interview': (
        "🎙️ *ראיון דמה — איך עובד?*\n\n"
        "אני אשאל אותך שאלות ראיון אמיתיות מהתעשייה.\n"
        "✍️ *כתוב את תשובתך* בצ'אט — בחופשיות, כמו בראיון אמיתי.\n"
        "אני אתן לך פידבק מיידי על התשובה שלך.\n\n"
        "כפתורים:\n"
        "➡️ *Next* — שאלה הבאה אחרי הפידבק\n"
        "⏭️ *Skip* — דלג על שאלה\n"
        "🛑 *End* — סיים את הראיון"
    ),
    'python': (
        "🐍 *Python Trivia — איך עובד?*\n\n"
        "שאלות Python עם 4 תשובות לבחירה.\n\n"
        "👤 *Solo* — תרגול עצמאי, 5 שאלות אקראיות\n"
        "🎮 *Multiplayer* — צור משחק, שתף קוד לחברים\n"
        "המשחק מתחיל אוטומטית כשכולם מצטרפים!\n\n"
        "⏱️ 15 שניות לכל שאלה\n"
        "📊 לוח תוצאות אחרי כל שאלה"
    ),
    'sysdesign': (
        "🏗️ *System Design — איך עובד?*\n\n"
        "שאלות עיצוב מערכות כמו בראיונות FAANG.\n"
        "בחר נושא (WhatsApp, YouTube, Uber...) ותענה על שאלות עם 4 אפשרויות.\n\n"
        "💡 אחרי כל תשובה תקבל הסבר מפורט למה זו התשובה הנכונה.\n"
        "📊 ציון בסוף כל נושא."
    ),
    'leetcode': (
        "🧩 *LeetCode — איך עובד?*\n\n"
        "אני מייצר לך שאלת LeetCode רמת Easy.\n"
        "קרא את השאלה, חשוב על הפתרון.\n\n"
        "💡 לחץ *Show Solution* לראות את הפתרון ב-Python\n"
        "🔄 לחץ *New Question* לשאלה חדשה"
    ),
    'cv': (
        "📄 *ניתוח CV — איך עובד?*\n\n"
        "שלח לי את קורות החיים שלך באחת מהדרכים:\n"
        "• 📎 קובץ PDF\n"
        "• 📎 קובץ Word (DOCX)\n"
        "• ✍️ הדבק את הטקסט ישירות\n\n"
        "אני אחזיר לך:\n"
        "✅ ניקוד ATS (1-10)\n"
        "✅ 3 חוזקות\n"
        "✅ 3 שיפורים\n"
        "✅ דוגמת bullet point משודרגת"
    ),
    'jd': (
        "🔍 *מנתח JD — איך עובד?*\n\n"
        "הדבק את תיאור המשרה (Job Description) מהאתר.\n\n"
        "אני אחלץ לך:\n"
        "🔑 10 מילות מפתח לשים ב-CV\n"
        "📋 דרישות חובה\n"
        "💡 3 טיפים לאיך להתאים את ה-CV למשרה"
    ),
}

def with_help_btn(markup, help_key):
    """Add help button to existing markup."""
    markup.add(types.InlineKeyboardButton("❓ עזרה", callback_data=f'help:{help_key}'))
    return markup

def python_mode_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("👤 Solo — Practice",            callback_data='solo_setup'),
        types.InlineKeyboardButton("🎮 Create Multiplayer Game",    callback_data='python_create'),
        types.InlineKeyboardButton("🔗 Join a Game",                callback_data='python_join'),
        types.InlineKeyboardButton("❓ Help",                       callback_data='help:python'),
        types.InlineKeyboardButton("◀️ Back",                      callback_data='menu'),
    )
    return m

def solo_difficulty_menu():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("🟢 Easy",   callback_data='python_solo:easy'),
        types.InlineKeyboardButton("🟡 Medium", callback_data='python_solo:medium'),
        types.InlineKeyboardButton("🔴 Hard",   callback_data='python_solo:hard'),
        types.InlineKeyboardButton("🎲 Mixed",  callback_data='python_solo:mixed'),
    )
    m.add(types.InlineKeyboardButton("◀️ Back", callback_data='python_menu'))
    return m

def game_setup_menu():
    m = types.InlineKeyboardMarkup(row_width=3)
    m.add(types.InlineKeyboardButton("─── Difficulty ───", callback_data='noop'))
    m.add(
        types.InlineKeyboardButton("🟢 Easy",   callback_data='game_diff:easy'),
        types.InlineKeyboardButton("🟡 Medium", callback_data='game_diff:medium'),
        types.InlineKeyboardButton("🔴 Hard",   callback_data='game_diff:hard'),
    )
    m.add(types.InlineKeyboardButton("🎲 Mixed",  callback_data='game_diff:mixed'))
    m.add(types.InlineKeyboardButton("◀️ Back",   callback_data='python_menu'))
    return m

def game_count_menu(diff):
    m = types.InlineKeyboardMarkup(row_width=4)
    m.add(types.InlineKeyboardButton("─── Questions ───", callback_data='noop'))
    btns = [types.InlineKeyboardButton(str(n), callback_data=f'game_count:{diff}:{n}') for n in [5, 10, 15, 20]]
    m.add(*btns)
    m.add(types.InlineKeyboardButton("◀️ Back", callback_data='python_create'))
    return m

def sd_topic_menu(lang='he'):
    m = types.InlineKeyboardMarkup(row_width=2)
    for key, data in SD_QUESTIONS.items():
        label = data.get(lang, key)
        m.add(types.InlineKeyboardButton(label, callback_data=f"sd_topic:{key}"))
    m.row(
        types.InlineKeyboardButton("❓ עזרה" if lang=='he' else "❓ Help", callback_data='help:sysdesign'),
        types.InlineKeyboardButton("◀️ חזרה" if lang=='he' else "◀️ Back", callback_data='menu'),
    )
    return m

# ═══════════════════════════════════════════════════════════════════════════
#  SOLO QUESTION SENDERS (with timer)
# ═══════════════════════════════════════════════════════════════════════════
def send_solo_question(c):
    s    = user_sessions.get(c)
    if not s: return
    lang = get_lang(c)
    idx  = s['q_idx']
    qs   = s['questions']
    if idx >= len(qs):
        score = s['score']
        total = len(qs)
        t     = title_for_score(score, total)
        done  = "✅ *הטריוויה הסתיימה!*" if lang == 'he' else "✅ *Quiz Complete!*"
        lbl   = "ניקוד" if lang == 'he' else "Score"
        bot.send_message(c,
            f"{done}\n\n"
            f"{lbl}: *{score} / {total}*\n"
            f"`{score_bar(score, total)}`\n\n"
            f"*{t}* 🎓",
            parse_mode="Markdown", reply_markup=back_btn())
        user_states[c] = None
        return
    qraw = qs[idx]
    q    = get_q(qraw, lang)
    m    = question_markup(q['options'], 'solo_ans', solo=True)
    q_text = q['q']
    if len(q_text) > 200:
        q_text = q_text[:197] + "..."
    bot.send_message(c,
        f"⚡ *{'שאלה' if lang=='he' else 'Q'} {idx+1}/{len(qs)}*\n\n{q_text}",
        parse_mode="Markdown", reply_markup=m)

    # Live timer message
    try:
        timer_msg = bot.send_message(c, timer_bar(TIMER_TOTAL), parse_mode="Markdown")
        timer_mid = timer_msg.message_id
    except Exception:
        timer_mid = None

    def solo_timer(q_idx):
        for secs in range(TIMER_TOTAL - 1, 0, -1):
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
        bot.send_message(c, "⏰ *נגמר הזמן!* עוברים הלאה...", parse_mode="Markdown")
        sess['q_idx'] += 1
        time.sleep(0.5)
        send_solo_question(c)
    threading.Thread(target=solo_timer, args=(idx,), daemon=True).start()

def send_sd_question(c):
    s    = user_sessions.get(c)
    if not s: return
    lang = get_lang(c)
    idx  = s['q_idx']
    topic_key  = s['topic']
    topic_data = SD_QUESTIONS.get(topic_key, {})
    qs         = topic_data.get('questions', [])
    topic_label = topic_data.get(lang, topic_key)
    if idx >= len(qs):
        score = s['score']
        total = len(qs)
        done  = "✅ *System Design — הסתיים!*" if lang == 'he' else "✅ *System Design Complete!*"
        lbl   = "ניקוד" if lang == 'he' else "Score"
        bot.send_message(c,
            f"*{DIV}*\n{done}\n*{DIV}*\n\n"
            f"{lbl}: *{score} / {total}*\n"
            f"`{score_bar(score, total)}`\n\n"
            f"*{title_for_score(score, total)}* 🎓",
            parse_mode="Markdown", reply_markup=back_btn())
        user_states[c] = None
        return
    qraw = qs[idx]
    q    = get_q(qraw, lang)
    m    = question_markup(q['options'], 'sd_ans', solo=True)
    qlbl = "שאלה" if lang == 'he' else "Q"
    bot.send_message(c,
        f"*{DIV}*\n🏗️ *{qlbl}{idx+1} / {len(qs)}* — _{topic_label}_\n*{DIV}*\n\n{q['q']}",
        parse_mode="Markdown", reply_markup=m)

def send_interview_question(c):
    s    = user_sessions.get(c)
    if not s: return
    lang  = get_lang(c)
    idx   = s['q_idx']
    total = len(INTERVIEW_QUESTIONS)
    if idx >= total:
        score = s.get('score', 0)
        done  = "🎙️ *הראיון הסתיים!*" if lang == 'he' else "🎙️ *Interview Complete!*"
        msg   = (f"עניתי על *{score} / {total}* שאלות\n\nכל הכבוד! עבור על הפידבק למעלה 💪"
                 if lang == 'he' else
                 f"✅ Answered: *{score} / {total}* questions\n\nGreat practice! Review the feedback above 💪")
        bot.send_message(c,
            f"*{DIV}*\n{done}\n*{DIV}*\n\n{msg}",
            parse_mode="Markdown", reply_markup=back_btn())
        user_states[c] = None
        return
    q_dict = INTERVIEW_QUESTIONS[idx]
    q_text = q_dict.get(lang, q_dict['en'])
    qlbl   = "שאלה" if lang == 'he' else "Question"
    hint   = "_כתוב את תשובתך בצ'אט..._" if lang == 'he' else "_Type your answer in the chat..._"
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("⏭️ דלג" if lang=='he' else "⏭️ Skip", callback_data='iv_skip'),
        types.InlineKeyboardButton("🛑 סיים" if lang=='he' else "🛑 End",  callback_data='iv_end'),
    )
    bot.send_message(c,
        f"*{DIV}*\n🎙️ *{qlbl} {idx+1} / {total}*\n*{DIV}*\n\n💬 {q_text}\n\n{hint}",
        parse_mode="Markdown", reply_markup=m)

# ═══════════════════════════════════════════════════════════════════════════
#  COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════════
def welcome_text(c, name=''):
    lang = get_lang(c)
    greeting = f"👋 *שלום, {name}!*\n\n" if name else "👋 *שלום!*\n\n"
    if lang == 'he':
        return (
            f"{greeting}"
            f"⚡ *DevBoost Career Coach*\n"
            f"_{DIV}_\n\n"
            f"הבוט שיהפוך אותך למפתח שכל חברה רוצה לגייס 🚀\n\n"
            f"_בחר מה תרצה לעשות:_"
        )
    greeting_en = f"👋 *Hey, {name}!*\n\n" if name else "👋 *Hey there!*\n\n"
    return (
        f"{greeting_en}"
        f"⚡ *DevBoost Career Coach*\n"
        f"_{DIV}_\n\n"
        f"The AI bot that turns you into a developer every company wants to hire 🚀\n\n"
        f"_Choose what you'd like to do:_"
    )

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    c = message.chat.id
    user_states[c] = None
    player_rooms.pop(c, None)
    try:
        name = message.from_user.first_name or ''
    except Exception:
        name = ''
    send_main_menu(c, welcome_text(c, name))

@bot.message_handler(commands=['interview'])
def cmd_interview(message):
    message.chat.id
    class FakeCall:
        def __init__(self, cid): self.message = type('M', (), {'chat': type('C', (), {'id': cid})()})(); self.data = 'interview'; self.id = 0; self.from_user = message.from_user
    handle_callbacks(FakeCall(message.chat.id))

@bot.message_handler(commands=['python'])
def cmd_python(message):
    class FakeCall:
        def __init__(self, cid): self.message = type('M', (), {'chat': type('C', (), {'id': cid})()})(); self.data = 'python_menu'; self.id = 0; self.from_user = message.from_user
    handle_callbacks(FakeCall(message.chat.id))

@bot.message_handler(commands=['sysdesign'])
def cmd_sysdesign(message):
    class FakeCall:
        def __init__(self, cid): self.message = type('M', (), {'chat': type('C', (), {'id': cid})()})(); self.data = 'sysdesign'; self.id = 0; self.from_user = message.from_user
    handle_callbacks(FakeCall(message.chat.id))

@bot.message_handler(commands=['leetcode'])
def cmd_leetcode(message):
    class FakeCall:
        def __init__(self, cid): self.message = type('M', (), {'chat': type('C', (), {'id': cid})()})(); self.data = 'leetcode'; self.id = 0; self.from_user = message.from_user
    handle_callbacks(FakeCall(message.chat.id))

@bot.message_handler(commands=['cv'])
def cmd_cv(message):
    class FakeCall:
        def __init__(self, cid): self.message = type('M', (), {'chat': type('C', (), {'id': cid})()})(); self.data = 'cv'; self.id = 0; self.from_user = message.from_user
    handle_callbacks(FakeCall(message.chat.id))

@bot.message_handler(commands=['jd'])
def cmd_jd(message):
    class FakeCall:
        def __init__(self, cid): self.message = type('M', (), {'chat': type('C', (), {'id': cid})()})(); self.data = 'jd'; self.id = 0; self.from_user = message.from_user
    handle_callbacks(FakeCall(message.chat.id))

# ═══════════════════════════════════════════════════════════════════════════
#  SPEED ROUND HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def send_speed_question(c, remaining=60):
    s    = user_sessions.get(c)
    if not s: return
    lang = get_lang(c)
    qraw = s['questions'][s['q_idx']]
    q    = get_q(qraw, lang)
    num  = s['score']
    time_lbl = f"⏱ *{remaining}s*" if remaining < 60 else "⏱ *60s*"
    m    = question_markup(q['options'], 'speed_ans', solo=True)
    bot.send_message(c,
        f"⚡ *#{num+1}* {time_lbl}\n\n{q['q']}",
        parse_mode="Markdown", reply_markup=m)

def _finish_speed(c):
    if user_states.get(c) != 'SPEED': return
    user_states[c] = None
    lang  = get_lang(c)
    s     = user_sessions.get(c, {})
    score = s.get('score', 0)
    # Update progress
    p = user_progress.setdefault(c, {})
    if score > p.get('speed_best', 0):
        p['speed_best'] = score
    title = "⚡ *Speed Round הסתיים!*" if lang == 'he' else "⚡ *Speed Round Over!*"
    record = "🏆 *שיא חדש!*" if score == p['speed_best'] and score > 0 else ""
    lbl    = "ענית על" if lang == 'he' else "You answered"
    q_lbl  = "שאלות" if lang == 'he' else "questions"
    bot.send_message(c,
        f"*{DIV}*\n{title}\n*{DIV}*\n\n{lbl} *{score}* {q_lbl}! {record}",
        parse_mode="Markdown", reply_markup=back_btn())

def _finish_daily(c):
    user_states[c] = None
    lang  = get_lang(c)
    s     = user_sessions.get(c, {})
    score = s.get('daily_score', 0)
    p     = user_progress.setdefault(c, {})
    p['daily_done'] = p.get('daily_done', 0) + 1
    p['daily_date'] = s.get('daily_date', datetime.date.today().isoformat())
    title = "🎯 *אתגר יומי הושלם!*" if lang == 'he' else "🎯 *Daily Challenge Complete!*"
    msg   = (f"עשית עבודה מדהימה היום! 🏆\n\nחזור מחר לאתגר חדש 🌅"
             if lang == 'he' else
             f"Amazing work today! 🏆\n\nCome back tomorrow for a new challenge 🌅")
    bot.send_message(c,
        f"*{DIV}*\n{title}\n*{DIV}*\n\n{msg}",
        parse_mode="Markdown", reply_markup=back_btn())

# ═══════════════════════════════════════════════════════════════════════════
#  CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    c    = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    # ── Help ──
    if data.startswith('help:'):
        key  = data.split(':', 1)[1]
        text = HELP_TEXTS.get(key, "❓ אין מידע עזרה לפיצ'ר זה.")
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("◀️ חזרה", callback_data=f'help_back:{key}'))
        bot.send_message(c, text, parse_mode="Markdown", reply_markup=m)
        return

    if data.startswith('help_back:'):
        key = data.split(':', 1)[1]
        # Return to the relevant feature entry point
        back_map = {
            'interview': 'interview',
            'python':    'python_menu',
            'sysdesign': 'sysdesign',
            'leetcode':  'leetcode',
            'cv':        'cv',
            'jd':        'jd',
        }
        # Simulate pressing the feature button
        call.data = back_map.get(key, 'menu')
        handle_callbacks(call)
        return

    # ── Menu ──
    if data == 'noop':
        return

    if data == 'menu':
        user_states[c] = None
        try:
            name = call.from_user.first_name or ''
        except Exception:
            name = ''
        send_main_menu(c, welcome_text(c, name))
        return

    # ── Language ──
    if data == 'lang':
        user_langs[c] = 'he' if get_lang(c) == 'en' else 'en'
        lang = get_lang(c)
        txt = "🌐 *שפה שונתה לעברית* ✅" if lang == 'he' else "🌐 *Language set to English* ✅"
        send_main_menu(c, txt)
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
        lang  = get_lang(c)
        title = "בחר מצב:" if lang == 'he' else "Choose your mode:"
        bot.send_message(c,
            f"*{DIV}*\n⚡ *DevDuel*\n*{DIV}*\n\n{title}",
            parse_mode="Markdown", reply_markup=python_mode_menu())
        return

    if data == 'solo_setup':
        lang = get_lang(c)
        desc = "בחר רמת קושי:" if lang == 'he' else "Choose difficulty:"
        bot.send_message(c, f"👤 *Solo Practice*\n\n{desc}", parse_mode="Markdown", reply_markup=solo_difficulty_menu())
        return

    if data.startswith('python_solo:'):
        diff = data.split(':')[1]
        lang = get_lang(c)
        if diff == 'easy':    pool = EASY_Q
        elif diff == 'medium': pool = MEDIUM_Q
        elif diff == 'hard':   pool = HARD_Q
        else:                  pool = ALL_QUESTIONS
        qs = random.sample(pool, min(5, len(pool)))
        user_sessions[c] = {'questions': qs, 'q_idx': 0, 'score': 0}
        user_states[c]   = 'SOLO'
        diff_labels = {'easy':'🟢 Easy','medium':'🟡 Medium','hard':'🔴 Hard','mixed':'🎲 Mixed'}
        lbl = diff_labels.get(diff, diff)
        msg = (f"⚡ *Solo Mode — {lbl}*\n5 שאלות • 10 שניות לשאלה\n\nבהצלחה! 🚀"
               if lang == 'he' else
               f"⚡ *Solo Mode — {lbl}*\n5 questions • 10 seconds each\n\nLet's go! 🚀")
        bot.send_message(c, msg, parse_mode="Markdown")
        send_solo_question(c)
        return

    if data == 'solo_quit':
        lang = get_lang(c)
        user_states[c] = None
        msg = "👋 *הפסקת את הטריוויה.* להתראות!" if lang == 'he' else "👋 *Quiz stopped.* See you next time!"
        bot.send_message(c, msg, parse_mode="Markdown", reply_markup=back_btn())
        return

    if data.startswith('solo_ans:'):
        if user_states.get(c) != 'SOLO': return
        chosen = int(data.split(':')[1])
        s      = user_sessions.get(c)
        if not s: return
        lang   = get_lang(c)
        qraw   = s['questions'][s['q_idx']]
        q      = get_q(qraw, lang)
        p      = user_progress.setdefault(c, {})
        p['python_total'] = p.get('python_total', 0) + 1
        if chosen == q['answer']:
            s['score'] += 1
            p['python_correct'] = p.get('python_correct', 0) + 1
            correct_msg = "נכון!" if lang == 'he' else "Correct!"
            bot.send_message(c, f"✅ *{correct_msg}* +1 🎉\n{q['tip']}", parse_mode="Markdown")
        else:
            wrong_msg   = "טעות!" if lang == 'he' else "Wrong!"
            correct_lbl = "נכון" if lang == 'he' else "Correct"
            bot.send_message(c,
                f"❌ *{wrong_msg}*\n"
                f"{correct_lbl}: {COLORS[q['answer']]} {SHAPES[q['answer']]} _{q['options'][q['answer']]}_\n\n"
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
        lang  = get_lang(c)
        title = "⚡ *DevDuel — צור משחק*" if lang == 'he' else "⚡ *DevDuel — Create Game*"
        desc  = "בחר רמת קושי:" if lang == 'he' else "Choose difficulty:"
        bot.send_message(c, f"{title}\n\n{desc}", parse_mode="Markdown", reply_markup=game_setup_menu())
        return

    if data.startswith('game_diff:'):
        diff = data.split(':')[1]
        lang = get_lang(c)
        diff_labels = {'easy':'🟢 Easy','medium':'🟡 Medium','hard':'🔴 Hard','mixed':'🎲 Mixed'}
        lbl  = diff_labels.get(diff, diff)
        desc = f"בחרת *{lbl}*\nכמה שאלות?" if lang == 'he' else f"Difficulty: *{lbl}*\nHow many questions?"
        bot.send_message(c, desc, parse_mode="Markdown", reply_markup=game_count_menu(diff))
        return

    if data.startswith('game_count:'):
        _, diff, n_str = data.split(':')
        n     = int(n_str)
        # Build question pool by difficulty
        if diff == 'easy':   pool = EASY_Q
        elif diff == 'medium': pool = MEDIUM_Q
        elif diff == 'hard':   pool = HARD_Q
        else:                  pool = ALL_QUESTIONS
        if len(pool) < n:
            pool = pool * (n // len(pool) + 1)
        qs   = random.sample(pool, n)
        code = gen_code()
        name = get_display_name(c)
        diff_labels = {'easy':'🟢 Easy','medium':'🟡 Medium','hard':'🔴 Hard','mixed':'🎲 Mixed'}
        game_rooms[code] = {
            'host':                c,
            'players':             {c: {'name': name, 'score': 0, 'answered': 0}},
            'questions':           qs,
            'q_idx':               0,
            'active':              False,
            'answered_this_round': set(),
            'max_players':         20,
            'timer_active':        False,
            'lobby_msg_id':        None,
            'difficulty':          diff,
        }
        player_rooms[c] = code
        user_states[c]  = 'GAME_LOBBY'
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("🚀 Start Game!", callback_data=f'game_start:{code}'))
        m.add(types.InlineKeyboardButton("🛑 Cancel",      callback_data='game_cancel'))
        sent = bot.send_message(c,
            f"⚡ *DevDuel — Game Created!*\n\n"
            f"┌─────────────────────┐\n"
            f"│   🎯 Code:  *{code}*    │\n"
            f"└─────────────────────┘\n\n"
            f"🎚️ Difficulty: *{diff_labels[diff]}*\n"
            f"❓ Questions: *{n}*\n"
            f"👥 Players: *1 / 20*\n"
            f"🟢 *{name}* _(you)_\n\n"
            f"📲 Share the code with friends!\n"
            f"_Start whenever you're ready._",
            parse_mode="Markdown", reply_markup=m)
        game_rooms[code]['lobby_msg_id'] = sent.message_id
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
            f"5 questions — Good luck! 🍀")
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
            bot.answer_callback_query(call.id, "⏳ כבר ענית!" if get_lang(c)=='he' else "⏳ Already answered!")
            return
        room['answered_this_round'].add(c)
        lang   = get_lang(c)
        qraw   = room['questions'][room['q_idx']]
        q      = get_q(qraw, lang)
        player = room['players'][c]
        player['answered'] += 1
        if chosen == q['answer']:
            player['score'] += 1
            correct_msg = "נכון!" if lang == 'he' else "Correct!"
            bot.send_message(c, f"✅ *{correct_msg}* +1 🎉\n{q['tip']}", parse_mode="Markdown")
        else:
            wrong_msg   = "טעות!" if lang == 'he' else "Wrong!"
            correct_lbl = "נכון" if lang == 'he' else "Correct"
            bot.send_message(c,
                f"❌ *{wrong_msg}*\n"
                f"{correct_lbl}: {COLORS[q['answer']]} {SHAPES[q['answer']]} _{q['options'][q['answer']]}_\n\n"
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
        lang = get_lang(c)
        title = "בחר מערכת לעיצוב:" if lang == 'he' else "Choose a system:"
        bot.send_message(c,
            f"*{DIV}*\n🏗️ *System Design*\n*{DIV}*\n\n{title}",
            parse_mode="Markdown", reply_markup=sd_topic_menu(lang))
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
        s      = user_sessions.get(c)
        if not s: return
        lang   = get_lang(c)
        topic_data = SD_QUESTIONS.get(s['topic'], {})
        qraw   = topic_data.get('questions', [])[s['q_idx']]
        q      = get_q(qraw, lang)
        if chosen == q['answer']:
            s['score'] += 1
            tip_lbl = "טיפ" if lang == 'he' else "Tip"
            bot.send_message(c, f"✅ *{'נכון!' if lang=='he' else 'Correct!'}*\n💡 _{q['tip']}_", parse_mode="Markdown")
        else:
            wrong_lbl   = "טעות!" if lang == 'he' else "Wrong!"
            correct_lbl = "תשובה נכונה" if lang == 'he' else "Correct"
            bot.send_message(c,
                f"❌ *{wrong_lbl}*\n{correct_lbl}: {COLORS[q['answer']]} _{q['options'][q['answer']]}_\n\n💡 _{q['tip']}_",
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
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("❓ עזרה", callback_data='help:interview'))
        bot.send_message(c,
            f"*{DIV}*\n"
            f"🎙️ *ראיון דמה*\n"
            f"*{DIV}*\n\n"
            f"אשאל אותך *{len(INTERVIEW_QUESTIONS)} שאלות* ראיון.\n"
            f"✍️ *כתוב את תשובתך* בצ'אט — אתן לך פידבק אמיתי! 💪\n\n"
            f"_בהצלחה!_ 🚀",
            parse_mode="Markdown", reply_markup=m)
        send_interview_question(c)
        return

    if data == 'iv_next':
        if user_states.get(c) != 'INTERVIEW': return
        s = user_sessions.get(c)
        if not s: return
        s['q_idx'] += 1
        send_interview_question(c)
        return

    if data == 'iv_skip':
        if user_states.get(c) != 'INTERVIEW': return
        s = user_sessions.get(c)
        if not s: return
        s['q_idx'] += 1
        bot.send_message(c, "⏭️ _Skipped._", parse_mode="Markdown")
        send_interview_question(c)
        return

    if data == 'iv_end':
        user_states[c] = None
        s = user_sessions.get(c, {})
        answered = s.get('score', 0)
        bot.send_message(c,
            f"🛑 *Interview ended.*\nYou answered *{answered}* questions. Keep practicing! 💪",
            parse_mode="Markdown", reply_markup=back_btn())
        return

    # ════════════════════════════════════════════════════
    #  LEETCODE
    # ════════════════════════════════════════════════════
    if data == 'leetcode':
        bot.send_message(c, "🧩 _מייצר שאלת LeetCode..._", parse_mode="Markdown")
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
                types.InlineKeyboardButton("💡 פתרון",    callback_data='leet_sol'),
                types.InlineKeyboardButton("🔄 שאלה חדשה", callback_data='leetcode'),
            )
            m.row(
                types.InlineKeyboardButton("❓ עזרה",   callback_data='help:leetcode'),
                types.InlineKeyboardButton("🏠 תפריט",  callback_data='menu'),
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
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(
            types.InlineKeyboardButton("❓ עזרה", callback_data='help:cv'),
            types.InlineKeyboardButton("🏠 תפריט", callback_data='menu'),
        )
        bot.send_message(c,
            f"*{DIV}*\n📄 *ניתוח CV*\n*{DIV}*\n\n"
            "שלח לי את קורות החיים שלך:\n"
            "• 📎 קובץ PDF / Word\n"
            "• ✍️ הדבק טקסט ישירות\n\n"
            "_אחזיר לך ניקוד ATS + שיפורים!_",
            parse_mode="Markdown", reply_markup=m)
        return

    if data == 'jd':
        user_states[c] = 'JD'
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(
            types.InlineKeyboardButton("❓ עזרה", callback_data='help:jd'),
            types.InlineKeyboardButton("🏠 תפריט", callback_data='menu'),
        )
        bot.send_message(c,
            f"*{DIV}*\n🔍 *מנתח משרות*\n*{DIV}*\n\n"
            "הדבק את תיאור המשרה (Job Description).\n\n"
            "_אחלץ Keywords + טיפים להתאמת ה-CV!_",
            parse_mode="Markdown", reply_markup=m)
        return

    # ════════════════════════════════════════════════════
    #  EXTRAS MENU
    # ════════════════════════════════════════════════════
    if data == 'extras_menu':
        lang = get_lang(c)
        title = "⚡ *פיצ'רים מיוחדים*" if lang == 'he' else "⚡ *Special Features*"
        desc  = "_פיצ'רים שלא תמצא בשום בוט אחר:_" if lang == 'he' else "_Features you won't find anywhere else:_"
        bot.send_message(c,
            f"*{DIV}*\n{title}\n*{DIV}*\n\n{desc}",
            parse_mode="Markdown", reply_markup=extras_menu(lang))
        return

    # ════════════════════════════════════════════════════
    #  🧠 AI DYNAMIC INTERVIEW
    # ════════════════════════════════════════════════════
    if data == 'ai_interview':
        lang = get_lang(c)
        user_sessions[c] = {'ai_iv_history': [], 'ai_iv_count': 0}
        user_states[c]   = 'AI_INTERVIEW'
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("🛑 סיים" if lang=='he' else "🛑 End", callback_data='ai_iv_end'))
        intro = (
            f"*{DIV}*\n🧠 *ראיון AI דינמי*\n*{DIV}*\n\n"
            "זהו ראיון חכם — אני מתאים את השאלות לפי התשובות שלך! 🎯\n"
            "✍️ ענה בחופשיות, אני אשאל follow-up רלוונטי.\n\n"
            "_מתחילים!_ 🚀"
            if lang == 'he' else
            f"*{DIV}*\n🧠 *AI Dynamic Interview*\n*{DIV}*\n\n"
            "This is a smart interview — I adapt questions based on your answers! 🎯\n"
            "✍️ Answer freely, I'll ask relevant follow-ups.\n\n"
            "_Let's go!_ 🚀"
        )
        bot.send_message(c, intro, parse_mode="Markdown", reply_markup=m)
        # Ask first question via AI
        bot.send_chat_action(c, 'typing')
        lang_instr = "שאל את השאלה הראשונה לראיון בעברית, שאלה פתוחה לא טכנית מדי." if lang == 'he' else "Ask the first interview question in English, open-ended, not too technical."
        first_q = call_ai("אתה מראיין טכני בכיר." if lang=='he' else "You are a senior technical interviewer.", lang_instr)
        user_sessions[c]['ai_iv_history'].append({'role': 'assistant', 'content': first_q})
        bot.send_message(c, f"💬 {first_q}", parse_mode="Markdown", reply_markup=m)
        return

    if data == 'ai_iv_end':
        lang = get_lang(c)
        user_states[c] = None
        count = user_sessions.get(c, {}).get('ai_iv_count', 0)
        msg = (f"🛑 *הראיון הסתיים!*\nעניתי על *{count}* שאלות. כל הכבוד! 💪"
               if lang == 'he' else
               f"🛑 *Interview ended!*\nYou answered *{count}* questions. Great job! 💪")
        bot.send_message(c, msg, parse_mode="Markdown", reply_markup=back_btn())
        return

    # ════════════════════════════════════════════════════
    #  📊 MY PROFILE
    # ════════════════════════════════════════════════════
    if data == 'my_profile':
        lang = get_lang(c)
        p    = user_progress.get(c, {})
        title = "📊 *הפרופיל שלי*" if lang == 'he' else "📊 *My Profile*"

        def bar(score, total):
            if total == 0: return "░░░░░░░░░░ 0%"
            pct = int((score / total) * 10)
            return f"{'▓' * pct}{'░' * (10-pct)} {int(score/total*100)}%"

        if lang == 'he':
            lines = [
                f"*{DIV}*\n{title}\n*{DIV}*\n",
                f"🐍 *Python Trivia:*\n`{bar(p.get('python_correct',0), p.get('python_total',0))}` — {p.get('python_correct',0)}/{p.get('python_total',0)} נכון",
                f"🏗️ *System Design:*\n`{bar(p.get('sd_correct',0), p.get('sd_total',0))}` — {p.get('sd_correct',0)}/{p.get('sd_total',0)} נכון",
                f"🎯 *אתגרים יומיים:* {p.get('daily_done',0)} הושלמו",
                f"⚡ *Speed Round שיא:* {p.get('speed_best',0)} שאלות",
                f"🎙️ *ראיונות שהושלמו:* {p.get('interviews_done',0)}",
            ]
        else:
            lines = [
                f"*{DIV}*\n{title}\n*{DIV}*\n",
                f"🐍 *Python Trivia:*\n`{bar(p.get('python_correct',0), p.get('python_total',0))}` — {p.get('python_correct',0)}/{p.get('python_total',0)} correct",
                f"🏗️ *System Design:*\n`{bar(p.get('sd_correct',0), p.get('sd_total',0))}` — {p.get('sd_correct',0)}/{p.get('sd_total',0)} correct",
                f"🎯 *Daily Challenges:* {p.get('daily_done',0)} completed",
                f"⚡ *Speed Round Best:* {p.get('speed_best',0)} questions",
                f"🎙️ *Interviews completed:* {p.get('interviews_done',0)}",
            ]
        bot.send_message(c, "\n\n".join(lines), parse_mode="Markdown", reply_markup=back_btn())
        return

    # ════════════════════════════════════════════════════
    #  🎯 DAILY CHALLENGE
    # ════════════════════════════════════════════════════
    if data == 'daily_challenge':
        lang  = get_lang(c)
        today = datetime.date.today().isoformat()
        p     = user_progress.setdefault(c, {})
        if p.get('daily_date') == today:
            done_msg = ("✅ *כבר השלמת את האתגר היומי להיום!*\nחזור מחר לאתגר חדש 🌅"
                        if lang == 'he' else
                        "✅ *You already completed today's challenge!*\nCome back tomorrow 🌅")
            bot.send_message(c, done_msg, parse_mode="Markdown", reply_markup=back_btn())
            return
        # Start daily challenge: Python question first
        q    = random.choice(ALL_QUESTIONS)
        q_l  = get_q(q, lang)
        user_sessions[c] = {'daily_stage': 'python', 'daily_q': q, 'daily_date': today, 'daily_score': 0}
        user_states[c]   = 'DAILY'
        title = "🎯 *אתגר יומי!*" if lang == 'he' else "🎯 *Daily Challenge!*"
        desc  = ("3 שלבים: Python → LeetCode → ראיון\nהשלם את כולם לקבלת 🏆"
                 if lang == 'he' else
                 "3 stages: Python → LeetCode → Interview\nComplete all for 🏆")
        bot.send_message(c,
            f"*{DIV}*\n{title}\n*{DIV}*\n\n{desc}\n\n*שלב 1/3 — Python 🐍*" if lang=='he' else
            f"*{DIV}*\n{title}\n*{DIV}*\n\n{desc}\n\n*Stage 1/3 — Python 🐍*",
            parse_mode="Markdown")
        m = question_markup(q_l['options'], 'daily_ans', solo=True)
        bot.send_message(c, f"*{DIV}*\n\n{q_l['q']}", parse_mode="Markdown", reply_markup=m)
        return

    if data.startswith('daily_ans:'):
        if user_states.get(c) != 'DAILY': return
        lang   = get_lang(c)
        chosen = int(data.split(':')[1])
        s      = user_sessions.get(c, {})
        stage  = s.get('daily_stage')

        if stage == 'python':
            q = get_q(s['daily_q'], lang)
            if chosen == q['answer']:
                s['daily_score'] += 1
                bot.send_message(c, f"✅ *{'נכון!' if lang=='he' else 'Correct!'}* +1 🎉\n_{q['tip']}_", parse_mode="Markdown")
            else:
                bot.send_message(c, f"❌ *{'טעות' if lang=='he' else 'Wrong'}*\n_{q['tip']}_", parse_mode="Markdown")
            # Stage 2: LeetCode
            s['daily_stage'] = 'leetcode'
            lbl = "*שלב 2/3 — LeetCode 🧩*\n_מייצר שאלה..._" if lang=='he' else "*Stage 2/3 — LeetCode 🧩*\n_Generating..._"
            bot.send_message(c, lbl, parse_mode="Markdown")
            bot.send_chat_action(c, 'typing')
            system = "Give ONE Easy LeetCode problem. Max 5 lines, 1 example. End with SOLUTION_PLACEHOLDER then Python solution."
            full   = call_ai(system, "Generate Easy LeetCode problem.")
            if 'SOLUTION_PLACEHOLDER' in full:
                q_txt, sol = full.split('SOLUTION_PLACEHOLDER', 1)
            else:
                q_txt, sol = full, ""
            s['daily_leet_sol'] = sol.strip()
            m = types.InlineKeyboardMarkup(row_width=2)
            m.add(
                types.InlineKeyboardButton("💡 פתרון" if lang=='he' else "💡 Solution", callback_data='daily_leet_sol'),
                types.InlineKeyboardButton("➡️ המשך" if lang=='he' else "➡️ Continue",  callback_data='daily_stage3'),
            )
            safe_send(c, q_txt.strip(), reply_markup=m)
        return

    if data == 'daily_leet_sol':
        lang = get_lang(c)
        sol  = user_sessions.get(c, {}).get('daily_leet_sol', '')
        lbl  = "פתרון" if lang == 'he' else "Solution"
        safe_send(c, f"💡 *{lbl}:*\n\n{sol}")
        return

    if data == 'daily_stage3':
        lang = get_lang(c)
        s    = user_sessions.get(c, {})
        s['daily_stage'] = 'interview'
        lbl = "*שלב 3/3 — ראיון 🎙️*\nענה על שאלת הראיון:" if lang=='he' else "*Stage 3/3 — Interview 🎙️*\nAnswer the interview question:"
        bot.send_message(c, lbl, parse_mode="Markdown")
        bot.send_chat_action(c, 'typing')
        lang_instr = "שאל שאלת ראיון טכנית קצרה בעברית." if lang=='he' else "Ask one short technical interview question."
        q_iv = call_ai("אתה מראיין." if lang=='he' else "You are an interviewer.", lang_instr)
        s['daily_iv_q'] = q_iv
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("🛑 דלג" if lang=='he' else "🛑 Skip", callback_data='daily_finish'))
        bot.send_message(c, f"💬 {q_iv}", parse_mode="Markdown", reply_markup=m)
        user_states[c] = 'DAILY_IV'
        return

    if data == 'daily_finish':
        _finish_daily(c)
        return

    # ════════════════════════════════════════════════════
    #  ⚡ SPEED ROUND
    # ════════════════════════════════════════════════════
    if data == 'speed_round':
        lang = get_lang(c)
        qs   = random.sample(ALL_QUESTIONS, len(ALL_QUESTIONS))
        user_sessions[c] = {'questions': qs, 'q_idx': 0, 'score': 0, 'speed_start': time.time()}
        user_states[c]   = 'SPEED'
        title = "⚡ *Speed Round!*"
        desc  = ("60 שניות — כמה שאלות תוכל לענות? 🔥\nאין טיימר לשאלה — הזמן הכולל הוא 60 שניות!"
                 if lang == 'he' else
                 "60 seconds — how many can you answer? 🔥\nNo per-question timer — total time is 60 seconds!")
        bot.send_message(c, f"*{DIV}*\n{title}\n*{DIV}*\n\n{desc}", parse_mode="Markdown")
        time.sleep(0.5)
        # Start 60s countdown in background
        def speed_timeout():
            time.sleep(60)
            if user_states.get(c) != 'SPEED': return
            _finish_speed(c)
        threading.Thread(target=speed_timeout, daemon=True).start()
        send_speed_question(c)
        return

    if data.startswith('speed_ans:'):
        if user_states.get(c) != 'SPEED': return
        lang   = get_lang(c)
        chosen = int(data.split(':')[1])
        s      = user_sessions.get(c, {})
        qraw   = s['questions'][s['q_idx']]
        q      = get_q(qraw, lang)
        if chosen == q['answer']:
            s['score'] += 1
            bot.send_message(c, f"✅ +1", parse_mode="Markdown")
        else:
            bot.send_message(c, f"❌", parse_mode="Markdown")
        s['q_idx'] += 1
        if s['q_idx'] >= len(s['questions']):
            s['questions'] = random.sample(ALL_QUESTIONS, len(ALL_QUESTIONS))
            s['q_idx']     = 0
        elapsed = int(time.time() - s['speed_start'])
        remaining = 60 - elapsed
        if remaining <= 0:
            _finish_speed(c)
        else:
            send_speed_question(c, remaining)
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
            n = len(room['players'])
            bot.send_message(c,
                f"✅ *Joined DevDuel!*\n🎯 Code: *{code}*\n\n_Waiting for host to start..._",
                parse_mode="Markdown")
            # Update host's lobby message
            host        = room['host']
            lobby_mid   = room.get('lobby_msg_id')
            player_list = '\n'.join(f"🟢 *{p['name']}*" for p in room['players'].values())
            m = types.InlineKeyboardMarkup()
            m.add(types.InlineKeyboardButton("🚀 Start Game!", callback_data=f'game_start:{code}'))
            m.add(types.InlineKeyboardButton("🛑 Cancel",      callback_data='game_cancel'))
            new_text = (
                f"⚡ *DevDuel — Lobby*\n\n"
                f"┌─────────────────────┐\n"
                f"│   🎯 Code:  *{code}*    │\n"
                f"└─────────────────────┘\n\n"
                f"👥 Players: *{n} / 20*\n\n"
                f"{player_list}\n\n"
                f"_Start whenever you're ready!_"
            )
            if lobby_mid:
                try:
                    bot.edit_message_text(new_text, host, lobby_mid,
                                          parse_mode="Markdown", reply_markup=m)
                except Exception:
                    pass
            return

        if state == 'INTERVIEW':
            s = user_sessions.get(c)
            if not s: return
            lang = get_lang(c)
            idx  = s['q_idx']
            if idx >= len(INTERVIEW_QUESTIONS):
                send_interview_question(c)
                return
            q_dict = INTERVIEW_QUESTIONS[idx]
            q_text = q_dict.get(lang, q_dict['en'])
            bot.send_chat_action(c, 'typing')
            if lang == 'he':
                system = (
                    "אתה מהנדס בכיר שעורך ראיון עבודה דמה. "
                    "המועמד ענה על שאלת ראיון. "
                    "תן פידבק קצר (מקסימום 5 שורות) בעברית: האם התשובה טובה/חלקית/שגויה, "
                    "מה חסר, ומה התשובה האידיאלית ב-2 שורות. "
                    "היה מעודד אך כנה."
                )
            else:
                system = (
                    "You are a senior software engineer conducting a mock interview. "
                    "Give SHORT feedback (max 5 lines): was the answer good/partial/wrong, "
                    "what was missing, and the ideal answer in 2 lines. "
                    "Be encouraging but honest."
                )
            prompt   = f"Question: {q_text}\n\nCandidate's answer: {text}"
            feedback = call_ai(system, prompt)
            m = types.InlineKeyboardMarkup(row_width=2)
            next_lbl = "➡️ הבא" if lang == 'he' else "➡️ Next"
            end_lbl  = "🛑 סיים" if lang == 'he' else "🛑 End"
            m.add(
                types.InlineKeyboardButton(next_lbl, callback_data='iv_next'),
                types.InlineKeyboardButton(end_lbl,  callback_data='iv_end'),
            )
            s['score'] += 1
            fb_lbl = "פידבק" if lang == 'he' else "Feedback"
            safe_send(c, f"*{DIV}*\n📝 *{fb_lbl}:*\n\n{feedback}", reply_markup=m)
        elif state == 'CV':
            _process_cv_or_jd(c, text, 'CV')
        elif state == 'JD':
            _process_cv_or_jd(c, text, 'JD')
        elif state == 'AI_INTERVIEW':
            s    = user_sessions.get(c, {})
            lang = get_lang(c)
            history = s.get('ai_iv_history', [])
            history.append({'role': 'user', 'content': text})
            s['ai_iv_count'] = s.get('ai_iv_count', 0) + 1
            bot.send_chat_action(c, 'typing')
            if lang == 'he':
                sys_prompt = (
                    "אתה מראיין טכני בכיר. תן פידבק קצר (2-3 שורות) על תשובת המועמד, "
                    "ואז שאל שאלת follow-up חכמה על בסיס מה שאמר. "
                    "ענה בעברית."
                )
            else:
                sys_prompt = (
                    "You are a senior technical interviewer. Give brief feedback (2-3 lines) on the candidate's answer, "
                    "then ask a smart follow-up question based on what they said."
                )
            msgs = [{'role': 'system', 'content': sys_prompt}] + history[-6:]
            try:
                resp = client.chat.completions.create(
                    model="llama3-8b-8192", messages=msgs, max_tokens=300
                ).choices[0].message.content
            except Exception:
                resp = call_ai(sys_prompt, text)
            history.append({'role': 'assistant', 'content': resp})
            s['ai_iv_history'] = history
            m = types.InlineKeyboardMarkup()
            m.add(types.InlineKeyboardButton("🛑 סיים" if lang=='he' else "🛑 End", callback_data='ai_iv_end'))
            safe_send(c, resp, reply_markup=m)
        elif state == 'DAILY_IV':
            lang = get_lang(c)
            s    = user_sessions.get(c, {})
            bot.send_chat_action(c, 'typing')
            q_iv = s.get('daily_iv_q', '')
            if lang == 'he':
                sys_p = "תן פידבק קצר (3 שורות) בעברית על התשובה לשאלת הראיון."
            else:
                sys_p = "Give brief feedback (3 lines) on the interview answer."
            fb = call_ai(sys_p, f"Q: {q_iv}\nA: {text}")
            s['daily_score'] = s.get('daily_score', 0) + 1
            fb_lbl = "פידבק" if lang == 'he' else "Feedback"
            bot.send_message(c, f"📝 *{fb_lbl}:*\n\n{fb}", parse_mode="Markdown")
            _finish_daily(c)
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
