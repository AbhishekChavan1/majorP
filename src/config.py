"""Configuration and constants for embedded systems agent"""

from pathlib import Path
from typing import Dict

# Base paths
BASE_DIR = Path(__file__).parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
PROJECTS_DIR = KNOWLEDGE_BASE_DIR / "projects"

# Groq Configuration
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_TEMPERATURE = 0.2  # Increased slightly for better tool decisions

# Embeddings Configuration
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"
CHROMA_DB_PATH = KNOWLEDGE_BASE_DIR / "chroma_db"

# Text Splitter Configuration
TEXT_SPLITTER_CHUNK_SIZE = 1000
TEXT_SPLITTER_CHUNK_OVERLAP = 200

# Web Search Configuration
WEB_SEARCH_MAX_RESULTS = 5

# Platform Configurations
PLATFORM_CONFIGS: Dict = {
    "arduino": {
        "language": "C++",
        "extensions": [".ino", ".cpp", ".h"],
        "libraries": ["Arduino.h", "SoftwareSerial.h", "Wire.h", "SPI.h"],
        "common_sensors": ["DHT22", "DS18B20", "BME280", "MPU6050"]
    },
    "esp32": {
        "language": "C++",
        "extensions": [".ino", ".cpp", ".h"],
        "libraries": ["WiFi.h", "WebServer.h", "BluetoothSerial.h", "SPIFFS.h"],
        "common_sensors": ["DHT22", "DS18B20", "BME280", "MPU6050", "HC-SR04"]
    },
    "raspberry_pi": {
        "language": "Python",
        "extensions": [".py"],
        "libraries": ["RPi.GPIO", "gpiozero", "picamera", "spidev", "smbus"],
        "common_sensors": ["DHT22", "DS18B20", "BME280", "MPU6050", "HC-SR04"]
    }
}

# Component Database
COMPONENT_DB: Dict = {
    "dht22": {
        "type": "Temperature & Humidity Sensor",
        "description": "Digital temperature and humidity sensor with high accuracy",
        "voltage": "3.3-5V",
        "pins": ["VCC (Red)", "Data (Yellow)", "NC (Not Connected)", "GND (Black)"],
        "libraries": ["DHT", "Adafruit_DHT"],
        "arduino_code": """#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  Serial.print("Humidity: ");
  Serial.print(h);
  Serial.print("%, Temperature: ");
  Serial.println(t);
  delay(2000);
}""",
        "raspberry_pi_code": """import Adafruit_DHT
sensor = Adafruit_DHT.DHT22
pin = 4

humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
if humidity is not None and temperature is not None:
    print(f'Temp: {temperature:.1f}°C  Humidity: {humidity:.1f}%')
"""
    },
    "hc-sr04": {
        "type": "Ultrasonic Distance Sensor",
        "description": "Measures distance using ultrasonic waves (2cm-400cm range)",
        "voltage": "5V",
        "pins": ["VCC", "Trig", "Echo", "GND"],
        "libraries": ["NewPing (Arduino)"],
        "arduino_code": """#define trigPin 9
#define echoPin 8

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  long duration, distance;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = (duration/2) / 29.1;

  Serial.print(distance);
  Serial.println(" cm");
  delay(1000);
}""",
        "raspberry_pi_code": """import RPi.GPIO as GPIO
import time

TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)
"""
    },
    "led": {
        "type": "Light Emitting Diode",
        "description": "Basic LED for visual indication",
        "voltage": "1.8-3.3V (with current limiting resistor)",
        "pins": ["Anode (+)", "Cathode (-)"],
        "arduino_code": """int ledPin = 13;

void setup() {
  pinMode(ledPin, OUTPUT);
}

void loop() {
  digitalWrite(ledPin, HIGH);
  delay(1000);
  digitalWrite(ledPin, LOW);
  delay(1000);
}""",
        "raspberry_pi_code": """import RPi.GPIO as GPIO
import time

LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    while True:
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
"""
    }
}

