from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, documents, companies, companytypes, documenttypes, categories, units, employees
from app.routers import auth

app = FastAPI(title="Inventory API")

# Настройка CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(products.router)
app.include_router(documents.router)
app.include_router(companies.router)
app.include_router(companytypes.router)
app.include_router(documenttypes.router)
app.include_router(categories.router)
app.include_router(units.router)
app.include_router(employees.router)
app.include_router(auth.router)

# Корневой эндпоинт
@app.get("/")
def root():
    return {"message": "Inventory API is running"}
