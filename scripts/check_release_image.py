"""Read-only startup/HTTP probe run inside the isolated production-image CI app."""

import json
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"


def response(path, method="GET"):
    request = urllib.request.Request(
        BASE + path, method=method, headers={"Host": "review2.test"}
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as result:
            return result.status
    except urllib.error.HTTPError as error:
        return error.code


def main():
    for _ in range(30):
        try:
            if response("/health") == 200:
                break
        except urllib.error.URLError:
            pass
        time.sleep(1)
    else:
        raise SystemExit("Isolated image did not become healthy")
    results = {}
    for path in [
        "/",
        "/builds",
        "/builds/skyline",
        "/builds/miata",
        "/builds/bmw",
        "/about",
        "/portfolio",
        "/portfolio/projects/rag",
        "/rag",
    ]:
        results[path] = response(path)
        assert results[path] == 200, (path, results[path])
    assert response("/api/me") == 401
    assert response("/api/admin") == 401
    assert response("/api/rag/import", method="POST") == 401
    print(json.dumps({"routes": results, "anonymous_protected_routes": 401}))


if __name__ == "__main__":
    main()
