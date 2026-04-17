from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from engine import ask_azm, generate_steps_with_ai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# سيرف الـ HTML مباشرة
app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/")
def root():
    return FileResponse("index.html")


class ChatRequest(BaseModel):
    messages: list
    profile: dict = {}


class StepsRequest(BaseModel):
    task: str
    profile: dict = {}


@app.post("/chat")
def chat(req: ChatRequest):
    reply = ask_azm(req.messages, profile=req.profile)
    return {"reply": reply}


@app.post("/steps")
def steps(req: StepsRequest):
    result = generate_steps_with_ai(req.task, profile=req.profile)
    return {"steps": result}
