import sys
import threading
import tkinter as ui
import common
import traceback
from common.configuration import Configuration
from common.models import Reports, ReportInformation, IssueComponentData
from report.mts_cpss_bugs_report import MtsCpssBugsReport
from report.all_stories_report import AllStoriesReport
from report.mts_projects_report import MtsProjectReport
from common.exceptions import SiteErrorException
from joblib import Parallel, delayed, parallel_backend
from report.versions_report import VersionsReport

# from tkinter import ttk
# from common.preserved_config import PreservedConfig
# from report.all_issues_components_report import AllIssuesComponentReport

WINDOWED = True

config: Configuration
issue_component_data: IssueComponentData = IssueComponentData()  # todo: remove mock mock=True


def download_versions_report():
    all_versions_data = reports.versions_report
    if all_versions_data.url is None:
        all_versions_data.url = common.VERSIONS_REPORT_URL

    try:
        report = VersionsReport(all_versions_data)
        report_data = report.get_report_content().replace("\r\n", "\n")
        with open(all_versions_data.output_file, 'w') as f:
            f.write(report_data)
            print(f"Report generated at: {all_versions_data.output_file}")
    except Exception as e:
        print('Error: {}'.format(e))


def download_all_stories_report():
    # window.clear_log()
    all_stories_data = reports.all_stories_report
    if all_stories_data.url is None:
        all_stories_data.url = common.ALL_STORIES_REPORT_URL

    try:
        report = AllStoriesReport(all_stories_data, tools_url=common.ALL_STORIES_TOOLS_REPORT_URL)
        report_data = report.get_report_content().replace("\r\n", "\n")
        with open(all_stories_data.output_file, 'w') as f:
            f.write(report_data)
            print(f"Report generated at: {all_stories_data.output_file}")
    except Exception as e:
        print('Error: {}'.format(e))


def download_mts_cpss_bugs_report():
    mts_cpss_bugs_report_data: ReportInformation = reports.mts_cpss_bugs_report
    if mts_cpss_bugs_report_data.url is None:
        mts_cpss_bugs_report_data.url = common.CPSS_BUGS_REPORT_URL

    try:
        mts_content = get_mts_bugs_report_content(common.MTS_IGNORE_OPTIONS)
        report = MtsCpssBugsReport(mts_cpss_bugs_report_data)
        report.get_report_content(mts_content=mts_content)
    except Exception as e:
        print('Error: {}'.format(e))


def get_mts_bugs_report_content(ignore=None):
    results = None
    mts_projects_data = reports.mts_projects_report
    if mts_projects_data.url is None:
        mts_projects_data.url = common.MTS_PROJECTS_URL

    if ignore is not None:
        mts_projects_data.ignore_options = ignore

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
            except Exception as ex:
                print(ex)
    except Exception as e:
        print(e)

    return results


def download_mts_projects_report():
    mts_projects_data = reports.mts_projects_report
    if mts_projects_data.url is None:
        mts_projects_data.url = common.MTS_PROJECTS_URL

    results = get_mts_bugs_report_content()
    if results is not None:
        MtsProjectReport.write_report(results, mts_projects_data)


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


def get_section_dict(section_name, default_output, default_url, ignore_optons=None, secondary_url=None):
    projects_list = config.get(section_name, "projects", None)
    if projects_list is not None:
        projects_list = [x.strip() for x in projects_list.split(',')]
    return {
        "name": section_name,
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
        "projects": projects_list,
        "secondary_url": config.get(section_name, "secondary_url", secondary_url)
    }


def get_reports_data():
    global reports, config
    reports = Reports()
    if config:
        config.read_from_cwd("automated_reports.ini")

    reports.versions_report = ReportInformation(
        **get_section_dict(common.VERSIONS_REPORT_NAME, 'C:\\Temp\\versions.csv', common.VERSIONS_REPORT_URL))

    reports.all_stories_report = ReportInformation(
        **get_section_dict(common.ALL_STORIES_REPORT_NAME, 'C:\\Temp\\all_stories.csv', common.ALL_STORIES_REPORT_URL))

    reports.mts_projects_report = ReportInformation(
        **get_section_dict(common.MTS_PROJECTS_REPORT_NAME, 'C:\\Temp\\mts_projects.csv', common.MTS_PROJECTS_URL,
                           common.MTS_IGNORE_OPTIONS)
    )

    reports.mts_cpss_bugs_report = ReportInformation(
        **get_section_dict(common.MTS_CPSS_BUGS_REPORT_NAME, 'C:\\Temp\mts_cpss_bugs.csv', common.CPSS_BUGS_REPORT_URL))

    return reports


class Logger:
    def __init__(self, text_widget):
        self.terminal = sys.stdout
        self.text_box = text_widget

    def write(self, message):
        self.terminal.write(message)
        self.text_box.insert(ui.END, str(message))
        self.text_box.see(ui.END)

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
        self.mts_cpss_bugs_report_button = None
        self.components_frame = None
        self.download_issues_components_button = None
        self.init_view()

    def init_view(self):
        self.ui = ui
        self.app = ui.Tk()
        self.app.title(common.APP_NAME)
        self.app.geometry('500x400')

        actions_frame = ui.Frame(self.app)

        self.versions_button = ui.Button(actions_frame, text="Versions", command=self.get_versions)
        self.versions_button.grid(row=0, column=0, padx=20, pady=3)

        self.mts_projects_button = ui.Button(actions_frame, text="MTS Bugs", command=self.get_mts_projects)
        self.mts_projects_button.grid(row=0, column=1, padx=20, pady=3)

        self.all_stories_button = ui.Button(actions_frame, text="All Stories", command=self.get_all_stories)
        self.all_stories_button.grid(row=1, column=0, padx=20, pady=3)

        self.mts_cpss_bugs_report_button = ui.Button(actions_frame, text="MTS & CPSS Bugs",
                                                     command=self.get_mts_cpss_bugs)
        self.mts_cpss_bugs_report_button.grid(row=1, column=1, padx=20, pady=3)
        # self.report2_button.config(state="disabled")

        actions_frame.pack()

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

    def get_mts_cpss_bugs(self):
        threading.Thread(target=self.get_mts_cpss_bugs_thread).start()

    def get_mts_cpss_bugs_thread(self):
        self.set_buttons_state(enabled=False)
        try:
            download_mts_cpss_bugs_report()
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
        self.mts_cpss_bugs_report_button.config(state=state)


if __name__ == "__main__":
    config = Configuration()
    window = WindowView()
    reports = get_reports_data()
    window.set_config_text("Config: {}".format(config.config_path))
    # download_versions_report(reports.versions_report)

    window.app.mainloop()
