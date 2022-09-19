### О проекте:
Данный проект является телеграм-ботом, который проверяет статус домашней работы на Яндекс.Практикуме и уведомляет ученика о его изменениях. Для подключения к Яндекс.Практикуму и телеграму используется API.

### Принцип работы бота:
• с переодичностью раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы.

• при обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram.

• логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

### Применены технологии
Python 3.7
python-telegram-bot

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Nedrya/homework_bot.git
```

Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
```
```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Запустить проект:
```
homework.py
```

Автор проекта: Недря Сергей.