
import json
from src.llm_agent import LLMAgent
from src.checkmarx_data_loader import CheckmarxDataLoader

class CheckmarxExpert(LLMAgent):
    def __init__(self, logging):
        super().__init__(system_role =
            f"ROLE DEFINITION:\n"
            f" - You are Checkmarx expert, a large language model developed by OpenAI.\n"
            f" - Your role includes providing code generation and problem-solving in response to user requests.\n"
            f" - Please do not translate or rephrase the user's request.\n."            
            f"GUIDELINES FOR C CODE GENERATION:\n"
            f" 0. Environment: Ubuntu Linux 22.04 LTS with gcc 12.2.1\n"
            f" 1. Understand User Intent:\n"
            f"    - Analyze the context provided by the user to understand the user's request.\n"
            f" 2. Write Accurate Code:\n"
            f"    - Generate code that adheres to best practices for the given language.\n"
            f"    - Ensure code correctness by avoiding common pitfalls and syntax errors.\n"
        )

        self.logging = logging
        self.checkmarx_data_loader = None
        self.issue_details = None

        with open("prompts.json", 'r', encoding='utf-8') as file:
            self.prompts = json.load(file)

    def execute_action(self, issue = "", action_plan="", code_snippets=[]):
        issue_details = self.details_from_issue(issue)

        Query = issue_details['Query']
        SrcFileName = issue_details['SrcFileName']
        Line = issue_details['Line']
        DestLine = issue_details['DestLine']
        Name = issue_details['Name']

        prompt = "".join(self.prompts[action_plan]).format(
            Query=Query, SrcFileName=SrcFileName, Line=Line, DestLine=DestLine, Name=Name)

        return self.chat_completions(prompt + "".join(code_snippets))

    def load_checkmarx_data(self):
        self.checkmarx_data_loader = CheckmarxDataLoader(file_path=self.csv_file)
        self.checkmarx_data_loader.load_data()
        # print("Data Summary:", self.checkmarx_data_loader.get_summary())
    
    def details_from_issue(self, issue):
        self.issue_details = self.checkmarx_data_loader.select_item_by_sample_issue(issue)
        return self.issue_details