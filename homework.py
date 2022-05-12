import logging
import os
import requests
import telegram

from dotenv import load_dotenv
import time


load_dotenv()
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = 995425006

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        print('Отправлено сообщение в Telegram')
        logging.INFO('Сообщение отправлено в Telegram')
    except Exception as error:
        logging.error(f'Ошибка "{error}" при отправке '
                      f'сообщения "{message}" в Telegram')


def get_api_answer(current_timestamp):
    """Делает запрос к  эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS,
                            params=params)
    status = response.status_code
    if status == requests.codes.ok:
        try:
            print(response.json())
            return response.json()
        except Exception as error:
            logging.error(f'API не доступен, код: {status}')
            raise error
    else:
        logging.error(f'API не доступен, код: {status}')
        raise(f'API не доступен, код: {status}')


def check_response(response):
    """Проверяет ответ API на корректность."""
    print(f'Начало responce {type(response)}')
    if type(response) == dict:
        homeworks = response['homeworks']
        if type(homeworks) == list:
            print(homeworks)
            return homeworks
        else:
            print('homeworks вернул None')
            logging.error('homeworks вернул None')
    else:
        logging.error('Не верный тип данных')
        raise TypeError


def parse_status(homework):
    """Извлекает из информации домашней работе статус этой работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
        print('Статус - {verdict}')
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except KeyError:
        logging.error(f'Статус домашней работы "{homework_status}" '
                      'отсутствует в списке')
        raise KeyError
    except Exception:
        logging.error('Отсутствует статус домашней работы')
        raise Exception


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN:
        print('Проверка токенов - Успешно')
        return True
    else:
        logging.critical('Отсутствует одна из обязательных переменных')
        return False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        return None

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            api_answer = get_api_answer(current_timestamp)
            response = check_response(api_answer)
            if response != []:
                status = parse_status(response[0])
                send_message(bot, status)
            else:
                logging.debug('Статус домашней работы не обновлен ревьюером')
                print('Нет изменений статуса')
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
