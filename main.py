import logging
import sqlite3
import random
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
    
