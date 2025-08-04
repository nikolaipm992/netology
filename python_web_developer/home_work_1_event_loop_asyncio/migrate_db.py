# migrate_db.py
import asyncio
import aiosqlite

# Имя файла базы данных
DB_NAME = 'star_wars.db'

async def create_table():
    """Создает таблицу characters в базе данных SQLite."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY,
                birth_year TEXT,
                eye_color TEXT,
                gender TEXT,
                hair_color TEXT,
                homeworld TEXT, -- Сохраняем URL родного мира
                mass TEXT,
                name TEXT,
                skin_color TEXT
            )
        ''')
        await db.commit()
        print(f"Таблица 'characters' в базе данных '{DB_NAME}' создана или уже существовала.")

if __name__ == "__main__":
    asyncio.run(create_table())
