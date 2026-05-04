@"
# AI Chatbot Project

A real-time AI chatbot with sentiment analysis powered by:
- FastAPI (Backend)
- Apache Kafka (Message Queue)
- Apache Spark (Stream Processing)
- PostgreSQL (Database)
- Streamlit (Analytics Dashboard)
- React (Frontend)

## Setup
1. Install dependencies: pip install -r requirements.txt
2. Configure .env with your database credentials
3. Start services: Zookeeper, Kafka, PostgreSQL
4. Run backend: uvicorn main:app --reload
5. Run dashboard: streamlit run dashboard.py
"@ | Out-File -Encoding utf8 README.md
