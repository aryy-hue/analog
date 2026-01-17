import json
import os
from pathlib import Path

class Database:
    def __init__(self):
        self.db_path = self.get_db_path()
        self.data = self.load_data()
    
    def get_db_path(self):
        home = Path.home()
        db_dir = home/'.watchlog'
        db_dir.mkdir(exist_ok = True)
        return db_dir / 'data.json'
    def load_data(self):
        if not self.db_path.exists():
            return []
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except:
            return []
    def save(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f , indent=2)
    def add_item(self, item):
        for existing in self.data:
            if existing['title'].lower() == item.title.lower():
                return False
        
            self.data.append(item.to_dict())
            self.save()
            return True

    def get_all(self):
        return self.data

    def find_by_title(self):
        for item in self.data:
            if item['title'].lower() == title.lower():
                return item
        return None

    def update_item(self, old_title, new_item_dict):
        for i, item in enumerate(self.data):
            if item['item'].lower() == old_title.lower():
                self.data[i] = new_item_dict
                self.save()
                return True
            
            return False

    def delete_item(self, title):
        for i, item in enumerate(self.data):
            if item['title'].lower() == title.lower():
                del self.data[i]
                self.save()
                return True
            return False
