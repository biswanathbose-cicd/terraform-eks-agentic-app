from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "GenAI app deployed successfully on EKS"}

@app.get("/health")
def health():
    return {"status": "ok"}