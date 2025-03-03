import sys
import random
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QTextEdit
from PyQt5.QtCore import Qt

# 生成随机邮件数据
def generate_random_emails(num_emails):
    subjects = ["项目进展汇报", "会议邀请", "技术分享", "培训通知", "活动公告"]
    senders = ["team1@example.com", "team2@example.com", "team3@example.com", "team4@example.com", "team5@example.com"]
    contents = ["项目已经完成了 50%", "本周三下午 3 点开会", "分享最新的技术趋势", "参加培训可获得证书", "周末有户外活动"]
    emails = []
    start_date = datetime.now() - timedelta(days=30)

    for i in range(num_emails):
        email = {
            "id": i + 1,
            "subject": random.choice(subjects),
            "sender": f"发件人 <{random.choice(senders)}>",
            "date": (start_date + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M"),
            "content": random.choice(contents)
        }
        emails.append(email)
    return emails

# 不同文件夹的虚拟邮件数据
folder_emails = {
    "Inbox": generate_random_emails(50),
    "垃圾邮件": [],
    "订阅邮件": []
}

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")
        layout.addWidget(self.username_input)

        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # 登录按钮
        login_button = QPushButton("登录")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)
        self.setWindowTitle("登录")
        self.setGeometry(300, 300, 300, 200)

    def login(self):
        # 这里简单模拟登录成功，实际应用中需要验证用户名和密码
        username = self.username_input.text()
        password = self.password_input.text()
        if username and password:
            self.close()
            self.mail_window = MailWindow()
            self.mail_window.show()

class MailWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_folder = "Inbox"
        self.current_page = 0
        self.items_per_page = 15
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        # 左侧文件夹列表，显示文件夹下邮件数量
        self.folder_list = QListWidget()
        for folder, emails in folder_emails.items():
            item = QListWidgetItem(f"{folder} ({len(emails)})")
            self.folder_list.addItem(item)
        self.folder_list.itemClicked.connect(self.show_emails)
        layout.addWidget(self.folder_list)

        # 右侧邮件列表
        self.email_list = QListWidget()
        self.email_list.setSelectionMode(QListWidget.MultiSelection)  # 设置多选模式
        layout.addWidget(self.email_list)

        # 分页布局
        self.page_layout = QHBoxLayout()
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(self.page_layout)

        # 退出按钮
        logout_button = QPushButton("退出")
        logout_button.clicked.connect(self.logout)
        main_layout.addWidget(logout_button)

        self.setLayout(main_layout)
        self.setWindowTitle("邮箱客户端")
        self.setGeometry(300, 300, 800, 600)

        # 初始显示收件箱邮件
        self.show_emails(self.folder_list.item(0))

    def show_emails(self, item):
        folder_name = item.text().split(" (")[0]
        self.current_folder = folder_name
        self.current_page = 0
        self.update_email_list()
        self.update_page_buttons()

    def update_email_list(self):
        emails = folder_emails[self.current_folder]
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        displayed_emails = emails[start_index:end_index]

        self.email_list.clear()
        for email in displayed_emails:
            item = QListWidgetItem(f"{email['subject']} - {email['sender']}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.email_list.addItem(item)

    def update_page_buttons(self):
        # 清空分页按钮
        for i in reversed(range(self.page_layout.count())):
            widget = self.page_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        emails = folder_emails[self.current_folder]
        total_pages = (len(emails) + self.items_per_page - 1) // self.items_per_page

        for page in range(total_pages):
            page_button = QPushButton(str(page + 1))
            if page == self.current_page:
                page_button.setStyleSheet("background-color: lightblue")
            page_button.clicked.connect(lambda _, p=page: self.change_page(p))
            self.page_layout.addWidget(page_button)

    def change_page(self, page):
        self.current_page = page
        self.update_email_list()
        self.update_page_buttons()

    def logout(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
