from fastapi import FastAPI, Query, HTTPException
from .services import fetch_country_info

app = FastAPI()


@app.get("/countries/")
async def get_country(
    name: str = Query(None),
    capital: str = Query(None),
    region: str = Query(None),
    subregion: str = Query(None),
    language: str = Query(None),
    currency: str = Query(None),
):
    data = await fetch_country_info(
        name=name,
        capital=capital,
        region=region,
        subregion=subregion,
        language=language,
        currency=currency,
    )

    # Check if the status code indicates an error
    if isinstance(data, dict) and data.get('status', 200) >= 400:
        status_code = data['status']
        detail = data.get('detail', 'An error occurred.')
        raise HTTPException(status_code=status_code, detail=detail)
    return data
