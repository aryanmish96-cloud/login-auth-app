import urllib.request
import json

def check_health():
    try:
        response = urllib.request.urlopen("http://127.0.0.1:5000/")
        data = json.load(response)
        print(f"Health Check Response: {data}")
        return True
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return False

if __name__ == "__main__":
    check_health()
