from typing import Dict, Optional

from application.servers.grpc.email_tagger.email_tagger import EmailTaggerServer
from application.servers.grpc.grpc import GrpcServer
from application.servers.grpc.rta.rta import RtaServer
from pydantic.env_settings import BaseSettings

# http proxies dict. It maps a port to an optional host.
# If any host was declared, unhandled requests will be proxied to the declared host.
# Otherwise, a default or crafted response will be returned, depending of the scenario implementation.
http_proxies: Dict[int, Optional[str]] = {
    8001: None,
    8002: None,
}

# grpc proxies dict. It maps a port to an optional host.
# If any host was declared, unhandled requests will be proxied to the declared host.
# Otherwise, a default or crafted response will be returned, depending of the scenario implementation.
grpc_servers: Dict[int, GrpcServer] = {
    50001: EmailTaggerServer(proxy=None),
    50002: RtaServer(proxy=None),
}


# Generic settings
class Settings(BaseSettings):
    notify_key = "dev-shared-secret-body-signature"
    notify_email_url = "http://email-tagger-monitor:5000/api/email-tagger-webhook/email"
    notify_ticket_url = "http://email-tagger-monitor:5000/api/email-tagger-webhook/ticket"


settings = Settings()
