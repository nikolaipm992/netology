# load_data.py
import asyncio
import aiohttp
import aiosqlite

# Конфигурация
DB_NAME = 'star_wars.db'
API_BASE_URL = "https://www.swapi.tech/api"
PEOPLE_ENDPOINT = f"{API_BASE_URL}/people"

# Ограничиваем количество одновременных запросов
SEMAPHORE = asyncio.Semaphore(10)

async def get_all_character_urls(session):
    """Получает список URL всех персонажей, обрабатывая пагинацию."""
    urls = []
    url = PEOPLE_ENDPOINT # Начинаем с первой страницы
    while url:
        try:
            async with SEMAPHORE:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Добавляем URL каждого персонажа на текущей странице
                        results = data.get("results", [])
                        urls.extend([char["url"] for char in results])
                        
                        # Проверяем, есть ли следующая страница
                        next_page = data.get("next")
                        url = next_page if next_page else None
                    else:
                        print(f"Ошибка при запросе списка персонажей: {response.status}")
                        break
        except Exception as e:
            print(f"Исключение при запросе списка персонажей: {e}")
            break
    print(f"Найдено {len(urls)} URL персонажей.")
    return urls

async def get_character_data(session, character_url):
    """Получает данные конкретного персонажа по его URL."""
    try:
        async with SEMAPHORE:
            async with session.get(character_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("result", {}).get("properties")
                else:
                    print(f"Ошибка при запросе персонажа {character_url}: статус {response.status}")
                    return None
    except Exception as e:
        print(f"Исключение при запросе персонажа {character_url}: {e}")
        return None

async def save_character_to_db(db, character_data):
    """Сохраняет данные персонажа в базу данных."""
    if not character_data:
        return

    # Извлекаем ID из URL
    char_id_str = character_data.get('url', '').rstrip('/').split('/')[-1]
    try:
        char_id = int(char_id_str) if char_id_str.isdigit() else None
    except ValueError:
        char_id = None

    if char_id is None:
        print(f"Не удалось извлечь ID для персонажа {character_data.get('name', 'Unknown')}")
        return

    fields = (
        char_id,
        character_data.get('birth_year'),
        character_data.get('eye_color'),
        character_data.get('gender'),
        character_data.get('hair_color'),
        character_data.get('homeworld'), # Сохраняем URL
        character_data.get('mass'),
        character_data.get('name'),
        character_data.get('skin_color')
    )

    try:
        await db.execute('''
            INSERT OR REPLACE INTO characters 
            (id, birth_year, eye_color, gender, hair_color, homeworld, mass, name, skin_color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', fields)
        print(f"Персонаж {character_data.get('name')} (ID: {char_id}) сохранен.")
    except Exception as e:
        print(f"Ошибка при сохранении персонажа {character_data.get('name')}: {e}")

async def process_character(session, db, character_url):
    """Обрабатывает одного персонажа: получает данные и сохраняет в БД."""
    character_data = await get_character_data(session, character_url)
    await save_character_to_db(db, character_data)

async def main():
    """Главная асинхронная функция."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу (на случай, если скрипт миграции не был запущен)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY,
                birth_year TEXT,
                eye_color TEXT,
                gender TEXT,
                hair_color TEXT,
                homeworld TEXT,
                mass TEXT,
                name TEXT,
                skin_color TEXT
            )
        ''')
        await db.commit()

        async with aiohttp.ClientSession() as session:
            print("Получение списка всех персонажей...")
            character_urls = await get_all_character_urls(session)

            if not character_urls:
                print("Не удалось получить список персонажей.")
                return

            print("Начало загрузки персонажей...")
            # Создаем список задач для обработки всех персонажей
            tasks = [
                process_character(session, db, url)
                for url in character_urls
            ]
            
            # Выполняем все задачи асинхронно
            await asyncio.gather(*tasks)
            
            # Фиксируем все изменения в БД
            await db.commit()
            print("Все персонажи загружены.")

if __name__ == "__main__":
    # pip install aiohttp aiosqlite
    asyncio.run(main())
