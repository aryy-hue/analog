import click 
import sys
import json
import os
from db import Database
from watch_item import WatchItem

try:
    from colorama import init, Fore, Back, Style
    init()  
    HAS_COLOR = True
except ImportError:
    class Fore:
        RED = ''; GREEN = ''; YELLOW = ''; BLUE = ''; MAGENTA = ''; CYAN = ''; WHITE = ''
        RESET = ''
    class Style:
        BRIGHT = ''; RESET_ALL = ''
    HAS_COLOR = False
    print("Tip: Install colorama for colorful output: pip install colorama")

db = Database()

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def print_header(text):
    """Print header with decoration"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ {text} ═══{Style.RESET_ALL}\n")

def get_status_emoji(status):
    """Get emoji for status"""
    emojis = {
        'watching': '▶️ ',
        'completed': '✅ ',
        'dropped': '⏹️ ',
        'all': '📋 '
    }
    return emojis.get(status, '')

def get_type_icon(item_type):
    return '🎬 ' if item_type == 'movie' else '📺 '

@click.group()
def cli():
    """Analog - Track your movies and TV shows!"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════╗
║              A N A L O G             ║
║     Track your movies & TV shows     ║
╚══════════════════════════════════════╝{Style.RESET_ALL}
    """
    click.echo(banner)

@cli.command()
@click.argument('title')
@click.option('--type','-t', default='series', type=click.Choice(['series','movie']))
@click.option('--season','-s', default=1, type=int)
@click.option('--episode','-e',default=0, type=int)
def add(title, type, season, episode):
    """Add new show or movie"""
    icon = get_type_icon(type)
    print_header("ADD NEW ITEM")
    
    item = WatchItem(title, item_type=type, season=season, episode=episode)
    if db.add_item(item):
        print_success(f"{icon} Added: {Fore.WHITE}{Style.BRIGHT}{title}{Style.RESET_ALL}")
        if type == 'series':
            print_info(f"   Season {season}, Episode {episode}")
    else:
        print_error(f"'{title}' already exists in your watchlist!")
        sys.exit(1)

@cli.command()
@click.option('--status', default='watching', type=click.Choice(['all','watching','completed','dropped']))
def list_items(status):
    """List all tracked items"""
    items = db.get_all()

    if not items:
        print_warning("No items in watchlist")
        print_info("Add some with: watchlog add \"Show Name\"")
        return

    filtered_items = [item for item in items if status == 'all' or item['status'] == status]
    
    if not filtered_items:
        print_warning(f"No {status} items found")
        return

    status_emoji = get_status_emoji(status)
    print_header(f"{status_emoji} {status.upper()} WATCHLIST ({len(filtered_items)} items)")
    
    print(f"{Fore.CYAN}{Style.BRIGHT}{'':<2} {'TITLE':<30} {'TYPE':<8} {'PROGRESS':<15} {'STATUS':<10}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-' * 70}{Style.RESET_ALL}")

    for idx, item in enumerate(filtered_items, 1):
        title_display = item['title'][:28] + '..' if len(item['title']) > 28 else item['title']
        
        if item['type'] == 'series':
            if item['episode'] > 0:
                progress = f"S{item['season']:02d} E{item['episode']:02d}"
            else:
                progress = "Not started"
        else:
            progress = "Movie"
        
        status_colors = {
            'watching': Fore.YELLOW,
            'completed': Fore.GREEN,
            'dropped': Fore.RED
        }
        status_color = status_colors.get(item['status'], Fore.WHITE)
        
        type_icon = get_type_icon(item['type'])
        
        print(f"{idx:2d} {type_icon} {title_display:<28} {item['type']:<8} {progress:<15} {status_color}{item['status']}{Style.RESET_ALL}")

@cli.command()
@click.argument('title')
@click.option('--season','-s', type=int)
@click.option('--episode','-e',type=int)
@click.option('--status', type=click.Choice(['watching','completed','dropped']))
def update(title, season, episode, status):
    """Update a show's progress"""
    print_header("UPDATE ITEM")
    
    item_data = db.find_by_title(title)
    if not item_data:
        print_error(f"'{title}' not found in watchlist")
        print_info("Use 'watchlog list' to see all items")
        sys.exit(1)

    changes = []
    if season is not None and item_data['type'] == 'series':
        item_data['season'] = season
        changes.append(f"Season {season}")
    if episode is not None and item_data['type'] == 'series':
        item_data['episode'] = episode
        changes.append(f"Episode {episode}")
    if status is not None:
        old_status = item_data['status']
        item_data['status'] = status
        changes.append(f"Status: {old_status} → {status}")
    
    if not changes:
        print_warning("No changes specified")
        print_info("Use --season, --episode, or --status flags")
        return
    
    if db.update_item(title, item_data):
        print_success(f"Updated: {Fore.WHITE}{Style.BRIGHT}{title}{Style.RESET_ALL}")
        for change in changes:
            print_info(f"  • {change}")
    else:
        print_error(f"Failed to update {title}")

@cli.command()
@click.argument('title', required=False)
def next_episode(title):
    """Show next episodes to watch"""
    items = db.get_all()
    
    if not items:
        print_warning("No items in watchlist")
        return
    
    if title:
        print_header(f"NEXT EPISODE: {title}")
        item_data = db.find_by_title(title)
        if not item_data:
            print_error(f"'{title}' not found")
            return
        if item_data['type'] != 'series':
            print_warning(f"'{title}' is a movie, not a series")
            return
        if item_data['status'] != 'watching':
            print_warning(f"'{title}' is not currently being watched")
            return

        next_ep = (item_data['season'], item_data['episode'] + 1)
        print(f"{Fore.GREEN}▶ Next:{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}Season {next_ep[0]}, Episode {next_ep[1]}{Style.RESET_ALL}")
        
    else:
        watching_series = [item for item in items 
                          if item['type'] == 'series' and item['status'] == 'watching']
        
        if not watching_series:
            print_warning("No series are currently being watched")
            return
        
        print_header("NEXT EPISODES TO WATCH")
        
        for item in watching_series:
            next_ep = (item['season'], item['episode'] + 1)
            type_icon = get_type_icon(item['type'])
            print(f"{type_icon} {Fore.WHITE}{item['title']:<30}{Style.RESET_ALL} "
                  f"{Fore.YELLOW}→ S{next_ep[0]:02d}E{next_ep[1]:02d}{Style.RESET_ALL}")

@cli.command()
@click.argument('title')
def complete(title):
    """Mark a show as completed"""
    print_header("COMPLETE ITEM")
    item_data = db.find_by_title(title)
    if not item_data:
        print_error(f"'{title}' not found")
        return
    
    old_status = item_data['status']
    item_data['status'] = 'completed'
    
    if db.update_item(title, item_data):
        print_success(f"Marked as completed: {Fore.WHITE}{Style.BRIGHT}{title}{Style.RESET_ALL}")
        print_info(f"  Status: {old_status} → completed")
    else:
        print_error(f"Failed to update {title}")

@cli.command()
@click.argument('title')
def drop(title):
    """Mark a show as dropped"""
    print_header("DROP ITEM")
    item_data = db.find_by_title(title)
    if not item_data:
        print_error(f"'{title}' not found")
        return
    
    old_status = item_data['status']
    item_data['status'] = 'dropped'
    
    if db.update_item(title, item_data):
        print_success(f"Marked as dropped: {Fore.WHITE}{Style.BRIGHT}{title}{Style.RESET_ALL}")
        print_info(f"  Status: {old_status} → dropped")
    else:
        print_error(f"Failed to update {title}")

if __name__ == "__main__":
    cli()