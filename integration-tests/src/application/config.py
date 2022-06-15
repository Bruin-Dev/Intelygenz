from typing import Dict, Optional

from application.servers.grpc.email_tagger.email_tagger import EmailTaggerServer
from application.servers.grpc.grpc import GrpcServer
from application.servers.grpc.rta.rta import RtaServer
from pydantic import BaseSettings

http_proxies: Dict[int, Optional[str]] = {8001: None, 8002: None}
grpc_servers: Dict[int, GrpcServer] = {
    5001: EmailTaggerServer(proxy=None),
    5002: RtaServer(proxy=None),
}


class Settings(BaseSettings):
    notify_email_key = "dev-shared-secret-body-signature"
    notify_email_url = "http://email-tagger-monitor:5000/api/email-tagger-webhook/email"


settings = Settings()
