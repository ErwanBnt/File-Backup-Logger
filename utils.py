import os
import logging
import json

class Logging:
    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_dir, "logs", "backup.log"),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def get_logger(self):
        return logging.getLogger("BackupLogger")


class ConfigManager:
    CONFIG_FILE = "config.json"
    DEFAULT_CONFIG = {
        "version": "1.0",
        "paths": [],
        "compress": False,
        "backup_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups"),
        "backup_interval": None
    }

    def __init__(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()  # créer le fichier config.json si inexistant

    # --- Propriétés pratiques ---
    @property
    def version(self):
        return self.config.get("version", "1.0")

    @version.setter
    def version(self, val):
        self.config["version"] = val

    @property
    def paths(self):
        return self.config.get("paths", [])

    @paths.setter
    def paths(self, val):
        self.config["paths"] = val

    @property
    def compress(self):
        return self.config.get("compress", False)

    @compress.setter
    def compress(self, val):
        self.config["compress"] = val

    @property
    def backup_dir(self):
        return self.config.get("backup_dir", self.DEFAULT_CONFIG["backup_dir"])

    @backup_dir.setter
    def backup_dir(self, val):
        self.config["backup_dir"] = val

    @property
    def backup_interval(self):
        return self.config.get("backup_interval", None)

    @backup_interval.setter
    def backup_interval(self, val):
        self.config["backup_interval"] = val

    # --- Sauvegarde et utilitaires ---
    def save(self):
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def increment_version(self):
        y, x = map(int, self.version.split("."))
        x += 1
        if x > 23 * y:
            y += 1
            x = 0
        self.version = f"{y}.{x}"
        self.save()
        return self.version

    @staticmethod
    def compute_interval(value, unit):
        try:
            value = int(value)
        except ValueError:
            return None
        if value <= 0:
            return None
        unit_map = {
            "minutes": 60,
            "hours": 3600,
            "days": 86400,
            "weeks": 604800
        }
        return value * unit_map.get(unit, 0)
