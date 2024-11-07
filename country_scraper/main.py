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
    if 'error' in data:
        status_code = data.get('status', 400)
        message = data.get('message', data['error'])
        raise HTTPException(status_code=status_code, detail=message)
    return data
