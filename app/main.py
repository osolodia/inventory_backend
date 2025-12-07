from fastapi import FastAPI
from app.api import documents
from fastapi.responses import RedirectResponse

app = FastAPI()

# Подключаем роутер
app.include_router(documents.router)
