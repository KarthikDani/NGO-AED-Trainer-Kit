#include <Arduino.h>
#include <SD.h>
#include <ESP32Encoder.h>
#include <ESP32Audio.h>

// SD Card Configuration
#define SD_CS_PIN 5
File root;
File currentDir;

// Rotary Encoder Pins
#define ROTARY_A_PIN 32
#define ROTARY_B_PIN 33
ESP32Encoder encoder;
int lastPosition = 0;

// Push Button Pin
#define BUTTON_PIN 27
bool lastButtonState = HIGH;
bool currentButtonState;

// I2S Configuration
#define I2S_BCK 26
#define I2S_WS 25
#define I2S_DATA_OUT 22
ESP32Audio audio;

// Variables to track current selection
int currentDirectoryIndex = 0;
int currentFileIndex = 0;
String directories[10];
int directoryCount = 0;

void setup() {
  Serial.begin(115200);

  // Initialize SD card
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("SD Card Initialization failed!");
    while (1);
  }
  Serial.println("SD Card Initialized.");
  
  // Load directories
  loadDirectories();

  // Initialize Rotary Encoder
  ESP32Encoder::useInternalWeakPullResistors = UP;
  encoder.attachHalfQuad(ROTARY_A_PIN, ROTARY_B_PIN);
  encoder.clearCount();

  // Initialize Button
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Initialize I2S
  audio.setPinout(I2S_BCK, I2S_WS, I2S_DATA_OUT);
  audio.i2sSetup(44100, 16);
}

void loop() {
  // Handle rotary encoder for directory selection
  int newPosition = encoder.getCount();
  if (newPosition != lastPosition) {
    lastPosition = newPosition;
    currentDirectoryIndex = (lastPosition / 2) % directoryCount;
    
    if (currentDirectoryIndex < 0) currentDirectoryIndex += directoryCount;
    Serial.println("Selected Directory: " + directories[currentDirectoryIndex]);
    currentFileIndex = 0; // Reset file index on directory change
  }

  // Handle button press for file selection
  currentButtonState = digitalRead(BUTTON_PIN);
  if (lastButtonState == HIGH && currentButtonState == LOW) {
    // Button pressed
    playNextFile();
  }
  lastButtonState = currentButtonState;
}

void loadDirectories() {
  root = SD.open("/");
  if (!root) {
    Serial.println("Failed to open root directory!");
    return;
  }

  directoryCount = 0;
  
  while (true) {
    File entry = root.openNextFile();
    if (!entry) {
      break; // No more files
    }

    if (entry.isDirectory()) {
      directories[directoryCount++] = String(entry.name());
      Serial.println("Directory: " + directories[directoryCount - 1]);
      if (directoryCount >= 10) break; // Limit to 10 directories
    }
    entry.close();
  }
}

void playNextFile() {
  if (currentDir) {
    currentDir.close();
  }

  currentDir = SD.open("/" + directories[currentDirectoryIndex]);
  int fileCount = 0;
  File fileToPlay;

  while (true) {
    File entry = currentDir.openNextFile();
    if (!entry) {
      break; // No more files
    }

    if (!entry.isDirectory()) {
      if (fileCount == currentFileIndex) {
        fileToPlay = entry;
        break;
      }
      fileCount++;
    }
    entry.close();
  }

  if (fileToPlay) {
    Serial.println("Playing File: " + String(fileToPlay.name()));
    audio.connecttoFS(SD, fileToPlay.name());
    currentFileIndex++;
  } else {
    currentFileIndex = 0; // Restart file index
    Serial.println("No more files in directory.");
  }
}
