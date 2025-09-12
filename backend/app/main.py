from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="AutoU - Backend (setup)")

@app.get("/health")
def health():
    return {"ok": True}
