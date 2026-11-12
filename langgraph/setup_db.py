"""Create films.db: 200 synthetic films so the example runs without any real data."""

import sqlite3
from pathlib import Path

GENRES = ["Sci-Fi", "Drama", "Comedy", "Action", "Documentary"]
COUNTRIES = ["Spain", "France", "USA", "India", "Japan"]

path = Path(__file__).parent / "films.db"
path.unlink(missing_ok=True)

db = sqlite3.connect(path)
db.execute(
    """CREATE TABLE films (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        genre TEXT NOT NULL,
        country TEXT NOT NULL,
        release_year INTEGER NOT NULL,
        rating REAL NOT NULL
    )"""
)
db.executemany(
    "INSERT INTO films VALUES (?, ?, ?, ?, ?, ?)",
    [
        (
            i + 1,
            f"Film {i + 1:03d}",
            GENRES[i % 5],
            COUNTRIES[(i // 5) % 5],
            1980 + (i * 7) % 45,
            5.0 + ((i * 3) % 50) / 10,
        )
        for i in range(200)
    ],
)
db.commit()
db.close()
print(f"created {path}")
