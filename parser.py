import time

import psutil
import requests, re
from aiogram import Bot


from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager



from config import settings
from database import OrderDAO


bot = Bot(token=settings.get_token())
# максимальная цена заказа
max_price = 10000

def get_projects(last_links):

    projects = []
    # Настройка WebDriverManager для Chrome
    chrome_service = ChromeService(ChromeDriverManager().install())

    # Конфигурация Chrome для работы в безголовом режиме
    chrome_options = Options()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--headless")
    # Инициализация ChromeDriver с опциями
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    # get запрос
    driver.get('https://kwork.ru/projects?fc=41')
    # ожидание загрузки
    time.sleep(10)
    # загрузка страницы
    html = driver.page_source

    soup = BeautifulSoup(html, 'lxml')
    # сохранение всех карточек заказов
    items = soup.find_all('div', class_='want-card want-card--list want-card--hover')

    for item in items:
        # заголовок
        title = item.find('h1')
        title = title.text if title else "Error title"
        # цена
        price = item.find("div", class_='wants-card__price').find('div', class_='d-inline')
        price = re.findall( r"\d{3}|\d{1,2}\s\d{3}", str(price))
        if int("".join(price).replace(" ", '')) >= max_price:
            continue
        price = " ".join(price)

        # ссылка
        link = item.find("a")
        link = f"https://kwork.ru{link['href']}/view" if link else "Link error"
        # проверка на то есть ли проект в базе данных
        if link in last_links:
            break
        params = {"title": title,"price":price,"link":link}
        projects.append(params)
    #driver.quit()

    return projects


async def work():
    # берет из базы данных 5 последних проектов
    # (нужен не 1 проект так как, его могут удалить и прога будет, брать больше чем нужно)
    last_links = await OrderDAO.find_last_record()
    # формирование списка
    last_links_projects = [x.link for x in last_links]
    projects = get_projects(last_links_projects)
    # переворот списка чтобы последними в базе данных были самые новые проекты
    projects.reverse()
    if projects:
        for project in projects:
            await OrderDAO.add(title=project['title'], price=project['price'], link=project['link'])
            # добавить parse_mode
            await bot.send_message(chat_id=settings.get_admin_id(),
                                   text=f"{project['title']}\nЦена:{project['price']}\nСсылка:{project['link']}",
                                   )

    return None
