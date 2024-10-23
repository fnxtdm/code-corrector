import pandas as pd

class BaseDataLoader:
    def display_data(self):
        """打印DataFrame的内容"""
        if self.data_frame is not None:
            print(self.data_frame)
        else:
            print("数据尚未加载。")

    def get_summary(self):
        """返回数据的基本信息"""
        if self.data_frame is not None:
            return self.data_frame.info()
        else:
            print("数据尚未加载。")

    def get_filtered_data(self, column_name, value):
        """根据列和特定值过滤数据"""
        if self.data_frame is not None:
            filtered_data = self.data_frame[self.data_frame[column_name] == value]
            return filtered_data
        else:
            print("数据尚未加载。")
            return None

    def iterate_rows(self, func):
        """逐行迭代DataFrame并执行用户自定义的函数"""
        if self.data_frame is not None:
            for index, row in self.data_frame.iterrows():
                if not func(index, row):  # 如果返回值为 False，则退出
                    break
        else:
            print("数据尚未加载。")