from to163 import EmailClient

user = 'jason_lu06@163.com'
pwd = 'ZVRcHrwZmW5S5pd6'

mail = EmailClient(user, pwd)
mail.login()
# mail.select_folder('inbox')
# mail.save_emails_to_local('inbox','./')
mail.select_folder('Test')
mailList = mail.search_emails('All')
dateDict = {}
saveList = []
delList = []
for i in mailList:
    tmp = mail.fetch_email(i)
    print(tmp.date)
    if tmp.date not in dateDict:
        dateDict[tmp.date] = tmp.email_id
        saveList.append(tmp.email_id)
    else:
        delList.append(tmp.email_id)
print(saveList)
print(delList)
# mail.fetch_email()
mail.logout()
