import shutil
import zipfile
import os
import time

class BackupError(Exception):
    """Custom exception for backup errors."""
    pass

class BackupManager:
    """Manager class to create folder or ZIP backups."""

    def __init__(self, sources, destination, compressed=False, logger=None):
        if not isinstance(sources, list):
            sources = [sources]
        self.sources = sources
        self.destination = destination
        self.compressed = compressed
        self.logger = logger

    def create_backup(self):
        if self.compressed:
            return self.create_zip_backup()
        else:
            return self.create_folder_backup()
    
    def create_folder_backup(self):
        start_time = time.time()
        file_count = 0
        total_size = 0
        try:
            backup_root = self.destination
            os.makedirs(backup_root, exist_ok=True)
            for src in self.sources:
                if os.path.isdir(src):
                    # Compter fichiers et taille
                    for root, _, files in os.walk(src):
                        file_count += len(files)
                        for f in files:
                            total_size += os.path.getsize(os.path.join(root, f))

                    # Nom du sous-dossier final dans backup_root
                    dest_name = os.path.basename(src)
                    unique_name = BackupManager.get_unique_name(backup_root, dest_name, logger=self.logger, original_path=src)
                    final_dest = os.path.join(backup_root, unique_name)

                    # Copier le dossier
                    shutil.copytree(src, final_dest)

                elif os.path.isfile(src):
                    # Copier un fichier dans backup_root
                    file_count += 1
                    total_size += os.path.getsize(src)

                    filename = os.path.basename(src)
                    unique_name = BackupManager.get_unique_name(backup_root, filename, logger=self.logger, original_path=src)
                    shutil.copy2(src, os.path.join(backup_root, unique_name))
                else:
                    raise BackupError("Source does not exist or is not a file/folder.")

            duration = time.time() - start_time
            return file_count, total_size, duration

        except FileExistsError:
            raise BackupError("Destination folder already exists.")
        except PermissionError:
            raise BackupError("Permission denied during copy.")
        except Exception as e:
            raise BackupError(f"Unexpected error: {e}")

    def create_zip_backup(self):
        start_time = time.time()
        file_count = 0
        total_size = 0
        try:
            zip_path = self.destination + ".zip"
            zip_dir = os.path.dirname(zip_path)
            if zip_dir:
                os.makedirs(zip_dir, exist_ok=True)

            zip_folder = zip_dir if zip_dir else "."
            zip_filename = os.path.basename(zip_path)
            zip_filename = BackupManager.get_unique_name(zip_folder, zip_filename)
            zip_path = os.path.join(zip_folder, zip_filename)

            added_files = set()

            with zipfile.ZipFile(zip_path, "w") as zipf:
                for src in self.sources:
                    if os.path.isdir(src):
                        for foldername, _, filenames in os.walk(src):
                            for filename in filenames:
                                abs_path = os.path.join(foldername, filename)
                                rel_path = os.path.relpath(abs_path, src)
                                rel_unique = BackupManager.get_unique_relpath(added_files, rel_path, logger=self.logger, abs_path=abs_path)
                                zipf.write(abs_path, rel_unique)
                                file_count += 1
                                total_size += os.path.getsize(abs_path)
                    elif os.path.isfile(src):
                        rel_unique = BackupManager.get_unique_relpath(added_files, os.path.basename(src), logger=self.logger, abs_path=src)
                        zipf.write(src, rel_unique)
                        file_count += 1
                        total_size += os.path.getsize(src)
                    else:
                        raise BackupError("Source does not exist or is not a file/folder.")

            duration = time.time() - start_time
            return file_count, total_size, duration
        
        except FileNotFoundError as e:
            raise BackupError(f"File not found: {e}")
        except PermissionError as e:
            raise BackupError(f"Access denied: {e}")
        except zipfile.BadZipFile as e:
            raise BackupError(f"Corrupted ZIP file: {e}")
        except Exception as e:
            raise BackupError(f"Unexpected error: {e}")

    # ----------------- STATIC METHODS ----------------- #

    @staticmethod
    def get_unique_name(folder, filename, logger=None, original_path=None):
        """Return a unique filename in folder if it already exists."""
        base, ext = os.path.splitext(filename)
        counter = 1
        new_name = filename
        while os.path.exists(os.path.join(folder, new_name)):
            if logger:
                logger.warning(f"Duplicate detected → renaming: {original_path or filename} → {new_name}")
            new_name = f"{base} ({counter}){ext}"
            counter += 1
        return new_name

    @staticmethod
    def get_unique_relpath(existing_names: set, rel_path: str, logger=None, abs_path=None) -> str:
        """
        Return a unique relative path for the ZIP if a duplicate name occurs.
        existing_names: set of already added names (with relative paths).
        """
        dirname, filename = os.path.split(rel_path)
        base, ext = os.path.splitext(filename)
        candidate = filename
        full = os.path.join(dirname, candidate) if dirname else candidate
        counter = 1
        while full in existing_names:
            new_candidate = f"{base} ({counter}){ext}"
            if logger:
                logger.warning(
                    f"Duplicate detected → renaming: {abs_path or rel_path} → {os.path.join(dirname, new_candidate)}"
                )
            candidate = new_candidate
            full = os.path.join(dirname, candidate) if dirname else candidate
            counter += 1
        existing_names.add(full)
        return full
