class WatchItem:
    def __init__(self, title, item_type="series", season =1 ,episode = 0, status="watching", rating=0, notes=""):
        self.title = title
        self.type = item_type
        self.season = season if item_type == "series" else None
        self.episode = episode if item_type == "series" else None
        self.status = status
        self.rating = rating
        self.notes = notes

    def to_dict(self):
        return{
            "title": self.title,
            "type": self.type,
            "season": self.season,
            "episode": self.episode,
            "status": self.status,
            "rating": self.rating,
            "notes": self.notes
        }
    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data['title'],
            item_type=data['type'],
            season=data['season'],
            episode=data['episode'],
            status=data['status'],
            rating=data['rating'],
            notes=data['notes']
        )

    def get_next_episode(self):
        if self.type !='series':
            return None
        if self.status !='watching':
            return None
        if self.episode is None:
            return (1,1)
        return (self.season, self.episode + 1)
