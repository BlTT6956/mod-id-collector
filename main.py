import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import zipfile

import toml
import pyperclip


class ModIdFrame(tk.Frame):
    def __init__(self, root, label_name: str, text_tuple=()):
        super().__init__(root)
        self.root = root

        self.mod_id_text = tk.Text(self)
        self.mod_id_text.place(relx=0.01, rely=0.08, relw=0.99, relh=0.76)
        if text_tuple:
            self.mod_id_text.insert(tk.END, "\n".join(text_tuple))
        root.bind_copy_paste(self.mod_id_text)
        root.bind_context_menu(self.mod_id_text)

        self.mod_id_label = ttk.Label(self, text=label_name.upper(), font=("Arial", 11, "bold"), anchor="center")
        self.mod_id_label.place(relx=0, rely=0.03, relw=1, relh=0.03)

        self.add_mods_button = ttk.Button(self, text="Add mods", command=self.get_mods)
        self.add_mods_button.place(relx=0, rely=0.85, relw=1, relh=0.05)

    def get_mods(self):
        mod_paths = filedialog.askopenfilenames(
            filetypes=[("JAR files", "*.jar")],
            defaultextension=".jar"
        )

        mod_ids = ModIdCollector.collect_mod_ids(mod_paths)
        if len(mod_ids) != 0:
            self.mod_id_text.insert(tk.END, "\n" + "\n".join(sorted(mod_ids)))


class ModIdCollectorTK(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mods ID Collector")
        self.iconbitmap("icon.ico")
        self.geometry("600x600")
        self.wm_minsize(400, 600)

        self.necessary_frame = ModIdFrame(self, "necessary", ("minecraft", "forge", "mod_whitelist"))
        self.necessary_frame.place(relx=0, rely=0, relw=0.5, relh=1)

        self.copy_button = ttk.Button(self.necessary_frame, text="Copy JSON", command=self.copy_json)
        self.copy_button.place(relx=0, rely=0.90, relw=1, relh=0.05)

        self.save_button = ttk.Button(self.necessary_frame, text="Save JSON", command=self.save_json)
        self.save_button.place(relx=0, rely=0.95, relw=1, relh=0.05)

        self.list_frame = ModIdFrame(self, "whitelist", ("minecraft", "forge", "mod_whitelist"))
        self.list_frame.place(relx=0.5, rely=0, relw=0.5, relh=1)

        self.list_switcher = ttk.Button(self.list_frame, text="Switch to BLACKLIST", command=self.switch_whitelist)
        self.list_switcher.place(relx=0, rely=0.90, relw=1, relh=0.05)

        self.import_button = ttk.Button(self.list_frame, text="Import JSON", command=self.import_json)
        self.import_button.place(relx=0, rely=0.95, relw=1, relh=0.05)

    def switch_whitelist(self):
        if self.list_switcher.cget("text") == "Switch to BLACKLIST":
            self.list_switcher.configure(text="Switch to WHITELIST")
            self.list_frame.mod_id_label.configure(text="BLACKLIST")
        else:
            self.list_switcher.configure(text="Switch to BLACKLIST")
            self.list_frame.mod_id_label.configure(text="WHITELIST")

    def get_json(self):
        use_whitelist_only = self.list_switcher.cget("text") == "Switch to BLACKLIST"
        whitelist_list = self.list_frame.mod_id_text.get(1.0, tk.END).split("\n")
        whitelist_list = [elem for elem in whitelist_list if elem]
        necessary_list = self.necessary_frame.mod_id_text.get(1.0, tk.END).split("\n")
        necessary_list = [elem for elem in necessary_list if elem]
        return {
            "USE_WHITELIST_ONLY": use_whitelist_only,
            "CLIENT_MOD_NECESSARY": necessary_list,
            "CLIENT_MOD_WHITELIST": whitelist_list if use_whitelist_only else [],
            "CLIENT_MOD_BLACKLIST": [] if use_whitelist_only else whitelist_list
        }

    def copy_json(self):
        json_data = self.get_json()
        pyperclip.copy(json.dumps(json_data))

    def save_json(self):
        json_data = self.get_json()
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="mod_whitelist-config.json"
        )
        with open(filename, "w") as file:
            json.dump(json_data, file, indent=4)

    def import_json(self):
        json_path = filedialog.askopenfilename(
            initialfile="mod_whitelist-config.json",
            filetypes=[("JSON files", "*.json")],
            defaultextension=".json",
        )
        with open(json_path, "r") as file:
            json_data = json.load(file)
        print(json_data.get("CLIENT_MOD_NECESSARY"))
        if (isinstance(json_data.get("USE_WHITELIST_ONLY"), bool) and isinstance(json_data.get("CLIENT_MOD_NECESSARY"), list) and
            isinstance(json_data.get("CLIENT_MOD_WHITELIST"), list) and isinstance(json_data.get("CLIENT_MOD_BLACKLIST"), list)):

            self.list_frame.mod_id_text.delete(1.0, tk.END)
            if json_data.get("USE_WHITELIST_ONLY"):
                self.list_switcher.configure(text="Switch to BLACKLIST")
                self.list_frame.mod_id_label.configure(text="WHITELIST")
                self.list_frame.mod_id_text.insert(tk.END, "\n".join(json_data.get("CLIENT_MOD_WHITELIST")))
            else:
                self.list_switcher.configure(text="Switch to WHITELIST")
                self.list_frame.mod_id_label.configure(text="BLACKLIST")
                self.list_frame.mod_id_text.insert(tk.END, "\n".join(json_data.get("CLIENT_MOD_BLACKLIST")))
            self.necessary_frame.mod_id_text.delete(1.0, tk.END)
            self.necessary_frame.mod_id_text.insert(tk.END, "\n".join(json_data.get("CLIENT_MOD_NECESSARY")))

    @staticmethod
    def bind_copy_paste(element):
        element.bind('<Control-c>', lambda e: element.event_generate('<<Copy>>'))
        element.bind('<Control-v>', lambda e: element.event_generate('<<Paste>>'))

    def bind_context_menu(self, element):
        element.bind("<Button-3>", lambda event: self.show_context_menu(event, element))

    def show_context_menu(self, event, entry_widget):
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Copy", command=lambda: entry_widget.event_generate('<<Copy>>'))
        context_menu.add_command(label="Paste", command=lambda: entry_widget.event_generate('<<Paste>>'))
        context_menu.post(event.x_root, event.y_root)


class ModIdCollector:
    meta_path = 'META-INF/mods.toml'

    @classmethod
    def collect_mod_ids(cls, filepaths: [str]) -> [str]:
        return [
            mod_id for filepath in filepaths if cls.is_file_jar(filepath)
            for mod_id in [cls.extract_mod_id_from_jar(filepath)] if mod_id is not None
        ]

    @classmethod
    def is_file_jar(cls, filepath: str) -> bool:
        return filepath.endswith(".jar")

    @classmethod
    def extract_mod_id_from_jar(cls, filepath: str) -> str:
        with zipfile.ZipFile(filepath, 'r') as jar:
            if cls.meta_path in jar.namelist():
                with jar.open(cls.meta_path) as file:
                    return cls.find_mod_id(file)

    @classmethod
    def find_mod_id(cls, file):
        mods_data = toml.loads(file.read().decode('utf-8'))
        mods_list = mods_data.get('mods', [])
        if mods_list:
            return mods_list[0].get('modId')


if __name__ == "__main__":
    app = ModIdCollectorTK()
    app.mainloop()

