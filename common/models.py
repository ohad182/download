from tkinter import Button

from common import Singleton


class Reports(object):
    def __init__(self):
        self.versions_report = ReportInformation()
        self.all_stories_report = ReportInformation()
        self.all_issues_components_report = ReportInformation()
        self.mts_projects_report = ReportInformation()

    def as_list(self):
        return [val for k, val in self.__dict__.items() if not str(hex(id(val))) in str(val)]


class ReportInformation(object):
    def __init__(self, **kwargs):
        self.url = kwargs.get('url', None)
        self.output_file = kwargs.get('output_file', None)
        self.report_type = kwargs.get('report_type', None)
        self.category = kwargs.get('category', None)

        self.apply_id = kwargs.get('apply_id', None)
        self.loader_id = kwargs.get('loader_id', None)
        self.select_category_id = kwargs.get('select_category_id', None)
        self.version_dropdown_id = kwargs.get('version_dropdown_id', None)
        self.main_menu_id = kwargs.get('main_menu_id', None)
        self.export_menu_id = kwargs.get('export_menu_id', None)
        self.export_type_id_prefix = kwargs.get('export_type_id_prefix', None)
        self.ignore_options = kwargs.get("ignore_options", None)
        self.projects = kwargs.get("projects", None)

    def print_getting(self):
        return print("Getting report for category: {} to: {}".format(self.category, self.output_file))


class VirtualEvent(object):
    def __init__(self, **kwargs):
        self.widget = kwargs.get("widget", None)


class IssueComponentSelection(object):
    def __init__(self, **kwargs):
        self.project = kwargs.get("project", None)
        self.version = kwargs.get("version", None)
        self.content = kwargs.get("content", None)

    def __str__(self):
        return "project: {}, version: {}".format(self.project, self.version)

    def __repr__(self):
        return "project: {}, version: {}".format(self.project, self.version)


class IssueComponentData(object, metaclass=Singleton):
    def __init__(self, **kwargs):
        if kwargs.get("mock", False):
            self.selections = [IssueComponentSelection(project="A", version="a"),
                               IssueComponentSelection(project="B", version="b")]
            self.projects_map = {
                "A": ["a", "1"],
                "B": ["b", "2"],
                "C": ["c", "3"]
            }
        else:
            self.projects_map = kwargs.get("projects_map", {})
            self.selections = []
        self.selection_added_callback = kwargs.get("selection_added_callback", None)
        self.selection_removed_callback = kwargs.get("selection_removed_callback", None)
        self.ui_components = []

    def get_projects(self):
        return list(self.projects_map.keys())

    def get_versions(self, project):
        return self.projects_map.get(project, [])

    def add_selection(self, project=None, version=None):
        new_selection = IssueComponentSelection(project=project, version=version)
        self.selections.append(new_selection)
        self.__notify_added(new_selection)

    # def remove_selection(self, project):
    #     selection_to_remove = next((x for x in self.selections if x.project == project), None)
    #     if selection_to_remove is not None:
    #         self.selections.remove(selection_to_remove)
    #         self.__notify_removed(selection_to_remove)

    def remove_selection(self, row):
        if row < len(self.selections):
            selection_to_remove = self.selections.pop(row)
            if selection_to_remove is not None:
                self.__notify_removed(selection_to_remove)

    def __notify_added(self, new_selection):
        if self.selection_added_callback is not None:
            self.selection_added_callback(new_selection)

    def __notify_removed(self, removed_selection):
        if self.selection_removed_callback is not None:
            self.selection_removed_callback(removed_selection)

    def project_selection_changed(self, event):
        mapped_ui = next((x for x in self.ui_components if x["component"] == event.widget), None)
        if mapped_ui is not None:
            self.selections[mapped_ui["row"]].project = event.widget.get()
            version_ui = next(
                (x for x in self.ui_components if x["row"] == mapped_ui["row"] and x["col"] == mapped_ui["col"] + 1),
                None)
            if version_ui is not None:
                self.refresh_versions_list(event.widget.get(), version_ui["component"])
        print("project selction changed! {}".format(self.selections))
        # project index is event.widget.current()
        # project text is event.widget.get()

    def version_selection_changed(self, event, real=True):
        mapped_ui = next((x for x in self.ui_components if x["component"] == event.widget), None)
        if mapped_ui is not None:
            self.selections[mapped_ui["row"]].version = event.widget.get()
        if real:
            print("version selection changed! {}".format(self.selections))

    def refresh_versions_list(self, project, widget):
        widget['values'] = self.get_versions(project)
        widget.current(0)
        self.version_selection_changed(VirtualEvent(widget=widget), False)

    def register_ui(self, ui_comp, row, col):
        self.ui_components.append({
            "component": ui_comp,
            "row": row,
            "col": col
        })

    def unregister_ui(self, owner):
        row = -1
        ui_to_remove = [x for x in self.ui_components if x['component'] == owner]
        if ui_to_remove is not None and len(ui_to_remove) > 0:
            row = ui_to_remove[0]['row']
            self.remove_selection(row)
            ui_to_remove = [x for x in self.ui_components if x['row'] == row]
            for ui in ui_to_remove:
                self.ui_components.remove(ui)
                ui['component'].destroy()

            # update indexes
            for i in range(row, int(len(self.ui_components) / 3)):
                next_row_items = [x for x in self.ui_components if x["row"] == i + 1]
                if next_row_items is not None and len(next_row_items) > 0:
                    for idx, item in enumerate(next_row_items):
                        item['row'] = i
                        item['component'].grid(row=i, column=idx, sticky='news', padx=3)

        return row

    def get_remove_btn(self, row: int):
        return next(
            (x["component"] for x in self.ui_components if x['row'] == row and isinstance(x["component"], Button)),
            None)

    def compare_dicts(self, dict1: dict, dict2: dict):
        for x1 in dict1.keys():
            if dict1.get(x1) != dict1.get(x1):
                return False
        return True
