import pytest
from island_backup.network import _Client




proxy_server_url = "http://127.0.0.1:7890"

@pytest.mark.asyncio
async def test_proxy_client_init():
    client = _Client()
    assert client._session is None
    await client.init_client()
    assert client._session is not None


# @pytest.mark.asyncio
# async def test_proxy_request():
#     from island_backup.network import client
#     await client.init_client(proxy=proxy_server_url)
#     await client.verify_proxy_server()
    

    







