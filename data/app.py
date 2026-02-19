from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
import json

app = FastAPI()

# ==============================
# 🌐 CORS CONFIG
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Safe since Node calls this
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# 📂 LOAD CSV (BOM SAFE)
# ==============================

BASE_DIR = Path(__file__).resolve().parent
csv_path = BASE_DIR / "Muhurta_2027_2.csv"

df = pd.read_csv(csv_path, encoding="utf-8-sig")

# ==============================
# 🗓 DATE CLEANING (MM/DD/YYYY)
# ==============================

df["Date"] = df["Date"].astype(str).str.strip()

df["Date"] = pd.to_datetime(
    df["Date"],
    format="%m/%d/%Y",   # Your confirmed format
    errors="coerce"
)

# Drop invalid date rows
df = df.dropna(subset=["Date"])

# Sort by date
df = df.sort_values("Date")

# Convert to ISO format
df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

# ==============================
# 🧹 CLEAN TEXT FIELDS
# ==============================

def clean_text(value):
    if isinstance(value, str):
        return (
            value.replace("\u0096", "-")
                 .replace("\u2013", "-")
                 .replace("\u2014", "-")
        )
    return value

for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].map(clean_text)

# ==============================
# 🔁 RENAME COLUMNS
# ==============================

df = df.rename(columns={
    "Muhurta Type": "muhurtaType",
    "Date": "date",
    "Day": "day",
    "Month": "month",
    "Paksha": "paksha",
    "Tithi": "tithi",
    "Nakshatra": "nakshatra",
    "Lagna": "lagna",
    "Time (From - To)": "time"
})

# ==============================
# 🚀 API ROUTES
# ==============================

@app.get("/api/v1/data")
def get_data():
    data_json = json.loads(
        df.to_json(
            orient="records",
            force_ascii=False
        )
    )

    print("Returned records:", len(data_json))  # Logs in Render console

    return {
        "status": "success",
        "count": len(data_json),
        "data": data_json
    }


@app.get("/")
def root():
    return {
        "message": "FastAPI is running",
        "endpoint": "/api/v1/data",
        "docs": "/docs"
    }
