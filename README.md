# 🌤 Telegram Weather Bot

A fast and lightweight Telegram bot that provides real-time weather information for any city in the world. 

Built as a portfolio project to demonstrate skills in working with external APIs, JSON parsing, and building interactive Telegram interfaces.

## ✨ Features

*   **Global Search:** Get weather for any city by simply typing its name.
*   **Detailed Info:** Temperature, humidity, wind speed, and weather conditions.
*   **Smart Emojis:** Automatically selects a weather emoji based on WMO weather codes.
*   **No API Key Required:** Uses the modern and free Open-Meteo API (geocoding + forecast).
*   **Error Handling:** Gracefully handles network errors, invalid city names, and timeouts.

## 🛠 Tech Stack

*   **Language:** Python 3.10+
*   **Libraries:** `pyTelegramBotAPI`, `requests`, `python-dotenv`
*   **API:** Open-Meteo (Geocoding & Forecast API)

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/corotyginn/weather-bot.git
