"""
Orchestrator Agent (Powered by Gemini)
──────────────────
1. Classifies intent with a confidence score
2. Routes to the correct sub-agent
3. Injects memory context into the sub-agent prompt
"""
import os, json, re
import google.generativeai as genai
from app.memory.memory_store import build_memory_context, stm_add

# ── Gemini Configuration ─────────────────────────────────────────────────────
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = os.getenv("LLM_MODEL", "gemini-2.5-flash")

# ── Intent classification ────────────────────────────────────────────────────

INTENT_SYSTEM = """You are an HR request classifier. 
Classify the user's message into exactly one of these intents:
  - scheduling   (meetings, interviews, calendar, shifts)
  - leave        (vacation, sick leave, PTO, time-off requests)
  - compliance   (policies, rules, legal, regulations, code of conduct)
  - clarification (anything ambiguous that needs more info)

Respond ONLY with a valid JSON object in this exact format (no markdown):
{"intent": "<intent>", "confidence": <0.0-1.0>}"""

def classify_intent(message: str) -> tuple[str, float]:
    """Returns (intent, confidence)."""
    classifier_model = genai.GenerativeModel(MODEL_NAME, system_instruction=INTENT_SYSTEM)
    resp = classifier_model.generate_content(message)
    
    raw = resp.text.strip()
    # strip markdown fences if model adds them
    raw = re.sub(r"```json|```", "", raw).strip()
    data = json.loads(raw)
    return data["intent"], float(data["confidence"])

# ── Sub-agent stubs ──────────────────────────────────────────────────────────

AGENT_PERSONAS = {
    "scheduling": (
        "You are the Scheduling Agent for ZeloraTech HR. "
        "Help employees with meeting bookings, interview scheduling, and shift management."
    ),
    "leave": (
        "You are the Leave Management Agent for ZeloraTech HR. "
        "Process leave requests, check balances, and explain leave policies."
    ),
    "compliance": (
        "You are the Compliance Agent for ZeloraTech HR. "
        "Answer questions about company policies, regulations, and the code of conduct."
    ),
    "clarification": (
        "You are a helpful HR assistant at ZeloraTech. "
        "The user's request was unclear. Ask a specific follow-up question to understand what they need."
    ),
}

def run_sub_agent(intent: str, message: str, memory_context: str) -> str:
    """Run the appropriate sub-agent with memory context injected."""
    persona = AGENT_PERSONAS.get(intent, AGENT_PERSONAS["clarification"])

    system_prompt = persona
    if memory_context:
        system_prompt += f"\n\n{memory_context}"

    agent_model = genai.GenerativeModel(MODEL_NAME, system_instruction=system_prompt)
    resp = agent_model.generate_content(message)
    
    return resp.text.strip()

# ── Main orchestrator entry-point ────────────────────────────────────────────

def orchestrate(user_id: str, message: str) -> dict:
    """Full pipeline: memory → classify → route → respond → store."""
    # 1. Retrieve memory context
    memory_context = build_memory_context(user_id)
    has_memory = bool(memory_context)

    # 2. Classify intent
    intent, confidence = classify_intent(message)

    # 3. Run sub-agent
    response = run_sub_agent(intent, message, memory_context)

    # 4. Store turn in STM
    stm_add(user_id, "user",      message)
    stm_add(user_id, "assistant", response)

    return {
        "intent":           intent,
        "confidence":       confidence,
        "agent_used":       f"{intent}_agent",
        "response":         response,
        "memory_injected":  has_memory,
    }