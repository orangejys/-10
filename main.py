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