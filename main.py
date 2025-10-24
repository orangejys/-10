import logging
import sqlite3
import random
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
def init_database():
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    
    # Таблица с разделами
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    # Таблица с материалами
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (section_id) REFERENCES sections (id)
        )
    ''')
    
    # Таблица с цитатами
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            quote_text TEXT NOT NULL
        )
    ''')
    
    # Заполняем начальными данными
    fill_initial_data(cursor)
    
    conn.commit()
    conn.close()

def fill_initial_data(cursor):
    # Проверяем, есть ли уже данные
    cursor.execute("SELECT COUNT(*) FROM sections")
    if cursor.fetchone()[0] > 0:
        return
    
    # Добавляем разделы
    sections = [
        ("📐 Аксиомы", "Аксиоматика вещественных чисел"),
        ("📊 Супремум и инфимум", "Верхние и нижние грани множеств"),
        ("🎯 Предел последовательности", "Теория пределов и сходимость"),
        ("🔍 Доказательства", "Важные математические доказательства"),
        ("🛠️ Методы решения", "Методы решения задач")
    ]
    cursor.executemany("INSERT INTO sections (name, description) VALUES (?, ?)", sections) 
    # Добавляем материалы для Аксиом
    axioms_materials = [
        (1, "16 аксиом ℝ", """
📚 16 АКСИОМ ВЕЩЕСТВЕННЫХ ЧИСЕЛ

Аксиомы сложения (A1-A4):
A1. (x + y) + z = x + (y + z) - ассоциативность
A2. x + y = y + x - коммутативность  
A3. ∃0: x + 0 = x - нулевой элемент
A4. ∀x ∃(-x): x + (-x) = 0 - противоположный элемент

Аксиомы умножения (A5-A8):
A5. (x·y)·z = x·(y·z) - ассоциативность
A6. x·y = y·x - коммутативность
A7. ∃1≠0: x·1 = x - единичный элемент
A8. ∀x≠0 ∃x⁻¹: x·x⁻¹ = 1 - обратный элемент

Аксиома дистрибутивности (A9):
A9. (x + y)·z = x·z + y·z

Аксиомы порядка (A10-A15):
A10. x ≤ x - рефлексивность
A11. (x ≤ y ∧ y ≤ z) ⇒ x ≤ z - транзитивность
A12. (x ≤ y ∧ y ≤ x) ⇒ x = y - антисимметричность
A13. x ≤ y ∨ y ≤ x - линейная упорядоченность
A14. x ≤ y ⇒ x + z ≤ y + z
A15. (0 ≤ x ∧ 0 ≤ y) ⇒ 0 ≤ x·y

Аксиома полноты (A16):
A16. ∀X,Y⊂ℝ, X≤Y ⇒ ∃c∈ℝ: X≤c≤Y
        """),
        
        (1, "Аксиома полноты", """
🎯 АКСИОМА ПОЛНОТЫ (НЕПРЕРЫВНОСТИ)

Формулировка:
Для любых непустых множеств X, Y ⊂ ℝ таких, что 
∀x∈X ∀y∈Y: x ≤ y, 
существует число c ∈ ℝ такое, что 
∀x∈X ∀y∈Y: x ≤ c ≤ y.

Геометрический смысл:
Числовая прямая не имеет "дырок" - между любыми двумя непересекающимися множествами найдётся разделяющее число.

Пример:
X = {x ∈ ℚ: x² < 2}, Y = {x ∈ ℚ: x² > 2}
c = √2 ∉ ℚ, но c ∈ ℝ
        """),
        
        (1, "Свойства операций", """
⚙️ СВОЙСТВА ОПЕРАЦИЙ

Из аксиом следуют:
1. Единственность нуля: если 0' - другой нуль, то 0' = 0
2. Единственность противоположного: -x определяется однозначно
3. 0·x = 0 для любого x ∈ ℝ
4. (-1)·x = -x
5. x·y = 0 ⇒ (x=0 ∨ y=0)
        """)
    ]
    
    # Добавляем материалы для Супремума и инфимума
    supremum_materials = [
        (2, "Определения", """
📖 ОПРЕДЕЛЕНИЯ

Множество X ⊂ ℝ называется:
• Ограниченным сверху, если ∃M∈ℝ: ∀x∈X x ≤ M
• Ограниченным снизу, если ∃m∈ℝ: ∀x∈X x ≥ m
• Ограниченным, если ограничено сверху и снизу

Верхняя грань (супремум):
sup X = min{M ∈ ℝ: ∀x∈X x ≤ M}

Нижняя грань (инфимум):
inf X = max{m ∈ ℝ: ∀x∈X x ≥ m}
        """),
        
        (2, "Свойства sup и inf", """
🔧 СВОЙСТВА SUP И INF

1. ∀x∈X: x ≤ sup X, x ≥ inf X
2. ∀ε>0 ∃x∈X: x > sup X - ε
3. ∀ε>0 ∃x∈X: x < inf X + ε
4. Если X ⊂ Y, то inf Y ≤ inf X ≤ sup X ≤ sup Y
5. sup(X ∪ Y) = max{sup X, sup Y}
6. inf(X ∪ Y) = min{inf X, inf Y}

Примеры:
• sup[0,1) = 1, inf[0,1) = 0
• sup(0,1) = 1, inf(0,1) = 0
• supℕ = +∞, infℕ = 1
        """),
        
        (2, "Критерий sup", """
🎯 КРИТЕРИЙ СУПРЕМУМА

Число α = sup X тогда и только тогда, когда:
1. α - верхняя граница: ∀x∈X x ≤ α
2. α - наименьшая верхняя граница: 
   ∀ε>0 ∃x∈X: x > α - ε

Эквивалентная формулировка:
α = sup X ⇔ [∀x∈X x≤α] ∧ [∀α'<α ∃x∈X x>α']
        """)
    ]
    

