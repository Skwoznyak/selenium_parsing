from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import os
import time
import csv

# ⚙️ НАСТРОЙКА БРАУЗЕРА
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=chrome_options)

# 📁 ФАЙЛ ДЛЯ СОХРАНЕНИЯ КУК
COOKIES_FILE = "cookies_for_max.pkl"


def manual_login():
    """Ручная авторизация пользователем"""
    print("🔐 НУЖНА РУЧНАЯ АВТОРИЗАЦИЯ")
    print("1. Браузер откроет страницу сайт")
    print("2. Войдите в свой аккаунт")
    print("3. После успешного входа нажмите Enter здесь в консоли")
    print("=" * 50)

    # Открываем сайт для ручного входа
    driver.get("ваша ссылка")
    time.sleep(2)

    # Ждем, пока пользователь вручную авторизуется
    input("После успешного входа нажмите Enter чтобы продолжить...")

    # Сохраняем куки после авторизации
    save_cookies()

    print("✅ Авторизация завершена! Куки сохранены.")
    return True


def save_cookies():
    """Сохраняет куки в файл"""
    cookies = driver.get_cookies()
    with open(COOKIES_FILE, 'wb') as file:
        pickle.dump(cookies, file)
    print("💾 Куки сохранены в файл")


def load_cookies():
    """Загружает куки из файла"""
    if os.path.exists(COOKIES_FILE):
        driver.get("ваша ссылка")
        time.sleep(2)

        with open(COOKIES_FILE, 'rb') as file:
            cookies = pickle.load(file)

            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    continue

        print("✅ Куки загружены!")
        return True
    else:
        print("❌ Файл с куками не найден!")
        return False


def check_login():
    """Проверяем, авторизовались ли мы"""
    try:
        driver.get("ваша ссылка")
        time.sleep(3)

        # Ищем признаки авторизации
        auth_signs = [
            "//a[contains(text(), 'Выйти')]",
            "//a[contains(text(), 'Logout')]",
            "//*[contains(@class, 'avatar')]",
            "//*[contains(text(), 'Мой аккаунт')]"
        ]

        for sign in auth_signs:
            try:
                elements = driver.find_elements(By.XPATH, sign)
                if elements:
                    return True
            except:
                continue

        return False

    except:
        return False


def perform_search(search_query):
    """Выполняет поиск по запросу"""
    print(f"🔍 Выполняем поиск: {search_query}")

    # Переходим на страницу поиска
    driver.get("ваша ссылка какую именно страницу нужно парсить")
    time.sleep(3)

    # Ждем появления поисковой строки
    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'q'))
        )

        # Очищаем и вводим запрос
        search_input.clear()
        search_input.send_keys(search_query)
        time.sleep(2)

        # Нажимаем Enter
        search_input.send_keys(Keys.RETURN)
        time.sleep(5)

        print("✅ Поиск выполнен успешно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при поиске: {e}")
        return False


def click_show_more():
    """Нажимает кнопку 'Показать больше'"""
    try:
        # Ищем кнопку по разным селекторам
        button_selectors = [
            "button.btn.btn-light.border.lm-button.py-1.min-width-220px",
            "button:contains('Показать больше')",
            "//button[contains(text(), 'Показать больше')]",
            "button[type='button']",
            ".lm-button",
            ".btn-light"
        ]

        for selector in button_selectors:
            try:
                if selector.startswith("//"):
                    buttons = driver.find_elements(By.XPATH, selector)
                elif "contains" in selector:
                    # Для jQuery-style селекторов используем XPath
                    buttons = driver.find_elements(
                        By.XPATH, "//button[contains(text(), 'Показать больше')]")
                else:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)

                for button in buttons:
                    if "Показать больше" in button.text:
                        print("🔄 Нажимаем 'Показать больше'...")
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(3)
                        return True

            except Exception as e:
                continue

        print("❌ Кнопка 'Показать больше' не найдена")
        return False

    except Exception as e:
        print(f"❌ Ошибка при нажатии кнопки: {e}")
        return False


