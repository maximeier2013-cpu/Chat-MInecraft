
import json
from pathlib import Path
from litemapy import Schematic, Region, BlockState

# --------------------------------------------------
# Dateien
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "semi_organic_medieval_townhouse.json"
OUTPUT_FILE = BASE_DIR / "semi_organic_medieval_townhouse.litematic"


# --------------------------------------------------
# GrabCraft-Namen in Minecraft-Blöcke umwandeln
# --------------------------------------------------

def convert_block(name):
    n = name.strip()

    # Double Slabs: gezielte Ersetzungen
    if n == "Double Stone Slab":
        return BlockState("minecraft:smooth_stone")

    if n == "Double Spruce Wood Slab":
        return BlockState("minecraft:spruce_planks")

    if n == "Double Cobblestone Slab":
        return BlockState("minecraft:cobblestone")

    # Normale Blöcke
    simple_blocks = {
        "Spruce Wood": "minecraft:spruce_log",
        "Spruce Wood Plank": "minecraft:spruce_planks",
        "Grass": "minecraft:grass_block",
        "White Wool": "minecraft:white_wool",
        "Cobblestone": "minecraft:cobblestone",
        "Stone": "minecraft:stone",
        "Dirt": "minecraft:dirt",
        "Oak Wood": "minecraft:oak_log",
        "Block of Coal": "minecraft:coal_block",
        "Glass Pane": "minecraft:glass_pane",
        "Gray Wool": "minecraft:gray_wool",
        "Iron Bars": "minecraft:iron_bars",
        "Cobblestone Wall": "minecraft:cobblestone_wall",
        "Stone Bricks": "minecraft:stone_bricks",
        "Oak Fence": "minecraft:oak_fence",
        "Poppy": "minecraft:poppy",
        "Wall Sign, west": "minecraft:oak_wall_sign",
    }

    if n in simple_blocks:
        return BlockState(simple_blocks[n])

    # Normale Slabs
    if n == "Stone Slab":
        return BlockState("minecraft:stone_slab")

    if n == "Stone Slab (Upper)":
        return BlockState("minecraft:stone_slab", {"type": "top"})

    if n == "Spruce Wood Slab (Upper)":
        return BlockState("minecraft:spruce_slab", {"type": "top"})

    if n == "Spruce Wood Slab (Bottom)":
        return BlockState("minecraft:spruce_slab", {"type": "bottom"})

    if n == "Cobblestone Slab":
        return BlockState("minecraft:cobblestone_slab")

    if n == "Cobblestone (Upper)":
        return BlockState("minecraft:cobblestone",)

    # Blätter
    if n.startswith("Spruce Leaves"):
        return BlockState(
            "minecraft:spruce_leaves",
            {"persistent": "true", "distance": "1"}
        )

    # Holzstämme mit Ausrichtung
    if n == "Spruce wood (facing east/west)":
        return BlockState("minecraft:spruce_log", {"axis": "x"})

    if n == "Spruce Wood (facing north/south)":
        return BlockState("minecraft:spruce_log", {"axis": "z"})

    if n == "Oak Wood (facing north/south)":
        return BlockState("minecraft:oak_log", {"axis": "z"})

    if n == "Oak Wood (facing east/west)":
        return BlockState("minecraft:oak_log", {"axis": "x"})

    # Treppen
    stair_map = {
        "Stone Brick Stairs": "minecraft:stone_brick_stairs",
        "Spruce Wood Stairs": "minecraft:spruce_stairs",
        "Cobblestone Stairs": "minecraft:cobblestone_stairs",
    }

    for prefix, block_id in stair_map.items():
        if n.startswith(prefix):
            facing = "north"
            half = "bottom"

            if "East" in n:
                facing = "east"
            elif "South" in n:
                facing = "south"
            elif "West" in n:
                facing = "west"
            elif "North" in n:
                facing = "north"

            if "Upside-down" in n:
                half = "top"

            shape = "straight"
            return BlockState(
                block_id,
                {
                    "facing": facing,
                    "half": half,
                    "shape": shape,
                    "waterlogged": "false",
                }
            )

    # Falltüren
    if n.startswith("Wooden Trapdoor"):
        facing = "north"

        if "East" in n:
            facing = "east"
        elif "South" in n:
            facing = "south"
        elif "West" in n:
            facing = "west"

        half = "bottom"
        if "Top Half" in n:
            half = "top"

        return BlockState(
            "minecraft:spruce_trapdoor",
            {
                "facing": facing,
                "half": half,
                "open": "true",
                "powered": "false",
                "waterlogged": "false",
            }
        )

    # Fackeln
    if n.startswith("Torch"):
        return BlockState("minecraft:torch")

    # Unbekannte Namen sichtbar melden
    print(f"WARNUNG: Nicht zugeordnet: {name}")
    return BlockState("minecraft:stone")


# --------------------------------------------------
# JSON laden
# --------------------------------------------------

print("Lade JSON-Datei ...")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


# --------------------------------------------------
# Blockpositionen auslesen
# --------------------------------------------------

blocks = []

def find_blocks(obj):
    if isinstance(obj, dict):
        # Häufige JSON-Varianten für Koordinaten
        if all(k in obj for k in ("x", "y", "z")):
            name = (
                obj.get("name")
                or obj.get("block")
                or obj.get("type")
                or obj.get("blockName")
            )

            if isinstance(name, str):
                try:
                    blocks.append((
                        int(obj["x"]),
                        int(obj["y"]),
                        int(obj["z"]),
                        name
                    ))
                except (ValueError, TypeError):
                    pass

        for value in obj.values():
            find_blocks(value)

    elif isinstance(obj, list):
        for item in obj:
            find_blocks(item)


find_blocks(data)

if not blocks:
    raise RuntimeError(
        "Keine Blöcke gefunden. Bitte prüfe das Format der JSON-Datei."
    )

print(f"{len(blocks)} Blockeinträge gefunden.")


# --------------------------------------------------
# Größe bestimmen und Litematic erstellen
# --------------------------------------------------

min_x = min(b[0] for b in blocks)
min_y = min(b[1] for b in blocks)
min_z = min(b[2] for b in blocks)

max_x = max(b[0] for b in blocks)
max_y = max(b[1] for b in blocks)
max_z = max(b[2] for b in blocks)

size_x = max_x - min_x + 1
size_y = max_y - min_y + 1
size_z = max_z - min_z + 1

print(f"Gebäudegröße: {size_x} x {size_y} x {size_z}")

region = Region(0, 0, 0, size_x, size_y, size_z)

unknown_names = set()

for x, y, z, name in blocks:
    try:
        block_state = convert_block(name)

        # GrabCraft-Koordinaten auf den Ursprung verschieben
        region.setblock(
            x - min_x,
            y - min_y,
            z - min_z,
            block_state
        )

    except Exception as e:
        unknown_names.add(name)
        print(f"Fehler bei Block '{name}': {e}")

schematic = Schematic(
    name="Semi Organic Medieval Townhouse",
    author="Maxi",
    description="Konvertiert aus einem GrabCraft-Modell"
)

schematic.regions["Townhouse"] = region
schematic.save(str(OUTPUT_FILE))

print()
print("Fertig!")
print(f"Datei erstellt: {OUTPUT_FILE}")

if unknown_names:
    print("\nNicht korrekt verarbeitete Blocktypen:")
    for name in sorted(unknown_names):
        print(f"- {name}")
