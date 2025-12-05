import json
from datetime import datetime
from pathlib import Path


def live_update_session(session_obj, base_dir: str = "memory/session_logs") -> None:
    """
    Update (or overwrite) the session file with latest data.
    In per-file format, this is identical to append.
    """

    try:
        append_session_to_store(session_obj, base_dir)
        print("📝 Session live-updated.")
    except Exception as e:
        print(f"❌ Failed to update session: {e}")


def append_session_to_store(session_obj, base_dir: str = "memory/session_logs") -> None:
    """
    Save the session object as a standalone file. If a file already exists and is corrupt,
    it will be overwritten with fresh data.
    """
    session_data = session_obj.to_json()
    session_data["_session_id_short"] = simplify_session_id(session_data["session_id"])

    store_path = get_store_path(session_data["session_id"], base_dir)

    if store_path.exists():
        try:
            with open(store_path, "r", encoding="utf-8") as f:
                existing = f.read().strip()
                if existing:
                    json.loads(existing)
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Corrupt JSON detected in {store_path}. Overwriting.")

    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2)

    print(f"✅ Session stored: {store_path}")


def simplify_session_id(session_id: str) -> str:
    """
    Return the simplified (short) version of the session ID for display/logging.
    """
    return session_id.split("-")[0]


def get_store_path(session_id: str, base_dir: str = "memory/session_logs") -> Path:
    """
    Construct the full path to the session file based on current date and session ID.
    Format: memory/session_ logs/YYYY/MM/DD/<session_id>.json
    """
    now = datetime.now()
    day_dir = Path(base_dir) / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
    day_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{session_id}.json"
    return day_dir / filename