def scrape_channels():
    """Собирает данные о каналах с текущей страницы"""
    print("📊 Собираем данные о каналах...")
    time.sleep(3)

    channels_data = []

    # Метод 1: Ищем элементы с data-src (кнопки избранного)
    favorite_elements = driver.find_elements(
        By.CSS_SELECTOR, "[data-src*='@']")
    print(f"🔍 Найдено {len(favorite_elements)} элементов с data-src")

    for element in favorite_elements:
        try:
            data_src = element.get_attribute("data-src")

            if data_src and "@" in data_src and "/create" in data_src:
                # Извлекаем @username из data-src
                username = data_src.split('@')[-1].split('/')[0]

                # Формируем полную ссылку
                full_url = f"нужно было в моем кейсе по поиску страниц каналов "

                channels_data.append({
                    'username': f"@{username}",
                    'url': full_url
                })

        except Exception as e:
            continue

    # Метод 2: Ищем ссылки на каналы (резервный метод)
    if not channels_data:
        channel_links = driver.find_elements(
            By.CSS_SELECTOR, "a[href*='/channel/@']")
        print(f"🔍 Найдено {len(channel_links)} ссылок на каналы")

        for link in channel_links:
            try:
                href = link.get_attribute("href")
                if href and "/channel/@" in href:
                    username = href.split('/channel/@')[-1].split('/')[0]

                    channels_data.append({
                        'username': f"@{username}",
                        'url': f"нужно было в моем кейсе по поиску страниц каналов "
                    })

            except Exception as e:
                continue

    print(f"✅ Собрано {len(channels_data)} каналов с текущей страницы")
    return channels_data


def scrape_with_pagination(search_query, max_channels=2000):
    """Парсит каналы с пагинацией 'Показать больше'"""
    all_channels = []

    # Выполняем поиск
    if not perform_search(search_query):
        return all_channels

    page = 1
    consecutive_failures = 0

    while len(all_channels) < max_channels and consecutive_failures < 3:
        print(f"\n📄 Страница {page} | Всего собрано: {len(all_channels)}")

        # Собираем каналы с текущей страницы
        current_channels = scrape_channels()

        if current_channels:
            # Добавляем только новые каналы
            new_channels = []
            for channel in current_channels:
                if channel not in all_channels:
                    new_channels.append(channel)

            all_channels.extend(new_channels)
            print(f"➕ Добавлено {len(new_channels)} новых каналов")

            # Сбрасываем счетчик неудач
            consecutive_failures = 0

        else:
            print("❌ Не удалось собрать каналы")
            consecutive_failures += 1

        # Проверяем лимит
        if len(all_channels) >= max_channels:
            print(f"🎯 Достигнут лимит в {max_channels} каналов!")
            break

        # Пытаемся нажать "Показать больше"
        if click_show_more():
            page += 1
            # Ждем загрузки новых элементов
            time.sleep(5)
        else:
            print("❌ Не удалось найти кнопку 'Показать больше'")
            consecutive_failures += 1

        # Если несколько неудач подряд - прекращаем
        if consecutive_failures >= 3:
            print("🚫 Слишком много неудач, прекращаем сбор")
            break

    return all_channels


def save_to_csv(data, filename="tgstat_channels.csv"):
    """Сохраняет данные в CSV файл"""
    if not data:
        print("⚠️ Нет данных для сохранения")
        return False

    try:
        # Удаляем дубликаты
        unique_data = []
        seen_usernames = set()

        for item in data:
            if item['username'] not in seen_usernames:
                unique_data.append(item)
                seen_usernames.add(item['username'])

        # Сохраняем в CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['username', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in unique_data:
                writer.writerow(row)

        print(f"💾 Данные сохранены в файл: {filename}")
        print(f"📊 Всего уникальных каналов: {len(unique_data)}")
        return True

    except Exception as e:
        print(f"❌ Ошибка при сохранении в CSV: {e}")
        return False


# 🚀 ЗАПУСКАЕМ ПРОЦЕСС
print("=" * 60)
print("🤖 БОТ ДЛЯ ПАРСИНГА какого-то сайта с авторизацией через тг")
print("=" * 60)

# Проверяем авторизацию
if not load_cookies() or not check_login():
    print("❌ Нужна ручная авторизация")
    manual_login()
else:
    print("✅ Авторизация через куки успешна!")

# Парсим каналы
search_query = "недвижимость"
max_channels = 2000

print(f"\n🚀 Начинаем парсинг по запросу: '{search_query}'")
print(f"🎯 Цель: собрать до {max_channels} каналов")

all_channels = scrape_with_pagination(search_query, max_channels)

# Сохраняем результаты
if all_channels:
    filename = f"tgstat_{search_query}_{len(all_channels)}_channels.csv"
    if save_to_csv(all_channels, filename):
        print("✅ Парсинг завершен успешно!")
    else:
        print("❌ Ошибка при сохранении файла")
else:
    print("❌ Не удалось собрать данные")

# Показываем статистику
print(f"\n📊 ИТОГИ:")
print(f"• Собрано каналов: {len(all_channels)}")
print(f"• Файл: n_{search_query}_*.csv")
print(f"• Текущий URL: {driver.current_url}")

input("\nНажми Enter чтобы закрыть браузер...")
driver.quit()
