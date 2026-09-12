"""
analytics/session_analytics.py — Analytics & Performance Service for HastaAI
Computes real practice statistics and trends from SQLite database records.
No fake values, random charts, or placeholder numbers.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
from db.database import get_user_sessions, get_session_details, get_session_results, _get_connection


def get_user_overview_metrics(user_id: int) -> Dict[str, Any]:
    """
    Computes overall summary statistics for a user:
    - total_sessions: int
    - total_practice_seconds: float
    - total_practice_display: str (formatted min/sec)
    - unique_mudras_practiced: int
    - average_confidence: float (0.0 - 1.0)
    - best_performance_score: float (0.0 - 100.0)
    - most_practiced_mudra: str
    """
    sessions = get_user_sessions(user_id, limit=500)
    if not sessions:
        return {
            "total_sessions": 0,
            "total_practice_seconds": 0.0,
            "total_practice_display": "0m 0s",
            "unique_mudras_practiced": 0,
            "average_confidence": 0.0,
            "best_performance_score": 0.0,
            "most_practiced_mudra": "None",
            "has_data": False,
        }

    df = pd.DataFrame(sessions)
    total_sessions = len(df)
    total_seconds = float(df["duration"].fillna(0).sum())

    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    practice_display = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"

    mudras_series = df["mudra_name"].dropna()
    unique_mudras = int(mudras_series.nunique())
    most_practiced = mudras_series.mode()[0] if not mudras_series.empty else "None"

    # Filter non-zero confidences
    valid_conf = df[df["average_confidence"] > 0]["average_confidence"]
    avg_conf = float(valid_conf.mean()) if not valid_conf.empty else 0.0

    best_score = float(df["performance_score"].max()) if not df["performance_score"].empty else 0.0

    return {
        "total_sessions": total_sessions,
        "total_practice_seconds": total_seconds,
        "total_practice_display": practice_display,
        "unique_mudras_practiced": unique_mudras,
        "average_confidence": round(avg_conf, 3),
        "best_performance_score": round(best_score, 1),
        "most_practiced_mudra": most_practiced,
        "has_data": True,
    }


def get_confidence_trend_df(user_id: int) -> pd.DataFrame:
    """
    Returns DataFrame of Date vs Average Confidence for the user.
    Columns: ['Date', 'Average Confidence', 'Mudra']
    """
    sessions = get_user_sessions(user_id, limit=100)
    if not sessions:
        return pd.DataFrame(columns=["Date", "Confidence", "Mudra"])

    df = pd.DataFrame(sessions)
    df = df[df["average_confidence"] > 0].copy()
    if df.empty:
        return pd.DataFrame(columns=["Date", "Confidence", "Mudra"])

    # Parse and format date
    df["Date"] = pd.to_datetime(df["start_time"]).dt.strftime("%b %d, %H:%M")
    df["Confidence"] = (df["average_confidence"] * 100).round(1)
    df["Mudra"] = df["mudra_name"].fillna("Mixed / Practice")

    # Chronological order
    df = df.iloc[::-1].reset_index(drop=True)
    return df[["Date", "Confidence", "Mudra"]]


def get_performance_trend_df(user_id: int) -> pd.DataFrame:
    """
    Returns DataFrame of Date vs Performance Score (0-100) for the user.
    """
    sessions = get_user_sessions(user_id, limit=100)
    if not sessions:
        return pd.DataFrame(columns=["Date", "Performance Score", "Mudra"])

    df = pd.DataFrame(sessions)
    df = df[df["performance_score"] > 0].copy()
    if df.empty:
        return pd.DataFrame(columns=["Date", "Performance Score", "Mudra"])

    df["Date"] = pd.to_datetime(df["start_time"]).dt.strftime("%b %d, %H:%M")
    df["Performance Score"] = df["performance_score"].round(1)
    df["Mudra"] = df["mudra_name"].fillna("Practice Session")
    df = df.iloc[::-1].reset_index(drop=True)
    return df[["Date", "Performance Score", "Mudra"]]


def get_mudra_distribution_df(user_id: int) -> pd.DataFrame:
    """
    Returns DataFrame of Mudra vs Practice Counts for the user.
    Columns: ['Mudra', 'Sessions']
    """
    sessions = get_user_sessions(user_id, limit=500)
    if not sessions:
        return pd.DataFrame(columns=["Mudra", "Sessions"])

    df = pd.DataFrame(sessions)
    counts = df["mudra_name"].dropna().value_counts().reset_index()
    counts.columns = ["Mudra", "Sessions"]
    return counts


def get_recent_sessions_df(user_id: int, limit: int = 10) -> pd.DataFrame:
    """
    Returns formatted table of recent practice sessions.
    """
    sessions = get_user_sessions(user_id, limit=limit)
    if not sessions:
        return pd.DataFrame()

    records = []
    for s in sessions:
        dt = datetime.fromisoformat(s["start_time"])
        records.append({
            "Session ID": s["id"],
            "Date": dt.strftime("%b %d, %Y %I:%M %p"),
            "Mudra": s["mudra_name"] or "Mixed Practice",
            "Duration (s)": f"{s['duration']:.1f}s",
            "Confidence": f"{s['average_confidence']:.1%}",
            "Score": f"{s['performance_score']:.1f} / 100",
        })
    return pd.DataFrame(records)


def export_session_to_csv(session_id: int, output_path: str) -> bool:
    """Export all recognition events of a session to CSV file."""
    results = get_session_results(session_id)
    if not results:
        return False
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    return True
