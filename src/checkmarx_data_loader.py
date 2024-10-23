from src.csv_data_loader import CSVDataLoader
from src.pdf_data_loader import PDFDataLoader

class CheckmarxDataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data_loader = None

    def load_data(self):
        try:
            if self.file_path.endswith('.csv'):
                self.data_loader = CSVDataLoader(self.file_path)
                self.data_loader.load_data()
            elif self.file_path.endswith('.pdf'):
                self.data_loader = PDFDataLoader(self.file_path)
                self.data_loader.load_data()
            # else:
                # raise ValueError("Unsupported file format.")
        except FileNotFoundError as e:
            print(f"Error: {e}")

    def display_data(self):
        """显示数据"""
        if self.data_loader:
            self.data_loader.display_data()
        else:
            print("数据尚未加载。")

    def get_summary(self):
        """返回数据的基本信息"""
        if self.data_loader:
            return self.data_loader.get_summary()
        else:
            print("数据尚未加载。")

    def iterate_rows(self, func):
        """逐行迭代数据"""
        if self.data_loader:
            self.data_loader.iterate_rows(func)
        else:
            print("数据尚未加载。")

    def get_column_names(self):
        """返回列名"""
        if self.data_loader:
            return self.data_loader.data_frame.columns
        else:
            print("数据尚未加载。")
            return None
    def get_row_count(self):
        """返回行数"""
        if self.data_loader:
            return len(self.data_loader.data_frame)
        else:
            print("数据尚未加载。")
            return None
        
    def get_column_count(self):
        """返回列数"""
        if self.data_loader:
            return len(self.data_loader.data_frame.columns)
        else:
            print("数据尚未加载。")
            return None
    
    # {'Query': 'Buffer Improper Index Access', 'QueryPath': 'CPP\\Cx\\CPP Buffer Overflow\\Buffer Improper Index Access Version:4', 'Custom': nan, 'PCI DSS v3.2.1': nan, 'OWASP Top 10 2013': nan, 'FISMA 2014': nan, 'NIST SP 800-53': nan, 'OWASP Top 10 2017': nan, 'OWASP Mobile Top 10 2016': nan, 'OWASP Top 10 API': nan, 'ASD STIG 4.10': nan, 'OWASP Top 10 2010': nan, 'OWASP Top 10 2021': nan, 'CWE top 25': nan, 'MOIS(KISA) Secure Coding 2021': nan, 'OWASP ASVS': nan, 'SANS top 25': nan, 'ASA Mobile Premium': nan, 'ASA Premium': 'ASA Premium', 'Top Tier': 'Top Tier', 'ASD STIG 5.3': nan, 'Base Preset': nan, 'OWASP Top 10 API 2023': nan, 'PCI DSS v4.0': nan, 'SrcFileName': 'bluetooth/src/bluetooth_server.c', 'Line': 691, 'Column': 13, 'NodeId': 1, 'Name': 'dname', 'DestFileName': 'bluetooth/src/bluetooth_server.c', 'DestLine': 691, 'DestColumn': 13, 'DestNodeId': 1, 'DestName': 'dname', 'Result State': 'Not Exploitable', 'Result Severity': 'High', 'Assigned To': nan, 'Comment': 'Arunkumar Kamatar ThinOS9.0_System_Deamons, [Wednesday, July 31, 2024 1:44:32 PM]: Changed status to Not Exploitable . FP: array length just enough', 'Link': 'https://cx.dell.com/CxWebClient/ViewerMain.aspx?scanid=9540495&projectid=240702&pathid=39', 'Result Status': 'Recurrent', 'Detection Date': '7/22/2024 6:09'}
    def get_unique_queries(self):
        """返回数据集中不同的Query类型数组"""
        if self.data_loader:
            unique_queries = self.data_loader.data_frame['Query'].unique()
            return unique_queries
        else:
            print("数据尚未加载。")
            return None

    def get_query_items(self, query):
        """返回数据集中指定Query类型的所有项"""
        if self.data_loader:
            query_items = self.data_loader.data_frame[self.data_loader.data_frame['Query'] == query].to_dict(orient='records')
            return query_items
        else:
            print("数据尚未加载。")
            return None

    def select_item_by_sample_issue(self, sample_issue):
        """通过样本问题(SrcFileName:Line)获取项"""
        if self.data_loader:
            src_file_name, line = sample_issue.split(':')
            line = int(line)
            item = self.data_loader.data_frame[
                (self.data_loader.data_frame['SrcFileName'] == src_file_name) &
                (self.data_loader.data_frame['Line'] == line)
            ]
            if not item.empty:
                return item.to_dict(orient='records')[0]
            else:
                print("未找到匹配的项。")
                return None
        else:
            print("数据尚未加载。")
            return None

    def load_sample_issues(self):
        items = []
        if self.data_loader is None:
            print("数据加载器尚未初始化。")
            return items

        # 确保 self.data_loader.data_frame 是一个有效的 DataFrame 对象
        if self.data_loader.data_frame is None:
            print("数据加载器的 data_frame 属性无效或未初始化。")
            return items

        for _, row in self.data_loader.data_frame.iterrows():
            file_name = row.get('SrcFileName')
            # query = row.get('Query')
            line = row.get('Line')
            item_str = f"{file_name}:{line}"
            items.append(item_str)
        items.sort(key=lambda x: (x.split(':')[0], int(x.split(':')[1])))
        return items