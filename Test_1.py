import machine
import onewire
import ds18x20
import time

# --- 1. PIN-KONFIGURATION (basierend auf eurem Schaltplan) ---

# Steuer-Pins für die Kanäle S0-S3 (teilen sich beide Multiplexer)
s0 = machine.Pin(25, machine.Pin.OUT)
s1 = machine.Pin(26, machine.Pin.OUT)
s2 = machine.Pin(27, machine.Pin.OUT)
s3 = machine.Pin(14, machine.Pin.OUT)

# Enable-Pins (E#) der beiden Multiplexer (Active Low: 0 = AN, 1 = AUS)
en1 = machine.Pin(12, machine.Pin.OUT) # U2 (Erster Mux)
en2 = machine.Pin(13, machine.Pin.OUT) # U3 (Zweiter Mux)

# Daten-Pins am ESP32
sig1_pin = machine.Pin(32)             # Datenleitung für U2 (Temperatur)
sig2_pin = machine.Pin(33, machine.Pin.IN) # Datenleitung für U3 (Andere Signale)

# OneWire für den ersten Multiplexer (U2) vorbereiten
ds_sensor = ds18x20.DS18X20(onewire.OneWire(sig1_pin))

# Funktion zum Prüfen aller Pins
def check_all_pins():
    print("Pin-Status Übersicht:")
    for pin_num in range(0, 40):
        try:
            pin = machine.Pin(pin_num, machine.Pin.IN)
            value = pin.value()
            print(f"Pin {pin_num}: Wert = {value}")
        except Exception:
            pass

# Alle Pins einmal durchchecken (optional, kann bei vielen Pins unübersichtlich sein)
def set_channel(channel):
    """Stellt die Steuer-Pins S0-S3 auf den gewünschten Kanal (0-15)"""
    s0.value(channel & 0b0001)
    s1.value((channel >> 1) & 0b0001)
    s2.value((channel >> 2) & 0b0001)
    s3.value((channel >> 3) & 0b0001)
    time.sleep_ms(5) # Kurze Zeit geben, damit die Hardware umschaltet

print("Starte System-Scan für beide Multiplexer...")
print("=" * 50)

check_all_pins() #  Checkt alle pins auf Verbindung (optional, kann bei vielen Pins unübersichtlich sein)

# --- 2. HAUPTSCHLEIFE ---
while True:
    for ch in range(16):
        # 1. Weiche für BEIDE Multiplexer auf den aktuellen Kanal stellen
        set_channel(ch)
        
        # ---------------------------------------------------------
        # CHECK 1: ERSTER MULTIPLEXER (U2) -> Temperatursensoren
        # ---------------------------------------------------------
        en1.value(0) # U2 EINSCHALTEN
        en2.value(1) # U3 AUSSCHALTEN
        time.sleep_ms(10) # Kurz warten, bis das Signal stabil ist
        
        try:
            # Auf dem aktuell geschalteten Kanal nach IDs scannen
            roms = ds_sensor.scan()
            for rom in roms:
                hex_id = ''.join(['%02x' % b for b in rom])
                print(f"🔥 TEMPERATUR-SENSOR ERKANNT!")
                print(f"   -> ESP32 Pin:   IO32")
                print(f"   -> Multiplexer: U2 (Mux 1)")
                print(f"   -> Mux-Kanal:   C{ch}")
                print(f"   -> Sensor-ID:   {hex_id}")
                print("-" * 30)
        except Exception:
            # Falls auf dem leeren Kanal Quatsch gelesen wird, ignorieren
            pass
            
        # ---------------------------------------------------------
        # CHECK 2: ZWEITER MULTIPLEXER (U3) -> Generelles Signal
        # ---------------------------------------------------------
        en1.value(1) # U2 AUSSCHALTEN
        en2.value(0) # U3 EINSCHALTEN
        time.sleep_ms(10)
        
        # Hier prüfen wir, ob ein Signal (z.B. Strom) am Pin anliegt.
        # Wenn ihr an U3 einfache Schalter/Signale habt, ist der Wert 1 (High)
        if sig2_pin.value() == 1:
            print(f"⚡ SIGNAL ERKANNT!")
            print(f"   -> ESP32 Pin:   IO33")
            print(f"   -> Multiplexer: U3 (Mux 2)")
            print(f"   -> Mux-Kanal:   C{ch}")
            print("-" * 30)

    # Wenn alle 16 Kanäle durch sind, kurz warten und von vorn beginnen
    time.sleep(2)