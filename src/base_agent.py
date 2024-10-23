
class BaseAgent:
    def __init__(self):
        self.logging = None
        self.answer_language = None
        self.url = None
        self.token = None

        self.system_role = (
            "You are an expert C programmer. "
            "Your task is to help users by reviewing and improving their C code. "
            "Provide concise, actionable advice without being too verbose."
        )

    def set_parameter(self, language, url, api_key, csv_file, code_dir):
        self.answer_language = language
        self.url = url
        self.token = api_key
        self.csv_file = csv_file
        self.code_dir = code_dir

    def set_system_role(self, role):
        self.system_role = role

    def log(self, message: str):
        print(message)
        if (self.logging is not None):
            self.logging.info(message)

    def generate_response(self, query):
        raise NotImplementedError("Subclass must implement abstract method")
