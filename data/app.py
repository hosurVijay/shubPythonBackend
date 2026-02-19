from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
import json

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
csv_path = BASE_DIR / "Muhurta_2027.csv"

df = pd.read_csv(csv_path, encoding="latin1")

df["Date"] = (
    df["Date"]
    .astype(str)
    .str.strip()
    .str.replace(r"[^\x20-\x7E]", "", regex=True)
    .replace(["", "-", "--", "NA", "N/A", "Nil", "nan"], pd.NA)
)

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce",
    dayfirst=False  
)

df = df.sort_values("Date")


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

df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

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

@app.get("/api/v1/data")
def get_data():
    return {
        "status": "success",
        "data": json.loads(
            df.to_json(
                orient="records",
                force_ascii=False
            )
        )
    }


@app.get("/")
def root():
    return {
        "message": "FastAPI is running",
        "endpoint": "/api/v1/data",
        "docs": "/docs"
    }
