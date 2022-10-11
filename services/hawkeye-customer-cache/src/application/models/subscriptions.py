from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class GetCustomers(Subscription):
    subject: str = "hawkeye.customer.cache.get"
    queue: str = "customer_cache"
