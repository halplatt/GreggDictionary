#!/usr/bin/env python3
"""
Image Resizer Script
Resizes all PNG files in a specified directory to 50% of their original size.
"""

import os
import sys
from PIL import Image
import argparse
from pathlib import Path


def resize_image(input_path, output_path, scale_factor=0.4):
    """
    Resize a single image by the given scale factor.
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path to save the resized image
        scale_factor (float): Factor to scale the image (0.4 = 40% size)
    """
    try:
        with Image.open(input_path) as img:
            # Get original dimensions
            original_width, original_height = img.size
            
            # Calculate new dimensions
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # Resize the image using high-quality resampling
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save the resized image
            resized_img.save(output_path, 'PNG')
            
        print(f"✓ Resized {os.path.basename(input_path)}: {original_width}x{original_height} → {new_width}x{new_height}")
            
    except Exception as e:
        print(f"✗ Error processing {os.path.basename(input_path)}: {str(e)}")


def resize_png_files(input_dir, output_dir=None, scale_factor=0.4):
    """
    Resize all PNG files in the input directory.
    
    Args:
        input_dir (str): Directory containing PNG files to resize
        output_dir (str): Directory to save resized images (optional)
        scale_factor (float): Factor to scale images (0.4 = 40% size)
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return
    
    if not input_path.is_dir():
        print(f"Error: '{input_dir}' is not a directory.")
        return
    
    # Set output directory
    if output_dir is None:
        output_path = Path("D:/annWordsResize")
    else:
        output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(exist_ok=True)
    
    # Find all PNG files
    png_files = list(input_path.glob("*.png"))
    
    if not png_files:
        print(f"No PNG files found in '{input_dir}'")
        return
    
    print(f"Found {len(png_files)} PNG file(s) to resize")
    print(f"Scale factor: {scale_factor} ({int(scale_factor * 100)}%)")
    print(f"Output directory: {output_path}")
    print("-" * 50)
    
    # Process each PNG file
    for png_file in png_files:
        output_file = output_path / png_file.name
        resize_image(str(png_file), str(output_file), scale_factor)
    
    print("-" * 50)
    print(f"Processing complete! Resized images saved to: {output_path}")


def main():
    """Main function to handle command line arguments and execute the resizing."""
    # Get the directory where the script is located
    script_dir = Path(__file__).parent.absolute()
    
    parser = argparse.ArgumentParser(
        description="Resize PNG files to 40% of their original size",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python !image_resizer.py
  python !image_resizer.py --output /path/to/resized
  python !image_resizer.py --scale 0.25
  python !image_resizer.py /path/to/images --scale 0.75

Default behavior: Process PNG files in the script directory ({script_dir})
        """
    )
    
    parser.add_argument(
        "input_dir",
        nargs='?',  # Make input_dir optional
        default=str(script_dir),  # Default to script directory
        help=f"Directory containing PNG files to resize (default: {script_dir})"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output directory for resized images (default: D:/annWordsResize)"
    )
    
    parser.add_argument(
        "--scale", "-s",
        type=float,
        default=0.4,
        help="Scale factor for resizing (default: 0.4 for 40%% size)"
    )
    
    args = parser.parse_args()
    
    # Validate scale factor
    if args.scale <= 0 or args.scale > 1:
        print("Error: Scale factor must be between 0 and 1")
        sys.exit(1)
    
    # Run the resizing process
    resize_png_files(args.input_dir, args.output, args.scale)
    
    # Keep the window open until a key is pressed
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()