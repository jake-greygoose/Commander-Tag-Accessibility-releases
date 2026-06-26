import os
import argparse
from PIL import Image

def convert_pngs_in_directory(directory, quality=85):
    print(f"Scanning for PNGs in: {os.path.abspath(directory)}")
    if not os.path.exists(directory):
        print("Directory does not exist.")
        return
        
    png_files = [f for f in os.listdir(directory) if f.lower().endswith('.png')]
    
    if not png_files:
        print("No PNG files found in the directory.")
        return
        
    print(f"Found {len(png_files)} PNG files. Starting WebP Conversion...\n")
    print(f"{'Filename':<35} | {'Orig Size (KB)':<15} | {'WebP Size (KB)':<15} | {'Compression Type':<20} | {'Savings':<10}")
    print("-" * 105)

    total_orig = 0
    total_webp = 0

    for filename in png_files:
        filepath = os.path.join(directory, filename)
        orig_size = os.path.getsize(filepath)
        total_orig += orig_size
        
        try:
            img = Image.open(filepath)
            
            # Try lossy
            import io
            buf_lossy = io.BytesIO()
            img.save(buf_lossy, format="WEBP", quality=quality)
            size_lossy = len(buf_lossy.getvalue())
            
            # Try lossless
            buf_lossless = io.BytesIO()
            img.save(buf_lossless, format="WEBP", lossless=True)
            size_lossless = len(buf_lossless.getvalue())
            
            # Choose smaller
            if size_lossy <= size_lossless:
                webp_data = buf_lossy.getvalue()
                comp_type = f"Lossy (Q={quality})"
                webp_size = size_lossy
            else:
                webp_data = buf_lossless.getvalue()
                comp_type = "Lossless"
                webp_size = size_lossless
                
            webp_filename = os.path.splitext(filename)[0] + ".webp"
            webp_filepath = os.path.join(directory, webp_filename)
            
            with open(webp_filepath, "wb") as f:
                f.write(webp_data)
                
            total_webp += webp_size
            savings = (orig_size - webp_size) / orig_size * 100
            print(f"{filename:<35} | {orig_size/1024:>13.2f} | {webp_size/1024:>13.2f} | {comp_type:<20} | {savings:>8.1f}%")
        except Exception as e:
            print(f"Error converting {filename}: {e}")

    savings_total = (total_orig - total_webp) / total_orig * 100 if total_orig > 0 else 0
    print("-" * 105)
    print(f"{'TOTAL':<35} | {total_orig/1024:>13.2f} | {total_webp/1024:>13.2f} | {'—':<20} | {savings_total:>8.1f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert all PNG files in a directory to WebP dynamically selecting the smaller compression format.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to process (defaults to current directory)")
    parser.add_argument("--quality", type=int, default=85, help="Quality for lossy WebP compression (default: 85)")
    
    args = parser.parse_args()
    convert_pngs_in_directory(args.directory, args.quality)
