from __future__ import annotations

import json
import os
from pathlib import Path
import uvicorn


def main() -> None:
    cfg = os.getenv("AETHER_CONFIG", "config/server_config.json")
    data = json.loads(Path(cfg).read_text(encoding="utf-8"))
    host = data.get("host", "0.0.0.0")
    port = int(data.get("port", 8000))
    uvicorn.run("aether.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
