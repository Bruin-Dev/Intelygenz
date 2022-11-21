import json
from framework.nats.models import Connection
from framework.nats.client import Client
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from redis import Redis
from dataclasses import asdict

r = Redis()
rs = RedisStorage(r)
nc = Client(rs)
conn = Connection()
await nc.connect(**asdict(conn))

ticket_ids = list(set(
    ...
))

details_by_id = {}
for t in ticket_ids:
    resp = await nc.request(subject="bruin.ticket.details.request", payload=json.dumps({"request_id": 123, "body": {"ticket_id": t}}).encode(), timeout=60)
    data = json.loads(resp.data)
    if data['status'] != 200:
        print(f"Failed to get details for ticket {t}")
    else:
        print(f'Got details for ticket {t}')
        details_by_id[t] = data['body']

for t, d in details_by_id.items():
    for d_item in d['ticketDetails']:
        resp = await nc.request(subject="bruin.ticket.status.resolve", payload=json.dumps({"request_id": 123, "body": {"ticket_id": t, "detail_id": d_item['detailID']}}).encode(), timeout=60)
        data = json.loads(resp.data)
        print(f"Ticket {t}: {data}")
