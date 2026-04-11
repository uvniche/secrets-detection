from fastapi import Depends, FastAPI, Header, HTTPException

from secure_api.config import Settings, get_settings

app = FastAPI(title="Secure API Demo", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/protected")
def protected(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    """Endpoint that requires a configured API key (from env)."""
    if not settings.api_key:
        raise HTTPException(
            status_code=503,
            detail="Server API key not configured (set API_KEY env var)",
        )
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return {"message": "authorized"}
