import traceback
from selenium.common.exceptions import WebDriverException

import common
from common.preserved_config import PreservedConfig
from report.base_report import BaseReport
from common.models import ReportInformation, IssueComponentData
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


class AllIssuesComponentReport(BaseReport):
    site_projects = []

    def __init__(self, report_info: ReportInformation, update_driver_lock=None):
        super(AllIssuesComponentReport, self).__init__(report_info, driver_update_lock=update_driver_lock
                                                       )
        self.load()

    def open_url(self, verbose=True):
        self.driver.get(self.report_info.url)
        if verbose:
            print("Page loading phase finished")

    def get_options_map(self, projects_list):
        options_map = dict()

        try:
            self.open_url(verbose=False)
            self.set_projects_list(force=True)
            for project_name in projects_list:
                project_index = AllIssuesComponentReport.site_projects.index(project_name)
                if project_index == -1:
                    print("Unable to find project name: {}".format(project_name))
                    continue
                self.select_option(self.report_info.select_category_id, project_index, True)
                # self.select_project(project_index)
                self.wait_element_enabled(self.report_info.version_dropdown_id)
                # time.sleep(0.8)
                versions = self.get_select_options(self.report_info.version_dropdown_id,
                                                   ignore_options=['<Select a Value>'])
                options_map[project_name] = versions

        except Exception as e:
            print(e)
        finally:
            self.close()

        print("Retrieved options map: {}".format(options_map))

        return options_map

    def get_report_content(self, issue_data: IssueComponentData):
        """
        Gets all selected reports content into single report with extra 2 columns "base_project" - "base_version"
        :param issue_data:
        :return:
        """
        try:
            self.open_url()
            self.set_projects_list()
            for selection in issue_data.selections:
                print("started {}".format(selection))
                project_index = AllIssuesComponentReport.site_projects.index(selection.project)
                if project_index == -1:
                    print("Unable to find project name: {}".format(selection.project))
                    continue
                self.select_option(self.report_info.select_category_id, project_index, True)
                self.wait_element_enabled(self.report_info.version_dropdown_id)
                version_options = self.get_select_options(self.report_info.version_dropdown_id)
                for idx, opt in enumerate(version_options):
                    if selection.version == opt:
                        self.select_option(self.report_info.version_dropdown_id, idx, True)
                        break
                self.press_apply()
                selection.content = self._get_table_content()
                AllIssuesComponentReport.save(issue_data)
                print("done {}".format(selection))
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
        finally:
            self.close()

        self.write_report(issue_data.selections)

    @staticmethod
    def save(issue_data: IssueComponentData):
        PreservedConfig().add(common.ALL_COMPONENTS_REPORT_NAME, {
            "site_projects": AllIssuesComponentReport.site_projects,
            "selections": [{"project": x.project, "version": x.version} for x in issue_data.selections],
            "projects_map": issue_data.projects_map
        })

    def write_report(self, selections):
        try:
            with open(self.report_info.output_file, 'w') as result_file:
                result_empty = True
                for selection in selections:
                    can_write = False
                    for line_content in selection.content.splitlines():
                        line_content = line_content.strip()
                        if line_content != "":
                            if can_write:
                                try:
                                    result_file.write(f"{selection.project},{selection.version},{line_content}\n")
                                except Exception as e:
                                    print("unable to write: {}".format(line_content))
                                continue
                            if line_content.lower().startswith('jproject') and not can_write:
                                can_write = True
                                if result_empty:
                                    result_file.write(f"Base_Project,Base_Version,{line_content}\n")
                                    result_empty = False

            print(f"Report generated at: {self.report_info.output_file}")
        except Exception as e:
            print(e)

    def select_option(self, drop_down_id, option_index, post_back=True):
        try:
            select_script = """var select = document.getElementById('<--drop_down_id-->');
select.value = <--new_val_index-->;
""".replace("<--drop_down_id-->", drop_down_id).replace("<--new_val_index-->", "{}".format(option_index))

            if post_back is True and '_ddValue' in drop_down_id:
                post_back = drop_down_id.replace('_ddValue', '')

                post_back_script = "$find('<--post_back_id-->').TriggerPostBackScript();".replace("<--post_back_id-->",
                                                                                                  post_back)
                select_script = "{}{}".format(select_script, post_back_script)
            self.driver.execute_script(select_script)
        except WebDriverException as e:
            if 'call function result missing \'value\'' in e.msg:
                pass  # ok exception raised due to chrome and chromedriver incompatibility
            else:
                print(f"Failed to execute script: {select_script}")

    def set_projects_list(self, force=False):
        """
        fills out site projects from the sharepoint site
        assumes open url was called
        :return:
        """
        if force is True or AllIssuesComponentReport.site_projects is None or len(
                AllIssuesComponentReport.site_projects) == 0:
            AllIssuesComponentReport.site_projects = self.get_select_options(self.report_info.select_category_id)

    def wait_element_enabled(self, el_id):
        element = self.wait.until(
            ec.element_to_be_clickable((By.ID, el_id)))
        return element
