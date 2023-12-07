import csv
import html
import os

from PyQt5.QtCore import pyqtSignal, QThread

from . import msg_db
from .package_msg import PackageMsg
from ..DataBase import hard_link_db
from ..person_pc import MePC
from ..util import path

os.makedirs('./data/聊天记录', exist_ok=True)


def makedirs(path):
    os.makedirs(path,exist_ok=True)
    os.makedirs(os.path.join(path, 'image'), exist_ok=True)
    os.makedirs(os.path.join(path, 'emoji'), exist_ok=True)
    os.makedirs(os.path.join(path, 'video'), exist_ok=True)
    os.makedirs(os.path.join(path, 'voice'), exist_ok=True)
    os.makedirs(os.path.join(path, 'file'), exist_ok=True)


def escape_js_and_html(input_str):
    # 转义HTML特殊字符
    html_escaped = html.escape(input_str, quote=False)

    # 手动处理JavaScript转义字符
    js_escaped = (
        html_escaped
        .replace("\\", "\\\\")
        .replace("'", r"\'")
        .replace('"', r'\"')
        .replace("\n", r'\n')
        .replace("\r", r'\r')
        .replace("\t", r'\t')
    )

    return js_escaped


class Output(QThread):
    """
    发送信息线程
    """
    progressSignal = pyqtSignal(int)
    rangeSignal = pyqtSignal(int)
    okSignal = pyqtSignal(int)
    i = 1
    CSV = 0
    DOCX = 1
    HTML = 2
    CSV_ALL = 3

    def __init__(self, contact, parent=None, type_=DOCX):
        super().__init__(parent)
        self.Child0 = None
        self.last_timestamp = 0
        self.sec = 2  # 默认1000秒
        self.contact = contact
        self.ta_username = contact.wxid if contact else ''
        self.msg_id = 0
        self.output_type = type_
        self.total_num = 0
        self.num = 0

    def progress(self, value):
        self.progressSignal.emit(value)

    def to_csv_all(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/"
        os.makedirs(origin_docx_path, exist_ok=True)
        filename = f"{os.path.abspath('.')}/data/聊天记录/messages.csv"
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['localId', 'TalkerId', 'Type', 'SubType',
                   'IsSender', 'CreateTime', 'Status', 'StrContent',
                   'StrTime', 'Remark', 'NickName', 'Sender']
        # messages = msg_db.get_messages_all()
        packagemsg = PackageMsg()
        messages = packagemsg.get_package_message_all()
        # 写入CSV文件
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            # 写入数据
            writer.writerows(messages)
        self.okSignal.emit(1)

    def run(self):
        if self.output_type == self.DOCX:
            return
        elif self.output_type == self.CSV_ALL:
            self.to_csv_all()
        else:
            self.Child = ChildThread(self.contact, type_=self.output_type)
            self.Child.progressSignal.connect(self.progress)
            self.Child.rangeSignal.connect(self.rangeSignal)
            self.Child.okSignal.connect(self.okSignal)
            self.Child.start()

    def cancel(self):
        self.requestInterruption()


class ChildThread(QThread):
    """
        子线程，用于导出部分聊天记录
    """
    progressSignal = pyqtSignal(int)
    rangeSignal = pyqtSignal(int)
    okSignal = pyqtSignal(int)
    i = 1
    CSV = 0
    DOCX = 1
    HTML = 2

    def __init__(self, contact, parent=None, type_=DOCX):
        super().__init__(parent)
        self.contact = contact
        self.last_timestamp = 0
        self.sec = 2  # 默认1000秒
        self.msg_id = 0
        self.output_type = type_

    def is_5_min(self, timestamp):
        if abs(timestamp - self.last_timestamp) > 300:
            self.last_timestamp = timestamp
            return True
        return False

    def text(self, doc, isSend, message, status):
        return

    def image(self, doc, isSend, Type, content, imgPath):
        return

    def emoji(self, doc, isSend, content, imgPath):
        return

    def wx_file(self, doc, isSend, content, status):
        return

    def retract_message(self, doc, isSend, content, status):
        return

    def reply(self, doc, isSend, content, status):
        return

    def pat_a_pat(self, doc, isSend, content, status):
        return

    def video(self, doc, isSend, content, status, img_path):
        return

    def to_csv(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        os.makedirs(origin_docx_path, exist_ok=True)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}.csv"
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['localId', 'TalkerId', 'Type', 'SubType',
                   'IsSender', 'CreateTime', 'Status', 'StrContent',
                   'StrTime']
        messages = msg_db.get_messages(self.contact.wxid)
        # 写入CSV文件
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            # 写入数据
            writer.writerows(messages)
        self.okSignal.emit('ok')

    def to_csv_all(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/"
        os.makedirs(origin_docx_path, exist_ok=True)
        filename = f"{os.path.abspath('.')}/data/聊天记录/messages.csv"
        # columns = ["用户名", "消息内容", "发送时间", "发送状态", "消息类型", "isSend", "msgId"]
        columns = ['localId', 'TalkerId', 'Type', 'SubType',
                   'IsSender', 'CreateTime', 'Status', 'StrContent',
                   'StrTime', 'Remark', 'NickName', 'Sender']
        # messages = msg_db.get_messages_all()
        packagemsg = PackageMsg()
        messages = packagemsg.get_package_message_all()
        # 写入CSV文件
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            # 写入数据
            writer.writerows(messages)
        self.okSignal.emit(1)

    def to_html(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        os.makedirs(origin_docx_path, exist_ok=True)
        messages = msg_db.get_messages(self.contact.wxid)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}.html"
        f = open(filename, 'w', encoding='utf-8')
        html_head = '''
                    <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Title</title>
            <style>

                *{
                padding: 0;
                margin: 0;
            }
            body{
                height: 100vh;
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container{
                height: 760px;
                width: 900px;
                border-radius: 4px;
                border: 0.5px solid #e0e0e0;
                background-color: #f5f5f5;
                display: flex;
                flex-flow: column;
                overflow: hidden;
            }
            .content{
                width: calc(100% - 40px);
                padding: 20px;
                overflow-y: scroll;
                flex: 1;
            }
            .content:hover::-webkit-scrollbar-thumb{
                background:rgba(0,0,0,0.1);
            }
            .bubble{
                max-width: 400px;
                padding: 10px;
                border-radius: 5px;
                position: relative;
                color: #000;
                word-wrap:break-word;
                word-break:normal;
            }
            .item-left .bubble{
                margin-left: 15px;
                background-color: #fff;
            }
            .item-left .bubble:before{
                content: "";
                position: absolute;
                width: 0;
                height: 0;
                border-left: 10px solid transparent;
                border-top: 10px solid transparent;
                border-right: 10px solid #fff;
                border-bottom: 10px solid transparent;
                left: -20px;
            }
            .item-right .bubble{
                margin-right: 15px;
                background-color: #9eea6a;
            }
            .item-right .bubble:before{
                content: "";
                position: absolute;
                width: 0;
                height: 0;
                border-left: 10px solid #9eea6a;
                border-top: 10px solid transparent;
                border-right: 10px solid transparent;
                border-bottom: 10px solid transparent;
                right: -20px;
            }
            .item{
                margin-top: 15px;
                display: flex;
                width: 100%;
            }
            .item.item-right{
                justify-content: flex-end;
            }
            .item.item-center{
                justify-content: center;
            }
            .item.item-center span{
                font-size: 12px;
                padding: 2px 4px;
                color: #fff;
                background-color: #dadada;
                border-radius: 3px;
                -moz-user-select:none; /*火狐*/
                -webkit-user-select:none; /*webkit浏览器*/
                -ms-user-select:none; /*IE10*/
                -khtml-user-select:none; /*早期浏览器*/
                user-select:none;
            }

            .avatar img{
                width: 42px;
                height: 42px;
                border-radius: 50%;
            }
            .input-area{
                border-top:0.5px solid #e0e0e0;
                height: 150px;
                display: flex;
                flex-flow: column;
                background-color: #fff;
            }
            textarea{
                flex: 1;
                padding: 5px;
                font-size: 14px;
                border: none;
                cursor: pointer;
                overflow-y: auto;
                overflow-x: hidden;
                outline:none;
                resize:none;
            }
            .button-area{
                display: flex;
                height: 40px;
                margin-right: 10px;
                line-height: 40px;
                padding: 5px;
                justify-content: flex-end;
            }
            .button-area button{
                width: 80px;
                border: none;
                outline: none;
                border-radius: 4px;
                float: right;
                cursor: pointer;
            }

            /* 设置滚动条的样式 */
            ::-webkit-scrollbar {
                width:10px;
            }
            /* 滚动槽 */
            ::-webkit-scrollbar-track {
                -webkit-box-shadow:inset006pxrgba(0,0,0,0.3);
                border-radius:8px;
            }
            /* 滚动条滑块 */
            ::-webkit-scrollbar-thumb {
                border-radius:10px;
                background:rgba(0,0,0,0);
                -webkit-box-shadow:inset006pxrgba(0,0,0,0.5);
            }
            </style>
        </head>
        <body>
        <div class="container" id="container" onscroll="handleScroll()">
            <div class="content">
                '''
        f.write(html_head)
        MePC().avatar.save(os.path.join(origin_docx_path, 'myhead.png'))
        self.contact.avatar.save(os.path.join(origin_docx_path, 'tahead.png'))
        self.rangeSignal.emit(len(messages))
        for index, message in enumerate(messages):
            type_ = message[2]
            str_content = message[7]
            str_time = message[8]
            # print(type_, type(type_))
            is_send = message[4]
            avatar = MePC().avatar_path if is_send else self.contact.avatar_path
            timestamp = message[5]
            self.progressSignal.emit(index)
            if type_ == 1:
                if self.is_5_min(timestamp):
                    f.write(
                        f'''
                                <div class="item item-center"><span>{str_time}</span></div>
                                '''
                    )
                if is_send:
                    f.write(
                        f'''
                                <div class="item item-right">
                    <div class="bubble bubble-right">{str_content}</div>
                    <div class="avatar">
                        <img src="myhead.png" />
                    </div>
                </div>
                                '''
                    )
                else:
                    f.write(
                        f'''
                                <div class="item item-left">
                    <div class="avatar">
                        <img src="tahead.png" />
                    </div>
                    <div class="bubble bubble-left">{str_content}
                    </div>
                </div>
                                '''
                    )
        html_end = '''

            </div>
        </div>
        <script>
  const container = document.getElementById('container');
  const content = document.getElementById('content');

  const totalItems = 1000;
  const itemsPerPage = 20;
  const itemHeight = 50;

  function updateContent() {
    const scrollTop = container.scrollTop;
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(startIndex + itemsPerPage, totalItems);

    // Remove existing items
    content.innerHTML = '';

    // Add new items
    for (let i = startIndex; i < endIndex; i++) {
      const item = document.createElement('div');
      item.className = 'item';
      item.textContent = `Item ${i}`;
      content.appendChild(item);
    }

    // Update container height to show correct scrollbar
    container.style.height = totalItems * itemHeight + 'px';
  }

  function handleScroll() {
    updateContent();
  }

  // Initial content rendering
  updateContent();
</script>
        </body>
        </html>
                '''
        f.write(html_end)
        f.close()
        self.okSignal.emit(1)

    def to_html_(self):
        origin_docx_path = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}"
        makedirs(origin_docx_path)
        messages = msg_db.get_messages(self.contact.wxid)
        filename = f"{os.path.abspath('.')}/data/聊天记录/{self.contact.remark}/{self.contact.remark}.html"
        f = open(filename, 'w', encoding='utf-8')
        html_head = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Records</title>
    <style>

      *{
      padding: 0;
      margin: 0;
  }
  body{
      height: 100vh;
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
  }
  
   .modal {
      display: none;
      position: fixed;
      z-index: 9999;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.8);
   }
 
   .modal-image {
      display: block;
      max-width: 90%;
      max-height: 90%;
      margin: auto;
      margin-top: 5%;
   }
  .container{
      height: 760px;
      width: 900px;
      border-radius: 4px;
      border: 0.5px solid #e0e0e0;
      background-color: #f5f5f5;
      display: flex;
      flex-flow: column;
      overflow: hidden;
  }
  .content{
      width: calc(100% - 40px);
      padding: 20px;
      overflow-y: scroll;
      flex: 1;
  }
  .content:hover::-webkit-scrollbar-thumb{
      background:rgba(0,0,0,0.1);
  }
  .bubble{
      max-width: 400px;
      padding: 10px;
      border-radius: 5px;
      position: relative;
      color: #000;
      word-wrap:break-word;
      word-break:normal;
  }
  .item-left .bubble{
      margin-left: 15px;
      background-color: #fff;
  }
  .item-left .bubble:before{
      content: "";
      position: absolute;
      width: 0;
      height: 0;
      border-left: 10px solid transparent;
      border-top: 10px solid transparent;
      border-right: 10px solid #fff;
      border-bottom: 10px solid transparent;
      left: -20px;
  }
  .item-right .bubble{
      margin-right: 15px;
      background-color: #9eea6a;
  }
  .item-right .bubble:before{
      content: "";
      position: absolute;
      width: 0;
      height: 0;
      border-left: 10px solid #9eea6a;
      border-top: 10px solid transparent;
      border-right: 10px solid transparent;
      border-bottom: 10px solid transparent;
      right: -20px;
  }
  .item{
      margin-top: 15px;
      display: flex;
      width: 100%;
  }
  .item.item-right{
      justify-content: flex-end;
  }
  .item.item-center{
      justify-content: center;
  }
  .item.item-center span{
      font-size: 12px;
      padding: 2px 4px;
      color: #fff;
      background-color: #dadada;
      border-radius: 3px;
      -moz-user-select:none; /*火狐*/
      -webkit-user-select:none; /*webkit浏览器*/
      -ms-user-select:none; /*IE10*/
      -khtml-user-select:none; /*早期浏览器*/
      user-select:none;
  }

  .chat-image img{
    margin-right: 18px;
    margin-left: 18px;
    max-width: 300px;
    max-height: auto;
  }
  .avatar img{
      width: 42px;
      height: 42px;
      border-radius: 50%;
  }
  .input-area{
      border-top:0.5px solid #e0e0e0;
      height: 150px;
      display: flex;
      flex-flow: column;
      background-color: #fff;
  }
  textarea{
      flex: 1;
      padding: 5px;
      font-size: 14px;
      border: none;
      cursor: pointer;
      overflow-y: auto;
      overflow-x: hidden;
      outline:none;
      resize:none;
  }
  .button-area{
      display: flex;
      height: 40px;
      margin-right: 10px;
      line-height: 40px;
      padding: 5px;
      justify-content: flex-end;
  }
  .button-area button{
      width: 80px;
      border: none;
      outline: none;
      border-radius: 4px;
      float: right;
      cursor: pointer;
  }

  /* 设置滚动条的样式 */
  ::-webkit-scrollbar {
      width:10px;
  }
  /* 滚动槽 */
  ::-webkit-scrollbar-track {
      -webkit-box-shadow:inset006pxrgba(0,0,0,0.3);
      border-radius:8px;
  }
  /* 滚动条滑块 */
  ::-webkit-scrollbar-thumb {
      border-radius:10px;
      background:rgba(0,0,0,0);
      -webkit-box-shadow:inset006pxrgba(0,0,0,0.5);
  }

  .pagination-container {
  display: flex;
  flex-direction: column;
  align-items: center; 
  margin-top: 20px;
  margin-left: 20px; /* 新增的左边距 */
}

