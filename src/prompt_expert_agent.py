import json
from src.llm_agent import LLMAgent

class PromptExpertAgent(LLMAgent):
    def __init__(self):
        super().__init__(system_role =
            f"You are an expert prompt engineer. "
            f"Your task is to help users by reviewing and improving their prompt."
            f"Provide concise, actionable advice without being too verbose."
            f"Please do not translate or rephrase the user's request."
            f"Provide a concise and actionable response without any explanation, punctuation, or unnecessary filler. Focus on the essentials and avoid redundancy."
        )

        self.prompts = []
        with open("prompts.json", 'r', encoding='utf-8') as file:
            self.prompts = json.load(file)

    def generate_prompt(self, prompt_type="", issue_details={}, code_snippets=[]):
        self.chat_history.clear()

        # print("prompt_type:", prompt_type)
        # print("issue_details:", issue_details)

        # {
        #     'Query': 'CGI Stored XSS',
        #     'QueryPath': 'CPP\\Cx\\CPP High Risk\\CGI Stored XSS Version:1',
        #     'Custom': nan,
        #     'PCI DSS v3.2.1': 'PCI DSS (3.2.1) - 6.5.7 - Cross-site scripting (XSS)',
        #     'OWASP Top 10 2013': 'A3-Cross-Site Scripting (XSS)',
        #     'FISMA 2014': 'System And Information Integrity',
        #     'NIST SP 800-53': 'SI-15 Information Output Filtering (P0)',
        #     'OWASP Top 10 2017': 'A7-Cross-Site Scripting (XSS)',
        #     'OWASP Mobile Top 10 2016': nan,
        #     'OWASP Top 10 API': nan,
        #     'ASD STIG 4.10': nan,
        #     'OWASP Top 10 2010': nan,
        #     'OWASP Top 10 2021': 'A3-Injection',
        #     'CWE top 25': 'CWE top 25',
        #     'MOIS(KISA) Secure Coding 2021': 'MOIS(KISA) Verification and representation of input data',
        #     'OWASP Top 10 API 2023': nan,
        #     'PCI DSS v4.0': 'PCI DSS (4.0) - 6.2.4 Vulnerabilities in software development',
        #     'SrcFileName': 'DakarMlkFWUpdate/FlashSectorInfo.cpp',
        #     'Line': 116,
        #     'Column': 14,
        #     'NodeId': 1,
        #     'Name': 'fwVer',
        #     'DestFileName': 'DakarMlkFWUpdate/FlashSectorInfo.cpp',
        #     'DestLine': 130,
        #     'DestColumn': 9,
        #     'DestNodeId': 8,
        #     'DestName': 'printf',
        #     'Result State': 'Not Exploitable',
        #     'Result Severity': 'High',
        #     'Assigned To': nan,
        #     'Comment': 'Arunkumar Kamatar ThinOS9.0_System_Deamons, [Wednesday, July 31, 2024 1:57:53 PM]: Changed status to Not Exploitable . FP: printf to console',
        #     'Link': 'https://cx.dell.com/CxWebClient/ViewerMain.aspx?scanid=9540495&projectid=240702&pathid=119',
        #     'Result Status': 'Recurrent',
        #     'Detection Date': '12/25/2023 5:09'
        # }

        template = "" #self.generate_fix_template(issue_details)
        # print("Template:", template)

        # subtasks = self.generate_subtask(issue_details)
        # print("Task:", subtasks)

        # think = self.think(result)
        # print("Think:", think)

        # temp = self.decide_action_plan(temp)
        # print("Decide:", temp)

        result = "".join(self.prompts[prompt_type]).format(
            Query=issue_details['Query'],
            QueryPath=issue_details['QueryPath'],
            Custom=issue_details['Custom'],
            SrcFileName=issue_details['SrcFileName'],
            Line=issue_details['Line'],
            DestLine=issue_details['DestLine'],
            Name=issue_details['Name'],
            ResultStatus=issue_details['Result Status'],
            Link=issue_details['Link'],
            template=template,
            code="".join(code_snippets),
            # subtasks="".join(subtasks),
        )

        print("result:", result)

        return "".join(result)

    def generate_subtask(self, prompt):
        # self.chat_history.clear()

        response = self.chat_completions(
            f"{prompt}\n"
            f"Divide this task into five subtasks!",
            temperature=0.5, top_p=0.95, max_tokens=2000)

        subtasks = []
        for i in range(1, 6):
            response = self.chat_completions(
                f"Give me the {i}th subtask's prompt. The answer must not contain any explanation.\n"
                f"Requirement: Simple and easy to understand!", max_tokens=2000)
            subtasks.append(response)

        print("###:", subtasks)

        return subtasks

    def think(self, subtask):
        response = self.chat_completions(
            f"{''.join(subtask)}\n"
            f"为这些subtasks生成具体的实施步骤！",
            temperature=0.5, top_p=0.95, max_tokens=2000)
        return response

    def decide_action_plan(self, plan):
        response = self.chat_completions(
            f"最后，请根据实施步骤，验证实施步骤是否符合要求。\n",
        )
        return response

    # receive_task
    # think
    # decide_action_plan
    # act
    # execute_action
    # handle_action_result
    # get_feedback
    # run

    # 生成issue修复模板
    def generate_fix_template(self, issue_details={}):
        response = self.chat_completions(
            f"对C语言{issue_details['Query']}问题生成修复模板\n",
            temperature=0.5, top_p=0.95, max_tokens=2000)
        return response

    # 生成issue审计模板
