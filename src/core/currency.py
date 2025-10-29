import requests, xml.etree.ElementTree as ET

def rub_to_kgs(amount_rub: float) -> float:
    xml = requests.get("https://www.nbkr.kg/XML/daily.xml", timeout=5).content
    root = ET.fromstring(xml)
    rub = root.find(".//Currency[@ISOCode='RUB']")
    nominal = int(rub.findtext("Nominal"))
    value = float(rub.findtext("Value").replace(",", "."))  # KGS за nominal RUB
    kgs_per_rub = value / nominal
    return round(amount_rub * kgs_per_rub, 2)