'''Unit tests for Vikunja API client.'''

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from src.client.vikunja_client import VikunjaClient


@pytest.fixture
def mock_env(monkeypatch):
    '''Mock environment variables.'''
    monkeypatch.setenv("VIKUNJA_URL", "https://test.example.com")
    monkeypatch.setenv("VIKUNJA_TOKEN", "test_token_12345")


@pytest.fixture
def client(mock_env):
    '''Create a test client instance.'''
    return VikunjaClient()


@pytest.mark.asyncio
async def test_client_initialization(client):
    '''Test client initialization with environment variables.'''
    assert client.base_url == "https://test.example.com"
    assert client.token == "test_token_12345"
    assert client.api_base == "https://test.example.com/api/v1"
    assert client._client is None


@pytest.mark.asyncio
async def test_client_initialization_strips_trailing_slash(monkeypatch):
    '''Test that trailing slashes are removed from base URL.'''
    monkeypatch.setenv("VIKUNJA_URL", "https://test.example.com/")
    monkeypatch.setenv("VIKUNJA_TOKEN", "test_token")

    client = VikunjaClient()
    assert client.base_url == "https://test.example.com"
    assert client.api_base == "https://test.example.com/api/v1"


@pytest.mark.asyncio
async def test_get_client_creates_async_client(client):
    '''Test that get_client() creates httpx.AsyncClient with correct headers.'''
    async_client = await client.get_client()

    assert isinstance(async_client, httpx.AsyncClient)
    assert async_client.headers["Authorization"] == "Bearer test_token_12345"
    assert async_client.headers["Content-Type"] == "application/json"
    assert client._client is async_client


@pytest.mark.asyncio
async def test_get_client_reuses_existing_client(client):
    '''Test that get_client() reuses existing client instance.'''
    first_client = await client.get_client()
    second_client = await client.get_client()

    assert first_client is second_client


@pytest.mark.asyncio
async def test_request_successful_get(client):
    '''Test successful GET request.'''
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "title": "Test Task"}
    mock_response.raise_for_status = MagicMock()

    with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        result = await client.request("GET", "tasks/1")

        assert result == {"id": 1, "title": "Test Task"}
        mock_request.assert_called_once()
        assert mock_request.call_args[0][0] == "GET"
        assert "tasks/1" in mock_request.call_args[0][1]


@pytest.mark.asyncio
async def test_request_successful_post_with_json(client):
    '''Test successful POST request with JSON payload.'''
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 2, "title": "New Task"}
    mock_response.raise_for_status = MagicMock()

    payload = {"title": "New Task", "description": "Test"}

    with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        result = await client.request("POST", "tasks", json_data=payload)

        assert result == {"id": 2, "title": "New Task"}
        assert mock_request.call_args[1]["json"] == payload


@pytest.mark.asyncio
async def test_request_with_params(client):
    '''Test request with query parameters.'''
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()

    with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        await client.request("GET", "tasks", params={"page": 1, "per_page": 20})

        assert mock_request.call_args[1]["params"] == {"page": 1, "per_page": 20}


@pytest.mark.asyncio
async def test_request_handles_404_error(client):
    '''Test that 404 errors are raised properly.'''
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=mock_response
        )

        with pytest.raises(httpx.HTTPStatusError):
            await client.request("GET", "tasks/99999")


@pytest.mark.asyncio
async def test_request_handles_401_error(client):
    '''Test that 401 authentication errors are raised.'''
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized",
            request=MagicMock(),
            response=mock_response
        )

        with pytest.raises(httpx.HTTPStatusError):
            await client.request("GET", "tasks")


@pytest.mark.asyncio
async def test_request_retries_on_429_rate_limit(client):
    '''Test exponential backoff retry on 429 rate limit.'''
    mock_response_429 = MagicMock()
    mock_response_429.status_code = 429
    mock_response_429.text = "Too Many Requests"

    mock_response_success = MagicMock()
    mock_response_success.json.return_value = {"id": 1}
    mock_response_success.raise_for_status = MagicMock()

    with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
        # First call raises 429, second succeeds
        mock_request.side_effect = [
            httpx.HTTPStatusError("429", request=MagicMock(), response=mock_response_429),
            mock_response_success
        ]

        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await client.request("GET", "tasks/1")

            assert result == {"id": 1}
            assert mock_request.call_count == 2
            mock_sleep.assert_called_once()


@pytest.mark.asyncio
async def test_request_max_retries_on_persistent_429(client):
    '''Test that request fails after max retries on persistent 429.'''
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Too Many Requests"

    with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = httpx.HTTPStatusError(
            "429",
            request=MagicMock(),
            response=mock_response
        )

        with patch('asyncio.sleep', new_callable=AsyncMock):
            with pytest.raises(httpx.HTTPStatusError):
                await client.request("GET", "tasks")

            # Should retry 3 times total
            assert mock_request.call_count == 3


@pytest.mark.asyncio
async def test_close_closes_http_client(client):
    '''Test that close() properly closes the HTTP client.'''
    await client.get_client()

    with patch.object(httpx.AsyncClient, 'aclose', new_callable=AsyncMock) as mock_close:
        await client.close()
        mock_close.assert_called_once()


@pytest.mark.asyncio
async def test_close_handles_none_client(client):
    '''Test that close() handles case where client is None.'''
    # Should not raise exception
    await client.close()
    assert client._client is None
