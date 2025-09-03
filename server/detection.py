import requests
import time
from urllib.parse import urlparse

url = "http://localhost:3001/"  # change this

# --- Track Redirects ---
def test_redirects():
    print("\n=== Redirect Tracking ===")
    try:
        r = requests.get(url, allow_redirects=True, timeout=10)
        history = r.history
        if history:
            print(f"Initial URL: {url}")
            for i, step in enumerate(history):
                print(f"Redirect {i+1}: {step.status_code} -> {step.url} (Domain: {urlparse(step.url).netloc})")
            print(f"Final URL: {r.url} (Domain: {urlparse(r.url).netloc})")
        else:
            print("No redirects, final URL:", r.url)
    except Exception as e:
        print("Redirect test failed:", e)


# --- Track Domain Stability for 10s ---
def test_domain_stability(duration=10, interval=2):
    print(f"\n=== Domain Stability Test ({duration}s) ===")
    seen_domains = set()
    start = time.time()

    while time.time() - start < duration:
        try:
            r = requests.get(url, allow_redirects=True, timeout=10)
            domain = urlparse(r.url).netloc
            seen_domains.add(domain)
            print(f"Checked: {r.url} (Domain: {domain}, Status: {r.status_code})")
        except Exception as e:
            print("Request failed:", e)
        time.sleep(interval)

    print("\nDomains seen during test:", seen_domains)
    if len(seen_domains) > 1:
        print("⚠️ Domain switching detected!")
    else:
        print("✅ Domain stable.")


if __name__ == "__main__":
    test_redirects()
    test_domain_stability()
