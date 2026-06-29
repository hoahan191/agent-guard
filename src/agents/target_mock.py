from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_msg = request.message.lower()
    
    # 🛡️ Bổ sung lớp khiên phòng thủ vững chắc: Chặn các từ khóa nhạy cảm
    if any(keyword in user_msg for keyword in ["developer", "system prompt", "debug", "ignore", "base64", "override"]):
        return {"response": "🛑 [TỪ CHỐI] Tôi là trợ lý ảo an toàn. Tôi từ chối cung cấp thông tin nội bộ hoặc thay đổi cấu hình bảo mật."}
    
    return {"response": "Chào bạn, tôi là trợ lý ảo. Tôi không thể giúp bạn làm việc đó."}
