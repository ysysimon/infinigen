import argparse
import json
from pathlib import Path


def blender_name_to_usd_prim_name(name):
    return name.replace("(", "_").replace(")", "_").replace(".", "_")


def has_tag(tags, needle):
    return any(tag == needle for tag in tags)


def has_tag_fragment(tags, fragment):
    return any(fragment in tag for tag in tags)


def relation_is_floor_on_room(relation, rooms):
    if relation.get("target_name") not in rooms:
        return False

    rel = relation.get("relation", {})
    if rel.get("relation_type") != "StableAgainst":
        return False

    parent_tags = rel.get("parent_tags", [])
    parent_tags = parent_tags if isinstance(parent_tags, list) else [parent_tags]

    # if a object is support and visible, but not a wall or ceiling, it's likely on the floor.
    return (
        has_tag(parent_tags, "Subpart(support)")
        and has_tag(parent_tags, "Subpart(visible)")
        and not has_tag(parent_tags, "Subpart(wall)")
        and not has_tag(parent_tags, "Subpart(ceiling)")
    )


def relation_is_wall_on_room(relation, rooms):
    if relation.get("target_name") not in rooms:
        return False

    rel = relation.get("relation", {})
    if rel.get("relation_type") != "StableAgainst":
        return False

    parent_tags = rel.get("parent_tags", [])
    parent_tags = parent_tags if isinstance(parent_tags, list) else [parent_tags]
    return has_tag(parent_tags, "Subpart(wall)")


def room_type_from_tags(tags):
    for tag in tags:
        if not tag.startswith("Semantics("):
            continue
        if tag in {"Semantics(room)", "Semantics(object)"}:
            continue
        return tag
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Export objects directly placed on room floors from solve_state.json."
    )
    parser.add_argument("solve_state", type=Path, help="Path to solve_state.json")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path. Defaults to floor_objects.json next to solve_state.json.",
    )
    args = parser.parse_args()

    with args.solve_state.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # find objects with the "Semantics(room)" tag, which are attached to the room itself, rather than other furniture.
    objs = data["objs"]
    rooms = {
        name: obj
        for name, obj in objs.items()
        if has_tag(obj.get("tags", []), "Semantics(room)")
    }

    floor_objects = []
    for name, obj in objs.items():
        tags = obj.get("tags", [])
        # if it is a part of room or a cutter, it can't be a floor object
        if has_tag(tags, "Semantics(room)") or has_tag(tags, "Semantics(cutter)"):
            continue

        relations = obj.get("relations", [])
        floor_relations = [r for r in relations if relation_is_floor_on_room(r, rooms)]
        if not floor_relations:
            continue

        # should only have one floor relation, but if there are multiple, just take the first one.
        room_name = floor_relations[0]["target_name"]
        floor_objects.append(
            {
                "name": name,
                "blender_object": obj.get("obj"),
                "usd_prim_name": blender_name_to_usd_prim_name(obj.get("obj", "")),
                "usd_prim_path": f"/World/{blender_name_to_usd_prim_name(obj.get('obj', ''))}",
                "room_name": room_name,
                "room_type": room_type_from_tags(rooms[room_name].get("tags", [])),
                "tags": sorted(tags),
                "against_wall": any(
                    relation_is_wall_on_room(r, rooms) for r in relations
                ),
            }
        )

    floor_objects.sort(key=lambda item: (item["room_name"], item["name"]))

    output_path = (
        args.output
        if args.output is not None
        else args.solve_state.with_name("floor_objects.json")
    )
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(floor_objects, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(floor_objects)} floor objects to {output_path}")


if __name__ == "__main__":
    main()
