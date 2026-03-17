# One-Run Pipeline for Single-Room Indoors

This document describes a cross-platform pipeline for generating a single-room indoor scene, exporting `floor_objects.json`, and exporting USD in one command.

The pipeline entrypoint is:

```bash
python scripts/run_one_room_pipeline.py --output-folder outputs/one_room_living
```

It runs these steps in order:

1. Generate a single-room indoor scene with `infinigen_examples.generate_indoors --task coarse`
2. Extract direct floor-placed objects into `floor_objects.json`
3. Export the resulting scene to USD with `infinigen.tools.export`

## What the pipeline produces

If `--output-folder outputs/one_room_living` is used, the pipeline writes:

- `outputs/one_room_living/scene.blend`
- `outputs/one_room_living/solve_state.json`
- `outputs/one_room_living/floor_objects.json`
- a USD export folder under `outputs/one_room_living/`

## Basic usage

### Default living room

```bash
python scripts/run_one_room_pipeline.py --output-folder outputs/one_room_living
```

Defaults:

- `seed=0`
- floor plan = `infinigen_examples.configs_indoor.floor_plans.single_room.living_room`
- USD format = `usdc`
- texture resolution = `1024`
- configs = `fast_solve.gin` and `singleroom.gin`

### Bedroom

```bash
python scripts/run_one_room_pipeline.py \
  --output-folder outputs/one_room_bedroom \
  --floor-plan infinigen_examples.configs_indoor.floor_plans.single_room.bedroom
```

### Export USDA instead of USDC

```bash
python scripts/run_one_room_pipeline.py \
  --output-folder outputs/one_room_living \
  --format usda
```

### Increase USD texture bake resolution

```bash
python scripts/run_one_room_pipeline.py \
  --output-folder outputs/one_room_living \
  --resolution 2048
```

## Passing single-room overrides

Extra indoor overrides can be passed with repeated `--override` flags. These are forwarded to the `coarse` generation command.

Example:

```bash
python scripts/run_one_room_pipeline.py \
  --output-folder outputs/one_room_living \
  --override "living_room.wall_margin=1.2" \
  --override "living_room.door_width=1.1" \
  --override "living_room.window_width=2.0"
```

Examples for other room types:

- `bedroom.wall_margin=1.0`
- `kitchen.window_width=2.2`
- `bathroom.door_width=0.9`

The selector prefix must match the selected floor-plan function:

- `living_room.*`
- `bedroom.*`
- `kitchen.*`
- `bathroom.*`
- `dining_room.*`

## Running only part of the pipeline

### Reuse an existing generated scene

If `scene.blend` and `solve_state.json` already exist, skip regeneration:

```bash
python scripts/run_one_room_pipeline.py \
  --output-folder outputs/one_room_living \
  --skip-generate
```

### Skip floor-object export

```bash
python scripts/run_one_room_pipeline.py \
  --output-folder outputs/one_room_living \
  --skip-floor-objects
```

### Skip USD export

```bash
python scripts/run_one_room_pipeline.py \
  --output-folder outputs/one_room_living \
  --skip-usd
```

## Adding extra gin configs

Additional configs can be appended with repeated `--config` flags:

```bash
python scripts/run_one_room_pipeline.py \
  --output-folder outputs/one_room_overhead \
  --config overhead.gin
```

These are appended after the defaults:

- `fast_solve.gin`
- `singleroom.gin`

## Related scripts

- `scripts/run_one_room_pipeline.py`: full one-run pipeline
- `scripts/export_floor_objects.py`: extract direct floor-placed objects from `solve_state.json`

## Notes

- USD export is a post-processing step. The scene is generated first, then exported from the saved `scene.blend`.
- `floor_objects.json` only contains objects directly placed on the room floor. It does not include items placed on tables, shelves, counters, or other furniture.
- For standalone USD export details, see [ExportingToExternalFileFormats.md](./ExportingToExternalFileFormats.md).

## Windows notes

The pipeline supports exporting USD into the same directory used for scene generation. For example:

```bash
python scripts/run_one_room_pipeline.py \
  --output-folder outputs/one_room_living \
  --skip-generate \
  --skip-floor-objects
```

This reruns only the USD export step using the existing scene outputs.

The exporter now handles these Windows-specific issues:

- absolute paths are used for export inputs and outputs
- Windows-invalid filename characters in exported texture names are sanitized
- same-directory export no longer fails when `solve_state.json` already exists
- ZIP packaging no longer depends on an external `zip` executable

If USD export was already attempted and scene generation succeeded, the recommended recovery command is:

```bash
python scripts/run_one_room_pipeline.py \
  --output-folder outputs/one_room_living \
  --skip-generate \
  --skip-floor-objects
```
