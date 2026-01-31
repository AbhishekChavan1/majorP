# RGB Signal Project

## Overview

This project creates a RGB LED blinker signal using Arduino. The RGB LED is connected to digital pins 9, 10, and 11.

## Hardware Setup

### Components

* Arduino Board
* RGB LED
* Breadboard
* Jumper Wires

### Connections

* Connect the RGB LED to digital pins 9, 10, and 11 on the Arduino board.

## Usage

### Code

```cpp
#include <Arduino.h>

const int redPin = 9;
const int greenPin = 10;
const int bluePin = 11;

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
}

void loop() {
  // Red blink
  digitalWrite(redPin, HIGH);
  delay(500);
  digitalWrite(redPin, LOW);
  delay(500);

  // Green blink
  digitalWrite(greenPin, HIGH);
  delay(500);
  digitalWrite(greenPin, LOW);
  delay(500);

  // Blue blink
  digitalWrite(bluePin, HIGH);
  delay(500);
  digitalWrite(bluePin, LOW);
  delay(500);
}

```