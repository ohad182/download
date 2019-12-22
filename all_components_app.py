import sys
import threading
import tkinter as ui
from tkinter import ttk
import common
import traceback
from common.configuration import Configuration
from common.models import Reports, ReportInformation, IssueComponentData, IssueComponentSelection
from common.preserved_config import PreservedConfig
from report.all_issues_components_report import AllIssuesComponentReport
from report.all_stories_report import AllStoriesReport
from report.mts_projects_report import MtsProjectReport
from common.exceptions import SiteErrorException
from joblib import Parallel, delayed, parallel_backend

from report.versions_report import VersionsReport

WINDOWED = True

config: Configuration
issue_component_data: IssueComponentData = IssueComponentData()  # todo: remove mock mock=True


def get_all_issues_components_report_obj() -> AllIssuesComponentReport:
    all_issues_components_data = reports.all_issues_components_report
    if all_issues_components_data.url is None:
        all_issues_components_data.url = common.ALL_COMPONENTS_REPORT_URL

    report = AllIssuesComponentReport(all_issues_components_data)
    return report


def download_all_issues_components_report():
    global issue_component_data
    all_issues_components_data = reports.all_issues_components_report
    if all_issues_components_data.url is None:
        all_issues_components_data.url = common.ALL_COMPONENTS_REPORT_URL

    report = get_all_issues_components_report_obj()
    report.get_report_content(issue_component_data)


def update_issues_components_projects_map(projects_list):
    global issue_component_data
    report = get_all_issues_components_report_obj()
    issue_component_data.projects_map = report.get_options_map(projects_list)


def get_section_dict(section_name, default_output, default_url, ignore_optons=None):
    projects_list = config.get(section_name, "projects", None)
    if projects_list is not None:
        projects_list = [x.strip() for x in projects_list.split(',')]
    return {
        "output_file": config.get(section_name, "output_file", default_output),
        "category": config.get(section_name, "category", "MTS"),
        "report_type": config.get(section_name, "report_type", "csv"),
        "url": config.get(section_name, "url", default_url),
        "apply_id": config.get(section_name, "apply_id", common.APPLY_ID),
        "loader_id": config.get(section_name, "loader_id", common.LOADER_ID),
        "select_category_id": config.get(section_name, "select_category_id", common.SELECT_CATEGORY_ID),
        "main_menu_id": config.get(section_name, "main_menu_id", common.MAIN_MENU_ID),
        "export_menu_id": config.get(section_name, "export_menu_id", common.EXPORT_MENU_ID),
        "export_type_id_prefix": config.get(section_name, "export_type_id_prefix", common.EXPORT_TYPE_ID_PREFIX),
        "ignore_options": config.get(section_name, "ignore_options", ignore_optons),
        "projects": projects_list
    }


def get_reports_data():
    global reports, config
    reports = Reports()
    if config:
        config.read_from_cwd("all_components.ini")

    reports.all_issues_components_report = ReportInformation(
        **get_section_dict(common.ALL_COMPONENTS_REPORT_NAME, 'C:\\Temp\\all_issues_components.csv',
                           common.ALL_COMPONENTS_REPORT_URL)
    )
    reports.all_issues_components_report.version_dropdown_id = common.VERSION_DROPDOWN_ID

    if reports.all_issues_components_report.projects is None:
        # got nothing from config, set defaults
        reports.all_issues_components_report.projects = common.DEFAULT_ALL_COMPONENTS_PROJECTS

    return reports


def load_app_config():
    config_section = PreservedConfig().get(common.ALL_COMPONENTS_REPORT_NAME)
    if config_section is not None:
        AllIssuesComponentReport.site_projects = config_section.get("site_projects", [])
        selections = config_section.get("selections", None)
        config_project_map = config_section.get("project_map", {})
        if selections is not None:
            for selection in selections:
                issue_component_data.selections.append(IssueComponentSelection(**selection))
                if selection['project'] not in config_project_map:
                    config_project_map[selection['project']] = []
                if selection['version'] not in config_project_map[selection['project']]:
                    config_project_map[selection['project']].append(selection['version'])
        issue_component_data.projects_map = config_project_map


class Logger:
    def __init__(self, text_widget):
        self.terminal = sys.stdout
        self.text_box = text_widget

    def write(self, message):
        self.terminal.write(message)
        self.text_box.insert(ui.END, str(message))
        self.text_box.see(ui.END)
        # self.log.write(message)

    def __getattr__(self, attr):
        return getattr(self.terminal, attr)