# Pinout Information
PINOUTS: Dict = {
    "arduino_uno": {
        "description": "Arduino Uno R3 Pinout",
        "digital_pins": "0-13 (pins 0,1 are RX,TX for serial communication)",
        "analog_pins": "A0-A5 (can also be used as digital pins 14-19)",
        "power_pins": "3.3V, 5V, GND, VIN (7-12V input)",
        "pwm_pins": "3, 5, 6, 9, 10, 11 (marked with ~ symbol)",
        "special_pins": {
            "I2C SDA": "A4 (or pin 18)",
            "I2C SCL": "A5 (or pin 19)",
            "SPI SS": "10",
            "SPI MOSI": "11",
            "SPI MISO": "12",
            "SPI SCK": "13",
            "LED_BUILTIN": "13"
        },
        "notes": "- Pins 0,1 used for USB communication\n- Pin 13 has built-in LED\n- Maximum current per pin: 20mA"
    },
    "esp32": {
        "description": "ESP32 Development Board Pinout",
        "digital_pins": "0-39 (some are input-only: 34, 35, 36, 39)",
        "analog_pins": "32-39, 25-27, 12-15, 2, 0, 4 (12-bit ADC)",
        "touch_pins": "0, 2, 4, 12, 13, 14, 15, 27, 32, 33",
        "pwm_pins": "All digital pins support PWM",
        "special_pins": {
            "I2C SDA": "21 (default)",
            "I2C SCL": "22 (default)",
            "UART RX": "3",
            "UART TX": "1",
            "SPI SS": "5",
            "SPI MOSI": "23",
            "SPI MISO": "19",
            "SPI SCK": "18",
            "Built-in LED": "2"
        },
        "notes": "- WiFi and Bluetooth built-in\n- 3.3V logic level\n- Some pins are strapping pins (0, 2, 5, 12, 15)\n- Pins 6-11 connected to flash memory"
    },
    "raspberry_pi": {
        "description": "Raspberry Pi 4 GPIO Pinout (40-pin header)",
        "gpio_pins": "GPIO 2-27 (40-pin header)",
        "power_pins": "3.3V (pins 1,17), 5V (pins 2,4), GND (pins 6,9,14,20,25,30,34,39)",
        "special_pins": {
            "I2C SDA": "GPIO 2 (pin 3)",
            "I2C SCL": "GPIO 3 (pin 5)",
            "UART RX": "GPIO 15 (pin 10)",
            "UART TX": "GPIO 14 (pin 8)",
            "SPI MOSI": "GPIO 10 (pin 19)",
            "SPI MISO": "GPIO 9 (pin 21)",
            "SPI SCK": "GPIO 11 (pin 23)",
            "SPI CE0": "GPIO 8 (pin 24)",
            "SPI CE1": "GPIO 7 (pin 26)",
            "PWM0": "GPIO 12 (pin 32)",
            "PWM1": "GPIO 13 (pin 33)"
        },
        "notes": "- 3.3V logic level (NOT 5V tolerant!)\n- Maximum current per pin: 16mA\n- Total current from 3.3V supply: 50mA\n- BCM numbering vs Physical pin numbering"
    }
}

