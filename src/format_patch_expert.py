import json
import os
import time
import subprocess
from src.llm_agent import LLMAgent

class FormatPatchExpert(LLMAgent):
    def __init__(self):
        super().__init__(system_role = f"ROLE DEFINITION:\n"
            f" - You are an expert patch generator, a large language model developed by OpenAI.\n"
            f" - Your role includes providing code generation, problem-solving, and language conversational assistance in response to user requests on Ubuntu Linux 22.04 LTS.\n"
            f"GUIDELINES FOR C CODE GENERATION:\n"
            f" 1. Understand User Intent:\n"
            f"    - Analyze the context provided by the user to understand the user's request.\n"
            f" 2. Write Accurate Code:\n"
            f"    - Generate code that adheres to best practices for the given language.\n"
            f"    - Ensure code correctness by avoiding common pitfalls and syntax errors.\n"
            f"Requirements:\n"
            f" - Please fix the Checkmarx issue in a git format patch based on the code i provided\n"
            f" - Please reply with the code only, without the issue description\n"
            f" - The issue fix code must be directly applied using Git command with am args\n"
            f" - The issue fix code should be complete and not have any ellipsis (....) or abbreviations or comments for the code part\n"
            f" - The issue fix code should not contain any line number markings\n")
        self.patch_file_path = None

        with open("prompts.json", 'r', encoding='utf-8') as file:
            self.prompts = json.load(file)

    def current_commit_id(self):
        # Get the current commit ID
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=self.code_dir)
        commit_id = result.stdout.strip()
        return commit_id

    def is_format_patch(self, patch_content, code_snippets=[]):
        # Check if the commit is a format patch
        prompt = "".join(self.prompts[
            "REVIEW_FORMAT_PATCH"]).format(patch_content=patch_content, code="".join(code_snippets))

        print("REVIEW:", prompt)
        response = self.chat_completions(prompt)

        return response

    def format_patch(self, src_file_name, patch_content):
        # Save the extracted code to a file in the patchs/ directory
        patch_dir = "patchs/"+self.model_name
        os.makedirs(patch_dir, exist_ok=True)

        timestamp = time.strftime("%Y%m%d%H%M%S")
        self.patch_file_path = os.path.join(patch_dir, f"patch_{timestamp}.diff")

        with open(self.patch_file_path, 'w', encoding='utf-8') as patch_file:
            patch_file.write(patch_content)

        print(f"Saved extracted code to {self.patch_file_path}")

    def review_patch(self, issue_details, code_snippets=[]):
        self.clean_history()

        patch_content = ""
        with open(self.patch_file_path, 'r', encoding='utf-8') as patch_file:
            patch_content = patch_file.read()

        prompt = "".join(self.prompts[
            "REVIEW_PATCH"]).format(
                Query=issue_details['Query'],
                QueryPath=issue_details['QueryPath'],
                Custom=issue_details['Custom'],
                SrcFileName=issue_details['SrcFileName'],
                Line=issue_details['Line'],
                DestLine=issue_details['DestLine'],
                Name=issue_details['Name'],
                patch_content=patch_content, code="".join(code_snippets))

        print("REVIEW:", prompt)
        response = self.chat_completions(prompt)

        return response

