import tkinter as tk
import tkinter.font as tkFont

from tkinter import ttk, filedialog, messagebox, simpledialog

class PropertiesDialog(simpledialog.Dialog):
    def __init__(self, parent, global_config):
        self.global_config = global_config
        super().__init__(parent, title="Properties")

    def body(self, master):
        # Define padding values to increase the size of the window
        padding = {'padx': 30, 'pady': 2}

        tk.Label(master, text="LLM API KEY:", anchor='e').grid(row=2, column=0, **padding)
        tk.Label(master, text="URL:", anchor='e').grid(row=3, column=0, **padding)
        tk.Label(master, text="Code Directory:", anchor='e').grid(row=0, column=0, **padding)
        tk.Label(master, text="CSV File:", anchor='e').grid(row=1, column=0, **padding)

        self.code_dir_entry = tk.Entry(master, width=40)
        self.csv_file_entry = tk.Entry(master, width=40)
        self.api_key_entry = tk.Entry(master, width=40)
        self.url_entry = tk.Entry(master, width=40)

        self.code_dir_entry.grid(row=0, column=1, **padding)
        self.csv_file_entry.grid(row=1, column=1, **padding)
        self.api_key_entry.grid(row=2, column=1, **padding)
        self.url_entry.grid(row=3, column=1, **padding)

        # 读取全局配置并显示到输入框中
        self.code_dir_entry.insert(0, self.global_config.code_dir)
        self.csv_file_entry.insert(0, self.global_config.csv_file)
        self.api_key_entry.insert(0, self.global_config.api_key)
        self.url_entry.insert(0, self.global_config.url)

        # 如果配置值为空，给出默认值作为例子
        if not self.global_config.code_dir:
            self.code_dir_entry.insert(0, "c:/example/code_directory")
        if not self.global_config.csv_file:
            self.csv_file_entry.insert(0, "c:/example/checkmarx_report.csv")
        if not self.global_config.api_key:
            self.api_key_entry.insert(0, "your_api_key_here")
        if not self.global_config.url:
            self.url_entry.insert(0, "http://example.com/api")
        return self.code_dir_entry

    def apply(self):
        self.global_config.code_dir = self.code_dir_entry.get()
        self.global_config.csv_file = self.csv_file_entry.get()
        self.global_config.api_key = self.api_key_entry.get()
        self.global_config.url = self.url_entry.get()

        # 保存配置内容到本地磁盘
        self.global_config.save_to_disk()