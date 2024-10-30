
import json
from typing import Callable
from src.llm_agent import LLMAgent
from src.checkmarx_data_loader import CheckmarxDataLoader

class CheckmarxExpert(LLMAgent):
    def __init__(self, prompt_agent, formatpatch_agent, ccode_agent, logging):
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
        self.prompt_agent = prompt_agent
        self.formatpatch_agent = formatpatch_agent
        self.ccode_agent = ccode_agent

        self.checkmarx_data_loader = None
        self.issue_details = None

        with open("prompts.json", 'r', encoding='utf-8') as file:
            self.prompts = json.load(file)

    def load_checkmarx_data(self):
        self.checkmarx_data_loader = CheckmarxDataLoader(file_path=self.csv_file)
        self.checkmarx_data_loader.load_data()
        # print("Data Summary:", self.checkmarx_data_loader.get_summary())
    
    def details_from_issue(self, issue):
        self.issue_details = self.checkmarx_data_loader.select_item_by_sample_issue(issue)
        return self.issue_details
        
    def run(self, output_callback: Callable[[str, str], None]):
        sample_issues = self.checkmarx_data_loader.load_sample_issues()

        for issue in sample_issues:
            self.clean_history()
            issue_details = self.details_from_issue(issue)

            line = issue_details['Line']
            src_file_name = issue_details['SrcFileName']
            query = issue_details['Query']

            if query != 'Use of Obsolete Functions':
                continue

            prompt = self.prompt_agent.generate_prompt("CHECKMARX_QUERY", issue_details)
            checkmarx_content = self.chat_completions(prompt)
            output_callback(checkmarx_content)

            code_snippets = self.ccode_agent.format_code_snippet(
            snippet_type="LINE_NUM", encoding="utf-8", file_path=src_file_name, line=line, chunk_size=100)

            prompt = self.prompt_agent.generate_prompt("IDENTIFY_VULNERABILITIES", issue_details, code_snippets)
            vulnerabilities_content = self.chat_completions(prompt)
            output_callback(vulnerabilities_content)

            prompt = self.prompt_agent.generate_prompt("AUTO_FIX_CODE", issue_details, code_snippets)
            fixcode_content = self.chat_completions(prompt)
            output_callback(fixcode_content)

            prompt = self.prompt_agent.generate_prompt("AUTO_FIX", issue_details, code_snippets=code_snippets)
            patch_content = self.chat_completions(prompt)
            output_callback(patch_content, "code_light_blue")

            # result = self.formatpatch_agent.is_format_patch(patch_content, code_snippets)
            # print(result)

            # Save format patch
            self.formatpatch_agent.format_patch(src_file_name, patch_content)
        return None
    
    def execute_action(self, issue = "", prompt_type="", code_snippets=[]):
        issue_details = self.details_from_issue(issue)

        prompt = self.prompt_agent.generate_prompt(prompt_type, issue_details, code_snippets)
        return self.chat_completions(prompt)

    def execute_action_with_patch(self, issue="", prompt_type="", code_snippets=[], output_callback: Callable[[str, str], None]=None):
        try:
            patch_content = self.execute_action(issue, prompt_type, code_snippets)
            output_callback(patch_content, "code_light_blue")

            # Save format patch
            result = self.formatpatch_agent.is_format_patch(patch_content, code_snippets)
            print(result)

            src_file_name = self.issue_details['SrcFileName']
            self.formatpatch_agent.format_patch(src_file_name, patch_content)

        except Exception as e:
            # Handle any other exceptions that might occur
            print(f"An error occurred: {e}")

        return None

    def identify_vulnerabilities(self, issue):
        line = self.issue_details['Line']
        src_file_name = self.issue_details['SrcFileName']

        # 1. CHECKMARX_QUERY Vulnerabilities
        prompt = self.prompt_agent.generate_prompt("CHECKMARX_QUERY", self.issue_details)
        self.chat_completions(prompt)

        # 2. Load the code snippets
        code_snippets = self.ccode_agent.format_code_snippet(
            snippet_type="LINE_NUM", encoding="utf-8", file_path=src_file_name, line=line, chunk_size=50)
        self.execute_action(
            issue, prompt_type="CODE_SNIPPETS_TEMPLATE", code_snippets=code_snippets)

        # 3. Execute Identify Vulnerabilities
        vulnerabilities = self.execute_action(issue, "IDENTIFY_VULNERABILITIES")
        return vulnerabilities