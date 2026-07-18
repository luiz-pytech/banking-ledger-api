from fastapi import FastAPI
from app.routers import auth, users, accounts, transactions, keys_pix

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)
#app.include_router(accounts.router)
#app.include_router(transactions.router)
#app.include_router(keys_pix.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}