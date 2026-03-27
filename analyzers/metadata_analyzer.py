import exifread
from PIL import Image
import os

def extract_image_metadata(file_path):
    result = {}
    try:
        with open(file_path, "rb") as f:
            tags = exifread.process_file(f, details=False)
        for tag, val in tags.items():
            result[tag] = str(val)

        # Ekstrak GPS kalau ada
        lat = tags.get("GPS GPSLatitude")
        lon = tags.get("GPS GPSLongitude")
        if lat and lon:
            result["gps_lat"] = str(lat)
            result["gps_lon"] = str(lon)
            result["has_gps"] = True

        img = Image.open(file_path)
        result["format"]     = img.format
        result["dimensions"] = f"{img.width}x{img.height}"
        result["mode"]       = img.mode
    except Exception as e:
        result["error"] = str(e)
    return result

def detect_magic_bytes(file_path):
    # Cek apakah ekstensi sesuai isi file
    magic_map = {
        b"\xff\xd8\xff":     "JPEG",
        b"\x89PNG":          "PNG",
        b"PK\x03\x04":       "ZIP/DOCX/XLSX",
        b"%PDF":             "PDF",
        b"MZ":               "Windows Executable",
        b"\x7fELF":          "Linux Executable",
    }
    with open(file_path, "rb") as f:
        header = f.read(8)
    detected = "Unknown"
    for magic, ftype in magic_map.items():
        if header.startswith(magic):
            detected = ftype
            break
    ext = os.path.splitext(file_path)[1].upper().strip(".")
    mismatch = ext not in detected.upper()
    return {"detected_type": detected,
            "extension": ext,
            "mismatch": mismatch}