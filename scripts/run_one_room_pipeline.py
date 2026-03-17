import argparse
import subprocess
import sys
from pathlib import Path


DEFAULT_FLOOR_PLAN = (
    "infinigen_examples.configs_indoor.floor_plans.single_room.living_room"
)


def run(cmd, cwd):
    print("Running:", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Run the single-room pipeline: generate scene, export floor_objects.json, "
            "and export USD."
        )
    )
    parser.add_argument(
        "--output-folder",
        type=Path,
        required=True,
        help="Folder where the generated scene already lives or will be generated.",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--floor-plan",
        default=DEFAULT_FLOOR_PLAN,
        help="Import path of the predefined single-room floor plan function.",
    )
    parser.add_argument(
        "--format",
        choices=["usdc", "usda"],
        default="usdc",
        help="USD export format.",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=1024,
        help="Baked texture resolution for USD export.",
    )
    parser.add_argument(
        "--config",
        action="append",
        dest="configs",
        default=[],
        help="Additional gin config to append after the defaults.",
    )
    parser.add_argument(
        "--override",
        action="append",
        dest="overrides",
        default=[],
        help="Additional coarse-stage gin override. Can be specified multiple times.",
    )
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Skip scene generation and only run floor-object export plus USD export.",
    )
    parser.add_argument(
        "--skip-floor-objects",
        action="store_true",
        help="Skip floor_objects.json export.",
    )
    parser.add_argument(
        "--skip-usd",
        action="store_true",
        help="Skip USD export.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    python = sys.executable
    output_folder = (
        args.output_folder
        if args.output_folder.is_absolute()
        else (repo_root / args.output_folder)
    ).resolve()
    output_folder.mkdir(parents=True, exist_ok=True)

    if not args.skip_generate:
        coarse_cmd = [
            python,
            "-m",
            "infinigen_examples.generate_indoors",
            "--seed",
            str(args.seed),
            "--task",
            "coarse",
            "--output_folder",
            str(output_folder),
            "-g",
            "fast_solve.gin",
            "singleroom.gin",
            *args.configs,
            "-p",
            f"Solver.floor_plan='{args.floor_plan}'",
            *args.overrides,
        ]
        run(coarse_cmd, cwd=repo_root)

    solve_state = output_folder / "solve_state.json"
    if not solve_state.exists():
        raise FileNotFoundError(f"Expected solve_state.json at {solve_state}")

    if not args.skip_floor_objects:
        floor_cmd = [
            python,
            str(repo_root / "scripts" / "export_floor_objects.py"),
            str(solve_state),
        ]
        run(floor_cmd, cwd=repo_root)

    if not args.skip_usd:
        usd_cmd = [
            python,
            "-m",
            "infinigen.tools.export",
            "--input_folder",
            str(output_folder),
            "--output_folder",
            str(output_folder),
            "-f",
            args.format,
            "-r",
            str(args.resolution),
        ]
        run(usd_cmd, cwd=repo_root)


if __name__ == "__main__":
    main()
