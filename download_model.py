
import json
import re
import requests

MODEL_URL = (
    "https://assets.grabcraft.com/files/products/3dmodel/4272.json"
)

PAGE_URL = (
    "https://www.grabcraft.com/minecraft/"
    "semi-organic-medieval-townhouse/other-193"
)


def download_model():
    headers = {"User-Agent": "Mozilla/5.0"}

    print("Lade GrabCraft-Seite ...")
    response = requests.get(
        PAGE_URL,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    match = re.search(
        r'fetch\(["\']([^"\']+\.json)["\']\)',
        response.text,
    )

    model_url = match.group(1) if match else MODEL_URL
    print("Modell-URL:", model_url)

    print("Lade 3D-Modell ...")
    model_response = requests.get(
        model_url,
        headers=headers,
        timeout=30,
    )
    model_response.raise_for_status()

    data = model_response.json()

    if not isinstance(data, (dict, list)) or not data:
        raise ValueError("Die heruntergeladenen Modelldaten sind leer.")

    filename = "semi_organic_medieval_townhouse.json"

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print("Modell erfolgreich heruntergeladen.")
    print("Gespeichert als:", filename)
    print("Datentyp:", type(data).__name__)

    if isinstance(data, dict):
        print("Hauptschlüssel:", list(data.keys())[:15])
    elif isinstance(data, list):
        print("Anzahl Einträge:", len(data))


if __name__ == "__main__":
    download_model()
