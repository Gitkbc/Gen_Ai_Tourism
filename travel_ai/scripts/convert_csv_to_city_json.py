import csv
import json
from pathlib import Path
from collections import defaultdict

BASE_PATH = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_PATH / "data" / "master_places.csv"
OUTPUT_DIR = BASE_PATH / "data" / "cities"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def convert():
    city_map = defaultdict(list)

    with open(CSV_PATH, newline="", encoding="latin-1") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            city = row["city"].strip()

            place = {
                "name": row["popular_destination"].strip(),
                "lat": float(row["latitude"]),
                "lng": float(row["longitude"]),
                "category": row["interest"],
                "rating": float(row["google_rating"]),
                "ticket_price": float(row["price_fare"])
            }

            city_map[city].append(place)

    for city, places in city_map.items():
        file_path = OUTPUT_DIR / f"{city.lower()}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "city": city,
                    "places": places
                },
                f,
                indent=2
            )

    print("Conversion completed.")


if __name__ == "__main__":
    convert()