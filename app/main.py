from fastapi import FastAPI
from app.routers import auth, users, accounts, transactions, keys_pix
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(keys_pix.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}