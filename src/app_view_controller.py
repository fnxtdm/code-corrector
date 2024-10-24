import os
import asyncio
import threading
import concurrent.futures
import tkinter as tk
import tkinter.font as tkFont

from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow

from tkinter import ttk, filedialog, messagebox
from src.properties_dialog import PropertiesDialog

# Traceloop.init(app_name="cc_generation_service", disable_batch=True, 
#   api_key="cfa27b109bf5f5b3d2df3498865cec19a37d55382524e7933d6c49e5637eff5e85e5ea147cc6f47b0d85195f94334fdb"
# )

class AppViewController:
    def __init__(self,
        root, global_config, prompt_agent, checkmarx_agent, ccode_agent, formatpatch_agent):
        self.root = root
        self.global_config = global_config
        self.prompt_agent = prompt_agent
        self.checkmarx_agent = checkmarx_agent
        self.ccode_agent = ccode_agent
        self.formatpatch_agent = formatpatch_agent

        self.dialog = None
        self._selected_issue = None

        self.root.title("Code Corrector")

        # Set window size to 1024x768
        self.root.geometry("1024x768")
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

        # Create a menu bar
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        # Create File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Run", command=self.run_all)
        self.file_menu.add_command(label="Properties", command=self.open_properties_dialog)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)

        # Create Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

        # Add status bar
        self.status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor='w')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10)

        # Frame for file list box
        self.listbox_frame = ttk.Frame(root)
        self.listbox_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        # Search box
        self.search_frame = ttk.Frame(self.listbox_frame)
        # Align the frame to the left
        self.search_frame.pack(pady=10, anchor='w')

        self.search_label = ttk.Label(
            self.search_frame, text="Checkmarx Report Issues: ", font=tkFont.Font(size=11, weight="bold"))
        # Align the label to the left
        self.search_label.pack(side=tk.LEFT, anchor='w')

        # Set width to twice the default size
        # self.search_entry = ttk.Entry(self.search_frame, width=23)
        # Align the entry to the left
        # self.search_entry.pack(side=tk.LEFT, anchor='w')

        self.issues_listbox = tk.Listbox(
            self.listbox_frame, width=45, height=40, font=tkFont.Font(size=10, weight="normal"))
        self.issues_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.issues_listbox.bind('<<ListboxSelect>>', self.on_selected_issue)

        self.scrollbar = ttk.Scrollbar(self.listbox_frame, command=self.issues_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.issues_listbox['yscrollcommand'] = self.scrollbar.set

        # Add issues to listbox
        sample_issues = []
        sample_issues = checkmarx_agent.checkmarx_data_loader.load_sample_issues()
        if not isinstance(sample_issues, list):
            sample_issues = []

        for issues in sample_issues:
            self.issues_listbox.insert(tk.END, issues)

        # self.issues_listbox.configure(font=font_style)

        # Label above the content display area
        self.description_label = ttk.Label(root, text="Description:", font=tkFont.Font(size=11, weight="bold"))
        # Align the label to the left and adjust pady to 55
        self.description_label.pack(padx=10, pady=5, anchor='w')

        self.detail_label = ttk.Label(
            root, text="\n\n\n\n\n", font=tkFont.Font(size=10, weight="bold"), foreground="red")
        # Align the label to the left
        self.detail_label.pack(padx=10, pady=1, anchor='w')

        # add buttons for handel auto and manual fix code
        button_frame = ttk.Frame(root)
        button_frame.pack(padx=10, pady=5, anchor='w')

        identify_vulnerabilities_button = ttk.Button(
            button_frame,
            text="Identify Vulnerabilitie",
            command=self.on_identify_vulnerabilities
        )
        identify_vulnerabilities_button.pack(side=tk.LEFT, padx=5, pady=5)

        auto_fix_button = ttk.Button(
            button_frame,
            text="Auto Fix",
            command=self.on_auto_fix
        )
        auto_fix_button.pack(side=tk.LEFT, padx=5, pady=5)

        review_patch_button = ttk.Button(
            button_frame,
            text="Review Patch",
            command=self.on_review_patch
        )
        review_patch_button.pack(side=tk.LEFT, padx=5, pady=5)

        refactor_fix_button = ttk.Button(
            button_frame,
            text="Refactor",
            command=self.on_refactor_fix
        )
        refactor_fix_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Content display area
        self.issues_text = tk.Text(
            root, wrap=tk.WORD, width=150, height=40, font=tkFont.Font(size=10, weight="normal"), foreground="#333333")
        self.issues_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configure the background color to black
        # self.issues_text.config(bg="black", fg="white")
        # self.issues_text.tag_configure("code_light_gray", background="#F5F5F5", foreground="#333333")  # 深灰色字体，浅灰背景
        self.issues_text.tag_configure("code_light_blue", background="#EAF3FF", foreground="#003366")  # 深蓝色字体，浅蓝背景
        # self.issues_text.tag_configure("code_light_green", background="#F0FFF0", foreground="#006400")  # 深绿色字体，淡绿色背景

        # self.issues_text.tag_configure("diff_add_green", background="#DFF0D8", foreground="#006400")  # 深绿色字体，新增绿色背景
        # self.issues_text.tag_configure("diff_remove_red", background="#F2DEDE", foreground="#8B0000")  # 深红色字体，删除红色背景
        # self.issues_text.tag_configure("diff_modify_yellow", background="#FCF8E3", foreground="#8B8000")  # 深黄色字体，修改黄色背景

        # self.issues_text.tag_configure("background_white", background="#FFFFFF", foreground="#000000")  # 黑色字体，白色背景
        # self.issues_text.tag_configure("background_light_gray", background="#F8F8F8", foreground="#333333")  # 深灰色字体，浅灰背景
        # self.issues_text.tag_configure("background_light_blue", background="#E6ECF0", foreground="#003366")  # 深蓝色字体，浅蓝背景

        # self.issues_text.tag_configure("dell_blue", background="#0076CE", foreground="#FFFFFF")  # 白色字体，Dell蓝色背景

        # self.issues_text.bind("<<Selection>>", highlight_selection)
        global sample_content
        sample_content = (
            "Please select an issue from the list to view AI generated corrections patches."
        )
        # Add content
        self.issues_text.insert(tk.END, sample_content)
        # self.issues_text.configure(font=font_style)

    @property
    def selected_issue(self):
        return self._selected_issue

    @selected_issue.setter
    def selected_issue(self, issue):
        # Call a function or perform any action when the value changes
        if self._selected_issue == issue:
            return None
        threading.Thread(
            target=lambda: asyncio.run(
                self.upload_code_snippets(issue))).start()
        self._selected_issue = issue
        return None

    def insert_issue_text(self, text, color="", clean=False):
        if clean:
            self.issues_text.delete("1.0", tk.END)

        self.issues_text.insert(tk.END, "\n\n")
        self.issues_text.insert(tk.END, text + '\n', color)

        self.issues_text.see(tk.END)

    async def upload_code_snippets(self, issue):
        self.status_bar.config(text="Processing...")

        # If dialog exists, do nothing
        # if self.dialog and self.dialog.winfo_exists():
        #     self.dialog.destroy()
        #     # return None

        # Clean the content of self.issues_text
        self.issues_text.delete("1.0", tk.END)
        self.checkmarx_agent.clean_history()

        # Change the value of self.detail_label to display multiple lines
        issue_details = self.checkmarx_agent.details_from_issue(issue)
        self.update_issue_details(issue_details)

        def on_upload_complete(result):
            self.issues_text.insert(tk.END, result, "code_light_blue")
            self.issues_text.see(tk.END)

        # prompt_snippets = []
        # prompt_snippets = self.prompt_agent.generate_prompt(
        #     "story", f"I have a Checkmarx scan report {self.selected_issue}, please help me fix it!")

        # for snippet in prompt_snippets:
        #     on_upload_complete(snippet)

        line = issue_details['Line']
        src_file_name = issue_details['SrcFileName']
        code_snippets = self.ccode_agent.format_code_snippet(
            snippet_type="LINE_NUM", encoding="utf-8", file_path=src_file_name, line=line, chunk_size=50)

        for snippet in code_snippets:
            on_upload_complete(snippet)
        self.status_bar.config(text="Ready")
        return None

    def open_properties_dialog(self):
        PropertiesDialog(self.root, self.global_config)

    async def async_identify_vulnerabilities(self, issue):
        # # If dialog exists, do nothing
        # if self.dialog and self.dialog.winfo_exists():
            # return None

        try:
            line = self.checkmarx_agent.issue_details['Line']
            src_file_name = self.checkmarx_agent.issue_details['SrcFileName']

            code_snippets = self.ccode_agent.format_code_snippet(
                snippet_type="LINE_NUM", encoding="utf-8", file_path=src_file_name, line=line, chunk_size=50)

            self.checkmarx_agent.execute_action(
                issue, action_plan="CODE_SNIPPETS_TEMPLATE", code_snippets=[])
            vulnerabilities = self.checkmarx_agent.execute_action(issue, "IDENTIFY_VULNERABILITIES")

            self.insert_issue_text(vulnerabilities)
        except Exception as e:
            # Handle any other exceptions that might occur
            print(f"An error occurred: {e}")

        self.status_bar.config(text="Ready")
        self.dialog.destroy()

        return None

    def on_identify_vulnerabilities(self):
        self.status_bar.config(text="Processing...")
        self.show_dialog("Generating Vulnerabilities Check...",
                        "Generating Vuilnerabilities Check, please wait...")

        threading.Thread(target=lambda: asyncio.run(
            self.async_identify_vulnerabilities(self.selected_issue))).start()
        return None

    async def async_execute_action(self, issue, prompt_type="", code_snippets=[]):
        try:
            issue_details = self.checkmarx_agent.details_from_issue(issue)
            prompt = self.prompt_agent.generate_prompt(prompt_type, issue_details)
            patch_content = self.checkmarx_agent.chat_completions(prompt)
            self.insert_issue_text(patch_content, "code_light_blue")

            # Save format patch
            result = self.formatpatch_agent.is_format_patch(patch_content, code_snippets)
            print(result)

            src_file_name = issue_details['SrcFileName']
            self.formatpatch_agent.format_patch(src_file_name, patch_content)

        except Exception as e:
            # Handle any other exceptions that might occur
            print(f"An error occurred: {e}")

        self.status_bar.config(text="Ready")
        self.dialog.destroy()

        return None

    def on_refactor_fix(self):
        self.status_bar.config(text="Processing...")
        self.show_dialog("Generating patch...", "Generating patch, please wait...")

        line = self.checkmarx_agent.issue_details['Line']
        src_file_name = self.checkmarx_agent.issue_details['SrcFileName']

        code_snippets = self.ccode_agent.format_code_snippet(
            snippet_type="WITHOUT_LINE_NUM", encoding="utf-8", file_path=src_file_name, line=line, chunk_size=100)

        threading.Thread(target=lambda: asyncio.run(
            self.async_execute_action(self.selected_issue, "REFRACT_FIX", code_snippets))).start()
        return None

    def on_auto_fix(self):
        self.status_bar.config(text="Processing...")
        self.show_dialog("Generating patch...", "Generating patch, please wait...")

        line = self.checkmarx_agent.issue_details['Line']
        src_file_name = self.checkmarx_agent.issue_details['SrcFileName']

        code_snippets = self.ccode_agent.format_code_snippet(
            snippet_type="WITHOUT_LINE_NUM", encoding="utf-8", file_path=src_file_name, line=line, chunk_size=100)

        threading.Thread(target=lambda: asyncio.run(
            self.async_execute_action(self.selected_issue, "AUTO_FIX", code_snippets))).start()
        return None

    def on_review_patch(self):
        async def fasync():

                line = self.checkmarx_agent.issue_details['Line']
                src_file_name = self.checkmarx_agent.issue_details['SrcFileName']

                code_snippets = self.ccode_agent.format_code_snippet(
                    snippet_type="LINE_NUM", encoding="utf-8", file_path=src_file_name, line=line, chunk_size=100)

                result = self.formatpatch_agent.review_patch(code_snippets)

                self.insert_issue_text(result)

                # fixed_code = self.checkmarx_agent.chat_completions(result)
                # self.insert_issue_text(fixed_code)

                self.status_bar.config(text="Ready")
                self.dialog.destroy()

        # Run the asynchronous function in a background thread
        threading.Thread(target=lambda: asyncio.run(fasync())).start()
        self.show_dialog("Generating result...", "Generating result, please wait...")

        return None

    @workflow(name="selected_issue")
    def on_selected_issue(self, event):
        try:
            curselection = self.issues_listbox.curselection()
            if curselection:
                self.selected_issue = self.issues_listbox.get(curselection)
        except Exception as e:
            # Handle any other exceptions that might occur
            print(f"An error occurred: {e}")
        return None

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Checkmarx files", "*.csv")])
        if not file_path:
            return

        self.formatpatch_agent.set_parameter(
            self.global_config.language,
            self.global_config.url,
            self.global_config.api_key,
            self.global_config.csv_file,
            self.global_config.code_dir)

        self.global_config.csv_file = file_path
        self.checkmarx_agent.set_parameter(
            self.global_config.language,
            self.global_config.url,
            self.global_config.api_key,
            self.global_config.csv_file,
            self.global_config.code_dir
        )
        self.checkmarx_agent.load_checkmarx_data()

        sample_issues = self.checkmarx_agent.checkmarx_data_loader.load_sample_issues()
        # Clear existing items from the listbox
        self.issues_listbox.delete(0, tk.END)
        # Insert sample_issues data into the listbox
        for issues in sample_issues:
            self.issues_listbox.insert(tk.END, issues)

        self.global_config.save_to_disk()

    def run_all(self):
        # 获取当前选中的索引
        try:
            issue_index = self.issues_listbox.curselection()[0]
        except IndexError:
            # 如果没有选中任何项目，直接返回
            return None

        # 获取列表中的所有项目
        issues_count = len(self.issues_listbox.get(0, tk.END))

        # 如果当前索引是最后一个项目，使用 after 方法保持 GUI 响应
        if issue_index >= issues_count - 1:
            self.root.after(100, self.run_all)
            return None

        # 清除所有选中状态
        self.issues_listbox.selection_clear(0, tk.END)
        # 激活下一个项目
        self.issues_listbox.activate(issue_index + 1)
        # 选中下一个项目
        self.issues_listbox.selection_set(issue_index + 1)

        return None

    def show_about(self):
        messagebox.showinfo("About", "Code Corrector v1.0")

    def update_issue_details(self, issue_details):
        formatted_issue = (
            f"Issue Type: {issue_details['Query']}\n"
            f"File Path: {issue_details['SrcFileName']}\n"
            f"Line Number: {issue_details['Line']}\n"
            f"Name: {issue_details['Name']}\n"
            f"Link: {issue_details['Link']}\n"
        )
        print(formatted_issue)
        self.detail_label.config(text=formatted_issue)

    def show_dialog(self, title: str, message: str) -> None:
        """
        Show a custom dialog.

        Parameters:
            title (str): The title of the dialog.
            message (str): The message in the dialog.
        """
        self.dialog = tk.Toplevel(self.root)
        self.dialog.withdraw()
        self.dialog.title(title)

        tk.Label(self.dialog, text=message).pack(padx=20, pady=20)

        # Disable minimize and maximize buttons
        self.dialog.resizable(False, False)
        self.dialog.attributes('-toolwindow', True)
        
        # Update the dialog to get its width and height
        self.dialog.update_idletasks()
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()

        # Get the parent window's position and size
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        # Calculate the position of the dialog box relative to the parent window
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)

        self.dialog.grab_set()  # Make the dialog modal
        # Set the position of the dialog box
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.dialog.deiconify()