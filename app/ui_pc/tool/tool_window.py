from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel

from app.ui_pc.Icon import Icon
from .pc_decrypt import DecryptControl
from .toolUI import Ui_Dialog

# 美化样式表
Stylesheet = """
QPushButton{
    background-color: #ffffff;
}
QPushButton:hover { 
    background-color: lightgray;
}
/*去掉item虚线边框*/
QListWidget, QListView, QTreeWidget, QTreeView {
    outline: 0px;
    border:none;
    background-color:rgb(240,240,240)
}
/*设置左侧选项的最小最大宽度,文字颜色和背景颜色*/
QListWidget {
    min-width: 400px;
    max-width: 400px;
    min-height: 80px;
    max-height: 80px;
    color: black;
    border:none;
}
QListWidget::item{
    height:80px;
    width:80px;
}
/*被选中时的背景颜色和左边框颜色*/
QListWidget::item:selected {
    background: rgb(204, 204, 204);
    border-bottom: 4px solid rgb(9, 187, 7);
    border-left:none;
    color: black;
    font-weight: bold;
}
/*鼠标悬停颜色*/
HistoryPanel::item:hover {
    background: rgb(52, 52, 52);
}
"""


class ToolWindow(QWidget, Ui_Dialog):
    get_info_signal = pyqtSignal(str)
    decrypt_success_signal = pyqtSignal(bool)
    load_finish_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setStyleSheet(Stylesheet)
        self.init_ui()
        self.load_finish_signal.emit(True)

    def init_ui(self):
        self.listWidget.clear()
        self.listWidget.currentRowChanged.connect(self.setCurrentIndex)
        chat_item = QListWidgetItem(Icon.Chat_Icon, '解密', self.listWidget)
        contact_item = QListWidgetItem(Icon.Contact_Icon, '别点', self.listWidget)
        myinfo_item = QListWidgetItem(Icon.MyInfo_Icon, '别点', self.listWidget)
        tool_item = QListWidgetItem(Icon.MyInfo_Icon, '别点', self.listWidget)
        decrypt_window = DecryptControl()
        decrypt_window.get_wxidSignal.connect(self.get_info_signal)
        decrypt_window.DecryptSignal.connect(self.decrypt_success_signal)
        self.stackedWidget.addWidget(decrypt_window)
        label = QLabel('都说了不让你点', self)
        label.setFont(QFont("微软雅黑", 50))
        label.setAlignment(Qt.AlignCenter)
        # 设置label的背景颜色(这里随机)
        # 这里加了一个margin边距(方便区分QStackedWidget和QLabel的颜色)
        # label.setStyleSheet('background: rgb(%d, %d, %d);margin: 50px;' % (
        #     randint(0, 255), randint(0, 255), randint(0, 255)))
        self.stackedWidget.addWidget(label)
        self.stackedWidget.addWidget(label)
        self.stackedWidget.addWidget(label)
        self.listWidget.setCurrentRow(0)
        self.stackedWidget.setCurrentIndex(0)

    def setCurrentIndex(self, row):
        print(row)
        self.stackedWidget.setCurrentIndex(row)
