# test.py
from db import Database
from watch_item import WatchItem

db = Database()

# Test 1: Add item
item = WatchItem("Test Show", season=1, episode=1)
print(f"Adding Test Show: {db.add_item(item)}")

# Test 2: List items
items = db.get_all()
print(f"Total items: {len(items)}")
for item in items:
    print(f"  - {item['title']}")

# Test 3: Find item
found = db.find_by_title("Test Show")
print(f"Found item: {found['title'] if found else 'Not found'}")
