import pandas as pd
# from PyPDF2 import PdfReader
from src.base_data_loader import BaseDataLoader

class PDFDataLoader(BaseDataLoader):
    def __init__(self, file_path):
        self.file_path = file_path
        self.data_frame = None

    def load_data(self):
        """读取PDF文件并提取文本内容"""
        # with open(self.file_path, 'rb') as file:
        #     reader = PdfReader(file)
        #     text_content = []
        #     for page in reader.pages:
        #         text_content.append(page.extract_text())
        #     self.data_frame = pd.DataFrame({'text': text_content})