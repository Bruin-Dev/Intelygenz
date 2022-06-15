import asyncio
import logging
import sys

from application.config import grpc_servers, http_proxies
from application.servers.http import http

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        "[%(asctime)s][%(levelname)8s][%(module)18s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
)

log = logging.getLogger("application")
log.addHandler(handler)


async def start():
    # Add ASGI server task
    tasks = [http.start(http_proxies)]

    # Add a task for each GRPC server
    for port, server in grpc_servers.items():
        tasks.append(server.start(port))

    # Wait for all tasks
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(start())
