import os
import telebot
import requests
from dotenv import load_dotenv
from telebot import types

# Загружаем переменные окружения (для локального запуска)
load_dotenv()

# Если переменной нет, бот возьмет токен напрямую (для GitHub)
# ВАЖНО: Вставь свой токен в кавычки ниже, если запускаешь на сервере без .env файла.
# Но на GitHub его оставлять нельзя, поэтому мы используем переменную.
TOKEN = os.getenv("TELEGRAM_TOKEN", "ТВОЙ_ТОКЕН_ОТ_BOTFATHER_СЮДА")

bot = telebot.TeleBot(TOKEN)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_coordinates(city: str):
    """Шаг 1: Получаем координаты города через геокодер Open-Meteo"""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "ru", "format": "json"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "results" not in data:
            return None, None, None
            
        location = data["results"][0]
        return location["latitude"], location["longitude"], location["name"]
    except Exception:
        return None, None, None

def get_weather_emoji(weather_code: int) -> str:
    """Возвращает эмодзи для кодов погоды Open-Meteo (WMO codes)"""
    if weather_code == 0: return "☀️ Ясно"
    elif weather_code in [1, 2, 3]: return "⛅️ Переменная облачность"
    elif weather_code in [45, 48]: return "🌫 Туман"
    elif weather_code in [51, 53, 55, 56, 57]: return "🌦 Морось"
    elif weather_code in [61, 63, 65, 66, 67, 80, 81, 82]: return "🌧 Дождь"
    elif weather_code in [71, 73, 75, 77, 85, 86]: return "❄️ Снег"
    elif weather_code in [95, 96, 99]: return "⛈ Гроза"
    else: return "🌍 Неизвестно"

def fetch_weather(city: str) -> str:
    """Шаг 2: Запрашиваем погоду по координатам"""
    lat, lon, city_name = get_coordinates(city)
    
    if lat is None:
        return "❌ Город не найден. Попробуй написать название по-другому (например, на английском)."

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "relative_humidity_2m",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        current = data["current_weather"]
        temp = current["temperature"]
        wind = current["windspeed"]
        weather_code = current["weathercode"]
        
        # Влажность берем из первого часа в массиве hourly
        humidity = data["hourly"]["relative_humidity_2m"][0]
        
        emoji = get_weather_emoji(weather_code)
        
        result_text = (
            f"📍 <b>Погода в городе {city_name}</b>\n\n"
            f"{emoji}\n"
            f"🌡 Температура: <b>{temp:.1f}°C</b>\n"
            f"💧 Влажность: {humidity}%\n"
            f"💨 Ветер: {wind} км/ч"
        )
        return result_text
        
    except requests.exceptions.Timeout:
        return "⏳ Сервер погоды не отвечает. Попробуйте позже."
    except Exception:
        return "📡 Ошибка при получении данных о погоде. Проверьте интернет."

# --- ОБРАБОТЧИКИ БОТА ---

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_madrid = types.KeyboardButton('🇪🇸 Погода в Мадриде')
    btn_kaluga = types.KeyboardButton('🇷🇺 Погода в Калуге')
    markup.add(btn_madrid, btn_kaluga)
    
    bot.send_message(
        message.chat.id,
        "Привет! 🌤 Я бот, который покажет погоду в любом городе мира.\n\n"
        "Просто напиши мне название города (например, <i>Москва</i> или <i>Barcelona</i>), и я пришлю сводку.\n\n"
        "Или выбери готовый вариант ниже 👇",
        parse_mode='HTML',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '🇪🇸 Погода в Мадриде')
def weather_madrid(message):
    bot.send_message(message.chat.id, fetch_weather("Madrid"), parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == '🇷🇺 Погода в Калуге')
def weather_kaluga(message):
    bot.send_message(message.chat.id, fetch_weather("Kaluga"), parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    city = message.text.strip()
    
    waiting_msg = bot.send_message(message.chat.id, f"🔍 Ищу погоду для города <b>{city}</b>...", parse_mode='HTML')
    
    weather_text = fetch_weather(city)
    
    bot.delete_message(message.chat.id, waiting_msg.message_id)
    bot.send_message(message.chat.id, weather_text, parse_mode='HTML')

# --- ЗАПУСК ---
if __name__ == '__main__':
    print("Weather bot (Open-Meteo) is running...")
    bot.infinity_polling()
