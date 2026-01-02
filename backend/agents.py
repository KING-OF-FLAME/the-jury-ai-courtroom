import os
import logging
import re
import ast
from typing import Dict, Any
from openai import AsyncOpenAI
import httpx
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()
logging.basicConfig(level=logging.INFO)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = os.getenv("OR_SITE_URL", "http://localhost:8501")
APP_NAME = os.getenv("OR_APP_NAME", "TheJuryAI")

# --- Prompts ---
DEFAULT_PROPOSER_PROMPT = "You are {persona}. Role: Creative Architect. Task: Provide a detailed, happy-path solution to the user query."
DEFAULT_CRITIC_PROMPT = "You are {persona}. Role: Skeptical Reviewer. Task: Review the Proposal. Find security flaws, logic errors, and missing constraints. Output a Dissenting Opinion."
DEFAULT_JUDGE_PROMPT = "You are {persona}. Role: Final Judge. Task: Weigh the Proposal against the Critique. Issue a Final Verdict. End your response with [[CONFIDENCE: 0-100]]."

http_client = httpx.AsyncClient(timeout=600.0)
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    http_client=http_client,
    default_headers={"HTTP-Referer": SITE_URL, "X-Title": APP_NAME},
)

def clean_reasoning(raw_data):
    """Fixes 'List of Dicts' strings from certain models"""
    if not raw_data: return None
    text_str = str(raw_data)
    
    # Regex for 'text': '...'
    pattern = r"'text':\s*([\"'])(.*?)\1"
    matches = re.findall(pattern, text_str, re.DOTALL)
    if matches:
        return "".join(m[1] for m in matches).replace("\\n", "\n")
    
    try:
        if isinstance(raw_data, str) and (raw_data.startswith('[') or raw_data.startswith('{')):
             parsed = ast.literal_eval(raw_data)
             if isinstance(parsed, list):
                 return "".join([x.get('text', '') for x in parsed if isinstance(x, dict)])
    except: pass
    return text_str

def extract_response_data(completion) -> Dict[str, Any]:
    msg = completion.choices[0].message
    content = msg.content or ""
    dump = msg.model_dump()
    
    reasoning = clean_reasoning(dump.get("reasoning_details") or dump.get("reasoning"))
    
    if not reasoning and "<think>" in content:
        try:
            parts = content.split("</think>")
            if len(parts) > 1:
                reasoning = parts[0].replace("<think>", "").strip()
                content = parts[1].strip()
        except: pass

    conf = 0.0
    try:
        m = re.search(r"\[\[CONFIDENCE:\s*(\d+)\]\]", content)
        if m: conf = float(m.group(1))
    except: pass

    final_content = content
    if reasoning:
        final_content = f"[Thinking Process]\n{reasoning}\n\n[Output]\n{content}"

    usage = completion.usage
    tok = usage.total_tokens if usage else 0
    cost = (tok / 1_000_000) * 2.00

    return {"content": final_content, "usage": {"total_tokens": tok}, "confidence": conf, "cost": cost}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10), retry=retry_if_exception_type(httpx.RequestError))
async def run_agent(model, sys_prompt, user_content):
    if len(user_content) > 15000: user_content = user_content[:7500] + "\n...[TRUNCATED]...\n" + user_content[-7500:]
    try:
        res = await client.chat.completions.create(
            model=model, messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_content}],
            extra_body={"include_reasoning": True}
        )
        return extract_response_data(res)
    except Exception as e:
        if "400" in str(e): 
            res = await client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": f"{sys_prompt}\n\n{user_content}"}]
            )
            return extract_response_data(res)
        raise e

async def get_proposer_response(q, m, p): return await run_agent(m, DEFAULT_PROPOSER_PROMPT.format(persona=p), f"Query: {q}")
async def get_critic_response(q, prop, m, p): return await run_agent(m, DEFAULT_CRITIC_PROMPT.format(persona=p), f"Query: {q}\n\nProposal:\n{prop}")
async def get_judge_verdict(q, prop, crit, m, p): return await run_agent(m, DEFAULT_JUDGE_PROMPT.format(persona=p), f"Query: {q}\n\n1. Proposal:\n{prop}\n\n2. Critique:\n{crit}")