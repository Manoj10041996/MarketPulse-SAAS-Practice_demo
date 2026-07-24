import tomllib
from pathlib import Path

from fastapi import FastAPI


def get_version() -> str:
    pyproject = Path(__file__).parent / "pyproject.toml"
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


app = FastAPI(title="MarketPulse SAAS", version=get_version())


@app.get("/health")
def health():
    return {"status": "live", "version": get_version()}


@app.get("/ping")
def ping():
    return {"message": "MarketPulse SAAS is live!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
