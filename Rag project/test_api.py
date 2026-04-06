import urllib.request
import json

try:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/recommend",
        data=b'{"story":"A hacker movie"}',
        headers={"Content-Type":"application/json"}
    )
    resp = urllib.request.urlopen(req)
    print(resp.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code)
    print(e.read().decode())
except Exception as e:
    print("ERROR:", e)
