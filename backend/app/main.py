from fastapi import FastAPI

app = FastAPI(title="MarketPulse")


@app.get("/health")
def health():
    return {"status": "ok"}
