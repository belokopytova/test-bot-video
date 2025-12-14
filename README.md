 Telegram-бот, который умеет по запросу на естественном языке считать нужные метрики по данным в итоговой статистике по видео . Парсинг естественных запросов выполняется с использованием регулярных выражений.


 #### Технологии
 
   - Python 3.12
 
   - Aiogram 3.x
 
   - PostgreSQL
 



### 1. Установка

* Клонировать репозиторий

  ```
  git clone https://github.com/belokopytova/test-bot-video
  ```

* создать базу данных PostgreSQL
  

* в файле .env заполнить переменные

  ```TG_BOT_TOKEN="" 

    POSTGRES_USER=""

    POSTGRES_PASSWORD=""

    POSTGRES_DB=""

    DATABASE_URL="postgresql://postgres:yourpassword@localhost:5432/namedatabase" 

    HOST_DB="localhost"

    PORT_DB=""
    ```

* установить зависимости
  
  `python -m pip install -r requirements.txt`

* создать таблицы в базе данных
  
    с помощью запуска `db.py`

### 2. Загрузить данные

  Чтобы из файла `videos.json` загрузить данные в базу данных, нужно запустить `load_data.py`

### 3. Запуск бота

  Чтобы запустить телеграм бота нужно использовать `bot.py`