# Code Templates
CODE_TEMPLATES: Dict = {
    "arduino": {
        "basic": """// Arduino Basic Template
#include <Arduino.h>

void setup() {
    Serial.begin(9600);
    Serial.println("Arduino Started!");
    // Initialize your components here
}

void loop() {
    // Main code here
    Serial.println("Hello World!");
    delay(1000);
}
""",
        "sensor": """// Arduino Sensor Reading Template
#include <Arduino.h>

// Pin definitions
const int sensorPin = A0;
const int ledPin = 13;

void setup() {
    Serial.begin(9600);
    pinMode(sensorPin, INPUT);
    pinMode(ledPin, OUTPUT);
    Serial.println("Sensor Monitor Started");
}

void loop() {
    int sensorValue = analogRead(sensorPin);
    float voltage = sensorValue * (5.0 / 1023.0);

    Serial.print("Sensor Value: ");
    Serial.print(sensorValue);
    Serial.print(", Voltage: ");
    Serial.print(voltage, 2);
    Serial.println("V");

    if (sensorValue > 512) {
        digitalWrite(ledPin, HIGH);
    } else {
        digitalWrite(ledPin, LOW);
    }

    delay(500);
}
""",
        "servo": """// Arduino Servo Control Template
#include <Servo.h>

Servo myServo;
const int servoPin = 9;
const int potPin = A0;

void setup() {
    Serial.begin(9600);
    myServo.attach(servoPin);
    Serial.println("Servo Control Ready");
}

void loop() {
    int potValue = analogRead(potPin);
    int angle = map(potValue, 0, 1023, 0, 180);

    myServo.write(angle);

    Serial.print("Potentiometer: ");
    Serial.print(potValue);
    Serial.print(", Servo Angle: ");
    Serial.println(angle);

    delay(50);
}
"""
    },
    "esp32": {
        "basic": """// ESP32 Basic Template
#include <WiFi.h>
#include <Arduino.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("ESP32 Starting...");

    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
}

void loop() {
    Serial.println("ESP32 is running...");
    delay(5000);
}
""",
        "webserver": """// ESP32 Web Server Template
#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

WebServer server(80);
int ledPin = 2;
bool ledState = false;

void handleRoot() {
    String html = "<html><body>";
    html += "<h1>ESP32 Web Server</h1>";
    html += "<p>LED Status: " + String(ledState ? "ON" : "OFF") + "</p>";
    html += "<p><a href='/led/on'>Turn LED ON</a></p>";
    html += "<p><a href='/led/off'>Turn LED OFF</a></p>";
    html += "</body></html>";

    server.send(200, "text/html", html);
}

void handleLEDOn() {
    ledState = true;
    digitalWrite(ledPin, HIGH);
    server.send(200, "text/plain", "LED is ON");
}

void handleLEDOff() {
    ledState = false;
    digitalWrite(ledPin, LOW);
    server.send(200, "text/plain", "LED is OFF");
}

void setup() {
    Serial.begin(115200);
    pinMode(ledPin, OUTPUT);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }

    Serial.println("WiFi connected!");
    Serial.println("IP address: " + WiFi.localIP().toString());

    server.on("/", handleRoot);
    server.on("/led/on", handleLEDOn);
    server.on("/led/off", handleLEDOff);

    server.begin();
    Serial.println("HTTP server started");
}

void loop() {
    server.handleClient();
}
""",
        "bluetooth": """// ESP32 Bluetooth Template
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;
String deviceName = "ESP32-Device";

void setup() {
    Serial.begin(115200);
    SerialBT.begin(deviceName);
    Serial.println("Device started, now you can pair it with bluetooth!");
    Serial.println("Device name: " + deviceName);
}

void loop() {
    if (Serial.available()) {
        String message = Serial.readString();
        SerialBT.print(message);
        Serial.print("Sent: " + message);
    }

    if (SerialBT.available()) {
        String message = SerialBT.readString();
        Serial.print("Received: " + message);
        SerialBT.print("Echo: " + message);
    }

    delay(20);
}
"""
    },
    "raspberry_pi": {
        "basic": """#!/usr/bin/env python3
# Raspberry Pi Basic Template

import time
import sys

def setup():
    \"\"\"Initialize your components here\"\"\"
    print("Raspberry Pi application starting...")
    print("Setup complete!")

def main_loop():
    \"\"\"Main program loop\"\"\"
    print("Entering main loop...")

    try:
        counter = 0
        while True:
            print(f"Loop iteration: {counter}")
            counter += 1
            time.sleep(2)

    except KeyboardInterrupt:
        cleanup()

def cleanup():
    \"\"\"Cleanup resources before exit\"\"\"
    print("\\nCleaning up and exiting...")
    sys.exit(0)

if __name__ == "__main__":
    setup()
    main_loop()
""",
        "gpio": """#!/usr/bin/env python3
# Raspberry Pi GPIO Template

import RPi.GPIO as GPIO
import time
import signal
import sys

LED_PIN = 18
BUTTON_PIN = 2

def setup_gpio():
    \"\"\"Setup GPIO pins\"\"\"
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    print("GPIO setup complete")

def signal_handler(sig, frame):
    \"\"\"Handle Ctrl+C gracefully\"\"\"
    cleanup()

def cleanup():
    \"\"\"Cleanup GPIO and exit\"\"\"
    print("\\nCleaning up GPIO...")
    GPIO.cleanup()
    sys.exit(0)

def main_loop():
    \"\"\"Main application loop\"\"\"
    print("Starting GPIO control loop...")
    print("Press Ctrl+C to exit")

    led_state = False

    try:
        while True:
            button_pressed = GPIO.input(BUTTON_PIN) == GPIO.LOW

            if button_pressed:
                led_state = not led_state
                GPIO.output(LED_PIN, GPIO.HIGH if led_state else GPIO.LOW)
                print(f"Button pressed! LED {'ON' if led_state else 'OFF'}")

                time.sleep(0.3)

            time.sleep(0.1)

    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    setup_gpio()
    main_loop()
""",
        "camera": """#!/usr/bin/env python3
# Raspberry Pi Camera Template

import time
from datetime import datetime
import os

try:
    from picamera2 import Picamera2
    CAMERA_LIB = "picamera2"
except ImportError:
    try:
        from picamera import PiCamera
        CAMERA_LIB = "picamera"
    except ImportError:
        CAMERA_LIB = None
        print("No camera library found. Install with: sudo apt install python3-picamera2")

def setup_camera():
    \"\"\"Initialize camera\"\"\"
    if CAMERA_LIB == "picamera2":
        camera = Picamera2()
        camera.configure(camera.create_still_configuration())
        camera.start()
        return camera
    elif CAMERA_LIB == "picamera":
        camera = PiCamera()
        camera.resolution = (1920, 1080)
        camera.start_preview()
        time.sleep(2)
        return camera
    else:
        return None

def capture_image(camera, filename=None):
    \"\"\"Capture a single image\"\"\"
    if not camera:
        print("Camera not available")
        return False

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.jpg"

    try:
        if CAMERA_LIB == "picamera2":
            camera.capture_file(filename)
        elif CAMERA_LIB == "picamera":
            camera.capture(filename)

        print(f"Image saved: {filename}")
        return True

    except Exception as e:
        print(f"Error capturing image: {e}")
        return False

def main_loop():
    \"\"\"Main camera application\"\"\"
    camera = setup_camera()

    if not camera:
        print("Failed to initialize camera")
        return

    print("Camera ready. Press Ctrl+C to exit")
    print("Capturing images every 10 seconds...")

    try:
        while True:
            capture_image(camera)
            time.sleep(10)

    except KeyboardInterrupt:
        print("\\nExiting...")
    finally:
        if CAMERA_LIB == "picamera2":
            camera.stop()
        elif CAMERA_LIB == "picamera":
            camera.stop_preview()
            camera.close()
        print("Camera closed")

if __name__ == "__main__":
    main_loop()
"""
    }
}

