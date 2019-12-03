# from download.Downloader import Downloader
import sys
import threading
import tkinter as ui
import common
from common.configuration import Configuration
from common.models import Reports, ReportInformation
from report.report import Report
from common.exceptions import SiteErrorException
from queue import Queue

WINDOWED = True

VERSIONS_REPORT = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/Versions%20Data.rdl&Source=http%3A%2F%2Fwebilsites%2Emarvell%2Ecom%2Fsites%2FMISLSites%2FFHILL%2FIT%2FIA%2FJIRA%2FPublicDocuments%2FForms%2FAllItems%2Easpx%3FRootFolder%3D%252fsites%252fMISLSites%252fFHILL%252fIT%252fIA%252fJIRA%252fPublicDocuments%252fReports%26FolderCTID%3D0x012000F0871E736C14AF4781864003DD2CBE29%23InplviewHash91b5b264%2D49d9%2D4948%2D94c9%2Db30bec91f7f8%3DTreeField%253DFolders%2DTreeValue%253DReports%2DProcessQStringToCAML%253D1%2DPaged%253DTRUE%2Dp%5FSortBehavior%253D0%2Dp%5FFileLeafRef%253DErratum%25255fHierarchy%25252erdl%2Dp%5FID%253D121%2DRootFolder%253D%25252fsites%25252fMISLSites%25252fFHILL%25252fIT%25252fIA%25252fJIRA%25252fPublicDocuments%25252fReports%2DPageFirstRow%253D31'
ALL_STORIES_REPORT = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/All%20Stories%20by%20Rank%20with%20sub%20tasks.rdl'

ALL_ISSUES_COMPONENTS = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/All_Issues_of_a_Project_with%20components.rdl'
MTS_PROJECTS = 'http://webilsites.marvell.com/sites/MISLSites/FHILL/IT/IA/JIRA/_layouts/15/ReportServer/RSViewerPage.aspx?rv:RelativeReportUrl=/sites/MISLSites/FHILL/IT/IA/JIRA/PublicDocuments/Reports/NPS%20All%20Bugs%20for%20project.rdl&Source=http%3A%2F%2Fwebilsites%2Emarvell%2Ecom%2Fsites%2FMISLSites%2FFHILL%2FIT%2FIA%2FJIRA%2FPublicDocuments%2FForms%2FAllItems%2Easpx%3FRootFolder%3D%252fsites%252fMISLSites%252fFHILL%252fIT%252fIA%252fJIRA%252fPublicDocuments%252fReports%26FolderCTID%3D0x012000F0871E736C14AF4781864003DD2CBE29%23InplviewHash91b5b264%2D49d9%2D4948%2D94c9%2Db30bec91f7f8%3DTreeField%253DFolders%2DTreeValue%253DReports%2DProcessQStringToCAML%253D1%2DPaged%253DTRUE%2Dp%5FSortBehavior%253D0%2Dp%5FFileLeafRef%253DErrata%252520with%252520same%252520JIRA%252520id%25252erdl%2Dp%5FID%253D96%2DRootFolder%253D%25252fsites%25252fMISLSites%25252fFHILL%25252fIT%25252fIA%25252fJIRA%25252fPublicDocuments%25252fReports%2DPageFirstRow%253D31'


def download_versions_report(versions_report, report=None):
    # window.clear_log()
    if versions_report.url is None:
        versions_report.url = VERSIONS_REPORT

    if report is None:
        report = Report(versions_report)
    report.connect()

    try:
        versions_report.print_getting()
        report.select_project_category(versions_report.category)
        report.press_apply()
        report.download(versions_report.report_type)
    except SiteErrorException as e:
        print('site error: {}'.format(e))
    finally:
        report.close()


def download_all_stories_report(all_stories_data, report=None):
    # window.clear_log()
    if all_stories_data.url is None:
        all_stories_data.url = ALL_STORIES_REPORT
    if report is None:
        report = Report(all_stories_data)
    report.connect()

    try:
        all_stories_data.print_getting()
        report.select_project_category(all_stories_data.category)
        report.press_apply()
        report.download(all_stories_data.report_type)

    except SiteErrorException as e:
        print('site error: {}'.format(e))
    finally:
        report.close()


