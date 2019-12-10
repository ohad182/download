class Reports(object):
    def __init__(self):
        self.versions_report = ReportInformation()
        self.all_stories_report = ReportInformation()
        self.all_issues_components_report = ReportInformation()
        self.mts_projects_report = ReportInformation()


class ReportInformation(object):
    def __init__(self, **kwargs):
        self.url = kwargs.get('url', None)
        self.output_file = kwargs.get('output_file', None)
        self.report_type = kwargs.get('report_type', None)
        self.category = kwargs.get('category', None)

        self.apply_id = kwargs.get('apply_id', None)
        self.loader_id = kwargs.get('loader_id', None)
        self.select_category_id = kwargs.get('select_category_id', None)
        self.main_menu_id = kwargs.get('main_menu_id', None)
        self.export_menu_id = kwargs.get('export_menu_id', None)
        self.export_type_id_prefix = kwargs.get('export_type_id_prefix', None)
        self.ignore_options = kwargs.get("ignore_options", None)

    def print_getting(self):
        return print("Getting report for category: {} to: {}".format(self.category, self.output_file))
