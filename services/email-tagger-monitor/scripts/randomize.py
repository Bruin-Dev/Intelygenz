import sys
import json
import random
import string

# Read input into binary string
data = sys.stdin.readlines()
data = json.loads("".join(data).replace("\n", ""))

body = data['Notification']['Body']


def number_randomize(input):
    return ''.join(random.choices(string.digits, k=len(str(input))))

if 'Ticket' in body:
    body['Ticket']["TicketID"] = number_randomize(body['Ticket']["TicketID"])

body["EmailId"] = number_randomize(body["EmailId"])
body["ClientId"] = number_randomize(body["ClientId"])

if random.randint(0, 100) > 90:
    body["ParentID"] = number_randomize(body["EmailId"])
else:
    body.pop("ParentID", None)

data['Notification']['Body'] = body

print(json.dumps(data), end="")