# Добавляем материалы для Пределов
    limits_materials = [
        (3, "Определение предела", """
🎯 ОПРЕДЕЛЕНИЕ ПРЕДЕЛА

Число a называется пределом последовательности {xₙ}, если:
∀ε>0 ∃N∈ℕ ∀n≥N: |xₙ - a| < ε

Обозначение: lim(xₙ) = a или xₙ → a

Геометрический смысл:
В любой ε-окрестности точки a лежат все члены последовательности, начиная с некоторого номера.
        """),
        
        (3, "Свойства пределов", """
🔧 СВОЙСТВА ПРЕДЕЛОВ

1. Единственность: если lim xₙ = a и lim xₙ = b, то a = b
2. Ограниченность: сходящаяся последовательность ограничена
3. Предел и неравенства: 
   если xₙ ≤ yₙ и lim xₙ = a, lim yₙ = b, то a ≤ b
4. Арифметические операции:
   • lim(xₙ + yₙ) = lim xₙ + lim yₙ
   • lim(xₙ · yₙ) = lim xₙ · lim yₙ
   • lim(xₙ / yₙ) = lim xₙ / lim yₙ (если lim yₙ ≠ 0)
        """),
        
        (3, "Важные пределы", """
📊 ВАЖНЫЕ ПРЕДЕЛЫ

1. lim(1/n) = 0
2. lim(1/nᵖ) = 0 (p > 0)
3. lim(qⁿ) = 0 (|q| < 1)
4. lim(1 + 1/n)ⁿ = e ≈ 2.71828
5. lim(ⁿ√n) = 1
6. lim(ⁿ√a) = 1 (a > 0)
7. lim(n!/nⁿ) = 0
        """),
        
        (3, "Монотонные последовательности", """
📈 МОНОТОННЫЕ ПОСЛЕДОВАТЕЛЬНОСТИ

Теорема (Вейерштрасса):
Всякая монотонная ограниченная последовательность сходится.

• Если {xₙ} неубывает и ограничена сверху, то 
  lim xₙ = sup{xₙ}
• Если {xₙ} невозрастает и ограничена снизу, то
  lim xₙ = inf{xₙ}

Пример: xₙ = (1 + 1/n)ⁿ - возрастает и ограничена ⇒ сходится к e
        """)
    ]
    
    # Добавляем материалы для Доказательств
    proofs_materials = [
        (4, "√2 иррационально", """
🔍 ИРРАЦИОНАЛЬНОСТЬ √2

Доказательство от противного:

Предположим: √2 ∈ ℚ, т.е. √2 = m/n, где m,n ∈ ℕ, дробь несократима

Тогда: 
m² = 2n² ⇒ m² чётно ⇒ m чётно ⇒ m = 2k

Подставляем:
(2k)² = 2n² ⇒ 4k² = 2n² ⇒ n² = 2k² ⇒ n² чётно ⇒ n чётно

Получили: m и n оба чётны ⇒ дробь m/n сократима

Противоречие с предположением о несократимости.
        """),
        
        (4, "0 < 1", """
🔢 ДОКАЗАТЕЛЬСТВО 0 < 1

1. По аксиоме (A7): 1 ≠ 0
2. По трихотомии (A13): либо 1 > 0, либо 1 < 0
3. Предположим: 1 < 0
4. Тогда -1 > 0 (по свойству)
5. (-1)·(-1) = 1 > 0 (по аксиоме A15)
6. Но если 1 < 0, то 1 не может быть > 0
7. Противоречие ⇒ 1 > 0
        """),
        
        (4, "Принцип индукции", """
🌀 ПРИНЦИП МАТЕМАТИЧЕСКОЙ ИНДУКЦИИ

Формулировка:
Если:
1. P(1) истинно
2. ∀n∈ℕ: P(n) ⇒ P(n+1)
Тогда: ∀n∈ℕ P(n) истинно

Доказательство эквивалентности принципу минимума:

Пусть M = {n∈ℕ: P(n) ложно}. 
Если M ≠ ∅, то по принципу минимума ∃min M = m.
Тогда m > 1 (т.к. P(1) истинно) и P(m-1) истинно.
Но тогда по условию 2 P(m) истинно ⇒ противоречие.
        """),
        
        (4, "Бесконечность ℕ", """
∞ БЕСКОНЕЧНОСТЬ МНОЖЕСТВА ℕ

Доказательство от противного:

Предположим: ℕ конечно ⇒ ∃max ℕ = M

Рассмотрим M + 1:
• M + 1 > M (по построению)
• M + 1 ∈ ℕ (по определению)

Противоречие: M не является максимумом ⇒ ℕ бесконечно.
        """)
    ]
    
 # Добавляем материалы для Методов решения
    methods_materials = [
        (5, "Неопределённые коэффициенты", """
🧮 МЕТОД НЕОПРЕДЕЛЁННЫХ КОЭФФИЦИЕНТОВ

Применяется для разложения рациональных дробей:

P(x)/Q(x) = A₁/(x-a₁) + A₂/(x-a₂) + ... + Aₖ/(x-aₖ)

Пример:
(3x+1)/((x-1)(x+2)) = A/(x-1) + B/(x+2)

Умножаем на знаменатель:
3x + 1 = A(x+2) + B(x-1)

Решаем систему:
{ A + B = 3
{ 2A - B = 1

Решение: A = 4/3, B = 5/3
        """),
        
        (5, "Метод математической индукции", """
🌀 МЕТОД МАТЕМАТИЧЕСКОЙ ИНДУКЦИИ

Шаги доказательства:
1. База индукции: проверяем утверждение для n=1
2. Индукционный переход: 
   Предполагаем верным для n=k
   Доказываем для n=k+1

Пример: 1 + 2 + ... + n = n(n+1)/2

База: n=1: 1 = 1·2/2 ✓
Переход: 
1+...+k+(k+1) = k(k+1)/2 + (k+1) = (k+1)(k/2+1) = (k+1)(k+2)/2
        """),
        
        (5, "Зажатие (теорема о двух милиционерах)", """
🎯 ТЕОРЕМА О ЗАЖАТОЙ ПОСЛЕДОВАТЕЛЬНОСТИ

Если:
1. lim xₙ = lim yₙ = a
2. ∃N: ∀n≥N xₙ ≤ zₙ ≤ yₙ
Тогда: lim zₙ = a

Пример:
lim (sin n)/n = 0, т.к.
-1/n ≤ (sin n)/n ≤ 1/n
и lim ±1/n = 0
        """),
        
        (5, "Критерий Коши", """
📏 КРИТЕРИЙ КОШИ СХОДИМОСТИ

Последовательность {xₙ} сходится тогда и только тогда, когда:
∀ε>0 ∃N∈ℕ ∀m,n≥N: |xₘ - xₙ| < ε

Геометрический смысл:
Члены последовательности становятся сколь угодно близкими друг к другу.

Применение:
Позволяет доказывать сходимость, не зная предела.
        """)
    ]
    
    # Объединяем все материалы
    all_materials = (axioms_materials + supremum_materials + 
                    limits_materials + proofs_materials + methods_materials)
    
    cursor.executemany(
        "INSERT INTO materials (section_id, title, content) VALUES (?, ?, ?)", 
        all_materials
    )
    
    # Добавляем цитаты
    quotes = [
        ("Платон", "Математика — это занятие для души"),
        ("Аристотель", "Математика выявляет порядок, симметрию и определённость"),
        ("Пифагор", "Всё есть число"),
        ("Евклид", "В математике нет царской дороги"),
        ("Архимед", "Дайте мне точку опоры, и я переверну мир"),
        ("Платон", "Бог вечно геометризует"),
        ("Пифагор", "Начало есть половина целого"),
        ("Аристотель", "Природа боится пустоты"),
        ("Евклид", "Что и требовалось доказать"),
        ("Архимед", "Эврика!")
    ]
    cursor.executemany(
        "INSERT INTO quotes (author, quote_text) VALUES (?, ?)", 
        quotes
    )

