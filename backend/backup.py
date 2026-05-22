import os
import shutil
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "bookstore.db")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "backups")


def backup():
    if not os.path.exists(DB_PATH):
        print("Database not found. Has the app been run at least once?")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"bookstore_{timestamp}.db")
    shutil.copy2(DB_PATH, dest)
    print(f"Backup saved: {dest}")

    # Keep only the 10 most recent backups
    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")],
        reverse=True,
    )
    for old in backups[10:]:
        os.remove(os.path.join(BACKUP_DIR, old))
        print(f"Removed old backup: {old}")


if __name__ == "__main__":
    backup()
