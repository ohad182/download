# from download.Downloader import Downloader
import sys
import os
import threading
import tkinter as ui
import common
import json
import traceback
from common.configuration import Configuration
from common.models import Reports, ReportInformation
from report.all_issues_components_report import AllIssuesComponentReport
from report.all_stories_report import AllStoriesReport
from report.mts_projects_report import MtsProjectReport
from common.exceptions import SiteErrorException
from joblib import Parallel, delayed, parallel_backend

from report.versions_report import VersionsReport

WINDOWED = True

VERSIONS_REPORT = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/Versions%20Data.rdl&Source=http%3A%2F%2Fwebilsites%2Emarvell%2Ecom%2Fsites%2FMISLSites%2FFHILL%2FIT%2FIA%2FJIRA%2FPublicDocuments%2FForms%2FAllItems%2Easpx%3FRootFolder%3D%252fsites%252fMISLSites%252fFHILL%252fIT%252fIA%252fJIRA%252fPublicDocuments%252fReports%26FolderCTID%3D0x012000F0871E736C14AF4781864003DD2CBE29%23InplviewHash91b5b264%2D49d9%2D4948%2D94c9%2Db30bec91f7f8%3DTreeField%253DFolders%2DTreeValue%253DReports%2DProcessQStringToCAML%253D1%2DPaged%253DTRUE%2Dp%5FSortBehavior%253D0%2Dp%5FFileLeafRef%253DErratum%25255fHierarchy%25252erdl%2Dp%5FID%253D121%2DRootFolder%253D%25252fsites%25252fMISLSites%25252fFHILL%25252fIT%25252fIA%25252fJIRA%25252fPublicDocuments%25252fReports%2DPageFirstRow%253D31'
ALL_STORIES_REPORT = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/All%20Stories%20by%20Rank%20with%20sub%20tasks.rdl'

ALL_ISSUES_COMPONENTS = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/All_Issues_of_a_Project_with%20components.rdl'
MTS_PROJECTS = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/NPS%20All%20Bugs%20for%20project.rdl&Source=http%3A%2F%2Fwebilsites%2Emarvell%2Ecom%2Fsites%2FMISLSites%2FFHILL%2FIT%2FIA%2FJIRA%2FPublicDocuments%2FForms%2FAllItems%2Easpx%3FRootFolder%3D%252fsites%252fMISLSites%252fFHILL%252fIT%252fIA%252fJIRA%252fPublicDocuments%252fReports%26FolderCTID%3D0x012000F0871E736C14AF4781864003DD2CBE29%23InplviewHash91b5b264%2D49d9%2D4948%2D94c9%2Db30bec91f7f8%3DTreeField%253DFolders%2DTreeValue%253DReports%2DProcessQStringToCAML%253D1%2DPaged%253DTRUE%2Dp%5FSortBehavior%253D0%2Dp%5FFileLeafRef%253DErrata%252520with%252520same%252520JIRA%252520id%25252erdl%2Dp%5FID%253D96%2DRootFolder%253D%25252fsites%25252fMISLSites%25252fFHILL%25252fIT%25252fIA%25252fJIRA%25252fPublicDocuments%25252fReports%2DPageFirstRow%253D31'

config: Configuration


def download_versions_report():
    all_versions_data = reports.versions_report
    if all_versions_data.url is None:
        all_versions_data.url = VERSIONS_REPORT

    try:
        report = VersionsReport(all_versions_data)
        report_data = report.get_report_content().replace("\r\n", "\n")
        with open(all_versions_data.output_file, 'w') as f:
            f.write(report_data)
    except SiteErrorException as e:
        print('site error: {}'.format(e))


def download_all_stories_report():
    # window.clear_log()
    all_stories_data = reports.all_stories_report
    if all_stories_data.url is None:
        all_stories_data.url = ALL_STORIES_REPORT

    try:
        report = AllStoriesReport(all_stories_data)
        report_data = report.get_report_content().replace("\r\n", "\n")
        with open(all_stories_data.output_file, 'w') as f:
            f.write(report_data)
    except SiteErrorException as e:
        print('site error: {}'.format(e))


