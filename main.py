from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from engine import ask_azm

app = FastAPI()

# مهم عشان الفرونت يتواصل مع الباك
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Request Model
# =========================
class ChatRequest(BaseModel):
    messages: list
    profile: dict | None = None


# =========================
# Chat Endpoint
# =========================
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        result = ask_azm(req.messages, req.profile)

        print("RESULT FROM ENGINE:", result)

        return JSONResponse(content={
            "reply": result.get("support_text", ""),
            "support_text": result.get("support_text", ""),
            "spark_task": result.get("spark_task", {}),
            "micro_tasks": result.get("micro_tasks", []),
            "follow_up_question": result.get("follow_up_question", "")
        })

    except Exception as e:
        print("ERROR:", e)
        return JSONResponse(
            status_code=500,
            content={"reply": "صار خطأ في السيرفر"}
        )


# =========================
# Serve HTML
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")

@app.get("/")
def serve_index():
    if os.path.exists(INDEX_PATH):
        return FileResponse(INDEX_PATH)
    return JSONResponse({"error": "index.html مو موجود"})

