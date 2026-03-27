import requests
import functools

# Cache hasil lookup agar IP yang sama tidak di-query berulang
@functools.lru_cache(maxsize=1000)
def get_geo(ip):
    # Skip IP lokal
    if ip.startswith(("127.", "192.168.", "10.")):
        return {"country": "Local", "city": "Local"}
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}",
            timeout=3
        ).json()
        return {
            "country": r.get("country", "Unknown"),
            "city":    r.get("city", "Unknown"),
            "lat":     r.get("lat"),
            "lon":     r.get("lon"),
        }
    except:
        return {"country": "Unknown", "city": "Unknown"}