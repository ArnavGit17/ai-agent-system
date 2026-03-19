"""Entry point — run with `python main.py` or `uvicorn api.app:app`."""

import uvicorn
from core.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "api.app:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
