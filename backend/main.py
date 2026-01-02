from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import time
from . import models, database, agents

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="The Jury API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def update_logs(case, role, model, content, duration, tokens, cost=0.0):
    current = list(case.debate_log) if case.debate_log else []
    current = [x for x in current if x.get('role') != role] 
    current.append({"role": role, "model": model, "content": content, "duration": duration, "tokens": tokens, "cost": cost})
    # Sort: Proposer(1) -> Critic(2) -> Judge(3)
    case.debate_log = sorted(current, key=lambda x: {"Proposer":1, "Critic":2, "Judge":3}.get(x.get("role"), 99))

def map_res(c):
    return models.CaseResponse(
        id=c.id, query=c.query_text,
        proposer_model=c.proposer_model, critic_model=c.critic_model, judge_model=c.judge_model,
        proposer_persona=c.proposer_persona or "Senior Architect",
        critic_persona=c.critic_persona or "Security Auditor",
        judge_persona=c.judge_persona or "Chief Justice",
        proposer=c.proposer_output, critic=c.critic_output, verdict=c.final_verdict,
        estimated_cost=c.estimated_cost or 0.0, confidence_score=c.judge_confidence or 0.0,
        logs=c.debate_log, total_time=c.total_time, total_tokens=c.total_tokens
    )

@app.post("/case/start", response_model=models.CaseResponse)
def start(req: models.CaseRequest, db: Session = Depends(database.get_db)):
    exist = db.query(models.CaseDB).filter(models.CaseDB.query_text == req.query, models.CaseDB.final_verdict.isnot(None)).first()
    if exist: return map_res(exist)
    
    new = models.CaseDB(
        query_text=req.query, proposer_model=req.proposer_model, critic_model=req.critic_model, judge_model=req.judge_model,
        proposer_persona=req.proposer_persona or "Senior Architect",
        critic_persona=req.critic_persona or "Security Auditor",
        judge_persona=req.judge_persona or "Chief Justice",
        debate_log=[]
    )
    db.add(new); db.commit(); db.refresh(new)
    return map_res(new)

@app.post("/case/{cid}/proposer", response_model=models.CaseResponse)
async def run_p(cid: int, db: Session = Depends(database.get_db)):
    c = db.query(models.CaseDB).get(cid)
    if not c: raise HTTPException(404)
    t0 = time.time()
    res = await agents.get_proposer_response(c.query_text, c.proposer_model, c.proposer_persona or "Proposer")
    c.proposer_output = res["content"]
    c.proposer_time = round(time.time()-t0, 2)
    c.proposer_tokens = res["usage"]["total_tokens"]
    c.estimated_cost = (c.estimated_cost or 0) + res["cost"]
    update_logs(c, "Proposer", c.proposer_model, c.proposer_output, c.proposer_time, c.proposer_tokens, res["cost"])
    db.commit()
    return map_res(c)

@app.post("/case/{cid}/critic", response_model=models.CaseResponse)
async def run_c(cid: int, db: Session = Depends(database.get_db)):
    c = db.query(models.CaseDB).get(cid)
    if not c: raise HTTPException(404)
    t0 = time.time()
    res = await agents.get_critic_response(c.query_text, c.proposer_output, c.critic_model, c.critic_persona or "Critic")
    c.critic_output = res["content"]
    c.critic_time = round(time.time()-t0, 2)
    c.critic_tokens = res["usage"]["total_tokens"]
    c.estimated_cost += res["cost"]
    update_logs(c, "Critic", c.critic_model, c.critic_output, c.critic_time, c.critic_tokens, res["cost"])
    db.commit()
    return map_res(c)

@app.post("/case/{cid}/judge", response_model=models.CaseResponse)
async def run_j(cid: int, db: Session = Depends(database.get_db)):
    c = db.query(models.CaseDB).get(cid)
    if not c: raise HTTPException(404)
    t0 = time.time()
    res = await agents.get_judge_verdict(c.query_text, c.proposer_output, c.critic_output, c.judge_model, c.judge_persona or "Judge")
    c.final_verdict = res["content"]
    c.judge_time = round(time.time()-t0, 2)
    c.judge_tokens = res["usage"]["total_tokens"]
    c.judge_confidence = res["confidence"]
    c.estimated_cost += res["cost"]
    update_logs(c, "Judge", c.judge_model, c.final_verdict, c.judge_time, c.judge_tokens, res["cost"])
    db.commit()
    return map_res(c)

@app.get("/history", response_model=List[models.CaseHistoryItem])
def get_hist(limit: int = 20, db: Session = Depends(database.get_db)):
    # Grab latest cases
    cases = db.query(models.CaseDB).order_by(models.CaseDB.created_at.desc()).limit(limit).all()
    # CRITICAL FIX: Ensure Frontend never receives NULL for Query, Cost, or Confidence
    return [models.CaseHistoryItem(
        id=x.id, 
        query=x.query_text or "Untitled Case", 
        verdict=x.final_verdict[:50] if x.final_verdict else "Pending...", 
        timestamp=str(x.created_at), 
        estimated_cost=x.estimated_cost or 0.0, 
        confidence=x.judge_confidence or 0.0
    ) for x in cases]

@app.get("/case/{cid}", response_model=models.CaseResponse)
def get_detail(cid: int, db: Session = Depends(database.get_db)):
    return map_res(db.query(models.CaseDB).get(cid))