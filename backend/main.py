from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SessionLocal
from models import ChatLog
from kafka_producer import send_to_kafka

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str
    message: str

def generate_reply(user_message):
    if "hello" in user_message.lower():
        return "Hi! How can I help you today?"
    elif "price" in user_message.lower():
        return "Our pricing details are available on the website."
    elif "help" in user_message.lower():
        return "Sure! I'm here to help. What do you need?"
    elif "bye" in user_message.lower():
        return "Goodbye! Have a great day!"
    else:
        return "I'm here to help you. Please tell me more."

def detect_sentiment(text):
    positive_words = ["good", "great", "happy", "hello", "thanks", "awesome", "love", "nice"]
    negative_words = ["bad", "worst", "angry", "hate", "terrible", "awful", "sad"]
    text_lower = text.lower()
    if any(word in text_lower for word in negative_words):
        return "negative"
    elif any(word in text_lower for word in positive_words):
        return "positive"
    else:
        return "neutral"

@app.get("/")
def home():
    return {"message": "Chatbot API is running"}

@app.post("/chat")
def chat(request: ChatRequest):
    db = SessionLocal()
    try:
        bot_reply = generate_reply(request.message)
        sentiment = detect_sentiment(request.message)

        new_chat = ChatLog(
            user_id=request.user_id,
            user_message=request.message,
            bot_response=bot_reply,
            sentiment=sentiment
        )
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        send_to_kafka({
            "user_id": request.user_id,
            "message": request.message,
            "response": bot_reply,
            "sentiment": sentiment
        })

        return {
            "user_message": request.message,
            "bot_response": bot_reply,
            "sentiment": sentiment
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@app.get("/chats")
def get_chats():
    db = SessionLocal()
    try:
        chats = db.query(ChatLog).order_by(ChatLog.created_at.desc()).limit(50).all()
        return chats
    finally:
        db.close()

@app.get("/stats")
def get_stats():
    db = SessionLocal()
    try:
        from sqlalchemy import func
        stats = db.query(ChatLog.sentiment, func.count().label("count"))\
                  .group_by(ChatLog.sentiment).all()
        return {s: c for s, c in stats}
    finally:
        db.close()