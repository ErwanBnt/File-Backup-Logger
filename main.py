import os
import tkinter as tk
from datetime import datetime
from utils import Logging, ConfigManager
from gui import BackupGUI
from backup import BackupManager, BackupError

def Backup_Name(version: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"backup_{timestamp}_V{version}"

def file_size_converter(file_size):
    if file_size == 0:
        return "0 bytes"
    units = ["bytes", "KB", "MB", "GB", "TB", "PB"]
    count = 0
    size = float(file_size)
    while size >= 1024 and count < len(units) - 1:
        size /= 1024
        count += 1
    return f"{size:.2f} {units[count]}"

def main():
    main_dir = os.path.dirname(os.path.abspath(__file__))

    # --- Logger ---
    log_manager = Logging(main_dir)
    logger = log_manager.get_logger()
    logger.info("Program started")

    # --- Config ---
    config_manager = ConfigManager()
    config_manager.increment_version()
    os.makedirs(config_manager.backup_dir, exist_ok=True)

    # --- Callback pour le GUI ---
    def run_backup(selected_paths, compress):
        if not selected_paths:
            selected_paths = config_manager.paths
            logger.warning("No paths selected. Using last saved paths.")

        destination = os.path.join(config_manager.backup_dir, Backup_Name(config_manager.version))
        backup = BackupManager(selected_paths, destination, compressed=compress)
        try:
            logger.info(f"Starting backup for {len(selected_paths)} items")
            file_count, file_size, duration = backup.create_backup()
            logger.info(f"Backup finished: {file_count} files ({file_size_converter(file_size)}) in {duration:.2f} seconds")
        except BackupError as e:
            logger.error(f"Backup failed: {e}")

        # --- Auto backup ---
        interval = config_manager.backup_interval
        if interval and interval > 0:
            logger.info(f"Next auto-backup in {interval} seconds")
            root.after(interval * 1000, lambda: run_backup(selected_paths, compress))

    # --- GUI ---
    root = tk.Tk()
    BackupGUI(root, start_backup_callback=run_backup, config=config_manager)
    root.mainloop()
    logger.info("Program finished")

if __name__ == "__main__":
    main()
