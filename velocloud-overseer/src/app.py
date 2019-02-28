from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient
import velocloud
import os


def get_all_edges_by_enterprise():
    velocloud.configuration.verify_ssl = False
    client = velocloud.ApiClient(host=os.environ["VELOCLOUD_HOST"])
    client.authenticate(os.environ["VELOCLOUD_USER"], os.environ["VELOCLOUD_PASS"], operator=True)
    api = velocloud.AllApi(client)
    try:
        # res = api.monitoringGetAggregates(body={})
        # enterprises = list()
        # for enterprise in res._enterprises:
        #     enterprises.append(enterprise._id)
        enterprises = [1]
        edges_by_enterprise = list()
        for enterprise in enterprises:
            fulledges = api.enterpriseGetEnterpriseEdges({"enterpriseId": enterprise})
            for edge in fulledges:
                new_edge = {"enterpriseId": enterprise, "id": edge.id}
                edges_by_enterprise.append(new_edge)
    except velocloud.rest.ApiException as e:
        print(e)
    return edges_by_enterprise


async def send_to_nats(edges):
    publisher = NatsStreamingClient(config, "velocloud-overseer-publisher")
    await publisher.connect_to_nats()
    for edge in edges:
        print(f'Edge discovered with data {edge}! Sending it to NATS edge.status.task queue')
        await publisher.publish("edge.status.task", repr(edge))
    await publisher.close_nats_connections()


@async_to_sync
async def run():
    edges = get_all_edges_by_enterprise()
    await send_to_nats(edges)


if __name__ == '__main__':
    print("Velocloud overseer starting...")
    run()