class WindowView(object):
    def __init__(self):
        self.ui = None
        self.log_panel = None
        self.config_string_var = None
        self.app = None
        self.components_frame = None
        self.download_issues_components_button = None
        self.init_view()

    def init_view(self):
        self.ui = ui
        self.app = ui.Tk()
        self.app.title(common.APP_NAME)
        self.app.geometry('500x400')

        self.build_components_frame()

        log_frame = ui.Frame(self.app)
        log_frame.pack(anchor=ui.N, fill="both", expand=True)

        text_scroll = ui.Scrollbar(log_frame)
        self.log_panel = ui.Text(log_frame, height=7)
        text_scroll.config(command=self.log_panel.yview)
        self.log_panel.config(yscrollcommand=text_scroll.set)
        text_scroll.pack(side=ui.RIGHT, fill=ui.Y)
        self.log_panel.pack(side=ui.LEFT, fill=ui.BOTH, expand=True)

        logger = Logger(self.log_panel)
        sys.stdout = logger
        sys.stderr = logger

        self.config_string_var = ui.StringVar()
        config_label = ui.Label(self.app, textvariable=self.config_string_var)
        config_label.pack()

    def build_components_frame(self):
        components_table = ui.Frame(self.app, borderwidth=4, relief='ridge')
        components_table.pack(fill='x')

        label = ui.Label(components_table, text="Issues Components Report")
        label.pack(padx=4, pady=4)

        headers_frm = ui.Frame(components_table)
        headers_frm.pack(fill='both')

        refresh_button = ui.Button(headers_frm, text="Refresh", command=self.refresh_components_list)
        refresh_button.pack(side=ui.LEFT, padx=3, pady=4)
        header1 = ui.Label(headers_frm, text="Project")
        header1.pack(side=ui.LEFT, padx=3, pady=4, fill=ui.X, expand=True)
        header2 = ui.Label(headers_frm, text="Version")
        header2.pack(side=ui.LEFT, padx=3, pady=4, fill=ui.X, expand=True)
        add_button = ui.Button(headers_frm, text="Add", command=self.add_component_row)
        add_button.pack(side=ui.LEFT, padx=3, pady=4)

        self.components_frame = ui.Frame(components_table)
        self.components_frame.pack(anchor=ui.N, fill=ui.X, expand=True, side=ui.TOP)

        download_issues_components_frame = ui.Frame(components_table)
        download_issues_components_frame.pack(fill='both')

        self.download_issues_components_button = ui.Button(download_issues_components_frame, text="Download",
                                                           command=lambda: threading.Thread(
                                                               target=self.download_issues_components).start())
        self.download_issues_components_button.pack(padx=3, pady=4)
        self.download_issues_components_button.config(state="disabled")

        if len(issue_component_data.projects_map) > 0:
            self.populate_components_list()

    def populate_components_list(self):
        global issue_component_data
        if issue_component_data.selections is not None and len(issue_component_data.selections) > 0:
            row = 0
            for item in issue_component_data.selections:  # Rows
                self.add_component_row(row, item)
                row = row + 1

    def refresh_components_list(self):
        self.remove_all_rows()
        update_issues_components_projects_map(reports.all_issues_components_report.projects)
        self.populate_components_list()

    def add_component_row(self, row=None, selection: IssueComponentSelection = None):
        global issue_component_data
        if selection is None:
            selection = IssueComponentSelection()
            issue_component_data.selections.append(selection)
        if row is None:
            row = int(len(issue_component_data.ui_components) / 3)

        self.components_frame.grid_columnconfigure(0, weight=1, uniform="group%s" % row)
        self.components_frame.grid_columnconfigure(1, weight=1, uniform="group%s" % row)
        self.components_frame.grid_rowconfigure(row)

        project_combo = ttk.Combobox(self.components_frame, values=issue_component_data.get_projects())
        if selection.project is not None:
            project_combo.current(issue_component_data.get_projects().index(selection.project))
        issue_component_data.register_ui(project_combo, row, 0)
        project_combo.bind("<<ComboboxSelected>>", issue_component_data.project_selection_changed)
        project_combo.grid(row=row, column=0, sticky='news', padx=3)

        versions_list = [] if selection.version is None else issue_component_data.get_versions(selection.project)
        version_combo = ttk.Combobox(self.components_frame,
                                     values=versions_list)
        if selection.version is not None:
            version_combo.current(issue_component_data.projects_map[selection.project].index(selection.version))
        issue_component_data.register_ui(version_combo, row, 1)
        version_combo.bind("<<ComboboxSelected>>", issue_component_data.version_selection_changed)
        version_combo.grid(row=row, column=1, sticky='news', padx=3)

        remove_button = ui.Button(self.components_frame, text="Remove",
                                  command=lambda arg1=row: self.remove_component_row(remove_button))
        remove_button.grid(row=row, column=2, sticky='news', padx=3)
        issue_component_data.register_ui(remove_button, row, 2)
        self.download_issues_components_button.config(state="normal")

    def remove_all_rows(self):
        global issue_component_data
        for idx, selection in enumerate(issue_component_data.selections):
            # send remove button from this row index
            remove_btn = issue_component_data.get_remove_btn(idx)
            self.remove_component_row(remove_btn, idx)

    def remove_component_row(self, btn, row=-1):
        global issue_component_data
        row = issue_component_data.unregister_ui(btn)
        self.components_frame.grid_rowconfigure(row)
        if len(issue_component_data.selections) == 0:
            self.download_issues_components_button.config(state="disabled")

    def download_issues_components(self):
        self._change_frame_state(self.components_frame, "disabled")
        global issue_component_data
        print("Download issues components {}".format(issue_component_data.selections))
        download_all_issues_components_report()
        self._change_frame_state(self.components_frame, "normal")

    def _change_frame_state(self, frame, state):
        for child in frame.winfo_children():
            child.configure(state=state)

    def clear_log(self):
        self.log_panel.delete('1.0', self.ui.END)

    def set_config_text(self, text):
        self.config_string_var.set(text)


if __name__ == "__main__":
    config = Configuration()
    PreservedConfig()
    window = WindowView()
    load_app_config()
    window.populate_components_list()
    reports = get_reports_data()
    window.set_config_text("Config: {}".format(config.config_path))
    # download_versions_report(reports.versions_report)

    window.app.mainloop()
