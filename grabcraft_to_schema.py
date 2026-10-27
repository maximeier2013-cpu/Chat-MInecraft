
import json
import re
import requests

from grabcraft_to_schema import RenderObject


MODEL_URL = (
    "https://assets.grabcraft.com/files/products/3dmodel/4272.json"
)

PAGE_URL = (
    "https://www.grabcraft.com/minecraft/"
    "semi-organic-medieval-townhouse/other-193"
)


def url_to_render_object_data(url):
    """Lädt die Modellinformationen von einer GrabCraft-Seite."""

    headers = {"User-Agent": "Mozilla/5.0"}

    page_response = requests.get(
        url.split("#")[0],
        headers=headers,
        timeout=30,
    )
    page_response.raise_for_status()

    html = page_response.text

    # Modell-JSON-Adresse aus der Seite ermitteln.
    match = re.search(
        r'fetch\(["\']([^"\']+\.json)["\']\)',
        html,
    )

    model_url = match.group(1) if match else MODEL_URL

    print("Modell-URL:", model_url)

    model_response = requests.get(
        model_url,
        headers=headers,
        timeout=30,
    )
    model_response.raise_for_status()

    model_data = model_response.json()

    if not isinstance(model_data, dict) or not model_data:
        raise ValueError(
            "Die heruntergeladenen Modelldaten sind leer "
            "oder haben ein unerwartetes Format."
        )

    print("JSON erfolgreich geladen.")
    print("Datentyp:", type(model_data).__name__)
    print("Hauptschlüssel:", list(model_data.keys())[:10])

    return model_data


def download_model():
    """Lädt das Hausmodell und speichert eine lokale JSON-Kopie."""

    data = url_to_render_object_data(PAGE_URL)

    output_file = "semi_organic_medieval_townhouse.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print(f"Modell gespeichert: {output_file}")


if __name__ == "__main__":
    download_model()
