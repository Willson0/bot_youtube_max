# MAX Video Downloader Bot

<p align="center">
  <img src="https://img.shields.io/badge/Status-Completed-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Language-Python-3776ab?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Platform-MAX%20Bot-111111?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Type-Downloader%20Bot-6c5ce7?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Deployment-systemctl-2ecc71?style=for-the-badge" />
</p>

<p align="center">
  Telegram-style bot for the <b>MAX</b> social network, designed to download videos from popular online platforms by link.
</p>

---

## О проекте

**MAX Video Downloader Bot** — это бот для социальной сети **MAX**, который позволяет пользователям скачивать видео по ссылке с различных интернет-ресурсов.

Бот поддерживает работу с популярными платформами, включая:
- YouTube
- Instagram
- Pinterest
- и другие источники

Также в проекте реализована возможность **обязательной подписки на канал в MAX** перед использованием функционала бота.

---

## Основной функционал

- Скачивание видео по ссылке
- Поддержка нескольких популярных платформ
- Проверка обязательной подписки на канал MAX
- Пользовательский интерфейс, адаптированный под MAX
- Простая и понятная навигация для пользователя
- Удобное администрирование и запуск на Linux-серверах

---

## Технологии

- Python
- Linux
- systemctl
- API-интеграция
- Парсинг / загрузка медиа-контента

---

## Скриншот

<p align="center">
  <img width="70%" alt="image" src="https://github.com/user-attachments/assets/9dfd8d35-503c-412e-99e8-203d8c9f5502" />
</p>

---

## Установка

Проект предназначен для стандартной Linux-установки и запуска через `systemctl`.

### 1. Клонирование репозитория

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка конфигурации

Заполните `.env` или конфигурационный файл проекта:
- токен бота
- параметры подключения
- ссылку на обязательный канал MAX
- дополнительные настройки загрузчика

### 5. Создание systemd-сервиса

Создайте файл:

```bash
sudo nano /etc/systemd/system/max-bot.service
```

Пример конфигурации:

```ini
Unit
Description=MAX Video Downloader Bot
After=network.target

Service
Type=simple
User=your-user
WorkingDirectory=/path/to/your-project
ExecStart=/path/to/your-project/venv/bin/python main.py
Restart=always
RestartSec=5

Install
WantedBy=multi-user.target```
```

### 6. Запуск сервиса

```bash
sudo systemctl daemon-reload
sudo systemctl enable max-bot
sudo systemctl start max-bot
sudo systemctl status max-bot
```

---

## Особенности

- Работа без пользовательского веб-интерфейса
- Удобный UX внутри соц. сети MAX
- Быстрый запуск на Linux
- Автоматический рестарт при падении
- Подходит для постоянной работы на сервере

---

## Автор

GitHub: https://github.com/Willson0

---

## Лицензия

Проект создан в демонстрационных и портфолио-целях.
