from watch_item import WatchItem
from db import Database

item = WatchItem("The Witcher", season=1, episode=2)
print(f"Created: {item.title} - S{item.season} E{item.episode}")

db = Database()
print(f"Database path: {db.db_path}")
print("setup Completed")
