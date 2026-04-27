from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from backend.database import get_db, init_db, Debate, BiasFlag
from backend.agents import run_advocate, run_challenger, run_arbitrator, run_bias_scanner, run_final_verdict

load_dotenv()

app = FastAPI(title="CivicMind API")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


@app.on_event("startup")
async def startup():
    init_db()
    print("🚀 CivicMind running at http://localhost:8000")


class DebateRequest(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})


@app.post("/api/debate")
async def run_debate(body: DebateRequest, db: Session = Depends(get_db)):
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        advocate_arg   = run_advocate(question)
        challenger_arg = run_challenger(question, advocate_arg)
        arb            = run_arbitrator(question, advocate_arg, challenger_arg)
        bias_flags     = run_bias_scanner(question)
        verdict        = run_final_verdict(question, arb["for_score"], arb["against_score"], arb["neutral_score"])

        debate = Debate(
            question       = question,
            advocate_arg   = advocate_arg,
            challenger_arg = challenger_arg,
            arbitrator_arg = arb["synthesis"],
            for_score      = arb["for_score"],
            against_score  = arb["against_score"],
            neutral_score  = arb["neutral_score"],
            final_verdict  = verdict,
            bias_flags     = bias_flags
        )
        db.add(debate)
        db.commit()
        db.refresh(debate)

        for flag in bias_flags:
            db.add(BiasFlag(debate_id=debate.id, bias_type=flag["type"], severity=flag["severity"], description=flag["description"]))
        db.commit()

        return {
            "id": debate.id, "question": debate.question,
            "advocate_arg": debate.advocate_arg, "challenger_arg": debate.challenger_arg,
            "arbitrator_arg": debate.arbitrator_arg, "for_score": debate.for_score,
            "against_score": debate.against_score, "neutral_score": debate.neutral_score,
            "final_verdict": debate.final_verdict, "bias_flags": debate.bias_flags
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/debates")
async def get_debates(db: Session = Depends(get_db)):
    debates = db.query(Debate).order_by(Debate.created_at.desc()).limit(20).all()
    return [{"id": d.id, "question": d.question, "for_score": d.for_score,
             "against_score": d.against_score, "final_verdict": d.final_verdict,
             "bias_count": len(d.bias_flags or []), "created_at": d.created_at.isoformat()} for d in debates]


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    debates = db.query(Debate).all()
    total = len(debates)
    return {
        "total_debates":       total,
        "avg_for_score":       round(sum(d.for_score for d in debates) / total, 1) if total else 0,
        "avg_against":         round(sum(d.against_score for d in debates) / total, 1) if total else 0,
        "total_bias_flags":    sum(len(d.bias_flags or []) for d in debates)
    }
