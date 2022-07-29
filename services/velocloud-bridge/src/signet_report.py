import asyncio
import csv
import json
import logging
from asyncio import BoundedSemaphore
from datetime import datetime, timedelta, timezone

from application.clients.velocloud_client import VelocloudClient
from application.repositories.velocloud_repository import VelocloudRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from dateutil.relativedelta import relativedelta

scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

logging.basicConfig(level=logging.NOTSET)

velo_client = VelocloudClient(config, logging.getLogger(), scheduler)
velo_repository = VelocloudRepository(config, logging.getLogger(), velo_client)

semaphore = BoundedSemaphore(1)

total_intervals = 0
intervals_processed = 0

config_modules_by_id = {}
result_mapping = {}


async def print_row(host, enterprise_id, interval):
    async with semaphore:
        start = datetime.fromtimestamp(interval["start"] // 1000, tz=timezone.utc)
        end = datetime.fromtimestamp(interval["end"] // 1000, tz=timezone.utc)
        print(f"get_links_metric_info with host: {host} and interval: [start: {start} -> end: {end}]")

        try:
            host_links_metrics_info = await velo_repository.get_links_metric_info(host, interval)
        except Exception as e:
            print(f"ERROR calling get_links_metric_info {e}")
            return

        if host_links_metrics_info["status"] not in range(200, 300):
            print(
                f"Bad status calling get_links_metric_info. Response {host_links_metrics_info} on [start: {start} -> end: {end}] and {host}"
            )
            return

        body_host_links_metrics_info = host_links_metrics_info["body"]
        if len(body_host_links_metrics_info) == 0:
            print("Not values in the response of host_links_metrics_info")
            return

        dict_edge_links = {}
        for link in body_host_links_metrics_info:
            if not link["link"].get("edgeId"):
                print("Not edge id link")
                continue

            if link["link"]["edgeId"] not in dict_edge_links:
                dict_edge_links[link["link"]["edgeId"]] = [link]
            else:
                dict_edge_links[link["link"]["edgeId"]].append(link)

        for edge_id in dict_edge_links.keys():
            edge_full_id = {
                "host": host,
                "enterprise_id": enterprise_id,
                "edge_id": edge_id,
            }

            if edge_id not in config_modules_by_id:
                links_config_response = await velo_repository.get_links_configuration(edge_full_id)

                if links_config_response["status"] not in range(200, 300):
                    print(
                        f"Bad status calling get_links_configuration. Response {links_config_response} on "
                        f"[start: {start} -> end: {end}] and edge {edge_full_id}"
                    )
                    continue

                config_modules_by_id[edge_id] = links_config_response["body"]

            for link in dict_edge_links[int(edge_id)]:
                link_interface = link["link"]["interface"]

                if enterprise_id == link["link"]["enterpriseId"]:
                    all_links_settings = config_modules_by_id[edge_id]

                    link_settings = None
                    for settings in all_links_settings:
                        if link_interface in settings["interfaces"]:
                            link_settings = settings
                            break

                    if not link_settings:
                        print(
                            f"No config module was found for link {link_interface} of edge {edge_full_id}. "
                            "Skipping link..."
                        )
                        continue

                    current_year = start.year
                    current_month = start.month

                    edge_id_int = int(edge_id)

                    bytes_tx = int(link["bytesTx"])
                    bytes_rx = int(link["bytesRx"])
                    total_bytes = bytes_tx + bytes_rx

                    link_interface = link["link"]["interface"]

                    result_mapping.setdefault(edge_id_int, {})
                    result_mapping[edge_id_int].setdefault(current_year, {})
                    result_mapping[edge_id_int][current_year].setdefault(current_month, {})

                    link_row = result_mapping[edge_id_int][current_year][current_month].get(link_interface)
                    if not link_row:
                        report_start_date = datetime(year=current_year, month=current_month, day=1)
                        report_end_date = report_start_date + relativedelta(months=1)

                        row = [
                            f'{link["link"]["edgeId"]}',
                            f'{link["link"]["edgeName"]}',
                            f'{link["link"]["displayName"]}',
                            f'{link["link"]["interface"]}',
                            f'{link_settings["mode"]}',
                            f'{link_settings["type"]}',
                            f"{report_start_date}",
                            f"{report_end_date}",
                            bytes_tx,
                            bytes_rx,
                            total_bytes,
                        ]

                        result_mapping[edge_id_int][current_year][current_month][link_interface] = row
                    else:
                        result_mapping[edge_id_int][current_year][current_month][link_interface][-3] += bytes_tx
                        result_mapping[edge_id_int][current_year][current_month][link_interface][-2] += bytes_rx
                        result_mapping[edge_id_int][current_year][current_month][link_interface][-1] += total_bytes

    global intervals_processed
    intervals_processed += 1
    print(f"Processed {intervals_processed} out of {total_intervals} intervals")


async def process_velo_management_status(csvfile):
    # host = "mettel.velocloud.net"
    # enterprise_id = 22  # O'Reilly
    host = "metvco02.mettel.net"
    enterprise_id = 2  # Signet
    tasks = []
    init_year = 2022
    end_year = 2022
    report_start_date = datetime(year=init_year, month=7, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)
    report_end_date = datetime(year=end_year, month=8, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)

    start = report_start_date
    while start < report_end_date:
        end = start + timedelta(hours=6)  # mod this to adjust the interval
        interval = {
            "start": int(start.timestamp()) * 1000,
            "end": int(end.timestamp()) * 1000,
        }
        start = end
        tasks.append(print_row(host, enterprise_id, interval))

    global total_intervals
    total_intervals = len(tasks)
    print(f"Processing {total_intervals} intervals...")
    await asyncio.gather(*tasks)

    rows = []
    for _, rows_by_year_and_month in result_mapping.items():
        for _, rows_by_month in rows_by_year_and_month.items():
            for _, rows_by_link in rows_by_month.items():
                for _, row in rows_by_link.items():
                    rows.append(row)

    csvfile.writerows(rows)
    print("done writing rows")


async def main():
    await velo_client.instantiate_and_connect_clients()
    with open(f"./signet_usage.csv", "w") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        titles = [
            "id",
            "edge",
            "link",
            "interface",
            "mode",
            "type",
            "start",
            "end",
            "bytesTx",
            "bytesRx",
            "bytesTotal",
        ]
        print(titles)
        filewriter.writerow(titles)

        await process_velo_management_status(filewriter)
        print("done!")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
