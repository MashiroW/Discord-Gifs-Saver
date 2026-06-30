# Discord Favorite GIFs Downloader & Optimizer

A lightweight, automated Python utility to export, download, and optimize your favorite GIFs from Discord. 

Discord rarely stores favorites as native `.gif` files; instead, they are usually modern, compressed video streams (like `.mp4` or `.webm`) served by platforms like Tenor. This tool extracts your exact favorites list from Discord, downloads the high-quality source video files, and uses smart `FFmpeg` processing to convert them back into highly optimized `.gif` files that strictly obey Discord's **10MB upload limit**.

Here's the reason of its existence:

![Alternative text here](https://media.discordapp.net/attachments/958361590959341650/1521623847760040036/image.png?ex=6a458223&is=6a4430a3&hm=3dd0ce37e95d607f0e42d7e4a2890e3aa6cabb0ef1ecbd62fe54f5ab74722473&=&format=webp&quality=lossless&width=587&height=777)

## ✨ Features

* **One-Click Export:** A simple browser console script pulls your entire Discord favorite GIFs list instantly.
* **Smart Asset Recovery:** Leverages native file magic bytes to accurately detect whether an asset is a native GIF, MP4, or WebM—even when URLs are masked.
* **Automated FFmpeg Conversion:** Converts video formats back into `.gif` files using a two-pass palette generator for maximum visual fidelity.
* **Auto-Compression Engine:** If a generated GIF exceeds 10MB, the script automatically applies heavy downscaling and frame-rate optimization to bring it under the 10MB Discord attachment ceiling.
* **Multi-threaded Speed:** Downloads and processes up to 5 files concurrently for rapid execution.

---

## 🛠️ Prerequisites

Before getting started, make sure you have the following installed on your machine:

1. **Python 3.8+**
2. **FFmpeg:** Must be installed and added to your system's `PATH`.
   * *Mac:* `brew install ffmpeg`
   * *Windows:* Install via Chocolatey `choco install ffmpeg` or download directly from the [official site](https://www.ffmpeg.org/download.html). 
3. **Python Dependencies:** Install via pip:
   ```bash
   pip install curl_cffi
---

## 🚀 How to Use

### Step 1: Extract Your Favorites List from Discord

1. Open your web browser and navigate to **Discord** (Web App).
2. Open your browser's Developer Tools Console (`F12` or `Ctrl+Shift+I` / `Cmd+Option+I`).
3. Open your GIF picker panel inside Discord, click on **Favorites**, and scroll down a bit to ensure the list initializes in your client session.
4. Copy and paste the following JavaScript snippet into your browser console and press `Enter`:

```javascript
window.FrecencyUserSettings ??= webpackChunkdiscord_app.push([[Symbol()],,e=>e.b&&Object.values(e.c).values().map(m=>m.exports).filter(x=>typeof x=="object"&&x!=window&&x!=DOMTokenList.prototype).flatMap(x=>[x,...Object.values(x)]).find(x=>x?.ProtoClass?.typeName?.endsWith(".FrecencyUserSettings"))]);

function downloadTxt(content, download) {
  const text = content.join("\n"); 
  Object.assign(document.createElement("a"), {
    href: URL.createObjectURL(new Blob([text], { type: "text/plain" })),
    download
  }).click();
}

FrecencyUserSettings.loadIfNecessary();

const gifsStore = FrecencyUserSettings.getCurrentValue().favoriteGifs.gifs;

const gifLinks = Object.values(gifsStore).map(gif => {
  let link = gif.src || gif.url || gif;
  if (typeof link === 'string') {
    return link.startsWith("//") ? "https:" + link : link;
  }
  return null;
}).filter(Boolean);

if (gifLinks.length > 0) {
  downloadTxt(gifLinks, "discord-favorite-gifs.txt");
  console.log(`Successfully extracted ${gifLinks.length} links.`);
} else {
  console.error("No GIF links could be found. Check if your favorites tab is currently loading in Discord.");
}

```

5. Your browser will automatically download a file named `discord-favorite-gifs.txt`.

### Step 2: Download and Convert the Assets

1. Move the downloaded `discord-favorite-gifs.txt` file into the same directory as the `gifs_dl.py` Python script.
2. Run the script:
```bash
python gifs_dl.py

```



---

## 📁 Folder Directory Details

When running the script, it will create two target folders to separate your assets based on their conversion lifecycle:

```text
├── discord-favorite-gifs.txt   # Your exported link dataset
├── gifs_dl.py                  # The execution script
├── raw/                        # The "As-Is" download folder
└── converted_gifs/             # The Discord-ready upload folder
```

### 📥 The `raw/` Folder

This folder saves the **untouched original assets** exactly as they are hosted online.

* **What it contains:** A mix of `.mp4`, `.webm`, and native `.gif` files.
* **The Reality Check:** You will notice that the vast majority of files here are actually silent video files (`.mp4`), not image files. This is because modern web platforms (like Tenor and Giphy) stream highly compressed video to your Discord app to drastically save your bandwidth and load instantly.
* **Use Case:** Keep these if you want the highest possible quality source files to archive on your hard drive, edit in video software, or use on platforms that natively support `.mp4` looping.

### 🎬 The `converted_gifs/` Folder

This folder holds the **processed, standard `.gif` image files** generated by the script's compression engine.

* **What it contains:** Strictly true `.gif` images. Every single file here has been processed through `FFmpeg`.
* **The Optimization Process:** For video files found in the raw folder, the script uses a two-step `FFmpeg` pipeline. It generates a custom high-fidelity 256-color palette to keep things looking sharp. If the converted GIF exceeds the **10MB limit**, a fallback rule instantly steps in—dropping the resolution to `320px` and the framerate to `12fps` to force the file under the ceiling.
* **The Exception:** Native `.gif` files that were already under 10MB in your favorites list are cleanly copied here without any re-encoding loss. If a native GIF is over 10MB, it will be skipped here to keep this directory strictly Discord-compliant.
* **Use Case:** This is your drop-and-go folder. Every asset in here is guaranteed to be universally shareable back into standard Discord text channels without hitting an upload error.

---

## ⚙️ Configuration Adjustments

You can tweak the constants directly inside `gifs_dl.py` to match your needs:

* `MAX_WORKERS = 5` — Adjusts how many downloads happen simultaneously. Reduce this if you have a weak internet connection.
* `MAX_SIZE_MB = 10.0` — The ceiling limit for standard Discord file uploads. You can boost this to `50.0` or `100.0` if you have Discord Nitro perks.
