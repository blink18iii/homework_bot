import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    handlers=[logging.FileHandler('filename.log'), logging.StreamHandler()],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


error_sent_messages = []


class CustomError(Exception):
    """Кастомная ошибка API."""

    pass


def send_message(bot, message):
    """отправляем сообщение о статусе задания в телеграм."""
    logging.debug(f'Отправляем сообщение в телеграм: {message}')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение отправлено: {message}')
    except Exception as e:
        logging.error(f'Ошибка отправки сообщения: {e}')


def log_and_telegram(bot, message):
    """Логи ошибок уровня ERROR.
    Однократно отправляет информацию об ошибках в телеграм,
    если это не та же ошибка.
    """
    logger.error(message)
    try:
        send_message(bot, message)
        error_sent_messages.append(message)
    except Exception as error:
        logger.info('Не удалось отправить сообщение об ошибке, '
                    f'{error}')


def get_api_answer(current_timestamp):
    """Отправляет запрос к API."""
    logging.info("Получение ответа от сервера")
    timestamp = current_timestamp - RETRY_TIME
    params = {'from_date': timestamp}
    try:
        # Делает запрос к единственному эндпоинту API-сервиса.
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            # В качестве параметра функция получает временную метку.
            params=params
        )
    except Exception:
        message = 'API ведет себя незапланированно'
        raise CustomError(message)
    try:
        if response.status_code != HTTPStatus.OK:
            message = 'Эндпоинт не отвечает'
            raise Exception(message)
    except Exception:
        message = 'API ведет себя незапланированно'
        raise CustomError(message)
    # В случае успешного запроса должна вернуть ответ API, преобразовав его
    # из формата JSON к типам данных Python.
    return response.json()


def check_response(response):
    """
    Проверяет ответ API на корректность.
    если ответ корректен - выводит список домашних работ.
    """
    logging.debug('Проверка ответа API на корректность')
    if not isinstance(response, dict):
        message = 'Ответ API не словарь, а что-то другое'
        raise TypeError(message)
    if ['homeworks'][0] not in response:
        message = 'В ответе API нет домашней работы, ты запушил?'
        raise IndexError(message)
    homework = response.get('homeworks')[0]
    return homework


def parse_status(homework):
    """
    Извлекает из информации о конкретной домашней работе статус этой работы.
    В качестве параметра функция получает только один элемент
    из списка домашних работ. В случае успеха, функция возвращает
    подготовленную для отправки в Telegram строку,
    содержащую один из вердиктов словаря HOMEWORK_VERDICTS.
    """
    keys = ['status', 'homework_name']
    for key in keys:
        if key not in homework:
            message = f'Ключа {key} нет в ответе API'
            raise KeyError(message)
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        message = 'Неизвестный статус домашней работы'
        raise KeyError(message)
    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет переменные окружения."""
    if not PRACTICUM_TOKEN or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 0
    check_result = check_tokens()
    if check_result is False:
        message = 'Проблемы с переменными окружения'
        logger.critical(message)
        raise SystemExit(message)

    while True:
        try:
            response = get_api_answer(current_timestamp)
            if 'current_date' in response:
                current_timestamp = response['current_date']
            homework = check_response(response)
            if homework is not None:
                message = parse_status(homework)
                if message is not None:
                    send_message(bot, message)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            log_and_telegram(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Выход из программы по команде Ctrl+C')
    sys.exit(0)