def download_mts_projects_report(mts_projects_data: ReportInformation, report=None):
    # window.clear_log()
    if mts_projects_data.url is None:
        mts_projects_data.url = MTS_PROJECTS
    if report is None:
        report = Report(mts_projects_data) #todo: , hidden=True
    report.connect()
    all_options = []
    try:
        all_options = report.get_select_options(mts_projects_data.select_category_id)
        print("Found {} projects to retrieve".format(len(all_options)))
        print("Closing all drivers to reduce traffic")

        q = Queue(maxsize=0)
        num_threads = min(5, len(all_options))  # TODO: should be 50
        results = [{"option": x} for x in all_options]  # should have dict of [option -> filepath]

        for i in range(len(all_options)):
            q.put((i, all_options[i]))

        print("Set data to {} tasks, starting".format(len(all_options)))
        for i in range(num_threads):
            worker = threading.Thread(target=download_mts_task, args=(mts_projects_data, q, results, report))
            worker.setDaemon(True)
            worker.start()

        print("{} Threads initiated to retrieve all data, waiting".format(num_threads))
        q.join()
        print("All tasks completed")
    except SiteErrorException as e:
        print('site error: {}'.format(e))
    finally:
        report.close()


def download_mts_task(mts_projects_data: ReportInformation, q: Queue, results, report):
    while not q.empty():
        data = q.get()
        try:
            output_file = common.change_file_name(mts_projects_data.output_file, data[1])
            # Psudo
            report.open_new_tab()
            report.select_project_category(data[1], data[0])
            report.press_apply(data[0])
            report.download(mts_projects_data.report_type, output_file, data[0])
            results[data[0]].output_file = output_file
        except Exception as e:
            print(e)
        q.task_done()


def get_section_dict(section_name, default_output, default_url):
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
        "export_type_id_prefix": config.get(section_name, "export_type_id_prefix", common.EXPORT_TYPE_ID_PREFIX)
    }


def get_reports_data():
    global reports
    reports = Reports()
    config.readcwd()

    reports.versions_report = ReportInformation(
        **get_section_dict('Versions', 'C:\\Temp\\versions.csv', VERSIONS_REPORT))

    reports.all_stories_report = ReportInformation(
        **get_section_dict('AllStories', 'C:\\Temp\\all_stories.csv', ALL_STORIES_REPORT))

    reports.all_issues_components_report = ReportInformation(
        **get_section_dict("AllIssuesComponents", 'C:\\Temp\\all_issues_components.csv', ALL_ISSUES_COMPONENTS)
    )

    reports.mts_projects_report = ReportInformation(
        **get_section_dict("MtsProjects", 'C:\\Temp\\mts_projects.csv', MTS_PROJECTS)
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

    def get_mts_projects(self):
        report = Report(reports.mts_projects_report) # todo:, hidden=True
        threading.Thread(target=self.get_mts_projects_thread, args=(report,)).start()

    def get_mts_projects_thread(self, report):
        self.mts_projects_button.config(state="disabled")
        try:
            download_mts_projects_report(reports.mts_projects_report, report)
        except Exception as e:
            print(str(e))
        finally:
            self.all_stories_button.config(state="normal")

    def get_all_stories(self):
        report = Report(reports.all_stories_report)
        threading.Thread(target=self.get_all_stories_thread, args=(report,)).start()

    def get_all_stories_thread(self, report):
        self.all_stories_button.config(state="disabled")
        try:
            download_all_stories_report(reports.all_stories_report, report)
        except Exception as e:
            print(str(e))
        finally:
            self.all_stories_button.config(state="normal")

    def get_versions(self):
        report = Report(reports.versions_report)
        threading.Thread(target=self.get_versions_thread, args=(report,)).start()

    def get_versions_thread(self, report):
        self.versions_button.config(state="disabled")
        try:
            download_versions_report(reports.versions_report, report)
        except Exception as e:
            print(str(e))
        finally:
            self.versions_button.config(state="normal")

    def clear_log(self):
        self.log_panel.delete('1.0', self.ui.END)

    def set_config_text(self, text):
        self.config_string_var.set(text)


if __name__ == "__main__":
    window = WindowView()
    config = Configuration()
    reports = get_reports_data()
    window.set_config_text("Config: {}".format(config.config_path))
    # download_versions_report(reports.versions_report)

    window.app.mainloop()
