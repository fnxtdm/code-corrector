import pandas as pd
from src.base_data_loader import BaseDataLoader

class CSVDataLoader(BaseDataLoader):
    def __init__(self, file_path):
        self.file_path = file_path
        self.data_frame = None

    def load_data(self, sep=',', usecols=None, na_values=None, index_col=None, dtype=None, skiprows=0, nrows=None):
        """读取CSV文件并保存为DataFrame"""
        self.data_frame = pd.read_csv(
            self.file_path,
            sep=sep,
            usecols=usecols,
            na_values=na_values,
            index_col=index_col,
            dtype=dtype,
            skiprows=skiprows,
            nrows=nrows
        )
