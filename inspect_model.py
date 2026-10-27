
import json
from collections import Counter

with open(
    "semi_organic_medieval_townhouse.json",
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)

blocks = []

def scan(obj):
    if isinstance(obj, dict):
        if all(k in obj for k in ("x", "y", "z", "name")):
            blocks.append(obj)
            return

        for value in obj.values():
            scan(value)

    elif isinstance(obj, list):
        for value in obj:
            scan(value)

scan(data)

print("Gefundene Blöcke:", len(blocks))
print("\nBlocknamen und Häufigkeit:")

for name, count in Counter(
    b["name"] for b in blocks
).most_common():
    print(f"{name}: {count}")

if blocks:
    for axis in ("x", "y", "z"):
        values = [int(b[axis]) for b in blocks]
        print(
            f"{axis}: {min(values)} bis {max(values)}"
        )
