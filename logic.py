import requests
import re
from prompts import INTENT_PROMPT, STRATEGY_PROMPT, REPLY_PROMPT, RED_FLAG_PROMPT

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_ID = "google/gemma-3n-e4b"

def call_model(prompt: str, temp: float = 0.3):
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "You are a confident, witty, masculine man helping craft dating conversations with women aged 21–27. You are charming, direct, and unafraid to be bold. Think of a blend of Harvey Specter and Ryan Gosling in Crazy, Stupid, Love— 40% Harvey (cocky, confident, unfiltered), 60% Gosling (charming, playful). You never sound corporate or cheesy. You are comfortable with flirting and sexual tension when appropriate."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temp
    }
    response = requests.post(LM_STUDIO_URL, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

def analyze_intent(msg: str, temp: float = 0.2) -> str:
    return call_model(INTENT_PROMPT.format(msg=msg), temp=temp)

# in logic.py

def generate_strategy(analysis: str, flags: str, temp: float = 0.5) -> str:
    """
    Combine intent analysis and red‐flag output into the STRATEGY_PROMPT
    and send to the model. If no flags are passed, inject "None".
    """
    # Default empty flags to the literal "None"
    flags_input = flags.strip() or "None"

    # Build the intent block exactly as your prompt expects
    intent_block = f"## Intent\n{analysis.strip()}"

    # Fill both placeholders and send to the model
    prompt_text = STRATEGY_PROMPT.format(
        analysis=intent_block,
        flags=flags_input
    )

    return call_model(prompt_text, temp=temp)

    
'''def generate_strategy_with_flags(analysis: str, flags: str, temp: float = 0.5) -> str:
    combined = f"## Intent\n{analysis}\n\n## Red Flags\n{flags}"
    return call_model(STRATEGY_PROMPT.format(analysis=combined), temp=temp)'''

def compose_replies(msg: str, strategy: str, temp: float = 0.9) -> str:
    # 1) If the strategy itself tells us to avoid replying, bail out immediately
    if re.search(r"## Ending Style\s*\n.*Avoid reply", strategy, re.IGNORECASE):
        return "🚫 Reply generation skipped per Ending Style."

    # 2) Extract the red flag lines under "## Red Flags"
    match = re.search(r"## Red Flags\s*(.*?)\s*##", strategy, re.DOTALL)
    flags_block = match.group(1) if match else ""
    # 3) Count non-empty, non-“None” lines
    flags = [line.strip("- \t") for line in flags_block.splitlines() if line.strip() and line.strip().lower() != "none"]
    if len(flags) >= 3:
        return "🚫 Too many red flags. Disengagement is recommended."

    # 4) All clear — generate the reply
    return call_model(REPLY_PROMPT.format(msg=msg, strategy=strategy), temp=temp)
   

def determine_temps(analysis: str):
    a = analysis.lower()
    if "sexual" in a:
        return 0.7, 0.95
    elif "flirty" in a or "playful" in a:
        return 0.6, 0.85
    elif "shy" in a or "reserved" in a:
        return 0.3, 0.6
    else:
        return 0.4, 0.7

def detect_red_flags(message):
    full_prompt = RED_FLAG_PROMPT.replace("{message}", message)
    return call_model(full_prompt, temperature = .05)