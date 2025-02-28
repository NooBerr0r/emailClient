from datetime import datetime
import imaplib
import email
from email.header import decode_header
import re
import logging

class EmailClient:
    def __init__(self, user=None, password=None):
        self.user = user
        self.password = password
        self.mail = None

    class Email:
        def __init__(self, email_id, subject, sender, date, content):
            """
            初始化邮件对象

            :param email_id: 邮件的唯一标识符
            :param subject: 邮件的主题
            :param sender: 邮件的发件人
            :param date: 邮件的发送日期
            :param content: 邮件的内容
            """
            try:
                self.date = self._parse_date(date)
            except ValueError:
                print(f"日期格式错误: {date}，使用原始日期。")
                self.date = date
            try:
                self.subject = self._decode_email_header(subject)
            except UnicodeDecodeError:
                print(f"无法解码主题: {subject}，使用原始主题。")
                self.subject = subject
            self.email_id = email_id
            self.sender = sender
            self.content = content

        def _parse_date(self, date):
            """
            解析日期字符串并格式化为 '%Y-%m-%d %H:%M:%S'

            :param date: 日期字符串
            :return: 格式化后的日期字符串
            """
            date_str = re.sub(r' \(CST\)', '', date)
            datetime_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        def _decode_email_header(self, header):
            '''解码邮件头'''
            decoded_header = decode_header(header)[0]
            if isinstance(decoded_header, tuple):
                part, charset = decoded_header
                if isinstance(part, bytes):  # 检查是否为字节串
                    if charset:  # 如果有字符集，按指定字符集解码
                        decoded_part = part.decode(charset)
                    else:  # 没有指定字符集时尝试UTF-8解码，或选择其他策略
                        decoded_part = part.decode('utf-8', errors='replace')
                else:  # 如果已经是字符串，直接使用
                    decoded_part = part
                return decoded_part
            else:
                # 如果解码结果不是元组，直接将其转换为字符串返回
                return str(decoded_header)

        def __str__(self):
            """
            返回邮件信息的字符串表示
            """
            return f"邮件ID: {self.email_id}\n主题: {self.subject}\n发件人: {self.sender}\n日期: {self.date}\n内容: {self.content}"

    def login(self):
        '''登录邮箱'''
        if not self.user or not self.password:
            print("用户名或密码未提供")
            return None

        try:
            self.mail = imaplib.IMAP4_SSL(port=993, host='imap.163.com')
            typ,dat = self.mail.login(self.user, self.password)
            # print(typ, dat)
            if typ == 'OK':
                print(f"登录成功: {self.user}")
            else:
                print(dat[0].decode())
                return None
        except imaplib.IMAP4.error as e:
            print(f"登录失败: {e}")
            return None

        try:
            imaplib.Commands["ID"] = ('AUTH',)
            args = ("name", self.user, "contact", self.user, "version", "1.0.0", "vendor", "myclient")
            self.mail._simple_command("ID", str(args).replace(",", "").replace("'", "\""))
        except imaplib.IMAP4.error as e:
            print(f"发送 ID 命令失败: {e}")
        
        return self.mail

    def select_folder(self, folder):
        '''选择文件夹'''
        if self.mail:
            try:
                typ, dat = self.mail.select(folder)
                if typ == 'OK':
                    print(f"已选择文件夹 {folder}")
                    print(f"邮件数量: {dat[0].decode()}")
                    return typ, dat
                else:
                    print(dat[0].decode())
            except imaplib.IMAP4.error as e:
                print(f"选择文件夹 {folder} 失败: {e}")
                return None
        return None

    def create_folder(self, folder_name):
        '''创建文件夹'''
        if self.mail:
            try:
                typ, dat = self.mail.create(folder_name)
                if typ == 'OK':
                    print(f"文件夹 {folder_name} 已成功创建")
                    return True
                else:
                    print(f"创建文件夹 {folder_name} 时收到非 OK 响应: {dat[0].decode()}")
                    return False
            except imaplib.IMAP4.error as e:
                print(f"创建文件夹 {folder_name} 失败，发生 IMAP4 错误: {e}")
                return False
        else:
            print("未登录邮箱，无法创建文件夹。")
            return False
        
    def delete_folder(self, folder_name):
        '''删除文件夹'''
        if self.mail:
            try:
                typ, dat = self.mail.delete(folder_name)
                # print(typ, dat)
                if typ == 'OK':
                    print(f"文件夹 {folder_name} 已删除")
                    return True
                else:
                    print(f"删除文件夹 {folder_name} 时收到非 OK 响应:{dat[0].decode()}")
                    return False
            except imaplib.IMAP4.error as e:
                print(f"删除文件夹 {folder_name} 失败: {e}")
                return False
        else:
            print("未登录邮箱，无法删除文件夹。")
            return False

    def list_folders(self):
        '''列出所有文件夹'''
        folder_list = []
        if self.mail:
            try:
                typ, data = self.mail.list()
                if typ == 'OK':
                    # 使用正则表达式提取文件夹名称
                    pattern = r'"([^"]+)"$'
                    for folder_info in data:
                        match = re.search(pattern, folder_info.decode())
                        if match:
                            folder_name = match.group(1)
                            folder_list.append(folder_name)
                return folder_list
            except imaplib.IMAP4.error as e:
                print(f"列出文件夹失败: {e}")
                return []  # 出现异常时返回空列表
        return []  # 未登录时返回空列表
    
    def search_emails(self, criteria):
        '''
        搜索邮件
        :param criteria: 搜索条件，例如 'FROM "sender@example.com"'
        :return: 搜索到的邮件 ID 列表
        '''
        if self.mail:
            try:
                typ, dat = self.mail.search(None, criteria)
                if typ == 'OK':
                    email_ids = dat[0].decode().split()
                    return email_ids
                else:
                    print(dat[0].decode())
                    return []
            except imaplib.IMAP4.error as e:
                print(f"搜索邮件失败: {e}")
                return []
        else:
            print("未登录邮箱，无法搜索邮件。")
            return []
        
    # 配置日志记录
    logging.basicConfig(level=logging.ERROR)
    
    def fetch_email(self, email_id):
            '''
            获取邮件内容
            :param email_id: 要获取的邮件的ID
            :return: 邮件对象
            '''
            if self.mail:
                try:
                    typ, dat = self.mail.fetch(email_id, '(RFC822)')
                    if typ == 'OK':
                        msg = email.message_from_bytes(dat[0][1])
                        subject = msg['Subject']
                        sender = msg['From']
                        date = msg['Date']
                        content = ''
    
                        # 获取邮件内容
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == 'text/plain':
                                    charset = part.get_content_charset() or 'utf-8'
                                    try:
                                        content = part.get_payload(decode=True).decode(charset)
                                    except UnicodeDecodeError:
                                        logging.error(f"无法解码邮件内容 (ID: {email_id})，使用默认字符集 'utf-8'。")
                                        content = part.get_payload(decode=True).decode('utf-8', errors='replace')
                                    break
                        else:
                            charset = msg.get_content_charset() or 'utf-8'
                            try:
                                content = msg.get_payload(decode=True).decode(charset)
                            except UnicodeDecodeError:
                                logging.error(f"无法解码邮件内容 (ID: {email_id})，使用默认字符集 'utf-8'。")
                                content = msg.get_payload(decode=True).decode('utf-8', errors='replace')
    
                        return self.Email(email_id, subject, sender, date, content)
                    else:
                        logging.error(f"获取邮件 (ID: {email_id}) 时收到非 OK 响应: {dat[0].decode()}")
                        return None
                except imaplib.IMAP4.error as e:
                    logging.error(f"获取邮件 (ID: {email_id}) 失败: {e}")
                    return None
            else:
                logging.error("未登录邮箱，无法获取邮件。")
                return None

    def copy_email(self, email_id, target_folder):
        '''
        复制邮件到指定文件夹
        :param email_id: 要复制的邮件的ID
        :param target_folder: 目标文件夹的名称
        :return: 复制成功返回 True，失败返回 False
        '''
        # 检查是否已经登录到邮箱
        if self.mail:
            try:
                typ, dat = self.mail.copy(email_id, target_folder)
                if typ == 'OK':
                    print(f"邮件已成功复制到 {target_folder} 文件夹")
                    return True
                else:
                    print(dat[0].decode())
                    return False
            except imaplib.IMAP4.error as e:    
                print(f"复制邮件失败: {e}")
                return False
        else:
            print("未登录邮箱，无法复制邮件。")
            return False
    def logout(self):
        '''退出登录'''
        if self.mail:
            typ,dat = self.mail.logout()
            print(typ, dat)