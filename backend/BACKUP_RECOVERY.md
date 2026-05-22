# Backup and Data Recovery Procedures

## Backup

Run the backup script manually from the `backend/` directory:

```
python3 backup.py
```

This copies the current database to `backend/backups/` with a timestamp in the filename (e.g. `bookstore_20260521_143000.db`). The script automatically removes any backups beyond the 10 most recent.

**Recommended:** Run this before any major change, deployment, or on a regular schedule.

---

## Restore

1. Stop the application if it is running.

2. Locate the backup file you want to restore from in `backend/backups/`.

3. Copy it over the active database:

```
cp backend/backups/bookstore_YYYYMMDD_HHMMSS.db backend/instance/bookstore.db
```

4. Restart the application:

```
cd backend
python3 app.py
```

5. Verify the restore by logging in and checking that expected data (books, orders, users) is present.

---

## Backup File Location

| Path | Description |
|---|---|
| `backend/instance/bookstore.db` | Live database used by the app |
| `backend/backups/` | Directory containing timestamped backup files |

---

## Notes

- The `backend/backups/` directory is gitignored — backups are local only and not pushed to GitHub.
- If the `instance/` directory is missing, run `python3 app.py` once to let the app create it, then restore the backup file into it.