# Library Database
LIBRARY_DATABASE: Dict = {
    "arduino": {
        "dht": {
            "name": "DHT sensor library",
            "description": "Arduino library for DHT11, DHT22, etc Temp & Humidity Sensors",
            "installation": "Arduino Library Manager: Search 'DHT sensor library'",
            "github": "https://github.com/adafruit/DHT-sensor-library",
            "example": "#include <DHT.h>\nDHT dht(2, DHT22);"
        },
        "servo": {
            "name": "Servo",
            "description": "Control servo motors",
            "installation": "Built-in Arduino library",
            "example": "#include <Servo.h>\nServo myservo;"
        },
        "wifi": {
            "name": "WiFi",
            "description": "WiFi functionality for ESP32/ESP8266",
            "installation": "Built-in for ESP32",
            "example": "#include <WiFi.h>\nWiFi.begin(ssid, password);"
        }
    },
    "raspberry_pi": {
        "rpi.gpio": {
            "name": "RPi.GPIO",
            "description": "Raspberry Pi GPIO control library",
            "installation": "pip install RPi.GPIO",
            "example": "import RPi.GPIO as GPIO\nGPIO.setmode(GPIO.BCM)"
        },
        "gpiozero": {
            "name": "GPIO Zero",
            "description": "Simple interface to GPIO devices",
            "installation": "pip install gpiozero",
            "example": "from gpiozero import LED\nled = LED(18)"
        },
        "picamera": {
            "name": "PiCamera",
            "description": "Raspberry Pi camera module interface",
            "installation": "pip install picamera",
            "example": "from picamera import PiCamera\ncamera = PiCamera()"
        }
    }
}
