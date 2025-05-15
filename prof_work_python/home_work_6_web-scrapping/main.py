import requests
from bs4 import BeautifulSoup

# Список ключевых слов для поиска
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}

URL = 'https://habr.com/ru/articles/'

response = requests.get(URL, headers=HEADERS)
text = response.text

soup = BeautifulSoup(text, 'html.parser')

articles = soup.find_all('article')

for article in articles:
    pub_time = article.find('time')
    pub_date = pub_time['datetime'][:10] if pub_time else 'Дата не указана'

    title_span = article.find('h2', class_='tm-title tm-title_h2')
    if not title_span:
        continue
    title = title_span.get_text(strip=True)
    link = title_span.find('a')['href']
    full_link = 'https://habr.com' + link

    preview_block = article.find('div', class_='article-formatted-body')
    preview_text = preview_block.get_text(strip=True).lower() if preview_block else ''

    combined_text = title.lower() + ' ' + preview_text

    for keyword in KEYWORDS:
        if keyword in combined_text:
            print(f'{pub_date} – {title} – {full_link}')
            break