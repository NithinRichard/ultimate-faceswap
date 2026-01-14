import os
import urllib.request
import ssl

# Bypass SSL verification if needed for some local environments, though typically not recommended, 
# it helps in some restrictive windows environments.
ssl._create_default_https_context = ssl._create_unverified_context

url = "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx"
dest_dir = os.path.expanduser("~/.insightface/models")
os.makedirs(dest_dir, exist_ok=True)
dest_path = os.path.join(dest_dir, "inswapper_128.onnx")

print(f"Downloading {url} to {dest_path}...")
try:
    urllib.request.urlretrieve(url, dest_path)
    print("Download complete!")
except Exception as e:
    print(f"Error: {e}")
