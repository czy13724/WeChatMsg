import ctypes
import sys
import time
import traceback

from PyQt5.QtWidgets import *

from app.log import logger
from app.ui_pc import mainview
from app.ui_pc.tool.pc_decrypt import pc_decrypt

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WeChatReport")


class ViewController(QWidget):
    def __init__(self):
        super().__init__()
        self.viewMainWIndow = None
        self.viewDecrypt = None

    def loadPCDecryptView(self):
        """
        登录界面
        :return:
        """
        self.viewDecrypt = pc_decrypt.DecryptControl()
        self.viewDecrypt.DecryptSignal.connect(self.show_success)
        self.viewDecrypt.show()

    def loadMainWinView(self, username=None):
        """
        聊天界面
        :param username: 账号
        :return:
        """
        username = ''
        start = time.time()
        self.viewMainWIndow = mainview.MainWinController(username=username)
        self.viewMainWIndow.exitSignal.connect(self.close)
        try:
            self.viewMainWIndow.setWindowTitle("留痕")
            self.viewMainWIndow.show()
            end = time.time()
            print('ok', end - start)
            self.viewMainWIndow.init_ui()
        except Exception as e:
            print(f"Exception: {e}")
            logger.error(traceback.print_exc())

    def show_success(self):
        QMessageBox.about(self, "解密成功", "数据库文件存储在\napp/DataBase/Msg\n文件夹下")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ViewController()
    try:
        # view.loadPCDecryptView()
        view.loadMainWinView()
        # view.show()
        # view.show_success()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Exception: {e}")
        logger.error(traceback.print_exc())
