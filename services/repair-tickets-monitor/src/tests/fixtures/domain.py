from typing import Callable

from pytest import fixture

from application.domain.asset import AssetId


@fixture(scope="function")
def make_asset_id() -> Callable[..., AssetId]:
    def builder(
        service_number: str = "any_service_number",
        client_id: int = hash("any_client_id"),
        site_id: int = hash("any_site_id")
    ) -> AssetId:
        return AssetId(service_number, client_id, site_id)

    return builder
