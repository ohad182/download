# download

a = Analysis(['myscript.py'],
             pathex=['path\\to\\my\\script'],
             binaries=[ ('path\\to\\my\\chromedriver.exe', '.\\selenium\\webdriver') ],
             datas=None,