.button-row,
.jump-row,
#paginationInfo {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 10px;
}

button {
  padding: 10px 25px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 0 14px;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #2980b9;
}

input {
  padding: 8px;
  width: 120px;
  box-sizing: border-box;
  margin-right: 0px;
  margin-left: 15px;
}

button,
input {
  font-size: 14px;
}

#paginationInfo {
  color: #555;
  font-size: 14px;
}

.emoji_img {
    width: 26px;
    height: 26px;
    position: relative;
    bottom: -6px;
}

  </style>
</head>
<body>
  <div class="container">
    <div class="content" id="chat-container">
        <div class="item item-center"><span>昨天 12:35</span></div>
        <div class="item item-center"><span>你已添加了凡繁烦，现在可以开始聊天了。</span></div>
        <div class="item item-left">
            <div class="avatar">
                <img src="https://dss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=25668084,2889217189&fm=26&gp=0.jpg" />
            </div>
            <div class="bubble bubble-left">您好,我在武汉，你可以直接送过来吗，我有时间的话，可以自己过去拿<br/>！！！<br/>123
            </div>
        </div>

        <div class="item item-right">
            <div class="bubble bubble-right">hello<br/>你好呀</div>
            <div class="avatar">
                <img src="https://ss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/u=3313909130,2406410525&fm=15&gp=0.jpg" />
            </div>
        </div>
        <div class="item item-center">
            <span>昨天 13:15</span>
        </div>

    </div>

