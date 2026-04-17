from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from engine import ask_azm, generate_steps_with_ai


BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"

app = FastAPI(title="Azm API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory=str(BASE_DIR)), name="static")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(default_factory=list)
    profile: dict[str, Any] = Field(default_factory=dict)


class StepsRequest(BaseModel):
    task: str
    profile: dict[str, Any] = Field(default_factory=dict)


@app.get("/")
def root():
    if not INDEX_FILE.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "ملف index.html غير موجود داخل المشروع"}
        )
    return FileResponse(INDEX_FILE)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        payload_messages = [msg.model_dump() for msg in req.messages]
        reply = ask_azm(payload_messages, profile=req.profile)
        return {"reply": reply}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "صار خطأ أثناء توليد الرد", "details": str(e)}
        )


@app.post("/steps")
def steps(req: StepsRequest):
    try:
        result = generate_steps_with_ai(req.task, profile=req.profile)
        return {"steps": result}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "صار خطأ أثناء توليد الخطوات", "details": str(e)}
        )