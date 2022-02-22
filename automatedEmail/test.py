# Install Courier SDK: pip install trycourier
import pandas as pd
from trycourier import Courier
import config


df = pd.read_csv("data/test.csv")

client = Courier(auth_token=config.AUTH_TOKEN)


def sendEmail(email, suffix, name):
    resp = client.send_message(
        message={
            "to": {
                "email": email,
            },
            "template": "0BYSNHS4S64362GEPS31EZQDX060",
            "data": {
                "Suffix": suffix,
                "Name": name,
            },
        },
    )

    return resp


fullName = []
requestId = []
employeeId = []

for i, row in df.iterrows():
    email = row['Email']
    title = row['TitleNew']

    if title == 'Lecturer':
        suffix = None
        name = row['CleanName']
    else:
        suffix = 'Dr.'
        name = row['LastName']

    resp = sendEmail(email, suffix, name)
    print(f'Email sent to {name}')

    fullName.append(name)
    requestId.append(resp['requestId'])
    employeeId.append(row['Id'])
