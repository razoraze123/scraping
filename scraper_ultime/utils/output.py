from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

from .logger import setup_logger


LOGGER = setup_logger(__name__)


def save_data(
    data: List[dict],
    output_dir: str,
    fmt: str = "csv",
    filename: Optional[str] = None,
) -> None:
    if not data:
        LOGGER.warning("No data to save")
        return
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = filename or f"produits_{ts}"
    path = Path(output_dir) / f"{name}.{fmt}"
    df = pd.DataFrame(data)
    if fmt == "csv":
        df.to_csv(path, index=False)
    elif fmt == "xlsx":
        df.to_excel(path, index=False)
    elif fmt == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        raise ValueError(f"Unsupported format: {fmt}")
    LOGGER.info("Saved data to %s", path)