def download_mts_projects_report():
    mts_projects_data = reports.mts_projects_report
    if mts_projects_data.url is None:
        mts_projects_data.url = MTS_PROJECTS

    report = MtsProjectReport(mts_projects_data)
    required_options = []
    try:
        report.open_url(verbose=False)
        all_options = report.get_select_options(mts_projects_data.select_category_id)
        ignore = [] if mts_projects_data.ignore_options is None else mts_projects_data.ignore_options
        required_options = [x for x in all_options if x.strip() not in ignore]
        print(
            "Found {}/{} projects to retrieve\nClosing all drivers to reduce memory usage".format(len(required_options),
                                                                                                  len(all_options)))
    except SiteErrorException as e:
        print('site error: {}'.format(e))
    finally:
        report.close()

    try:
        lock = threading.Lock()
        with parallel_backend('threading', n_jobs=-1):
            try:
                results = Parallel()(
                    delayed(download_mts_task)(mts_projects_data, option, lock) for option in required_options)
                print("All tasks completed")
                MtsProjectReport.write_report(results, mts_projects_data)
            except Exception as ex:
                print(ex)
    except Exception as e:
        print(e)


def download_mts_task(mts_projects_data: ReportInformation, option_select, lock=None):
    result = {"option": option_select, "data": ""}
    try:
        report = MtsProjectReport(mts_projects_data, lock)
        data = report.get_report_content(option=option_select)
        result["data"] = data
    except Exception as e:
        print(e)
        print(traceback.print_exc())
    return result


def download_all_issues_components_report():
    all_issues_components_data = reports.all_issues_components_report
    if all_issues_components_data.url is None:
        all_issues_components_data.url = ALL_ISSUES_COMPONENTS

    report = AllIssuesComponentReport(all_issues_components_data)
    required_options = []


def get_section_dict(section_name, default_output, default_url, ignore_optons=None):
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
        "ignore_options": config.get(section_name, "ignore_options", ignore_optons)
    }


