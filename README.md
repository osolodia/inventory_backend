## Установка
Создаём виртуальное окружение:
python -m venv venv

Активируем виртуальное окружение:  
Windows: venv\Scripts\activate  
Linux: source venv/bin/activate

Устанавливаем зависимости:
pip install -r requirements.txt  

## Настройка базы данных
В файле app/db/database.py укажите параметры подключения:
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/inventory_db"

## Запуск сервера
uvicorn app.main:app --reload

Эндпоинт всех документов: http://127.0.0.1:8000/documents  
Эндпоинт конкретного документа: http://127.0.0.1:8000/documents/{id}

## Примеры API
Получить все документы: http://127.0.0.1:8000/documents   
Пример ответа: [{"id":1,"number":"DOC-001","date":"2025-12-07","comment":"Тестовый документ","company":"Компания А","document_type":"Приход"}]

Получить конкретный документ: http://127.0.0.1:8000/documents/1 
Пример ответа: {"id":1,"number":"DOC-001","date":"2025-12-07","comment":"Тестовый документ","company":"Компания А","document_type":"Приход"}
