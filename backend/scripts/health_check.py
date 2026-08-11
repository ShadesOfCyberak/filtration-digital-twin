import sys
import httpx


def check_system():
    url = "http://localhost:8000/health"
    try:
        response = httpx.get(url, timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print("System Health Check PASSED:")
            print(data)
            sys.exit(0)
        else:
            print(f"Health check failed with status code {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Health check error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    check_system()
