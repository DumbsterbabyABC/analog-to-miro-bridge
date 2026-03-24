import network
import time


def connect_wifi(ssid, password, max_retries=3, connect_timeout_s=20):
    wlan = network.WLAN(network.STA_IF)

    for attempt in range(1, max_retries + 1):
        try:
            # Reset WLAN interface to clear internal driver states.
            wlan.active(False)
            time.sleep(1)
            wlan.active(True)
            time.sleep(0.5)

            if wlan.isconnected():
                print("WLAN connected! IP:", wlan.ifconfig()[0])
                return wlan

            print("Connecting WiFi... (try {}/{})".format(attempt, max_retries))
            wlan.connect(ssid, password)

            start = time.time()
            while not wlan.isconnected() and (time.time() - start) < connect_timeout_s:
                time.sleep(0.5)
                print(".", end="")

            if wlan.isconnected():
                print("\nWLAN connected! IP:", wlan.ifconfig()[0])
                return wlan

            print("\nWiFi timeout, retrying...")
            wlan.disconnect()
            time.sleep(1)

        except OSError as err:
            print("\nWiFi error:", err)
            try:
                wlan.disconnect()
            except Exception:
                pass
            wlan.active(False)
            time.sleep(1)

    raise RuntimeError("WiFi could not connect after multiple retries.")
