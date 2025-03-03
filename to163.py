from datetime import datetime
import imaplib
import email
from email.header import decode_header
import re
import logging
import time
import os
import json

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
            return datetime_obj.strftime('%Y-%m-%d')
        def _decode_email_header(self, header):
            '''解码邮件头'''
            if header is None:
                return ""  # Return an empty string if the header is None
            decoded_header = decode_header(header)[0]
            if isinstance(decoded_header, tuple):
                part, charset = decoded_header
                if isinstance(part, bytes):  # 检查是否为字节串
                    try:
                        # 尝试使用指定的字符集进行解码
                        if charset and charset.lower() != 'unknown-8bit':
                            decoded_part = part.decode(charset)
                        else:
                            # 若字符集为 unknown-8bit 或为空，使用 utf-8 并采用 replace 策略解码
                            decoded_part = part.decode('utf-8', errors='replace')
                    except (UnicodeDecodeError, LookupError):
                        # 若解码失败，使用 utf-8 并采用 replace 策略解码
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
    def save_emails_to_local(self, folder, save_path):
        """
        按邮箱文件夹获取所有邮件并以 JSON 格式保存在本地
        :param folder: 邮箱文件夹名称
        :param save_path: 保存邮件的本地路径
        :return: 成功保存的邮件数量
        """
        if not self.mail:
            print("未登录邮箱，无法获取邮件。")
            return 0
    
        # 选择文件夹
        result = self.select_folder(folder)
        if not result:
            return 0
    
        # 获取所有邮件的ID
        email_ids = self.search_emails('ALL')
        if not email_ids:
            print(f"在文件夹 {folder} 中未找到邮件。")
            return 0
    
        # 创建保存路径
        if not os.path.exists(save_path):
            os.makedirs(save_path)
    
        # 生成文件名
        filename = f"{folder}.json"
        file_path = os.path.join(save_path, filename)
    
        saved_count = 0
        # 以追加模式打开文件，写入左中括号表示开始一个 JSON 数组
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('[')
            first_email = True
            for email_id in email_ids:
                # 获取邮件内容
                email_obj = self.fetch_email(email_id)
                if email_obj:
                    # 确保所有值都是 JSON 可序列化的
                    email_dict = {
                        "email_id": str(email_obj.email_id),
                        # 调用正确的解码方法
                        "subject": str(EmailClient.Email._decode_email_header(email_obj, email_obj.subject)),
                        "sender": str(EmailClient.Email._decode_email_header(email_obj, email_obj.sender)),
                        "date": str(email_obj.date),
                        "content": str(email_obj.content)
                    }
                    # 如果不是第一封邮件，先写入逗号分隔
                    if not first_email:
                        f.write(',')
                    else:
                        first_email = False
                    # 将邮件信息以 JSON 格式写入文件
                    json.dump(email_dict, f, ensure_ascii=False, indent=4)
                    saved_count += 1
                    print(f"已保存邮件: {email_obj.subject}")
    
                # 添加小的延迟，避免瞬间完成请求
                time.sleep(0.5)
            # 写入右中括号表示 JSON 数组结束
            f.write(']')
    
        print(f"共保存 {saved_count} 封邮件到 {file_path}。")
        return saved_count
    
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