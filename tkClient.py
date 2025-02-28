import tkinter as tk
from tkinter import messagebox

# 不同文件夹的虚拟邮件数据
folder_emails = {
    "Inbox": [
        {
            "id": 1,
            "subject": "重要会议通知",
            "sender": "会议组织者 <organizer@example.com>",
            "date": "2025-02-28 10:00",
            "content": "各位同事，本周将召开重要会议，请准时参加。"
        },
        {
            "id": 2,
            "subject": "项目进度更新",
            "sender": "项目负责人 <project_manager@example.com>",
            "date": "2025-02-27 14:30",
            "content": "项目目前进展顺利，预计下周完成第一阶段。"
        },
        {
            "id": 3,
            "subject": "技术分享邀请",
            "sender": "技术团队 <tech_team@example.com>",
            "date": "2025-02-26 16:15",
            "content": "诚邀大家参加本周的技术分享会。"
        }
    ],
    "垃圾邮件": [
        {
            "id": 4,
            "subject": "快速致富秘籍",
            "sender": "不明发件人 <spammer@example.com>",
            "date": "2025-02-27 12:00",
            "content": "点击链接，轻松致富！"
        },
        {
            "id": 5,
            "subject": "免费礼品领取",
            "sender": "可疑发件人 <scammer@example.com>",
            "date": "2025-02-26 11:30",
            "content": "填写表格，免费领取礼品！"
        }
    ],
    "订阅邮件": [
        {
            "id": 6,
            "subject": "最新科技资讯",
            "sender": "科技杂志 <tech_magazine@example.com>",
            "date": "2025-02-28 09:00",
            "content": "本期科技杂志带来最新的科技动态。"
        },
        {
            "id": 7,
            "subject": "时尚潮流推荐",
            "sender": "时尚杂志 <fashion_magazine@example.com>",
            "date": "2025-02-27 10:30",
            "content": "了解最新的时尚潮流。"
        }
    ]
}


class EmailClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("邮件客户端")
        self.geometry("800x600")

        # 创建文件夹选择下拉菜单
        folder_frame = tk.Frame(self)
        folder_frame.pack(side=tk.TOP, fill=tk.X)

        self.selected_folder = tk.StringVar(self)
        self.selected_folder.set("Inbox")  # 默认选择收件箱

        folder_menu = tk.OptionMenu(folder_frame, self.selected_folder, *folder_emails.keys(),
                                    command=self.change_folder)
        folder_menu.pack(side=tk.LEFT)

        # 创建搜索框和搜索按钮
        search_frame = tk.Frame(self)
        search_frame.pack(side=tk.TOP, fill=tk.X)

        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        search_button = tk.Button(search_frame, text="搜索", command=self.search_emails)
        search_button.pack(side=tk.RIGHT)

        # 创建左侧邮件列表区域
        self.email_listbox = tk.Listbox(self, width=30)
        self.email_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.populate_email_listbox(folder_emails[self.selected_folder.get()])
        self.email_listbox.bind("<<ListboxSelect>>", self.show_email_detail)

        # 创建右侧邮件详情区域
        self.detail_frame = tk.Frame(self)
        self.detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.subject_label = tk.Label(self.detail_frame, text="主题: ")
        self.subject_label.pack(pady=10)

        self.sender_label = tk.Label(self.detail_frame, text="发件人: ")
        self.sender_label.pack(pady=10)

        self.date_label = tk.Label(self.detail_frame, text="日期: ")
        self.date_label.pack(pady=10)

        self.content_text = tk.Text(self.detail_frame, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True)

    def populate_email_listbox(self, emails):
        self.email_listbox.delete(0, tk.END)
        for email in emails:
            self.email_listbox.insert(tk.END, f"{email['subject']} - {email['sender']}")

    def search_emails(self):
        keyword = self.search_entry.get().lower()
        current_folder = self.selected_folder.get()
        if keyword:
            filtered_emails = [email for email in folder_emails[current_folder] if
                               keyword in email['subject'].lower() or keyword in email['sender'].lower()]
            self.populate_email_listbox(filtered_emails)
        else:
            self.populate_email_listbox(folder_emails[current_folder])

    def show_email_detail(self, event):
        selected_index = self.email_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            # 获取当前显示的邮件列表
            current_emails = self.get_current_emails()
            email = current_emails[index]
            self.subject_label.config(text=f"主题: {email['subject']}")
            self.sender_label.config(text=f"发件人: {email['sender']}")
            self.date_label.config(text=f"日期: {email['date']}")
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, email['content'])

    def get_current_emails(self):
        keyword = self.search_entry.get().lower()
        current_folder = self.selected_folder.get()
        if keyword:
            return [email for email in folder_emails[current_folder] if
                    keyword in email['subject'].lower() or keyword in email['sender'].lower()]
        return folder_emails[current_folder]

    def change_folder(self, folder):
        self.populate_email_listbox(folder_emails[folder])


if __name__ == "__main__":
    app = EmailClient()
    app.mainloop()