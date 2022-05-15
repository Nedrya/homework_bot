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
    log_message = 'API не доступен, код: '
    if status == requests.codes.ok:
        try:
            return response.json()
        except Exception as error:
            logging.error(f'{log_message} {status}')
            raise error
    else:
        logging.error(f'{log_message} {status}')
        raise(f'{log_message} {status}')


def check_response(response):
    """Проверяет ответ API на корректность."""
    if type(response) == dict:
        if 'homeworks' in response:
            homeworks = response['homeworks']
            if type(homeworks) == list:

                return homeworks
            else:
                logging.error('homeworks вернул None')
                raise TypeError
        else:
            logging.error('homeworks в ответе не найден')
            raise AssertionError
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
            current_timestamp = api_answer.get('current_date')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
