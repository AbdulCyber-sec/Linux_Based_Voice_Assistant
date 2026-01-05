# Linux-Based Voice Assistant
 - This project is a voice-controlled assistant designed for Linux systems. It enables users to perform tasks through voice commands, such as managing files, searching the web, and more. Built using Python and open-source tools, it focuses on simplicity, efficiency, and user-friendliness. Perfect for enhancing productivity on Linux!
 - This project is a Python-based voice assistant designed for Linux systems. It leverages voice commands to execute system operations, fetch information, and perform other tasks seamlessly. The assistant, named Igris, provides a user-friendly interface for automation and productivity.

## Features

- Voice Recognition: Captures and processes user voice commands using the `speech_recognition` library.
- Text-to-Speech (TTS): Converts text responses into speech using the `gTTS` library.
- Custom Greetings: Provides greetings based on the time of day.
- Application Management: Opens and closes Linux applications.
- System Monitoring: Checks CPU, memory, disk, and battery status.
- Google Search: Fetches top results for queries using the SerpAPI.
- Weather Updates: Displays current weather for a specified city using OpenWeatherMap API.
- File and Folder Search: Locates files and folders using Linux commands.
- Mouse and Keyboard Automation: Controls mouse and keyboard actions programmatically.
- Dynamic Commands: Allows execution of system commands and typing automation.

## Installation

1. Clone the Repository:

   ```bash
   git clone https://github.com/yourusername/linux-voice-assistant.git
   cd linux-voice-assistant
   ```

2. Install Dependencies:
   Ensure you have Python 3.7 or higher installed. Install required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Setup APIs:

   - [SerpAPI](https://serpapi.com/): Get an API key for Google Search integration.
   - [OpenWeatherMap](https://openweathermap.org/): Get an API key for weather updates.

4. Pre-Generate Responses:
   Run the script to cache common TTS responses for faster playback:

   ```bash
   python main.py --cache-tts
   ```

5. Run the Assistant:

   ```bash
   python main.py
   ```

## Usage

1. Launch the assistant and speak commands like:

   - "Open Firefox"
   - "Search Linux tutorials"
   - "Check CPU usage"
   - "What's the weather in Madurai?"

2. The assistant will execute tasks and provide spoken feedback.

## Configuration

- Custom Commands: Add or modify commands in the `execute_command` function.
- Voice Parameters: Adjust TTS speed or language in the `speak` function.
- Default City: Update the default city for weather in the `get_weather` function.

## Requirements

- Python 3.7+
- Libraries: `speech_recognition`, `gTTS`, `playsound`, `psutil`, `pyautogui`, `pynput`, `requests`
- Linux utilities: `xdotool`, `locate`

## Troubleshooting

- Microphone Issues: Ensure your microphone is configured correctly in Linux.
- API Errors: Verify your SerpAPI and OpenWeatherMap API keys.
- Dependencies Missing: Reinstall missing packages using `pip`.

## Contribution

Contributions are welcome! Feel free to fork the repository and submit pull requests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

### Acknowledgements

- [Google Text-to-Speech](https://gtts.readthedocs.io/)
- [SpeechRecognition Library](https://pypi.org/project/SpeechRecognition/)
- [SerpAPI](https://serpapi.com/)
- [OpenWeatherMap](https://openweathermap.org/)


