from to163 import EmailClient

user = 'jason_lu06@163.com'
pwd = 'ZVRcHrwZmW5S5pd6'

mail = EmailClient(user, pwd)
mail.login()
# mail.select_folder('inbox')
mail.save_emails_to_local('inbox','./')
