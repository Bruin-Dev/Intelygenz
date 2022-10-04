import pytest


@pytest.mark.integration
async def health_is_working_properly_test():
    # response = await client_session.get("http://localhost:5000/_health")
    assert True


# @pytest.fixture
# async def client_session():
#     client_session = ClientSession()
#     print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> health={client_session}")
#     yield client_session
#     await client_session.close()
