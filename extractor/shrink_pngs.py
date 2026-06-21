import argparse
from pathlib import Path


def shrink_pngs(input_dir: Path, output_dir: Path, scale: float = 0.5) -> tuple[int, int]:
    if scale <= 0:
        raise ValueError("Scale must be greater than 0")

    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is required. Install it with: pip install pillow"
        ) from exc

    output_dir.mkdir(parents=True, exist_ok=True)

    png_files = list(input_dir.rglob("*.png"))
    if not png_files:
        return 0, 0

    processed = 0
    skipped = 0

    for src in png_files:
        rel_path = src.relative_to(input_dir)
        dest = output_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            with Image.open(src) as img:
                new_width = max(1, int(img.width * scale))
                new_height = max(1, int(img.height * scale))
                resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized.save(dest, format="PNG", optimize=True)
                processed += 1
        except OSError:
            skipped += 1

    return processed, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Shrink PNG files by 50% from found_dir into shrink_dir."
    )
    parser.add_argument(
        "--input-dir",
        default="found_dir",
        help="Directory containing source PNG files.",
    )
    parser.add_argument(
        "--output-dir",
        default="shrink_dir",
        help="Directory to write resized PNG files.",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=0.5,
        help="Resize scale factor (default: 0.5 = 50%%).",
    )

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    input_dir = (script_dir / args.input_dir).resolve()
    output_dir = (script_dir / args.output_dir).resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Input directory does not exist or is not a directory: {input_dir}")
        return 1

    try:
        processed, skipped = shrink_pngs(input_dir, output_dir, args.scale)
    except (RuntimeError, ValueError) as exc:
        print(exc)
        return 1

    print(f"Input directory:  {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Processed PNGs:   {processed}")
    print(f"Skipped files:    {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
