# debug_db.py
import json
from pathlib import Path

home = Path.home()
db_path = home / '.watchlog' / 'data.json'

print(f"Database path: {db_path}")
print(f"Exists: {db_path.exists()}")

if db_path.exists():
    with open(db_path, 'r') as f:
        data = json.load(f)
    print(f"Current data: {data}")
    print(f"Number of items: {len(data)}")
    for item in data:
        print(f"  - {item['title']}")
