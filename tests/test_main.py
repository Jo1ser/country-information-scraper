import pytest
from httpx import AsyncClient, ASGITransport
from country_scraper.main import app


@pytest.mark.asyncio
@pytest.mark.parametrize("country_name", ["Poland", "France", "Japan", "Brazil", "Australia"])
async def test_get_country_by_name_success(country_name):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/countries/?name={country_name}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Normalize country names for comparison
    returned_names = [country['name']['common'].lower() for country in data]
    assert country_name.lower() in returned_names


@pytest.mark.asyncio
@pytest.mark.parametrize("nonexistent_country", ["NonExistentCountry", "Atlantis", "ElDorado"])
async def test_get_country_by_name_not_found(nonexistent_country):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/countries/?name={nonexistent_country}")
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == 'Country not found.'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "capital_city, expected_country",
    [
        ("Tokyo", "Japan"),
        ("Berlin", "Germany"),
        ("Canberra", "Australia"),
        ("Ottawa", "Canada"),
        ("Brasília", "Brazil"),
    ],
)
async def test_get_country_by_capital_success(capital_city, expected_country):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/countries/?capital={capital_city}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check if expected country is in the returned data
    returned_countries = [country['name']['common'] for country in data]
    assert expected_country in returned_countries


@pytest.mark.asyncio
@pytest.mark.parametrize("language_name", ["english", "spanish", "french",
                                           "japanese", "portuguese"])
async def test_get_country_by_language_success(language_name):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/countries/?language={language_name}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize("region", ["Europe", "Asia", "Africa", "Americas", "Oceania"])
async def test_get_country_by_region_success(region):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/countries/?region={region}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check that all returned countries belong to the requested region
    for country in data:
        assert country['region'] == region


@pytest.mark.asyncio
@pytest.mark.parametrize("subregion", ["Northern Europe", "Southern Asia",
                                       "Eastern Africa", "South America", "Melanesia"])
async def test_get_country_by_subregion_success(subregion):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/countries/?subregion={subregion}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check that all returned countries belong to the requested subregion
    for country in data:
        assert country['subregion'] == subregion


@pytest.mark.asyncio
@pytest.mark.parametrize("currency_code", ["USD", "EUR", "JPY", "AUD", "BRL"])
async def test_get_country_by_currency_success(currency_code):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/countries/?currency={currency_code}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check that all returned countries use the requested currency
    for country in data:
        assert currency_code in country.get('currencies', {})


@pytest.mark.asyncio
async def test_get_country_no_criteria():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/countries/")
    assert response.status_code == 400
    data = response.json()
    assert data['detail'] == 'No search criteria provided.'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params",
    [
        "name=Poland&capital=Warsaw",
        "region=Europe&language=en",
        "currency=USD&subregion=North America",
    ],
)
async def test_get_country_multiple_criteria(params):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/countries/?{params}")
    assert response.status_code == 400
    data = response.json()
    assert data['detail'] == 'Please provide only one search criterion at a time.'


@pytest.mark.asyncio
async def test_get_country_server_error(monkeypatch):
    async def mock_fetch_country_info(*args, **kwargs):
        return {"status": 500, "detail": "An unexpected error occurred."}

    monkeypatch.setattr('country_scraper.main.fetch_country_info', mock_fetch_country_info)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/countries/?name=AnyCountry")
    assert response.status_code == 500
    data = response.json()
    assert data['detail'] == 'An unexpected error occurred.'
