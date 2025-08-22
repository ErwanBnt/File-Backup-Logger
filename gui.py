import tkinter as tk
from tkinter import filedialog, ttk
from utils import ConfigManager

class BackupGUI:
    def __init__(self, root, start_backup_callback, config):
        self.root = root
        self.root.title("Backup Manager")
        self.root.geometry("800x600")
        self.root.minsize(500, 500)

        self.start_backup_callback = start_backup_callback
        self.config = config

        # List of selected files/folders
        self.selected_paths = config.paths
        compress_default = config.compress

        # --- Title ---
        title = tk.Label(root, text="Backup Manager", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # --- Main frame ---
        main_frame = tk.Frame(root)
        main_frame.pack(pady=10, padx=10, fill="both")

        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=0)
        main_frame.rowconfigure(2, weight=0)

        # Listbox showing selected paths
        self.listbox = tk.Listbox(main_frame, selectmode=tk.MULTIPLE, font=("Arial", 11))
        self.listbox.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="nsew")

        for path in self.selected_paths:
            self.listbox.insert(tk.END, path)

        # File / Folder buttons
        file_btn = tk.Button(main_frame, text="Import File(s)", font=("Arial", 11), command=self.import_files)
        file_btn.grid(row=0, column=1, padx=10, pady=20, ipady=10, sticky="ew")

        folder_btn = tk.Button(main_frame, text="Import Folder", font=("Arial", 11), command=self.import_folder)
        folder_btn.grid(row=1, column=1, padx=10, pady=20, ipady=10, sticky="ew")

        delete_btn = tk.Button(main_frame, text="Delete Selection", font=("Arial", 11), command=self.delete_selected)
        delete_btn.grid(row=2, column=1, padx=10, pady=20, ipady=10, sticky="ew")

        # --- Backup destination folder ---
        dest_frame = tk.Frame(root)
        dest_frame.pack(pady=5, fill="x", padx=10)

        tk.Label(dest_frame, text="Backup Folder:", font=("Arial", 11)).pack(side="left")

        self.dest_var = tk.StringVar(value=self.config.backup_dir)
        dest_entry = tk.Entry(dest_frame, textvariable=self.dest_var, font=("Arial", 11))
        dest_entry.pack(side="left", fill="x", expand=True, padx=5, ipady=2)

        dest_btn = tk.Button(dest_frame, text="Select...", font=("Arial", 11), command=self.select_backup_folder)
        dest_btn.pack(side="left", padx=10, ipadx=80, ipady=2)

        # --- Compression options ---
        self.compress_var = tk.BooleanVar(value=compress_default)
        compress_frame = tk.Frame(root)
        compress_frame.pack(pady=5)

        tk.Radiobutton(
            compress_frame, text="Uncompressed", variable=self.compress_var, value=False, font=("Arial", 11)
        ).pack(side="left", padx=5)
        tk.Radiobutton(
            compress_frame, text="Compressed (ZIP)", variable=self.compress_var, value=True, font=("Arial", 11)
        ).pack(side="left", padx=5)

        # --- Automatic backup interval ---
        interval_frame = tk.Frame(root)
        interval_frame.pack(pady=10)

        tk.Label(interval_frame, text="Automatic Backup:", font=("Arial", 11)).pack(side="left")

        self.interval_value = tk.StringVar(value="0")
        self.interval_unit = tk.StringVar(value="hours")

        entry = tk.Entry(interval_frame, textvariable=self.interval_value, width=5)
        entry.pack(side="left", padx=5)

        unit_menu = ttk.Combobox(
            interval_frame,
            textvariable=self.interval_unit,
            values=["minutes", "hours", "days", "weeks"],
            width=10,
            state="readonly"
        )
        unit_menu.pack(side="left", padx=5)

        # Load existing interval config
        interval_val = self.config.backup_interval
        if interval_val is not None:
            if interval_val % 604800 == 0:
                self.interval_value.set(str(interval_val // 604800))
                self.interval_unit.set("weeks")
            elif interval_val % 86400 == 0:
                self.interval_value.set(str(interval_val // 86400))
                self.interval_unit.set("days")
            elif interval_val % 3600 == 0:
                self.interval_value.set(str(interval_val // 3600))
                self.interval_unit.set("hours")
            elif interval_val % 60 == 0:
                self.interval_value.set(str(interval_val // 60))
                self.interval_unit.set("minutes")

        # Auto backup status indicator
        self.auto_status_label = tk.Label(interval_frame, text="OFF", bg="red", fg="white", width=10, font=("Arial", 11))
        self.auto_status_label.pack(side="left", padx=10)

        # --- Start Backup button ---
        backup_btn = tk.Button(root, text="Start Backup", font=("Arial", 11), command=self.start_backup)
        backup_btn.pack(pady=10, padx=10, ipadx=30)

        # --- Status label ---
        self.status_label = tk.Label(root, text="Waiting...", fg="blue", anchor="w", font=("Arial", 11))
        self.status_label.pack(pady=5)

        # Save config on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # --- Methods ---
    def import_files(self):
        paths = filedialog.askopenfilenames(title="Select Files")
        for path in paths:
            if path not in self.selected_paths:
                self.selected_paths.append(path)
                self.listbox.insert(tk.END, path)

    def import_folder(self):
        path = filedialog.askdirectory(title="Select Folder")
        if path and path not in self.selected_paths:
            self.selected_paths.append(path)
            self.listbox.insert(tk.END, path)

    def delete_selected(self):
        selected_indices = self.listbox.curselection()
        for index in reversed(selected_indices):
            self.listbox.delete(index)
            del self.selected_paths[index]

    def select_backup_folder(self):
        path = filedialog.askdirectory(title="Select Backup Folder")
        if path:
            self.dest_var.set(path)

    def start_backup(self):
        compress = self.compress_var.get()
        interval_seconds = ConfigManager.compute_interval(self.interval_value.get(), self.interval_unit.get())

        if interval_seconds:
            self.auto_status_label.config(text="ON", bg="green")
            self.root.after(interval_seconds * 1000, lambda: self.start_backup_callback(self.selected_paths, compress))
        else:
            self.auto_status_label.config(text="OFF", bg="red")
        self.status_label.config(text="Backup in progress...")
        self.start_backup_callback(self.selected_paths, compress)
        self.status_label.config(text="Backup completed ✅")

    def on_close(self):
        self.config.paths = self.selected_paths
        self.config.compress = self.compress_var.get()
        self.config.backup_dir = self.dest_var.get()
        self.config.save()
        self.root.destroy()
