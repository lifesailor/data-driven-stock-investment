from pywinauto import application
from pywinauto import timings
import time
import os

app = application.Application()
address = 'C:\KiwoomFlash3\\bin\\nkministarter.exe'
app.start(address)

title = "번개3 Login"
dlg = timings.wait_until_passes(20, 0.5, lambda: app.window(title=title))

pass_ctrl = dlg.Edit2
pass_ctrl.SetFocus()
pass_ctrl.TypeKeys('gjgd1020')

cert_ctrl = dlg.Edit3
cert_ctrl.SetFocus()
cert_ctrl.TypeKeys('Intheflow91!')

btn_ctrl = dlg.Button0
btn_ctrl.Click()

time.sleep(50)
os.system("taskkill /im khmini.exe")
