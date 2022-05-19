Бот умеет:

<ol>
<li>раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы;</li>
<li>при обновлении статуса анализировать ответ API и отправлять пользователю соответствующее уведомление в Telegram;</li>
<li>логировать свою работу и сообщать пользователю о важных проблемах сообщением в Telegram.</li>
</ol>

## Технологии:
<ol>
<li>Python 3</li>
<li>Django REST Framework</li>
<li>SQLite3</li>
<li>SimpleJWT</li>
</ol>

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/blink18iii/homework_bot.git
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```
```
cd homework_bot/
```
```
. venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