</div>
<div></div>
<div id="modal" class="modal" onclick="hideModal()">
  <img id="modal-image" class="modal-image">
</div>
<div class="pagination-container">
  <div class="button-row">
    <button onclick="prevPage()">上一页</button>
    <button onclick="nextPage()">下一页</button>
  </div>
  <div class="jump-row">
    <input type="number" id="gotoPageInput" placeholder="跳转到第几页">
    <button onclick="gotoPage()">跳转</button>
  </div>
  <div id="paginationInfo"></div>
</div>
<script>
const chatContainer = document.getElementById('chat-container');
// Sample chat messages (replace this with your actual data)
const chatMessages = [
        '''
        f.write(html_head)
        MePC().avatar.save(os.path.join(origin_docx_path, 'myhead.png'))
        self.contact.avatar.save(os.path.join(origin_docx_path, 'tahead.png'))
        self.rangeSignal.emit(len(messages))
        emoji = {
            '[微笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_1@2x.png" id="微笑" class="emoji_img">',
            '[撇嘴]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_2@2x.png" id="撇嘴" class="emoji_img">',
            '[色]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_3@2x.png" id="色" class="emoji_img">',
            '[发呆]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_4@2x.png" id="发呆" class="emoji_img">',
            '[得意]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_5@2x.png" id="得意" class="emoji_img">',
            '[流泪]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_6@2x.png" id="流泪" class="emoji_img">',
            '[害羞]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_7@2x.png" id="害羞" class="emoji_img">',
            '[闭嘴]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_8@2x.png" id="闭嘴" class="emoji_img">',
            '[睡]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_9@2x.png" id="睡" class="emoji_img">',
            '[大哭]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_10@2x.png" id="大哭" class="emoji_img">',
            '[尴尬]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_11@2x.png" id="尴尬" class="emoji_img">',
            '[发怒]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_12@2x.png" id="发怒" class="emoji_img">',
            '[调皮]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_13@2x.png" id="调皮" class="emoji_img">',
            '[呲牙]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_14@2x.png" id="呲牙" class="emoji_img">',
            '[惊讶]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_15@2x.png" id="惊讶" class="emoji_img">',
            '[难过]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_16@2x.png" id="难过" class="emoji_img">',
            '[抓狂]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_19@2x.png" id="抓狂" class="emoji_img">',
            '[吐]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_20@2x.png" id="吐" class="emoji_img">',
            '[偷笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_21@2x.png" id="偷笑" class="emoji_img">',
            '[愉快]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_22@2x.png" id="愉快" class="emoji_img">',
            '[白眼]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_23@2x.png" id="白 眼" class="emoji_img">',
            '[傲慢]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_24@2x.png" id="傲慢" class="emoji_img">',
            '[困]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_26@2x.png" id="困" class="emoji_img">',
            '[惊恐]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_27@2x.png" id="惊恐" class="emoji_img">',
            '[憨笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_29@2x.png" id="憨笑" class="emoji_img">',
            '[悠闲]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_30@2x.png" id="悠闲" class="emoji_img">',
            '[咒骂]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_32@2x.png" id="咒骂" class="emoji_img">',
            '[疑问]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_33@2x.png" id="疑问" class="emoji_img">',
            '[嘘]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_34@2x.png" id="嘘" class="emoji_img">',
            '[晕]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_35@2x.png" id="晕" class="emoji_img">',
            '[衰]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_37@2x.png" id="衰" class="emoji_img">',
            '[骷髅]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_38@2x.png" id="骷髅" class="emoji_img">',
            '[敲打]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_39@2x.png" id="敲打" class="emoji_img">',
            '[再见]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_40@2x.png" id="再见" class="emoji_img">',
            '[擦汗]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_41@2x.png" id="擦汗" class="emoji_img">',
            '[抠鼻]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_42@2x.png" id="抠鼻" class="emoji_img">',
            '[鼓掌]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_43@2x.png" id="鼓掌" class="emoji_img">',
            '[坏笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_45@2x.png" id="坏笑" class="emoji_img">',
            '[右哼哼]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_47@2x.png" id="右哼哼" class="emoji_img">',
            '[鄙视]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_49@2x.png" id="鄙视" class="emoji_img">',
            '[委屈]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_50@2x.png" id="委屈" class="emoji_img">',
            '[快哭了]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_51@2x.png" id="快哭了" class="emoji_img">',
            '[阴险]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_52@2x.png" id="阴险" class="emoji_img">',
            '[亲亲]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_53@2x.png" id="亲亲" class="emoji_img">',
            '[可怜]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_55@2x.png" id="可怜" class="emoji_img">',
            '[笑脸]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Happy.png" id="笑脸" class="emoji_img">',
            '[生病]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Sick.png" id="生病" class="emoji_img">',
            '[脸红]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Flushed.png" id="脸红" class="emoji_img">',
            '[破涕为笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Lol.png" id="破涕为笑" class="emoji_img">',
            '[恐惧]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Terror.png" id="恐惧" class="emoji_img">',
            '[失望]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/LetDown.png" id="失望" class="emoji_img">',
            '[无语]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Duh.png" id="无语" class="emoji_img">',
            '[嘿哈]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_04.png" id="嘿哈" class="emoji_img">',
            '[捂脸]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_05.png" id="捂脸" class="emoji_img">',
            '[奸笑]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_02.png" id="奸笑" class="emoji_img">',
            '[机智]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_06.png" id="机智" class="emoji_img">',
            '[皱眉]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_12.png" id="皱眉" class="emoji_img">',
            '[耶]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_11.png" id="耶" class="emoji_img">',
            '[吃瓜]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Watermelon.png" id="吃瓜" class="emoji_img">',
            '[加油]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Addoil.png" id="加油" class="emoji_img">',
            '[汗]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Sweat.png" id="汗" class="emoji_img">',
            '[天啊]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Shocked.png" id="天啊" class="emoji_img">',
            '[Emm]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Cold.png" id="Emm" class="emoji_img">',
            '[社会社会]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Social.png" id="社会社会" class="emoji_img">',
            '[旺柴]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Yellowdog.png" id="旺柴" class="emoji_img">',
            '[好的]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/NoProb.png" id="好的" class="emoji_img">',
            '[打脸]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Slap.png" id="打脸" class="emoji_img">',
            '[哇]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Wow.png" id="哇" class="emoji_img">',
            '[翻白眼]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Boring.png" id="翻白眼" class="emoji_img">',
            '[666]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/666.png" id="666" class="emoji_img">',
            '[让我看看]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/LetMeSee.png" id="让我看看" class="emoji_img">',
            '[叹气]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Sigh.png" id="叹气" class="emoji_img">',
            '[苦涩]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Hurt.png" id="苦涩" class="emoji_img">',
            '[裂开]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Broken.png" id="裂开" class="emoji_img">',
            '[嘴唇]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_66@2x.png" id="嘴唇" class="emoji_img">',
            '[爱心]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_67@2x.png" id="爱心" class="emoji_img">',
            '[心碎]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_68@2x.png" id="心碎" class="emoji_img">',
            '[拥抱]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_79@2x.png" id="拥抱" class="emoji_img">',
            '[强]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_80@2x.png" id="强" class="emoji_img">',
            '[弱]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_81@2x.png" id="弱" class="emoji_img">',
            '[握手]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_82@2x.png" id="握手" class="emoji_img">',
            '[胜利]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_83@2x.png" id="胜利" class="emoji_img">',
            '[抱拳]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_84@2x.png" id="抱拳" class="emoji_img">',
            '[勾引]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_85@2x.png" id="勾引" class="emoji_img">',
            '[拳头]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_86@2x.png" id="拳头" class="emoji_img">',
            '[OK]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_90@2x.png" id="OK" class="emoji_img">',
            '[合十]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Worship.png" id="合十" class="emoji_img">',
            '[啤酒]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_58@2x.png" id="啤酒" class="emoji_img">',
            '[咖啡]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_61@2x.png" id="咖啡" class="emoji_img">',
            '[蛋糕]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_69@2x.png" id="蛋糕" class="emoji_img">',
            '[玫瑰]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_64@2x.png" id="玫 瑰" class="emoji_img">',
            '[凋谢]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_65@2x.png" id="凋谢" class="emoji_img">',
            '[菜刀]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_56@2x.png" id="菜刀" class="emoji_img">',
            '[炸弹]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_71@2x.png" id="炸弹" class="emoji_img">',
            '[便便]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_75@2x.png" id="便便" class="emoji_img">',
            '[月亮]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_76@2x.png" id="月亮" class="emoji_img">',
            '[太阳]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_77@2x.png" id="太阳" class="emoji_img">',
            '[庆 祝]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Party.png" id="庆祝" class="emoji_img">',
            '[礼物]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_78@2x.png" id="礼物" class="emoji_img">',
            '[红包]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_09.png" id="红包" class="emoji_img">',
            '[發]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_16.png" id="發" class="emoji_img">',
            '[福]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/2_15.png" id="福" class="emoji_img">',
            '[烟花]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Fireworks.png" id="烟花" class="emoji_img">',
            '[爆竹]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Firecracker.png" id="爆竹" class="emoji_img">',
            '[猪头]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_63@2x.png" id="猪头" class="emoji_img">',
            '[跳跳]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_93@2x.png" id="跳跳" class="emoji_img">',
            '[发抖]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_94@2x.png" id="发抖" class="emoji_img">',
            '[转圈]': '<img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/Expression/Expression_96@2x.png" id="转圈" class="emoji_img">'}
        from re import findall
        for index, message in enumerate(messages):
            type_ = message[2]
            str_content = message[7]
            str_time = message[8]
            # print(type_, type(type_))
            is_send = message[4]
            # avatar = MePC().avatar_path if is_send else self.contact.avatar_path
            # avatar = avatar.replace('\\', '\\\\')
            avatar = 'myhead.png' if is_send else 'tahead.png'
            timestamp = message[5]
            self.progressSignal.emit(index)
            if type_ == 1:
                str_content = escape_js_and_html(str_content)
                if self.is_5_min(timestamp):
                    f.write(
                        f'''{{ type:0, text: '{str_time}',is_send:0,avatar_path:''}},'''
                    )

                emojiText = findall(r"(\[.+?\])", str_content)
                for emoji_text in emojiText:
                    if emoji_text in emoji:
                        str_content = str_content.replace(emoji_text, emoji[emoji_text])
                f.write(
                    f'''{{ type:{type_}, text: '{str_content}',is_send:{is_send},avatar_path:'{avatar}'}},'''
                )
            elif type_ == 3:
                import re
                pattern1 = r'<msg><img length="\d+" hdlength="0" /><commenturl></commenturl></msg>'
                pattern2 = r'<msg><img /></msg>'
                match = re.search(pattern1, str_content)
                if match:
                    continue
                match = re.search(pattern2, str_content)
                if match:
                    continue
                image_path = hard_link_db.get_image(content=str_content, thumb=False)
                image_path = path.get_relative_path(image_path, base_path=f'/data/聊天记录/{self.contact.remark}/image')
                image_path = image_path.replace('\\', '/')
                # print(f"tohtml:---{image_path}")
                if self.is_5_min(timestamp):
                    f.write(
                        f'''{{ type:0, text: '{str_time}',is_send:0,avatar_path:''}},'''
                    )
                f.write(
                    f'''{{ type:{type_}, text: '{image_path}',is_send:{is_send},avatar_path:'{avatar}'}},'''
                )
        html_end = '''
];
    function renderMessages(messages) {
        for (const message of messages) {
            const messageElement = document.createElement('div');
            if (message.type == 1){
                if (message.is_send == 1){
                messageElement.className = "item item-right";
                messageElement.innerHTML = `<div class='bubble bubble-right'>${message.text}</div><div class='avatar'><img src="${message.avatar_path}" /></div>`
            }
            else if(message.is_send==0){
                messageElement.className = "item item-left";
                messageElement.innerHTML = `<div class='avatar'><img src="${message.avatar_path}" /></div><div class='bubble bubble-right'>${message.text}</div>`
            }
            }
            else if(message.type == 0){
                messageElement.className = "item item-center";
                messageElement.innerHTML = `<span>${message.text}</span>`
            }
            else if (message.type == 3){
                if (message.is_send == 1){
                messageElement.className = "item item-right";
                messageElement.innerHTML = `<div class='chat-image'><img src="${message.text}" /></div><div class='avatar'><img src="${message.avatar_path}" /></div>`
            }
            else if(message.is_send==0){
                messageElement.className = "item item-left";
                messageElement.innerHTML = `<div class='avatar'><img src="${message.avatar_path}" /></div><div class='chat-image'><img src="${message.text}" /></div>`
            }
            }
            chatContainer.appendChild(messageElement);
        }
    }


  const itemsPerPage = 100; // 每页显示的元素个数
  let currentPage = 1; // 当前页

  function renderPage(page) {
    const container = document.getElementById('chat-container');
    container.innerHTML = ''; // 清空容器

    // 计算当前页应该显示的元素范围
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    console.log(page);
    // 从数据列表中取出对应范围的元素并添加到容器中
    for (let i = startIndex; i < endIndex && i < chatMessages.length; i++) {
        const message = chatMessages[i];
        const messageElement = document.createElement('div');
            if (message.type == 1){
                if (message.is_send == 1){
                messageElement.className = "item item-right";
                messageElement.innerHTML = `<div class='bubble bubble-right'>${message.text}</div><div class='avatar'><img src="${message.avatar_path}" /></div>`
            }
            else if(message.is_send==0){
                messageElement.className = "item item-left";
                messageElement.innerHTML = `<div class='avatar'><img src="${message.avatar_path}" /></div><div class='bubble bubble-right'>${message.text}</div>`
            }
            }
            else if(message.type == 0){
                messageElement.className = "item item-center";
                messageElement.innerHTML = `<span>${message.text}</span>`
            }
            else if (message.type == 3){
                if (message.is_send == 1){
                messageElement.className = "item item-right";
                messageElement.innerHTML = `<div class='chat-image' ><img src="${message.text}" onclick="showModal(this)"/></div><div class='avatar'><img src="${message.avatar_path}" /></div>`
            }
            else if(message.is_send==0){
                messageElement.className = "item item-left";
                messageElement.innerHTML = `<div class='avatar'><img src="${message.avatar_path}"/></div><div class='chat-image'><img src="${message.text}" onclick="showModal(this)"/></div>`
            }
            }
            chatContainer.appendChild(messageElement);
    }
    updatePaginationInfo();
  }

  function prevPage() {
    if (currentPage > 1) {
      currentPage--;
      renderPage(currentPage);
    }
  }

  function nextPage() {
    const totalPages = Math.ceil(chatMessages.length / itemsPerPage);
    if (currentPage < totalPages) {
      currentPage++;
      renderPage(currentPage);
    }
  }
  function updatePaginationInfo() {
    const totalPages = Math.ceil(chatMessages.length / itemsPerPage);
    const paginationInfo = document.getElementById('paginationInfo');
    paginationInfo.textContent = `共 ${totalPages} 页，当前第 ${currentPage} 页`;
  }
  function gotoPage() {
    const totalPages = Math.ceil(chatMessages.length / itemsPerPage);
    const inputElement = document.getElementById('gotoPageInput');
    const targetPage = parseInt(inputElement.value);

    if (targetPage >= 1 && targetPage <= totalPages) {
      currentPage = targetPage;
      renderPage(currentPage);
    } else {
      alert('请输入有效的页码');
    }
  }

  // 初始化页面
  renderPage(currentPage);
</script>

<script>
   function showModal(image) {
      var modal = document.getElementById("modal");
      var modalImage = document.getElementById("modal-image");
      modal.style.display = "block";
      modalImage.src = image.src;
      console.log(image.src);
   }
 
   function hideModal() {
      var modal = document.getElementById("modal");
      modal.style.display = "none";
   }
</script>
</body>
</html>
'''
        f.write(html_end)
        f.close()
        self.okSignal.emit(1)

    def run(self):
        if self.output_type == Output.DOCX:
            return
        elif self.output_type == Output.CSV:
            self.to_csv()
        elif self.output_type == Output.HTML:
            self.to_html_()
        elif self.output_type == Output.CSV_ALL:
            self.to_csv_all()

    def cancel(self):
        self.requestInterruption()
