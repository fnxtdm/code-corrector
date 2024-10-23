import os

class Config:
    def __init__(self):
        self.language = "English"
        self.code_dir = ""
        self.csv_file = ""
        self.api_key = ""
        self.url = ""
        self.config_path = os.path.join("", "cc.cfg")
        # self.config_path = os.path.join(os.path.expanduser("~"), "cc.cfg")

    def save_to_disk(self):
        with open(self.config_path, 'w') as config_file:
            config_file.write(f"language={self.language}\n")
            config_file.write(f"code_dir={self.code_dir}\n")
            config_file.write(f"csv_file={self.csv_file}\n")
            config_file.write(f"api_key={self.api_key}\n")
            config_file.write(f"url={self.url}\n")

    def load_from_disk(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as config_file:
                for line in config_file:
                    key, value = line.strip().split('=')
                    setattr(self, key, value)