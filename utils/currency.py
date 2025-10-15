import requests

def rub_to_kgs(amount_rub):
    url = "https://api.exchangerate.host/latest?base=RUB&symbols=KGS"
    try:
        response = requests.get(url)
        data = response.json()
        rate = data["rates"]["KGS"]

        return round(amount_rub * rate, 2)
    except Exception:
        # fallback если нет интернета
        fallback_rate = 1.084343
        return round(amount_rub * fallback_rate, 2)