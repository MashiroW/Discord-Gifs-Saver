import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from curl_cffi import requests

# Configurations
INPUT_FILE = "discord-favorite-gifs.txt"
RAW_FOLDER = "raw"
CONVERTED_FOLDER = "converted_gifs"
MAX_WORKERS = 5
MAX_SIZE_MB = 10.0

# Ensure directories exist
os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)


def extract_urls_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: '{file_path}' not found.")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return re.findall(r"(https?://\S+)", content)


def convert_video_to_gif(input_path, output_path):
    """
    Uses FFmpeg to convert a video file into a standard .gif file.
    Includes smart optimizations to drastically reduce file size under 10MB.
    """
    try:
        # Step 1: Attempt conversion at high quality using a split palette generator
        # Scales width to a standard 400px (retaining aspect ratio) and targets 20 frames per second
        command = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", "fps=20,scale=400:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse=dither=sierra2_4a",
            output_path
        ]
        
        # Run conversion silently
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        # Step 2: Safety Check. If the resulting GIF is STILL over 10MB, compress it strictly.
        if os.path.exists(output_path) and (os.path.getsize(output_path) / (1024 * 1024)) > MAX_SIZE_MB:
            print(f"⚠️ GIF too large ({os.path.getsize(output_path) / (1024*1024):.1f}MB). Applying heavier compression...")
            
            # Drops resolution to 320px and drops framerate to 12fps to ensure it strictly respects the 10MB ceiling
            fallback_command = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", "fps=12,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=none",
                output_path
            ]
            subprocess.run(fallback_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Final absolute size check
        final_size = os.path.getsize(output_path) / (1024 * 1024)
        if final_size > MAX_SIZE_MB:
            print(f"❌ Could not bring {os.path.basename(output_path)} under 10MB safely (Final: {final_size:.1f}MB)")
            # Delete if it broke the rule
            os.remove(output_path)
            return False
            
        return True
    except subprocess.CalledProcessError:
        print(f"❌ FFmpeg error during conversion for: {os.path.basename(input_path)}. Is FFmpeg installed?")
        return False
    except Exception as e:
        print(f"💥 Error converting {input_path}: {e}")
        return False


def process_url(url):
    try:
        # Clean URL base name mapping
        clean_url = url.split("?")[0]
        base_name = clean_url.split("/")[-1]
        
        if not base_name or base_name in ["mp4", "webm", "gif"]:
            parts = [p for p in clean_url.split("/") if p]
            base_name = f"tenor_{parts[-2]}" if len(parts) >= 2 else "asset"

        name_without_ext = re.sub(r"\.(gif|mp4|webm|png|jpg|jpeg)$", "", base_name, flags=re.IGNORECASE)

        headers = {"Accept": "*/*", "Referer": "https://tenor.com/"}
        response = requests.get(url, impersonate="chrome", headers=headers, timeout=20)

        if response.status_code == 200 and response.content:
            file_bytes = response.content

            # Detect content type natively via Magic Bytes
            if file_bytes.startswith(b"GIF87a") or file_bytes.startswith(b"GIF89a"):
                detected_ext = ".gif"
                is_video = False
            elif file_bytes.startswith(b"\x00\x00\x00") and b"ftyp" in file_bytes[4:16]:
                detected_ext = ".mp4"
                is_video = True
            elif file_bytes.startswith(b"\x1a\x45\xdf\xa3"):
                detected_ext = ".webm"
                is_video = True
            elif b"<!DOCTYPE html>" in file_bytes[:100]:
                return
            else:
                detected_ext = ".mp4" if "mp4" in url.lower() else (".webm" if "webm" in url.lower() else ".gif")
                is_video = detected_ext in [".mp4", ".webm"]

            # Paths
            raw_filename = f"{name_without_ext}{detected_ext}"
            raw_path = os.path.join(RAW_FOLDER, raw_filename)
            gif_filename = f"{name_without_ext}.gif"
            gif_path = os.path.join(CONVERTED_FOLDER, gif_filename)

            # Save the untouched raw asset first
            with open(raw_path, "wb") as f:
                f.write(file_bytes)

            # Handle the folder distribution logic
            if not is_video:
                # It's already a native GIF or image file. Ensure it obeys the 10MB limit before copying.
                if (len(file_bytes) / (1024 * 1024)) <= MAX_SIZE_MB:
                    with open(gif_path, "wb") as f:
                        f.write(file_bytes)
                    print(f"✅ Saved Native GIF to both folders: {gif_filename}")
                else:
                    print(f"⏭️ Native GIF {gif_filename} skipped in converted folder because it exceeds 10MB.")
            else:
                # It is a video format asset (MP4/WebM). Trigger specialized FFmpeg processing.
                success = convert_video_to_gif(raw_path, gif_path)
                if success:
                    print(f"🎬 Successfully converted video to GIF under 10MB: {gif_filename}")

        else:
            print(f"❌ Download failed ({response.status_code}): {url}")

    except Exception as e:
        print(f"💥 Error processing {url}: {e}")


def main():
    urls = extract_urls_from_file(INPUT_FILE)
    if not urls:
        print("No URLs found to process.")
        return

    print(f"Found {len(urls)} links. Processing raw downloads and generating optimized gifs...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_url, urls)

    print(f"\n🎉 All tasks complete!\n📁 Raw files -> '{RAW_FOLDER}/'\n📁 Valid GIFs (<10MB) -> '{CONVERTED_FOLDER}/'")


if __name__ == "__main__":
    main()