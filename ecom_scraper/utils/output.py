import os
import json
import pandas as pd


def save_data(data: list, output_dir: str, fmt: str = "csv"):
    os.makedirs(output_dir, exist_ok=True)
    if fmt == "csv":
        df = pd.DataFrame(data)
        path = os.path.join(output_dir, "produits.csv")
        df.to_csv(path, index=False)
    elif fmt == "xlsx":
        df = pd.DataFrame(data)
        path = os.path.join(output_dir, "produits.xlsx")
        df.to_excel(path, index=False)
    elif fmt == "json":
        path = os.path.join(output_dir, "produits.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        raise ValueError(f"Unsupported format: {fmt}")
