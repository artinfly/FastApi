from fastapi import FastAPI, HTTPException
import requests
from fastapi.responses import JSONResponse

app = FastAPI()

CBR_DAILY_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


def get_currency_rate(cur, date):
    params = {"date_req": date}  # формат даты: DD/MM/YYYY
    response = requests.get(CBR_DAILY_URL, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Не удалось получить данные от ЦБ РФ.")

    from xml.etree import ElementTree as ET
    root = ET.fromstring(response.content)

    for valute in root.findall("Valute"):
        char_code = valute.find("CharCode").text
        if char_code == cur:
            value = float(valute.find("Value").text.replace(",", "."))
            nominal = int(valute.find("Nominal").text)
            return value / nominal
    raise HTTPException(status_code=404, detail="Валюта не найдена.")


@app.get("/daily/{cur}/{date}")
async def daily_rate(cur: str, date: str):

    try:
        day, month, year = date.split("-")
        formatted_date = f"{day}/{month}/{year}"
        rate = get_currency_rate(cur, formatted_date)
        return {"currency": cur, "date": date, "rate": rate}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/convert")
async def convert_currency(data: dict):

    try:
        from_cur = data["from_currency"]
        to_cur = data["to_currency"]
        amount = data["amount"]
        date = data["date"]

        day, month, year = date.split("-")
        formatted_date = f"{day}/{month}/{year}"

        from_rate = get_currency_rate(from_cur, formatted_date)
        to_rate = get_currency_rate(to_cur, formatted_date)

        converted_amount = amount * from_rate / to_rate

        return JSONResponse(content={
            "from_currency": from_cur,
            "to_currency": to_cur,
            "amount": amount,
            "converted_amount": converted_amount,
            "date": date
        })
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Пропущен параметр: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
