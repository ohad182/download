import os
from datetime import datetime

APP_NAME = "Automated Reports"
APP_DATA = 'APPDATA'

# Website ID fields
APPLY_ID = "m_sqlRsWebPart_ctl00_ctl19_ApplyParameters"
LOADER_ID = "m_sqlRsWebPart_ctl00_ReportViewer_AsyncWait_Wait"
SELECT_CATEGORY_ID = "m_sqlRsWebPart_ctl00_ctl19_ctl06_ctl03_ddValue"

MAIN_MENU_ID = "m_sqlRsWebPart_RSWebPartToolbar_ctl00_RptControls_RSActionMenu_ctl01_t"
EXPORT_MENU_ID = "m_sqlRsWebPart_RSWebPartToolbar_ctl00_RptControls_RSActionMenu_Export"
EXPORT_TYPE_ID_PREFIX = "m_sqlRsWebPart_RSWebPartToolbar_ctl00_RptControls_RSActionMenu_"

NEW_DRIVER_DATE = datetime.strptime('2019-12-09', '%Y-%m-%d').date()

MTS_IGNORE_OPTIONS = ['ARC-II-III', 'Astute', 'Belkin', 'CORE', 'CPSS', 'CPSS_JOBS', 'CS Belkin', 'CS Cisco', 'CS Dell',
                      'CS Demo', 'CS Dormant', 'CS Eltex', 'CS Extreme', 'CS Internal Info', 'CS Larch', 'CS Netgear',
                      'CS Tachi', 'Contax', 'Contax_Maintenance', 'Contax_PostRTS', 'Continuous Integration', 'DFM',
                      'FE_Test', 'FPA', 'Franchise', 'Franchise_Eltex', 'Franchise_Larch', 'Hybrid-Stack', 'ISR',
                      'LGS3xx', 'LGS5xx', 'Lessons Learned', 'MK CS Tachi', 'MKT Pilgrim', 'MTS Microsoft',
                      'MTS Opportunities', 'MTS Robot Pilot', 'MTS SIP5', 'MTS_Off_The_Shelf', 'MTS_PIPE', 'Micro-Init',
                      'NG-GS7XXTP', 'NG-XS728T', 'NG-XS748T', 'NPS ET', 'NPS Internal Info', 'NetGear_MS510',
                      'Nikola_ESW2_SG350G', 'Nikola_ESW2_SG550X', 'Nikola_SG500X', 'Nikola_SG500XG', 'Nikola_Sx200',
                      'Nikola_Sx300', 'Nikola_Sx500', 'OAM FW', 'OpenSwitch', 'Plasma_ARCII', 'PoE',
                      'Python Automation', 'RD_Aldrin', 'RD_Lewis', 'RD_xCat3', 'RnD Demo', 'Ryan', 'SAI-SONiC',
                      'SAI1.0', 'SNI', 'SONIC', 'SONIC-Alibaba', 'SV Networking Automation',
                      'SW Infrastructure and Tools', 'Serdes', 'Switch Dashboard', 'SwitchDev', 'TI-PoE', 'TL-SH1226',
                      'Tachi', 'Tachi 2 (920)', 'Tesla 2.0', 'Tesla 2.1', 'Tesla 2.2', 'Tesla 2.2.5', 'Tesla 2.2.7',
                      'Tesla 2.2.8', 'Tesla 2.3', 'Tesla 2.3.5', 'Tesla 2.4', 'Tesla 2.4.5', 'Test Security',
                      'Test import web project', 'Troya', 'Validation Book', 'Validation Infra']


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
