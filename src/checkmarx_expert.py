
from src.llm_agent import LLMAgent
from src.checkmarx_data_loader import CheckmarxDataLoader

class CheckmarxExpert(LLMAgent):
    def __init__(self, logging):
        super().__init__(model_name = "llama-3-8b-instruct")
        self.logging = logging

        self.checkmarx_data_loader = None

        self.set_system_role(
            f"ROLE DEFINITION:\n"
            f" - You are Checkmarx expert, a large language model developed by OpenAI.\n"
            f" - Your role includes providing code generation, problem-solving, and language conversational assistance in response to user requests.\n"
            f"GUIDELINES FOR C CODE GENERATION:\n"
            f" 0. Ubuntu Linux 22.04 LTS with gcc 12.2.1\n"
            f" 1. Understand User Intent:\n"
            f"    - Analyze the context provided by the user to understand the user's request.\n"
            f" 2. Write Accurate Code:\n"
            f"    - Generate code that adheres to best practices for the given language.\n"
            f"    - Ensure code correctness by avoiding common pitfalls and syntax errors.\n"
        )

    def upload_file(self, file_path, seek=0, on_upload_complete=None):
        self.generate_response(
            "Please note that: I'm going to send multiple code snippets, When you see the code snippet, please do not feedback it."
        )

        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        # Split the file content into chunks by lines to avoid exceeding token limits
        lines = file_content.splitlines()
        # Limit the lines to a maximum of 600 starting from the seek position
        lines_to_upload = lines[seek:seek + 500]

        chunk_size = 250  # Adjust the chunk size as needed
        # chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
        chunks = [lines_to_upload[i:i + chunk_size] for i in range(0, len(lines_to_upload), chunk_size)]

        for i, chunk in enumerate(chunks):
            # chunk_text = "\n".join(chunk)
            # Add line numbers to each line in the chunk
            chunk_with_line_numbers = [f"{seek + j + 1 + i * chunk_size}: {line}" for j, line in enumerate(chunk)]
            chunk_text = "\n".join(chunk_with_line_numbers)

            if (on_upload_complete):
                on_upload_complete(chunk_text)

            message = f"Thanks for your feedback! Here is the {'first' if i == 0 else 'next'} code snippet, start from line {seek + 1}:\n\n{chunk_text}"
            self.generate_response(message)

        self.generate_response("Thanks for your feedback! I have sent complete code snippets.")

    def report_vulnerabilities(self, query_item, src_file_name, line, dest_line, name, result_status):
        # f"Requirements:\n"
        # f" - Please fix the Checkmarx issue in a git format patch based on the code i provided\n"
        # f" - Please reply with the code only, without the issue description\n"
        # f" - The issue fix code must be directly applied using Git command with am args\n"
        # f" - The issue fix code should be complete and not have any ellipsis (....) or abbreviations or comments for the code part\n"
        # f" - The issue fix code should not contain any line number markings\n"

        response = self.generate_response(
            f"Checkmarx Scan Report存在一个{query_item} 的问题\n"
            f"请仔核对{line}到{dest_line}行的代码，确认{name}问题的存在\n"
            f"要求：\n"
            f" - 这份代码的文件名是{src_file_name}，范围开始行号为{line}，结束行号为{dest_line}\n"
            f" - 请结合Checkmarx的错误类型评估\n"
            f" - 请使用{self.answer_language}进行回答\n"
            f" - 如果缺失什么信息，请提示我\n"
        )

        return response

    def identify_vulnerabilities(self, query_item, src_file_name, line, dest_line, name, result_status):
        response = self.generate_response(
            f"在我之前提供的代码中，Checkmarx工具报告存在{name} {query_item} 的问题, "
            f"请仔核对{line}到{dest_line}行的代码，确认问题的存在，给出问题评估结果。"
            f"要求：\n"
            f" - 这份代码的文件名是{src_file_name}，范围开始行号为{line}，结束行号为{dest_line}\n"
            f" - 请结合Checkmarx的错误类型评估\n"
            f" - 请使用{self.answer_language}进行回答\n"
            f" - 如果缺失什么信息，请提示我\n"
        )

        return response

    def refactor_fix(self, query_item, src_file_name, line, dest_line, name, result_status):
        response = self.generate_response(
            f"Refactor the code to fix the issue.\n"
            f"Requirements:\n"
            f" - Please fix the Checkmarx issue in a git format patch based on the code i provided, to focus on the start with '{line}:' line\n"
            f" - Checkmarx found this line the {name} has {query_item} issues, you need to fix it\n"
            f" - The name of the code file is {src_file_name}, the start line number of the fix range is {line}, and the end line number is {dest_line}\n"
        )
        return response

    def auto_fix(self, query_item, src_file_name, line, dest_line, name, result_status):
        response = self.generate_response(
            f"Please give me the {name} has {query_item} issue fix patch, with the following format just on line:{line} to {dest_line} code snippet.\n"
            f"Requirements:\n"
            f" - Follow the code format of the patch.\n"
            f" - Discard the other lines.\n"
            f" - The patch minimal 8 lines.\n"
            f" - Please fix the Checkmarx issue in a git format patch based on the code i provided\n"
            f" - Please reply with the code only, without the issue description\n"
            f" - The issue fix code must be directly applied using Git command with am args\n"
            f" - The issue fix code should be complete and not have any ellipsis (....) or abbreviations or comments for the code part\n"
            f" - The issue fix code should not contain any line number markings\n"
            f"Format:\n"
            f"  From ffd25d3c6905c4877b40284e0a6d209bb27539cc\n"
            f"  From: Lin_Cheng <lin_cheng@dell.com>\n"
            f"  Date: Wed, 9 Oct 2024 13:06:43 +0530\n"
            f"  Subject: [PATCH] FRN: {src_file_name}: {line} to {dest_line} {name} is {query_item} fix\n"
            f"  index using code Git commit ID: ffd25d3c6905c4877b40284e0a6d209bb27539cc\n"
        )
        return response

    # def generate_audit_report(self, query_item, src_file_name, line, dest_line, name, result_status):
    #     report = "Audit Report:\n"

    #     response = self.generate_response(
    #         f"在我之前提供的代码中，Checkmarx工具报告存在{name} {query_item} 的问题, "
    #         f"请仔细检查一下{line}到{dest_line}行的代码。并给出复代码。"
    #         f"要求：\n"
    #         f"0. 这份代码的文件名是{src_file_name}，修复范围开始行号为{line}，结束行号为{dest_line}，"
    #         f"1. 尽量简明扼要提供问题报告，如需必要可以列表方式提供"
    #     )
    #     # self.log(f"Audit report generated for {src_file_name} from line {line} to {dest_line}.")

    #     # for vulnerability, severity in vulnerabilities:
    #     #     suggestion = self.suggest_fixes((vulnerability, severity))
    #     #     report += f"{vulnerability} (Severity: {severity}) - Suggestion: {suggestion}\n"
    #     return report

    def recommend_best_practices(self):
        practices = [
            "Always validate input data.",
            "Avoid using dangerous functions like strcpy and system.",
            "Use memory-safe functions (e.g., strncpy, snprintf).",
            "Handle errors gracefully and avoid exposing sensitive information.",
        ]
        return practices

    # 使用 CheckmarxDataLoader 加载数据
    def load_checkmarx_data(self):
        self.checkmarx_data_loader = CheckmarxDataLoader(file_path=self.csv_file)
        self.checkmarx_data_loader.load_data()
        # print("Data Summary:", self.checkmarx_data_loader.get_summary())

    def find_src_file_name(self, file_name):
        self.checkmarx_data_loader.get_column_count