# Функции для работы с базой данных
def get_sections():
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM sections ORDER BY id")
    sections = cursor.fetchall()
    conn.close()
    return sections

def get_section_materials(section_id):
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM materials WHERE section_id = ?", (section_id,))
    materials = cursor.fetchall()
    conn.close()
    return materials

def get_random_quote():
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT author, quote_text FROM quotes ORDER BY RANDOM() LIMIT 1")
    quote = cursor.fetchone()
    conn.close()
    return quote

def search_materials(query):
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.id, m.title, m.content, s.name 
        FROM materials m 
        JOIN sections s ON m.section_id = s.id 
        WHERE m.title LIKE ? OR m.content LIKE ?
    ''', (f'%{query}%', f'%{query}%'))
    results = cursor.fetchall()
    conn.close()
    return results

# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📐 Аксиомы", callback_data="section_1")],
        [InlineKeyboardButton("📊 Супремум и инфимум", callback_data="section_2")],
        [InlineKeyboardButton("🎯 Предел последовательности", callback_data="section_3")],
        [InlineKeyboardButton("🔍 Доказательства", callback_data="section_4")],
        [InlineKeyboardButton("🛠️ Методы решения", callback_data="section_5")],
        [InlineKeyboardButton("💬 Случайная цитата", callback_data="random_quote")],
        [InlineKeyboardButton("🔍 Поиск", callback_data="search")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📚 *Добро пожаловать в бот по математическому анализу!*\n\n"
        "Выберите раздел:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 *Доступные команды:*

/start - начать работу
/help - помощь  
/quote - случайная цитата
/search - поиск по материалам

*Или используйте кнопки меню!*

🎯 *Разделы:*
• Аксиомы вещественных чисел
• Супремум и инфимум  
• Предел последовательности
• Доказательства
• Методы решения задач
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "random_quote":
        await show_random_quote(query)
    elif data == "search":
        await query.edit_message_text("🔍 *Поиск по материалам*\n\nВведите: /search <запрос>\n\nНапример: /search предел", parse_mode='Markdown')
    elif data == "main_menu":
        await show_main_menu(query)
    elif data.startswith("section_"):
        section_id = int(data.split("_")[1])
        await show_section_materials(query, section_id)
    elif data.startswith("material_"):
        material_id = int(data.split("_")[1])
        await show_material(query, material_id)

async def show_main_menu(query):
    keyboard = [
        [InlineKeyboardButton("📐 Аксиомы", callback_data="section_1")],
        [InlineKeyboardButton("📊 Супремум и инфимум", callback_data="section_2")],
        [InlineKeyboardButton("🎯 Предел последовательности", callback_data="section_3")],
        [InlineKeyboardButton("🔍 Доказательства", callback_data="section_4")],
        [InlineKeyboardButton("🛠️ Методы решения", callback_data="section_5")],
        [InlineKeyboardButton("💬 Случайная цитата", callback_data="random_quote")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📚 *Выберите раздел:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_section_materials(query, section_id):
    sections = get_sections()
    section_name = next((name for id, name, desc in sections if id == section_id), "Раздел")
    materials = get_section_materials(section_id)
    
    if not materials:
        await query.edit_message_text(f"В разделе '{section_name}' пока нет материалов")
        return
    
    keyboard = []
    for material_id, title, content in materials:
        keyboard.append([InlineKeyboardButton(f"📄 {title}", callback_data=f"material_{material_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📚 *{section_name}:*\n\nВыберите тему:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_material(query, material_id):
    conn = sqlite3.connect('math_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.title, m.content, s.name 
        FROM materials m 
        JOIN sections s ON m.section_id = s.id 
        WHERE m.id = ?
    ''', (material_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        await query.answer("Материал не найден", show_alert=True)
        return

    title, content, section_name = row

    # Кнопки «назад»
    section_id_for_back = next((sid for sid, name, _ in get_sections() if name == section_name), 1)
    keyboard = [
        [InlineKeyboardButton("🔙 Назад к разделу", callback_data=f"section_{section_id_for_back}")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Экраннирование для HTML
    safe_title = html.escape(title)
    safe_content = html.escape(content)

    # Разбиваем длинные тексты
    header = f"<b>{safe_title}</b>\n\n"
    max_len = 4096  # лимит Telegram
    first_chunk_space = max_len - len(header)

    if len(safe_content) > first_chunk_space:
        parts = [safe_content[i:i+max_len] for i in range(0, len(safe_content), max_len)]
        await query.edit_message_text(
            header + parts[0],
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        for part in parts[1:]:
            await query.message.reply_text(part, parse_mode='HTML')
    else:
        await query.edit_message_text(
            header + safe_content,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

async def show_random_quote(query):
    author, quote_text = get_random_quote()
    
    keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"_{quote_text}_\n\n— *{author}*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🔍 *Поиск по материалам*\n\n"
            "Использование: `/search <запрос>`\n\n"
            "Примеры:\n"
            "• `/search предел`\n"
            "• `/search аксиома`\n"
            "• `/search доказательство`",
            parse_mode='Markdown'
        )
        return
    
    query = " ".join(context.args)
    results = search_materials(query)
    
    if not results:
        await update.message.reply_text(f"🔍 По запросу '*{query}*' ничего не найдено", parse_mode='Markdown')
        return
    
    text = f"🔍 *Результаты поиска по запросу '{query}':*\n\n"
    for i, (material_id, title, content, section_name) in enumerate(results[:5], 1):
        # Создаем превью содержимого
        preview = content.replace('\n', ' ')[:100] + "..." if len(content) > 100 else content
        text += f"{i}. **{title}** (*{section_name}*)\n{preview}\n\n"
    
    if len(results) > 5:
        text += f"*... и ещё {len(results) - 5} результатов*"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    author, quote_text = get_random_quote()
    await update.message.reply_text(
        f"_{quote_text}_\n\n— *{author}*",
        parse_mode='Markdown'
    )

def main():
    # Инициализируем базу данных
    init_database()
    
    # Создаем приложение
    application = Application.builder().token("8373835216:AAF8m-ktBUj36hfgGm9x4pFwHPw_T2zfzck").build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("quote", quote_command))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
