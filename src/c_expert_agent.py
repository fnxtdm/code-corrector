import os
from src.llm_agent import LLMAgent

class CExpertAgent(LLMAgent):
    def __init__(self):
        super().__init__(system_role =
            f"You are an expert C programmer. "
            f"Your task is to help users by reviewing and improving their C code. "
            f"Provide concise, actionable advice without being too verbose."
        )

    def format_code_snippet(self, snippet_type="LINE_NUM", encoding="utf-8", file_path ="", line=0, chunk_size=400):
        # ```cpp
        # // Code here...
        # ``` 

        seek = 0
        code_snippets = []
        file_fullpath = os.path.join(self.code_dir, file_path)

        with open(file_fullpath, 'r', encoding=encoding) as file:
            file_content = file.read()

        # Split the file content into chunks by lines
        # Limit the lines to a maximum of 400 starting from the seek position
        lines = file_content.splitlines()

        if len(lines) > chunk_size:
            seek = max(0, line - int(chunk_size/2))

        lines_to_upload = lines[seek:seek + chunk_size]

        chunks = [lines_to_upload[i:i + chunk_size] for i in range(0, len(lines_to_upload), chunk_size)]

        for i, chunk in enumerate(chunks):
            if (snippet_type == "LINE_NUM"):
                # Add line numbers to each line in the chunk
                chunk_with_line_numbers = [f"{seek + j + 1 + i * chunk_size}:   {line}" for j, line in enumerate(chunk)]
                chunk_text = "\n".join(chunk_with_line_numbers)
            else:
                chunk_text = "\n".join(chunk)

            code_snippets.append(f"这个段代码是从第 {seek + 1} 行开始:\n```c\n{chunk_text}\n```\n")
        return code_snippets

    def run_code(self, code):
        self.log(f"Running C code: {code}")
        return "Execution results..."
