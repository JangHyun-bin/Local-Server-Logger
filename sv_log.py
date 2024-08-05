import os
import time
import socket
import hashlib
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import csv
from datetime import datetime, timedelta
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

file_metadata = {}

def get_file_metadata(file_path):
    try:
        stat = os.stat(file_path)
        return stat.st_size, stat.st_mtime
    except IOError:
        return None, None

class DirectoryHandler(FileSystemEventHandler):
    def __init__(self, log_file):
        self.log_file = log_file
        self.computer_name = socket.gethostname()

    def log_event(self, event_type, src_path):
        try:
            with open(self.log_file, "a", newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event_type, src_path, self.computer_name])
        except Exception as e:
            print(f"Error logging event: {e}")

    def on_created(self, event):
        try:
            if not event.is_directory and event.src_path != self.log_file:
                self.log_event("created", event.src_path)
                file_metadata[event.src_path] = get_file_metadata(event.src_path)
        except Exception as e:
            print(f"Error handling created event: {e}")

    def on_deleted(self, event):
        try:
            if event.src_path != self.log_file:
                self.log_event("deleted", event.src_path)
                if event.src_path in file_metadata:
                    del file_metadata[event.src_path]
        except Exception as e:
            print(f"Error handling deleted event: {e}")

    def on_modified(self, event):
        try:
            if not event.is_directory and event.src_path != self.log_file:
                new_size, new_mtime = get_file_metadata(event.src_path)
                if event.src_path not in file_metadata:
                    file_metadata[event.src_path] = (new_size, new_mtime)
                    self.log_event("modified", event.src_path)
                elif file_metadata[event.src_path] != (new_size, new_mtime):
                    file_metadata[event.src_path] = (new_size, new_mtime)
                    self.log_event("modified", event.src_path)
        except Exception as e:
            print(f"Error handling modified event: {e}")

    def on_moved(self, event):
        try:
            if event.src_path != self.log_file and event.dest_path != self.log_file:
                self.log_event("moved", event.dest_path)
                if not event.is_directory:
                    old_metadata = file_metadata.pop(event.src_path, None)
                    if old_metadata:
                        file_metadata[event.dest_path] = old_metadata
        except Exception as e:
            print(f"Error handling moved event: {e}")

def create_log_backup(log_file_path):
    try:
        backup_dir = os.path.join(os.path.dirname(log_file_path), "log_backup")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        date_str = datetime.now().strftime("%Y-%m-%d")
        backup_file_path = os.path.join(backup_dir, f"directory_log_backup_{date_str}.csv")

        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            with open(backup_file_path, 'w', newline='', encoding='utf-8') as backup_file:
                for line in log_file:
                    backup_file.write(line)
    except Exception as e:
        print(f"Error creating log backup: {e}")

def start_monitoring():
    directory_path = r"Z:\z_3D"
    log_file_path = os.path.join(directory_path, "directory_log.csv")
    
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Event Type", "Path", "Computer Name"])

    event_handler = DirectoryHandler(log_file_path)
    observer.schedule(event_handler, directory_path, recursive=True)
    observer.start()

    def periodic_backup():
        while True:
            now = datetime.now()
            next_backup_time = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            backup_interval = (next_backup_time - now).total_seconds()
            time.sleep(backup_interval)
            create_log_backup(log_file_path)

    backup_thread = threading.Thread(target=periodic_backup, daemon=True)
    backup_thread.start()

def setup_tray_icon():
    def on_quit(icon, item):
        icon.stop()
        observer.stop()
        observer.join()

    image = Image.new('RGB', (64, 64), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, 64, 64], fill="white")
    icon = pystray.Icon("FileMonitor")
    icon.icon = image
    icon.title = "File Monitor"
    icon.menu = pystray.Menu(item('Quit', on_quit))
    icon.run()

observer = Observer(timeout=1)
start_monitoring()

tray_thread = threading.Thread(target=setup_tray_icon, daemon=True)
tray_thread.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        break
