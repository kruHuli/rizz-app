from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from logic import analyze_intent, generate_strategy, compose_replies, determine_temps

app = FastAPI()

class TextRequest(BaseModel):
    text: str

@app.post("/suggest_reply_text", response_class=PlainTextResponse)
async def suggest_reply_text(req: TextRequest):
    text = req.text.strip()
    if not text:
        return "Error: Empty text."

    temp_analysis = 0.2
    analysis = analyze_intent(text, temp=temp_analysis).strip()
    strategy_temp, reply_temp = determine_temps(analysis)
    strategy = generate_strategy(analysis, temp=strategy_temp).strip()
    replies = compose_replies(text, strategy, temp=reply_temp).strip()

    formatted_output = (
        "=== ANALYSIS (Temp: " + str(temp_analysis) + ") ===\n\n"
        + analysis
        + "\n\n=== STRATEGY (Temp: " + str(strategy_temp) + ") ===\n\n"
        + strategy
        + "\n\n=== REPLIES (Temp: " + str(reply_temp) + ") ===\n\n"
        + replies
    )
    return formatted_output
