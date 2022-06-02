import json
import random
import string
import sys

# Read input into binary string
data = sys.stdin.readlines()
data = json.loads("".join(data).replace("\n", ""))

alphabet = string.ascii_uppercase + string.digits

body = data["Notification"]["Body"]


def randomize(input):
    return "".join(random.choices(alphabet, k=len(str(input))))


if "Ticket" in body:
    body["Ticket"]["TicketID"] = randomize(body["Ticket"]["TicketID"])

body["EmailId"] = randomize(body["EmailId"])
body["ClientId"] = randomize(body["ClientId"])

if random.randint(0, 100) > 90:
    body["ParentID"] = randomize(body["EmailId"])
else:
    body.pop("ParentID", None)

data["Notification"]["Body"] = body

print(json.dumps(data), end="")
