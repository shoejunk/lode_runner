#!/usr/bin/env python3
import os
import json
import xml.etree.ElementTree as ET
from constants import TILE_SIZE, TileType
from tile import Tile

def validate_level(level_data):
    # Check required keys
    required_keys = ["tiles", "spawn", "enemies", "treasures"]
    for key in required_keys:
        if key not in level_data:
            raise ValueError(f"Missing required key: {key}")
    
    # Validate tiles: must be a list of lists with valid tile type strings.
    valid_tile_types = {t.name for t in TileType}
    if not isinstance(level_data["tiles"], list) or not level_data["tiles"]:
        raise ValueError("Tiles must be a non-empty list.")
    for row in level_data["tiles"]:
        if not isinstance(row, list) or not row:
            raise ValueError("Each row in tiles must be a non-empty list.")
        for tile_str in row:
            if not isinstance(tile_str, str) or tile_str.upper() not in valid_tile_types:
                raise ValueError(f"Invalid tile type: {tile_str}")
    
    # Validate spawn: must be a list of two numbers.
    spawn = level_data["spawn"]
    if (not isinstance(spawn, list) or len(spawn) != 2 or
        not all(isinstance(n, (int, float)) for n in spawn)):
        raise ValueError("Spawn must be a list of two numbers.")
    
    # Validate enemies: list (can be empty) of positions as list of two numbers.
    enemies = level_data["enemies"]
    if not isinstance(enemies, list):
        raise ValueError("Enemies must be a list.")
    for pos in enemies:
        if (not isinstance(pos, list) or len(pos) != 2 or
            not all(isinstance(n, (int, float)) for n in pos)):
            raise ValueError("Each enemy position must be a list of two numbers.")
    
    # Validate treasures: list (can be empty) of positions as list of two numbers.
    treasures = level_data["treasures"]
    if not isinstance(treasures, list):
        raise ValueError("Treasures must be a list.")
    for pos in treasures:
        if (not isinstance(pos, list) or len(pos) != 2 or
            not all(isinstance(n, (int, float)) for n in pos)):
            raise ValueError("Each treasure position must be a list of two numbers.")
    
    return True

