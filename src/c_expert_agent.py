import os
from src.llm_agent import LLMAgent

class CExpertAgent(LLMAgent):
    def __init__(self, c_code_directory):
        super().__init__(model_name = "llama-3-8b-instruct")
        self.c_code_directory = c_code_directory

    def analyze_code(self, code):
        self.log(f"Analyzing C code: {code}")

    def format_code(self, code):
        formatted_code = code.strip()
        self.log(f"Formatted C code: {formatted_code}")
        return formatted_code

    def generate_code_snippet(self, snippet_type):
        snippets = {
            "for_loop": "for (int i = 0; i < n; i++) { /* code */ }",
            "if_statement": "if (condition) { /* code */ }",
        }
        return snippets.get(snippet_type, "Snippet not found")

    def static_analysis(self, code):
        issues = []
        if "unused_variable" in code:
            issues.append("Warning: Unused variable found.")
        self.log(f"Static analysis results: {issues}")
        return issues

    def run_code(self, code):
        self.log(f"Running C code: {code}")
        return "Execution results..."

    def compare_code(self, code1, code2):
        differences = set(code1.splitlines()) ^ set(code2.splitlines())
        return differences
    
    def set_code_directory(self, c_code_directory):
        self.c_code_directory = c_code_directory
        # self.log(f"C code directory set to: {c_code_directory}")

    def get_current_commit_id(self):
        try:
            # Change directory to the C code directory
            os.chdir(self.c_code_directory)
            # Retrieve the current commit ID
            commit_id = os.popen('git rev-parse HEAD').read().strip()
            self.log(f"Current commit ID: {commit_id}")
            return commit_id
        except Exception as e:
            self.log(f"Error retrieving commit ID: {e}")
            return None

    def read_code_file(self, src_file_name, line, dest_line):
        # Construct the full path to the source file
        src_file_path = os.path.join(self.c_code_directory, src_file_name)

        # Read the code from the source file
        try:
            with open(src_file_path, 'r') as file:
                code_lines = file.readlines()
                # Extract the relevant lines of code
                code = ''.join(code_lines[line-1:dest_line])
                print(code)
                return code
        except FileNotFoundError:
            self.log(f"Source file {src_file_name} not found in directory {self.c_code_directory}.")
            return None
        except Exception as e:
            self.log(f"Error reading source file {src_file_name}: {e}")
            return None