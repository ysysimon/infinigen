import random

import gin
import shapely


def _sample_span(rng, length, span_width, margin):
    half_span = span_width / 2
    center = rng.uniform(margin + half_span, length - margin - half_span)
    return center - half_span, center + half_span


def _sample_wall_segment(rng, wall, width, depth, span_width, margin):
    if wall in ("bottom", "top"):
        start, end = _sample_span(rng, width, span_width, margin)
        y = 0 if wall == "bottom" else depth
        return shapely.LineString([(start, y), (end, y)])

    start, end = _sample_span(rng, depth, span_width, margin)
    x = 0 if wall == "left" else width
    return shapely.LineString([(x, start), (x, end)])


def _single_room(
    room_name,
    width,
    depth,
    factory_seed,
    wall_margin=0.9,
    door_width=1.0,
    window_width=1.6,
):
    rng = random.Random(factory_seed)
    walls = ("bottom", "right", "top", "left")
    door_wall = rng.choice(walls)
    window_wall = rng.choice([wall for wall in walls if wall != door_wall])

    entrance = _sample_wall_segment(
        rng, door_wall, width, depth, door_width, wall_margin
    )
    window = _sample_wall_segment(
        rng, window_wall, width, depth, window_width, wall_margin
    )

    return {
        "rooms": {
            room_name: {
                "shape": shapely.box(0, 0, width, depth),
            }
        },
        "entrance": {
            "entrance": {
                "shape": entrance
            }
        },
        "windows": {
            "window": {
                "shape": window
            }
        },
    }


@gin.configurable
def living_room(
    factory_seed,
    width=6.5,
    depth=5.5,
    wall_margin=0.9,
    door_width=1.0,
    window_width=1.6,
):
    return _single_room(
        "living-room_0/0",
        width=width,
        depth=depth,
        factory_seed=factory_seed,
        wall_margin=wall_margin,
        door_width=door_width,
        window_width=window_width,
    )


@gin.configurable
def bedroom(
    factory_seed,
    width=5.2,
    depth=4.6,
    wall_margin=0.9,
    door_width=1.0,
    window_width=1.6,
):
    return _single_room(
        "bedroom_0/0",
        width=width,
        depth=depth,
        factory_seed=factory_seed,
        wall_margin=wall_margin,
        door_width=door_width,
        window_width=window_width,
    )


@gin.configurable
def kitchen(
    factory_seed,
    width=5.4,
    depth=4.8,
    wall_margin=0.9,
    door_width=1.0,
    window_width=1.6,
):
    return _single_room(
        "kitchen_0/0",
        width=width,
        depth=depth,
        factory_seed=factory_seed,
        wall_margin=wall_margin,
        door_width=door_width,
        window_width=window_width,
    )


@gin.configurable
def bathroom(
    factory_seed,
    width=3.6,
    depth=3.0,
    wall_margin=0.9,
    door_width=1.0,
    window_width=1.0,
):
    return _single_room(
        "bathroom_0/0",
        width=width,
        depth=depth,
        factory_seed=factory_seed,
        wall_margin=wall_margin,
        door_width=door_width,
        window_width=window_width,
    )


@gin.configurable
def dining_room(
    factory_seed,
    width=5.8,
    depth=4.8,
    wall_margin=0.9,
    door_width=1.0,
    window_width=1.6,
):
    return _single_room(
        "dining-room_0/0",
        width=width,
        depth=depth,
        factory_seed=factory_seed,
        wall_margin=wall_margin,
        door_width=door_width,
        window_width=window_width,
    )