def get_reports_data():
    global reports, config
    reports = Reports()
    if config:
        config.readcwd()

    reports.versions_report = ReportInformation(
        **get_section_dict('Versions', 'C:\\Temp\\versions.csv', VERSIONS_REPORT))

    reports.all_stories_report = ReportInformation(
        **get_section_dict('AllStories', 'C:\\Temp\\all_stories.csv', ALL_STORIES_REPORT))

    reports.all_issues_components_report = ReportInformation(
        **get_section_dict("AllIssuesComponents", 'C:\\Temp\\all_issues_components.csv', ALL_ISSUES_COMPONENTS)
    )

    reports.mts_projects_report = ReportInformation(
        **get_section_dict("MtsProjects", 'C:\\Temp\\mts_projects.csv', MTS_PROJECTS, common.MTS_IGNORE_OPTIONS)
    )

    return reports


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
        self.all_stories_button = None
        self.versions_button = None
        self.mts_projects_button = None
        self.report2_button = None
        self.components_frame = None
        self.init_view()

    def init_view(self):
        self.ui = ui
        self.app = ui.Tk()
        self.app.title(common.APP_NAME)
        self.app.geometry('500x200')

        actions_frame = ui.Frame(self.app)

        self.versions_button = ui.Button(actions_frame, text="Versions", command=self.get_versions)
        # self.versions_button.pack()
        self.versions_button.grid(row=0, column=0, padx=20, pady=3)

        self.mts_projects_button = ui.Button(actions_frame, text="MTS Projects", command=self.get_mts_projects)
        self.mts_projects_button.grid(row=0, column=1, padx=20, pady=3)
        # self.mts_projects_button.config(state="disabled")

        self.all_stories_button = ui.Button(actions_frame, text="All Stories", command=self.get_all_stories)
        self.all_stories_button.grid(row=1, column=0, padx=20, pady=3)

        self.report2_button = ui.Button(actions_frame, text="report2", command=self.get_versions)
        self.report2_button.grid(row=1, column=1, padx=20, pady=3)
        self.report2_button.config(state="disabled")

        actions_frame.pack()

        # self.build_components_frame()

        log_frame = ui.Frame(self.app)
        log_frame.pack(anchor=ui.N, fill=ui.Y, expand=True)

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
        self.components_table = ui.Frame(self.app, borderwidth=4, relief='ridge')
        self.components_table.pack(fill='both', expand=True)

        headers_frm = ui.Frame(self.components_table)
        headers_frm.pack(fill='both')

        header1 = ui.Label(headers_frm, text="Project")
        header1.pack(side=ui.LEFT, padx=3, pady=4, fill=ui.X, expand=True)
        header2 = ui.Label(headers_frm, text="Version")
        header2.pack(side=ui.LEFT, padx=3, pady=4, fill=ui.X, expand=True)
        add_button = ui.Button(headers_frm, text="Add", command=self.add_component_row)
        add_button.pack(side=ui.LEFT, padx=3, pady=4)

        self.components_frame = ui.Frame(self.components_table)
        self.components_frame.pack(anchor=ui.N, fill=ui.X, expand=True, side=ui.TOP)

    def populate_components_list(self, components_list):
        if components_list is not None and len(components_list) > 0:
            row = 0
            self.components_table.pack(anchor=ui.N, fill=ui.X, expand=True, side=ui.TOP)
            for item in components_list:  # Rows
                self.components_frame.grid_columnconfigure(0, weight=1, uniform="group%s" % row)
                self.components_frame.grid_columnconfigure(1, weight=1, uniform="group%s" % row)
                self.components_frame.grid_rowconfigure(row)

                key_entry_text = ui.StringVar()
                key_entry_text.set(item.path_in_set)
                b0 = ui.Entry(self.components_frame, textvariable=key_entry_text)
                b0.config(state=ui.DISABLED)
                b0.grid(row=row, column=0, sticky='news', padx=3)

                value_entry_text = ui.StringVar()
                value_entry_text.set(item.path_in_fs)
                b1 = ui.Entry(self.components_frame, textvariable=value_entry_text)
                b1.grid(row=row, column=1, sticky='news', padx=3)

                row += 1
        else:
            self.components_frame.pack_forget()

    def add_component_row(self):
        print("add component row")

    def remove_component_row(self):
        print("remove component row")

    def get_mts_projects(self):
        threading.Thread(target=self.get_mts_projects_task).start()

    def get_mts_projects_task(self):
        self.set_buttons_state(enabled=False)
        try:
            download_mts_projects_report()
        except Exception as e:
            print(str(e))
        finally:
            self.set_buttons_state(enabled=True)

    def get_all_stories(self):
        threading.Thread(target=self.get_all_stories_thread).start()

    def get_all_stories_thread(self):
        self.set_buttons_state(enabled=False)
        try:
            download_all_stories_report()
        except Exception as e:
            print(str(e))
        finally:
            self.set_buttons_state(enabled=True)

    def get_versions(self):
        threading.Thread(target=self.get_versions_thread).start()

    def get_versions_thread(self):
        self.set_buttons_state(enabled=False)
        try:
            download_versions_report()
        except Exception as e:
            print(str(e))
        finally:
            self.set_buttons_state(enabled=True)

    def clear_log(self):
        self.log_panel.delete('1.0', self.ui.END)

    def set_config_text(self, text):
        self.config_string_var.set(text)

    def set_buttons_state(self, enabled=True):
        state = "normal" if enabled else "disabled"
        self.versions_button.config(state=state)
        self.all_stories_button.config(state=state)
        self.mts_projects_button.config(state=state)


if __name__ == "__main__":
    window = WindowView()
    config = Configuration()
    reports = get_reports_data()
    window.set_config_text("Config: {}".format(config.config_path))
    # download_versions_report(reports.versions_report)
    # window.populate_components_list([])
    window.app.mainloop()
