import os
import time
import subprocess
from src.llm_agent import LLMAgent

class FormatPatchExpert(LLMAgent):
    def __init__(self):
        super().__init__(model_name = "llama-3-8b-instruct")
        self.patch_file_path = None
        self.set_system_role(
            f"ROLE DEFINITION:\n"
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
            f" - The issue fix code should not contain any line number markings\n"
        )

    def current_commit_id(self):
        # Get the current commit ID
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=self.code_dir)
        commit_id = result.stdout.strip()
        return commit_id

    def format_patch(self, src_file_name, fixed_code):
        # Save the extracted code to a file in the patchs/ directory
        patch_dir = "patchs"
        os.makedirs(patch_dir, exist_ok=True)

        timestamp = time.strftime("%Y%m%d%H%M%S")
        self.patch_file_path = os.path.join(patch_dir, f"patch_{timestamp}.diff")
        
        with open(self.patch_file_path, 'w') as patch_file:
            patch_file.write(fixed_code)

        print(f"Saved extracted code to {self.patch_file_path}")

    def review_patch(self):
        """
        评估patch的好坏
        """

        self.clean_history()

        with open(self.patch_file_path, 'r') as patch_file:
            patch_content = patch_file.read()

        prompt = f"Please review the following patch and give me a score: {patch_content}, 如果缺失什么信息，请提示我"
        response = self.generate_response(prompt)

        if "Score: " in response:
            score = int(response.split("Score: ")[-1].split(" ")[0])
            print(f"Patch {self.patch_file_path} has a score of {score}")
        else:
            print(f"Failed to review patch {self.patch_file_path}, please check the patch file.")

        return response

