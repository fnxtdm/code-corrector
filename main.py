import os
import logging
import argparse
import tkinter as tk

from src.c_expert_agent import CExpertAgent
from src.config import Config
from src.app_view_controller import AppViewController
from src.checkmarx_expert import CheckmarxExpert
from src.format_patch_expert import FormatPatchExpert
from src.prompt_expert_agent import PromptExpertAgent

global_config = Config()

# Configure logging
logging.basicConfig(
    filename='cc.log', encoding='utf-8', level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a Checkmarx Expert agent
prompt_agent = PromptExpertAgent()
checkmarx_agent = CheckmarxExpert(logging)
formatpatch_agent = FormatPatchExpert()
ccode_agent = CExpertAgent()

def main():
    def process_row(index, row):
        query_item = row.get("Query")
        src_file_name = row.get("SrcFileName")
        line = row.get("Line")
        dest_line = row.get("DestLine")
        name = row.get("Name")
        result_status = row.get("Result Status")

        # special_files = [
        #     "sso/src/imprivata_fps_wrapper32.c", 
        # ]
        # if src_file_name not in special_files:
        #     # print(f"Processing special file: {src_file_name}")
        #     return True

        # 读取源文件, 上传文件到LLMAgent
        src_file_path = os.path.join(checkmarx_agent.c.c_code_directory, src_file_name)
        if os.path.getsize(src_file_path) > 10 * 1024:
            return True

        checkmarx_agent.upload_file(src_file_path)

        # 识别脆弱性
        vulnerabilities = checkmarx_agent.identify_vulnerabilities(
            query_item=query_item,
            src_file_name=src_file_name,
            line=line,
            dest_line=dest_line,
            name=name,
            result_status=result_status
        )
        # print("Identified Vulnerabilities:", vulnerabilities)

        # # 生成审计报告
        report = checkmarx_agent.generate_audit_report(
            query_item=query_item,
            src_file_name=src_file_name,
            line=line,
            dest_line=dest_line,
            name=name,
            result_status=result_status
        )
        # print("\nAudit Report:")
        # print(report)

        # 自动修复代码
        fixed_code = checkmarx_agent.auto_fix(
            query_item=query_item,
            src_file_name=src_file_name,
            line=line,
            dest_line=dest_line,
            name=name,
            result_status=result_status)
        # print("Fixed Code:", fixed_code)

        # 运行集成测试
        # test_result = checkmarx_agent.run_integrated_tests(fixed_code)
        # print("Integration Test Result:", test_result)

        # # 推荐最佳实践
        # best_practices = checkmarx_agent.recommend_best_practices()
        # print("\nRecommended Best Practices:")
        # for practice in best_practices:
        #     print(f"- {practice}")

        checkmarx_agent.clean_up()

        # 只处理前 5 行
        # return index < 5
        return True

    checkmarx_agent.checkmarx_data_loader.iterate_rows(process_row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--antigui', action='store_true', help='Run the Anti GUI version of the application')
    args = parser.parse_args()

    global_config.load_from_disk()

    # checkmarx_agent.set_parameter(
    #     "C:/Work/system-daemons/",
    #     "./checkmarx/ThinOS9.0_System_Deamons.csv"
    # )

    formatpatch_agent.set_parameter(
        global_config.language,
        global_config.url,
        global_config.api_key,
        global_config.csv_file,
        global_config.code_dir)

    ccode_agent.set_parameter(
        global_config.language,
        global_config.url,
        global_config.api_key,
        global_config.csv_file,
        global_config.code_dir)

    prompt_agent.set_parameter(
        global_config.language,
        global_config.url,
        global_config.api_key,
        global_config.csv_file,
        global_config.code_dir
    )

    checkmarx_agent.set_parameter(
        global_config.language,
        global_config.url,
        global_config.api_key,
        global_config.csv_file,
        global_config.code_dir
    )
    checkmarx_agent.load_checkmarx_data()

    if args.antigui:
        main()
    else:
        root = tk.Tk()
        app = AppViewController(
            root,
            global_config,
            prompt_agent,
            checkmarx_agent,
            ccode_agent,
            formatpatch_agent
        )
        root.mainloop()
