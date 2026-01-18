import click 
import sys
from db import Database
from watch_item import WatchItem

db = Database()

@click.group()
def cli():
    "Track your movies and TV shows now!"
    pass

    
@cli.command()
@click.argument('title')
@click.option('--type','-t', default='series', type=click.Choice(['series','movie']))
@click.option('--season','-s', default=1, type=int)
@click.option('--episode','-e',default=0, type=int)
def add(title, type, season, episode):
    "Add new show or movie"
    item = WatchItem(title, item_type=type, season=season, episode=episode)
    if db.add_item(item):
        print(f"Added: {title}")
    else:
        print(f"Error: {title} already exists")
        sys.exit(1)
@cli.command()
@click.option('--status', default='watching', type=click.Choice(['all','watching','completed','dropped']))

def list_items(status):
    "List all tracked items"
    items = db.get_all()

    if not items:
        print("No items in watchlist")
        return

    print(f"{'Title':<30} {'Type':<10} {'Status':<10} {'Progress':<10}")
    print("-"*70)

    for item in items:
        if status != 'all' and item['status'] != status:
            continue
        title = item['title'][:28] + '...' if len(item['title']) > 28 else item['title']

        if item['type'] == 'series':
            if item['episode'] > 0:
                progress = f"S{item['season']} E{item['episode']}"
            else:
                progress = "Not started"
        else:
            progress = "Movie"

        print(f"{title:<30} {item['type']:<10} {item['status']:<10} {progress:<10}")

@cli.command()
@click.argument('title')
@click.option('--season','-s', type=int)
@click.option('--episode','-e',type=int)
@click.option('--status', type=click.Choice(['watching','completed','dropped']))
def update(title,season,episode,status):
    "Update a shows progress"
    item_data = db.find_by_title(title)
    if not item_data:
        print(f"Error: {title} not found")
        sys.exit(1)

    if season is not None and item_data['type'] == 'series':
        item_data['season'] = season
    if episode is not None and item_data['type'] == 'series':
        item_data['episode'] = episode
    if status is not None:
        item_data['status']= status
    if db.update_item(title,item_data):
        print(f"Title {title} has been updated")
    else:
        print(f"Error updating {title}")

@cli.command()
@click.argument('title', required=False)
def next_episode(title):
    "Show next episodes to watch"
    items = db.get_all()
    if not items:
        print("No items in watchlist")
        return
    
    if title:
        item_data = db.find_by_title(title)
        if not item_data:
            print(f"Error: {title} not found")
            return
        if item_data['type'] != 'series':
            print(f"{title} is a movie, not a series")
            return
        if item_data['status'] != 'watching':
            print(f"{title} is not currently being watched")
            return

        next_ep = (item_data['season'], item_data['episode'] + 1)
        print(f"{title} : Season {next_ep[0]}, Episode {next_ep[1]}")

    else:
        print("Next episodes to watch:")
        print("-" * 40)

        for item in items:
            if item['type'] == 'series' and item['status'] == 'watching':
                next_ep = (item['season'], item['episode']+ 1)
                print(f"{item['title']}: S{next_ep[0]}E{next_ep[1]}")

@cli.command()
@click.argument('title')
def complete(title):
    "Mark as complete"
    item_data = db.find_by_title(title)
    if not item_data:
        print(f"Error: {title} not found")
        return
    
    item_data['status'] = 'completed'
    if db.update_item(title, item_data):
        print(f"Marked as completed: {title}")
    else:
        print(f"Error updating {title}")

@cli.command()
@click.argument('title')
def drop(title):
    "Mark a show as dropped"
    item_data = db.find_by_title(title)
    if not item_data:
        print(f"Error: {title} not found")
        return
    item_data['status']='dropped'
    if db.update_item(title, item_data):
        print(f"Marked as dropped: {title}")
    else:
        print(f"Error when dropping {title}")

if __name__ == "__main__":
    cli()

