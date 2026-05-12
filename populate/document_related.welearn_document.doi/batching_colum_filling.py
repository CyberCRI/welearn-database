import json
import os
from datetime import datetime
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()
DSN = f'postgresql://{os.getenv("PG_USER")}:{os.getenv("PG_PASSWORD")}@dev-lab-projects-backend.postgres.database.azure.com:{os.getenv("PG_PORT")}/{os.getenv("PG_DB")}'
BATCH_SIZE = 1000
PROGRESS_FILE = Path("update_doi_progress.json")
SQL_FILE = Path("update_doi.sql")


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {
        "total_updated": 0,
        "batches": 0,
        "started_at": None,
        "last_updated_at": None,
    }


def save_progress(progress: dict):
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))


if __name__ == "__main__":
    query = SQL_FILE.read_text()
    progress = load_progress()

    if progress["started_at"] is None:
        progress["started_at"] = datetime.now().isoformat()

    print(
        f"Reprise — {progress['total_updated']} lignes déjà traitées sur {progress['batches']} batches"
    )

    with psycopg2.connect(DSN) as conn:
        print("Preparing data...")
        with conn.cursor() as cur:
            while True:
                print("Executing query...")
                cur.execute(query, {"batch_size": BATCH_SIZE})
                conn.commit()

                updated = cur.rowcount
                progress["total_updated"] += updated
                progress["batches"] += 1
                progress["last_updated_at"] = datetime.now().isoformat()
                save_progress(progress)

                print(
                    f"[Batch {progress['batches']}] {updated} lignes — total : {progress['total_updated']}"
                )

                if updated == 0:
                    print("Terminé.")
                    break
