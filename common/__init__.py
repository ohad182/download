import os

APP_NAME = "Automated Reports"
APP_DATA = 'APPDATA'

# Website ID fields
APPLY_ID = "m_sqlRsWebPart_ctl00_ctl19_ApplyParameters"
LOADER_ID = "m_sqlRsWebPart_ctl00_ReportViewer_AsyncWait_Wait"
SELECT_CATEGORY_ID = "m_sqlRsWebPart_ctl00_ctl19_ctl06_ctl03_ddValue"

MAIN_MENU_ID = "m_sqlRsWebPart_RSWebPartToolbar_ctl00_RptControls_RSActionMenu_ctl01_t"
EXPORT_MENU_ID = "m_sqlRsWebPart_RSWebPartToolbar_ctl00_RptControls_RSActionMenu_Export"
EXPORT_TYPE_ID_PREFIX = "m_sqlRsWebPart_RSWebPartToolbar_ctl00_RptControls_RSActionMenu_"


def create_temp_folder(notify: bool):
    app_data = os.getenv(APP_DATA)
    if app_data is not None:
        app_data = os.path.join(app_data, APP_NAME)
        try:
            os.makedirs(app_data)
        except:
            pass

    if notify:
        print("App temp directory: {}".format(app_data))
    return app_data


def rreplace(s: str, old: str, new: str, occurences):
    li = s.rsplit(old, occurences)
    return new.join(li)


def change_file_name(filepath, to):
    path, ext = os.path.splitext(filepath)
    filename = os.path.split(path)[-1]
    new_path = rreplace(filepath, filename, to, -1)
    return new_path
