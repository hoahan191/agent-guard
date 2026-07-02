from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_msg = request.message.lower()
    
    # 🛡️ Defense layer: Block known attack keywords
    if any(keyword in user_msg for keyword in ["developer", "system prompt", "debug", "ignore", "base64", "override"]):
        return {"response": "🛑 [REFUSED] I am a safe virtual assistant. I refuse to provide internal information or modify security configurations."}
    
    return {"response": "Hello, I am a virtual assistant. I cannot help you with that request."}
