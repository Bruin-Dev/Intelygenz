from typing import Callable

from pytest import fixture

from application.domain.asset import AssetId


@fixture(scope="function")
def make_asset_id() -> Callable[..., AssetId]:
    def builder(
        client_id: str = "any_client_id",
        site_id: str = "any_site_id",
        service_number: str = "any_service_number"
    ) -> AssetId:
        return AssetId(client_id=client_id, site_id=site_id, service_number=service_number)

    return builder
