import smtplib
import email.message
import datetime

from_addr = 'chsharemovie@gmail.com'
from_passwd = 'share1234'

def create_mail_content(reminders):
    html = """
    <html>
     
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>LIC Policy Payment Reminder</title>
    <style type="text/css">
    #policys {
        font-family: Tahoma, Geneva, sans-serif;
        border-collapse: collapse;
        width: 100%;
    }
    #policys th {
        padding: 4px;
        text-align: left;
        background-color: darkblue;
        color: white;
        font-size: 120%;
        border: 2px solid #ddd;
    }
    #policys tr td {
        font-size: 110%;
        border: 2px solid #ddd;
    }
    
    body {
        font-size: 110%;
        font-family: Tahoma, Geneva, sans-serif;
    }
    </style>
    </head>
     
    <body>
    <p>Dear Sir/Madam,<br/><br/>
    Greetings from Jayasri Associates.<br/><br/>
    I am pleased to bring to your kind notice about the renewal of your LIC Policies. I have tabulated here under the details of premium amount for your reference and effecting payment thereto.<br/><br/>
    The Premium details are tabulated below:<br/></p>
    <table id="policys">
        <th>Name</th>
        <th>Policy No</th>
        <th>Due Date</th>
        <th>Grace Period</th>
        <th>Premium</th>
        -policy_rows-
    </table>
    <p>You may pay the premium through online and the link is given below:</p><br/>
    https://ebiz.licindia.in/D2CPM/#directpay/Premium/PremiumLanding<br/>
    <p>This is for your kind information and records.<br/><br/>
    Kindly feel free to contact me for further clarifications.<br/><br/>
    Thanking you and assuring my best services at all times.<br/><br/></p>
    <p style="color:blue;">
    ......................................................<br/>
    Trustfully Yours<br/>
    J.GANAPATHY SUBRAMANIAM<br/>
    Agent LIC of India,<br/>
    M/s.Jayasri Associates,<br/>
    Business Associates for General Insurance,<br/>
    104/2, Ranalakshmanan Nagar,<br/>
    Teachers Colony,<br/>
    Erode - 638 011.<br/>
    Mobile:98427 55445,<br/>
    Office: (0424) 2275994</p>
    </body>
    </html>
    """

    policy_row = '<tr>{}</tr>'.format('<td>{}</td>' * 5)
    policy_rows = ''
    for r in reminders:
        p = r.due.policy
        d = r.due
        due_date = d.due_date.strftime('%d/%m/%Y')
        grace_date = d.grace_date()
        policy_rows += policy_row.format(p.client.full_name(), p.number, due_date, grace_date, 'Rs. ' + str(p.premium_amount))

    return html.replace('-policy_rows-', policy_rows)

def send_reminder_mail(reminders):
    if len(reminders) == 0:
        print('No reminders pending.')
        return

    mail_addresses = {}
    for reminder in reminders:
        email_id = reminder.email
        if email_id not in mail_addresses:
            mail_addresses[email_id] = []
        mail_addresses[email_id].append(reminder)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(from_addr, from_passwd)
    except:
        print('Something went wrong...')
        raise

    for email_id, reminders in mail_addresses.items():
        msg = email.message.Message()
        # due_date = reminders[0].due.due_date
        # msg['Subject'] = "LIC policy Renewal Premium Intimation for {} {}".format(due_date.strftime('%B'), due_date.strftime('%Y'))
        msg['Subject'] = "LIC policy Renewal Premium Intimation for {}".format(datetime.datetime.now().strftime("%B %Y"))
        msg['From'] = from_addr
        msg['To'] = email_id
        html = create_mail_content(reminders)
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(html)
        try:
            server.sendmail(from_addr, email_id, msg.as_string())
            server.close()
        except:
            print('Something went wrong...')
            raise
        for r in reminders:
            r.reminder_sent = True
            r.save()

    print('Email sent!')
