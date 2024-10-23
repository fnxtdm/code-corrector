import os
import asyncio
import threading
import concurrent.futures
import tkinter as tk
import tkinter.font as tkFont

from tkinter import ttk, filedialog, messagebox
from src.c_expert_agent import CExpertAgent
from src.properties_dialog import PropertiesDialog

class CCViewerApp:
    def __init__(self, root, global_config, checkmarx_agent, formatpatch_agent):
        self.root = root
        self.global_config = global_config
        self.checkmarx_agent = checkmarx_agent
        self.formatpatch_agent = formatpatch_agent

        self.dialog = None
        # Initialize the current selection variable
        self.current_selection = None
        self.c = CExpertAgent(global_config.code_dir)

        self.root.title("Code Corrector")
        
        # Set window size to 1024x768
        self.root.geometry("1024x768")
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

        # Create a menu bar
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        # Define the desired font properties
        font_style = tkFont.Font(family="Segoe UI", size=12, weight="normal")
        font_style_bold = tkFont.Font(family="Segoe UI", size=12, weight="bold")

        # Create File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_file)
        # self.file_menu.add_command(label="Save", command=self.save_file)
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

        self.search_label = ttk.Label(self.search_frame, text="SEARCH ISSUES: ", font=font_style_bold)
        # Align the label to the left
        self.search_label.pack(side=tk.LEFT, anchor='w')

        # Set width to twice the default size
        # self.search_entry = ttk.Entry(self.search_frame, width=23)
        # Align the entry to the left
        # self.search_entry.pack(side=tk.LEFT, anchor='w')

        # File listbox
        self.issues_listbox = tk.Listbox(self.listbox_frame, width=45, height=40)
        self.issues_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.issues_listbox.bind('<<ListboxSelect>>', self.on_issues_select)

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
        self.description_label = ttk.Label(root, text="Description:", font=font_style_bold)
        # Align the label to the left and adjust pady to 55
        self.description_label.pack(padx=10, pady=5, anchor='w')

        self.detail_label = ttk.Label(root, text="\n\n\n\n\n")
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

        refactor_fix_button = ttk.Button(
            button_frame,
            text="Refactor",
            command=self.on_refactor_fix
        )
        refactor_fix_button.pack(side=tk.LEFT, padx=5, pady=5)

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

        # Content display area
        self.issues_text = tk.Text(root, wrap=tk.WORD, width=150, height=40)
        self.issues_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # Configure the background color to black
        # self.issues_text.config(bg="black", fg="white")

        global sample_content
        sample_content = (
            "Please select an issue from the list to view AI generated corrections patches."
        )
        # Add content
        self.issues_text.insert(tk.END, sample_content)
        # self.issues_text.configure(font=font_style)

    def open_properties_dialog(self):
        PropertiesDialog(self.root, self.global_config)

    def on_identify_vulnerabilities(self):
        try:
            self.status_bar.config(text="Processing...")

            # Display selected item in content area
            query_item = self.current_selection_issue.get("Query")
            src_file_name = self.current_selection_issue.get("SrcFileName")
            line = self.current_selection_issue.get("Line")
            dest_line = self.current_selection_issue.get("DestLine")
            name = self.current_selection_issue.get("Name")
            result_status = self.current_selection_issue.get("Result Status")

            async def fasync():
                vulnerabilities = self.checkmarx_agent.identify_vulnerabilities(
                    query_item=query_item,
                    src_file_name=src_file_name,
                    line=line,
                    dest_line=dest_line,
                    name=name,
                    result_status=result_status)

                # self.issues_text.delete("1.0", tk.END)
                self.issues_text.insert(tk.END, "\n\n" + vulnerabilities)
                self.issues_text.see(tk.END)
                self.status_bar.config(text="Ready")
                self.dialog.destroy()

            # Run the asynchronous function in a background thread
            threading.Thread(target=lambda: asyncio.run(fasync())).start()
            self.show_dialog("Generating Vulnerabilities Check...", "Generating Vuilnerabilities Check, please wait...")
        except Exception as e:
            # Handle any other exceptions that might occur
            return None

    def on_refactor_fix(self):
        try:
            self.status_bar.config(text="Processing...")

            # Display selected item in content area
            query_item = self.current_selection_issue.get("Query")
            src_file_name = self.current_selection_issue.get("SrcFileName")
            line = self.current_selection_issue.get("Line")
            dest_line = self.current_selection_issue.get("DestLine")
            name = self.current_selection_issue.get("Name")
            result_status = self.current_selection_issue.get("Result Status")

            async def fasync():
                fixed_code = self.checkmarx_agent.refactor_fix(
                    query_item=query_item,
                    src_file_name=src_file_name,
                    line=line,
                    dest_line=dest_line,
                    name=name,
                    result_status=result_status)
                
                # self.issues_text.delete("1.0", tk.END)
                self.issues_text.insert(tk.END, "\n\n" + fixed_code)
                self.issues_text.see(tk.END)

                self.formatpatch_agent.format_patch(src_file_name, fixed_code)

                self.status_bar.config(text="Ready")
                self.dialog.destroy()

            # Run the asynchronous function in a background thread
            threading.Thread(target=lambda: asyncio.run(fasync())).start()
            self.show_dialog("Generating patch...", "Generating patch, please wait...")
        except Exception as e:
            # Handle any other exceptions that might occur
            return None
    def on_auto_fix(self):
        try:
            self.status_bar.config(text="Processing...")

            # Display selected item in content area
            query_item = self.current_selection_issue.get("Query")
            src_file_name = self.current_selection_issue.get("SrcFileName")
            line = self.current_selection_issue.get("Line")
            dest_line = self.current_selection_issue.get("DestLine")
            name = self.current_selection_issue.get("Name")
            result_status = self.current_selection_issue.get("Result Status")

            async def fasync():
                fixed_code = self.checkmarx_agent.auto_fix(
                    query_item=query_item,
                    src_file_name=src_file_name,
                    line=line,
                    dest_line=dest_line,
                    name=name,
                    result_status=result_status)
                
                # self.issues_text.delete("1.0", tk.END)
                self.issues_text.insert(tk.END, "\n\n" + fixed_code)
                self.issues_text.see(tk.END)

                self.formatpatch_agent.format_patch(src_file_name, fixed_code)

                self.status_bar.config(text="Ready")
                self.dialog.destroy()

            # Run the asynchronous function in a background thread
            threading.Thread(target=lambda: asyncio.run(fasync())).start()
            self.show_dialog("Generating patch...", "Generating patch, please wait...")
        except Exception as e:
            # Handle any other exceptions that might occur
            return None

    def on_review_patch(self):
        async def fasync():
                result = self.formatpatch_agent.review_patch()
                
                # self.issues_text.delete("1.0", tk.END)
                self.issues_text.insert(tk.END, "\n\n" + result)
                self.issues_text.see(tk.END)

                fixed_code = self.checkmarx_agent.generate_response(result)
                self.issues_text.insert(tk.END, "\n\n" + fixed_code)
                self.issues_text.see(tk.END)

                self.status_bar.config(text="Ready")
                self.dialog.destroy()

        # Run the asynchronous function in a background thread
        threading.Thread(target=lambda: asyncio.run(fasync())).start()
        self.show_dialog("Generating result...", "Generating result, please wait...")

        return None

    def on_issues_select(self, event):
        seek = 0
        selected_issue = None

        try:
            selection = self.issues_listbox.curselection()
            selected_issue = self.issues_listbox.get(selection)
            self.status_bar.config(text="Processing...")

            raw_data = self.checkmarx_agent.checkmarx_data_loader.select_item_by_sample_issue(selected_issue)
            self.current_selection_issue = raw_data
            print(raw_data)

            # Change the value of self.detail_label to display multiple lines
            formatted_issue = self.format_issue_text(raw_data)
            self.detail_label.config(text=formatted_issue)

            # Display selected item in content area
            query_item = raw_data.get("Query")
            src_file_name = raw_data.get("SrcFileName")
            line = raw_data.get("Line")
            dest_line = raw_data.get("DestLine")
            name = raw_data.get("Name")
            result_status = raw_data.get("Result Status")

            src_file_path = os.path.join(self.global_config.code_dir, src_file_name)
            if os.path.getsize(src_file_path) > 10 * 1024:
                seek = max(0, line - 300)

            self.issues_text.delete("1.0", tk.END)
            # self.issues_text.insert(tk.END, src_file_name+"\n")

            async def auto_fix_code_async():
                self.checkmarx_agent.clean_history()
                def on_upload_complete(result):
                    self.issues_text.insert(tk.END, result)
                    self.issues_text.see(tk.END)

                response = self.checkmarx_agent.report_vulnerabilities(query_item, src_file_name, line, dest_line, name, result_status)

                self.checkmarx_agent.upload_file(src_file_path, seek, on_upload_complete)

                self.status_bar.config(text="Ready")
                self.dialog.destroy()

            # Run the asynchronous function in a background thread
            threading.Thread(target=lambda: asyncio.run(auto_fix_code_async())).start()
            self.show_dialog("Uploading ...", "Uploading code, please wait...")
        except Exception as e:
            # Handle any other exceptions that might occur
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

    def show_about(self):
        messagebox.showinfo("About", "Code Corrector v1.0")

    def format_issue_text(self, issue):
        formatted_issue = (
            f"Issue Type: {issue['Query']}\n"
            f"File Path: {issue['SrcFileName']}\n"
            f"Line Number: {issue['Line']}\n"
            f"Name: {issue['Name']}\n"
            f"Link: {issue['Link']}\n"
        )
        print(formatted_issue)
        return formatted_issue

    def show_dialog(self, title: str, message: str) -> None:
        """
        Show a custom dialog.

        Parameters:
            title (str): The title of the dialog.
            message (str): The message in the dialog.
        """
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title(title)
        tk.Label(self.dialog, text=message).pack(padx=20, pady=20)

        # Disable minimize and maximize buttons
        self.dialog.resizable(False, False)
        self.dialog.attributes('-toolwindow', True)
        
        # Update the dialog to get its width and height
        self.dialog.update_idletasks()
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()

        # Get the screen width and height
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()

        # Calculate the position of the dialog box
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)

        # Set the position of the dialog box
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")