def load_level(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Level file not found: {filepath}")
    
    filename, ext = os.path.splitext(filepath)
    level_data = None

    if ext.lower() == ".json":
        with open(filepath, "r") as f:
            level_data = json.load(f)
    elif ext.lower() == ".xml":
        tree = ET.parse(filepath)
        root = tree.getroot()
        level_data = {}
        # Parse tiles: expect <tiles><row>...</row><row>...</row></tiles>
        tiles_elem = root.find("tiles")
        if tiles_elem is None:
            raise ValueError("XML missing <tiles> element")
        tiles = []
        for row_elem in tiles_elem.findall("row"):
            # Expect comma separated tile names or space separated.
            row_text = row_elem.text.strip()
            if "," in row_text:
                row = [t.strip() for t in row_text.split(",") if t.strip()]
            else:
                row = row_text.split()
            tiles.append(row)
        level_data["tiles"] = tiles
        
        # Parse spawn: expect <spawn x="..." y="..."/>
        spawn_elem = root.find("spawn")
        if spawn_elem is None or "x" not in spawn_elem.attrib or "y" not in spawn_elem.attrib:
            raise ValueError("XML missing spawn element or coordinates")
        level_data["spawn"] = [float(spawn_elem.attrib["x"]), float(spawn_elem.attrib["y"])]
        
        # Parse enemies: expect <enemies><enemy x="..." y="..."/></enemies>
        enemies_elem = root.find("enemies")
        enemies = []
        if enemies_elem is not None:
            for enemy_elem in enemies_elem.findall("enemy"):
                if "x" in enemy_elem.attrib and "y" in enemy_elem.attrib:
                    enemies.append([float(enemy_elem.attrib["x"]), float(enemy_elem.attrib["y"])])
        level_data["enemies"] = enemies
        
        # Parse treasures: expect <treasures><treasure x="..." y="..."/></treasures>
        treasures_elem = root.find("treasures")
        treasures = []
        if treasures_elem is not None:
            for treasure_elem in treasures_elem.findall("treasure"):
                if "x" in treasure_elem.attrib and "y" in treasure_elem.attrib:
                    treasures.append([float(treasure_elem.attrib["x"]), float(treasure_elem.attrib["y"])])
        level_data["treasures"] = treasures
    else:
        raise ValueError("Unsupported file format. Only .json and .xml are supported.")
    
    # Validate level structure.
    validate_level(level_data)
    
    # Generate tile grid using the tiles layout.
    grid = []
    tile_type_mapping = {
        "GROUND": TileType.GROUND,
        "WALL": TileType.WALL,
        "PLATFORM": TileType.PLATFORM,
        "SPIKE": TileType.SPIKE,
        "LADDER": TileType.LADDER
    }
    for row_idx, row in enumerate(level_data["tiles"]):
        grid_row = []
        for col_idx, tile_str in enumerate(row):
            tile_str_upper = tile_str.upper()
            tile_type = tile_type_mapping[tile_str_upper]
            # Calculate position on screen.
            position = (col_idx * TILE_SIZE, row_idx * TILE_SIZE)
            grid_row.append(Tile(tile_type, position))
        grid.append(grid_row)
    
    # Prepare the final level dictionary.
    level = {
        "tiles": grid,
        "spawn": tuple(level_data["spawn"]),
        "enemies": [tuple(pos) for pos in level_data["enemies"]],
        "treasures": [tuple(pos) for pos in level_data["treasures"]]
    }
    return level

def main():
    import tempfile
    import pygame
    pygame.init()

    # Create sample JSON level configuration
    sample_json_level = {
        "tiles": [
            ["GROUND", "WALL", "PLATFORM"],
            ["SPIKE", "LADDER", "GROUND"]
        ],
        "spawn": [64, 64],
        "enemies": [[128, 128], [192, 192]],
        "treasures": [[256, 256]]
    }
    
    # Write JSON level config to temporary file.
    json_temp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(sample_json_level, json_temp)
    json_temp.close()
    
    # Create sample XML level configuration.
    sample_xml = """<?xml version="1.0"?>
<level>
    <tiles>
        <row>GROUND, WALL, PLATFORM</row>
        <row>SPIKE, LADDER, GROUND</row>
    </tiles>
    <spawn x="64" y="64"/>
    <enemies>
        <enemy x="128" y="128"/>
        <enemy x="192" y="192"/>
    </enemies>
    <treasures>
        <treasure x="256" y="256"/>
    </treasures>
</level>
"""
    xml_temp = tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False)
    xml_temp.write(sample_xml)
    xml_temp.close()
    
    # Test load_level with JSON file.
    level_json = load_level(json_temp.name)
    # Verify that level JSON loaded correctly.
    assert isinstance(level_json, dict), "Level JSON should be a dictionary."
    assert "tiles" in level_json and isinstance(level_json["tiles"], list), "Tiles missing in level JSON."
    assert len(level_json["tiles"]) == 2, "Tile grid row count mismatch in JSON."
    # Check spawn position.
    assert level_json["spawn"] == (64, 64), "Spawn position mismatch in JSON."
    # Check enemy placements.
    assert level_json["enemies"] == [(128, 128), (192, 192)], "Enemy positions mismatch in JSON."
    # Check treasure placements.
    assert level_json["treasures"] == [(256, 256)], "Treasure positions mismatch in JSON."
    
    # Test load_level with XML file.
    level_xml = load_level(xml_temp.name)
    # Verify that level XML loaded correctly.
    assert isinstance(level_xml, dict), "Level XML should be a dictionary."
    assert "tiles" in level_xml and isinstance(level_xml["tiles"], list), "Tiles missing in level XML."
    assert len(level_xml["tiles"]) == 2, "Tile grid row count mismatch in XML."
    # Check spawn position.
    assert level_xml["spawn"] == (64.0, 64.0), "Spawn position mismatch in XML."
    # Check enemy placements.
    assert level_xml["enemies"] == [(128.0, 128.0), (192.0, 192.0)], "Enemy positions mismatch in XML."
    # Check treasure placements.
    assert level_xml["treasures"] == [(256.0, 256.0)], "Treasure positions mismatch in XML."
    
    # Test validate_level with invalid data.
    invalid_level = {
        "tiles": [["GROUND", "INVALID_TILE"]],
        "spawn": [64, 64],
        "enemies": [],
        "treasures": []
    }
    try:
        validate_level(invalid_level)
        assert False, "Invalid tile type should have raised ValueError."
    except ValueError:
        pass

    # Test validate_level with missing key.
    invalid_level_2 = {
        "tiles": [["GROUND", "WALL"]],
        "spawn": [64, 64],
        "enemies": []
        # Missing treasures
    }
    try:
        validate_level(invalid_level_2)
        assert False, "Missing key should have raised ValueError."
    except ValueError:
        pass

    # Create a pygame window to visually render the JSON level's tile grid for a brief moment.
    screen = pygame.display.set_mode((400, 300))
    clock = pygame.time.Clock()
    running = True
    render_time = pygame.time.get_ticks()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        for row in level_json["tiles"]:
            for tile in row:
                tile.render(screen)
        pygame.display.flip()
        # Render for 2 seconds.
        if pygame.time.get_ticks() - render_time > 2000:
            running = False
        clock.tick(60)
    pygame.quit()
    
    # Clean up temporary files.
    os.unlink(json_temp.name)
    os.unlink(xml_temp.name)
    
    print("All tests passed successfully.")

if __name__ == "__main__":
    main()