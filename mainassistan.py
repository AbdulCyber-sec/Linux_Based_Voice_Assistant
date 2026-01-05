import os
import subprocess
import datetime
import logging
import time
import requests
from gtts import gTTS
import playsound
import psutil
import pyautogui
from pynput.keyboard import Key, Controller
from sklearn.pipeline import check_memory
import speech_recognition as sr
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cache common responses to improve speed
PREGENERATED_RESPONSES = {
    "greeting": "welcome back sir ",
    "goodbye": "Goodbye! Have a great day.",
    "did_not_understand": "Sorry, I didn't understand that. Please try again.",
    "hello": "Hello sir! I am igris.",
    "how_are_you": "I'm fine. How about you?",
    "thank_you": "You're welcome! I'm always here to help.",
}


# Function to pre-cache TTS audio
def cache_tts():
    """Pre-generate TTS responses for faster playback."""
    for key, text in PREGENERATED_RESPONSES.items():
        file_name = f"{key}.mp3"
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(file_name)

# Function to play pre-generated or dynamic TTS
def speak(text, speed_factor=1.5,cache_key=None):
    """Convert text to speech and play it, using pre-cached responses if available."""
    try:
        if cache_key and os.path.exists(f"{cache_key}.mp3"):
            playsound.playsound(f"{cache_key}.mp3")
        else:
            tts = gTTS(text=text, lang='en', slow=False)
            audio_file = "intro.mp3"
            tts.save(audio_file)
            playsound.playsound(audio_file)
            os.remove(audio_file)
    except Exception as e:
        logging.error(f"Error in text-to-speech: {str(e)}")

# Greeting based on the time of day
def greet():
    """Greet the user based on the current time."""
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        speak("Good morning sir!")
    elif 12 <= hour < 18:
        speak("Good afternoon sir!")
    else:
        speak("Good evening sir!")

# Function to capture voice input
def get_voice_input():
    """Capture voice input from the user."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
            command = recognizer.recognize_google(audio)
            logging.info(f"User said: {command}")
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak(PREGENERATED_RESPONSES["did_not_understand"], "did_not_understand")
            return ""
        except sr.RequestError:
            speak("Speech recognition service is unavailable.")
            return ""
        except Exception as e:
            logging.error(f"Error capturing voice input: {str(e)}")
            return ""

# Google search function using Opera
def search_google(query):

    """Perform a Google search using SerpAPI and fetch the top result."""
    try:
        # Replace 'YOUR_API_KEY' with your SerpAPI key
        api_key = "Your_Api_key"
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": 1
        }
        response = requests.get("https://serpapi.com/search", params=params)
        if response.status_code == 200:
            data = response.json()
            if "organic_results" in data and len(data["organic_results"]) > 0:
                # Fetch the first result's snippet
                snippet = data["organic_results"][0].get("snippet", "No snippet available")
                print(f"\n I found this:{snippet}")
                speak(f"I found this: {snippet}")
                
            else:
                speak("I couldn't find any relevant results. Please try again.")
        else:
            speak("Failed to fetch search results. Please try again later.")
    except Exception as e:
        logging.error(f"Error performing Google search: {str(e)}")
        speak("An error occurred while searching. Please try again.")


def get_weather(city= "Madurai"):
    """Fetch current weather information using an API."""
    try:
        api_key = "bd5e378503939ddaee76f12ad7a97608"  # Replace with your API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data.get("main"):
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            speak(f"The weather in {city} is {desc} with a temperature of {temp} degrees Celsius.")
        else:
            speak("Unable to fetch weather data. Please check the city name.")
    except Exception as e:
        logging.error(f"Error fetching weather: {str(e)}")
        speak("An error occurred while fetching the weather.")


# Function to execute commands
def execute_command(command):
    """Execute system commands or provide assistant responses."""
    try:
        if "open" in command:
            app_name = command.replace("open ", "").strip()
            result = subprocess.run(["which", app_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                subprocess.Popen([app_name])
                speak(f"Opening {app_name}")
            else:
                speak(f"Application {app_name} not found.")

        elif "type" in command:
            # Type a command into the terminal
            command_to_type = command.replace("type ", "").strip()
            os.system(f'xdotool type "{command_to_type}"')  # Requires xdotool
            os.system("xdotool key Return")
            speak(f"Typed the command: {command_to_type}")

        elif "close" in command:
            app_name = command.replace("close ", "").strip()
            result = subprocess.run(["pkill", app_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                    speak(f"Closing {app_name}")
            else:
                    speak(f"Failed to close {app_name}. Make sure it is running.")
        
        elif "Run file" in command:
            # Extract file name from command
            file_name = command.replace("run file ", "").strip()
            run_file(file_name)

        elif "check" in command:
            if "cpu" in command:
                check_cpu()
            elif "disk" in command:
                check_disk()
            elif "memory" in command:
                check_memory()
            elif "network" in command:
                check_network()
            elif "battery" in command:
                check_battery()
            else:
                speak("Sorry, I didn't understand what to check.")

        elif "shortcut" in command:
            execute_shortcut(command.replace("shortcut ", "").strip())

        elif "mouse" in command:
            control_mouse(command)

        elif "find" in command:
            if "file" in command:
                find_with_locate(command.replace("find file ", "").strip(), "file")
            elif "folder" in command:
                find_with_locate(command.replace("find folder ", "").strip(), "folder")
            else:
                speak("I didn't understand what to find.")

        elif "search" in command:
            query = command.replace("search ", "").strip()
            url = f"https://www.google.com/search?q={query}"
            subprocess.Popen(["xdg-open", url])
            speak(f"Searching for {query}")

        elif "weather" in command:
            city = command.replace("weather in ", "").strip() if "weather in" in command else "Madurai"
            get_weather(city)

        elif "hello" in command:
            speak(PREGENERATED_RESPONSES["hello"], "hello")
        
        elif "how are you" in command:
            speak(PREGENERATED_RESPONSES["how_are_you"], "how_are_you")
            
        elif "who are you" in command or "introduce yourself" in command:
            speak(PREGENERATED_RESPONSES["greeting"], "greeting")

        elif "thank you" in command or "thanks" in command:
            speak(PREGENERATED_RESPONSES["thank_you"], "thank_you")

        elif "show your brain" in command:
            show_you()

        elif "time" in command:
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            speak(f"The current time is {current_time}")

        elif "date" in command:
            today = datetime.date.today()
            speak(f"Today's date is {today}")

        elif "shutdown" in command:
            speak("Shutting down the system.")
            subprocess.call(["shutdown", "now"])

        elif "restart" in command:
            speak("Restarting the system.")
            subprocess.call(["reboot"])

        elif "joke" in command:
            speak("Why don’t skeletons fight each other? They don’t have the guts!")

        elif "fact" in command:
            speak("Did you know? Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old!")
        
        else:
            speak("I will search this on Google.")
            search_google(command)

    except Exception as e:
        logging.error(f"Error executing command: {str(e)}")
        speak(f"An error occurred while executing your command.")

def show_you():
    """Display an image or GIF at program startup."""
    # Create a Tkinter window
    root = tk.Tk()
    root.title("Welcome Screen")
    root.geometry("800x600")  # Adjust the window size

    # Load the image or GIF
    try:
        gif_path = "brain.gif"  # Replace with your image or GIF path
        img = Image.open(gif_path)
        gif_frames = []

        # If it's a GIF, split into frames
        try:
            while True:
                gif_frames.append(ImageTk.PhotoImage(img.copy()))
                img.seek(len(gif_frames))  # Move to the next frame
        except EOFError:
            pass

        def animate(index=0):
            """Animate the GIF frames."""
            frame = gif_frames[index]
            image_label.config(image=frame)
            index += 1
            if index == len(gif_frames):
                index = 0
            root.after(100, animate, index)  # Adjust the delay for your GIF

        # Display the first frame
        image_label = Label(root)
        image_label.pack(expand=True)
        animate()  # Start animation if it's a GIF

    except Exception as e:
        # If loading fails, show an error
        error_label = Label(root, text="Failed to load image or GIF!", font=("Arial", 16))
        error_label.pack(expand=True)

    # Start the Tkinter event loop
    root.mainloop()

keyboard_controller = Controller()

def execute_shortcut(shortcut):
    """Execute a keyboard shortcut."""
    shortcuts = {
        "copy": [Key.ctrl,key.shift, 'c'],
        "paste": [Key.ctrl,key.shift, 'v'],
        "cut": [Key.ctrl, 'x'],
        "undo": [Key.ctrl, 'z'],
        "redo": [Key.ctrl, 'y'],
        "open terminal": [Key.ctrl, 't'],
        "close window": [Key.alt, 'q'],
        "switch tab": [Key.ctrl, Key.tab],
        "close tab": [Key.ctrl, 'q'],
        "lock screen": [Key.ctrl, Key.alt, 'L'],
        "switch workspace": [Key.ctrl, Key.alt, Key.right],
    }
    
    if shortcut in shortcuts:
        keys = shortcuts[shortcut]
        for key in keys:
            keyboard_controller.press(key)
        for key in reversed(keys):
            keyboard_controller.release(key)
        speak(f"Executed {shortcut} shortcut.")
    else:
        speak("Shortcut not recognized.")


def control_mouse(command):
    """Control mouse movements and clicks."""
    if "move mouse" in command:
        direction = command.replace("move mouse ", "").strip()
        if direction == "up":
            pyautogui.move(0, -20)
        elif direction == "down":
            pyautogui.move(0, 20)
        elif direction == "left":
            pyautogui.move(-20, 0)
        elif direction == "right":
            pyautogui.move(20, 0)
        speak(f"Moved mouse {direction}.")

    elif "click" in command:
        if "left click" in command:
            pyautogui.click(button='left')
            speak("Left click.")
        elif "right click" in command:
            pyautogui.click(button='right')
            speak("Right click.")
        else:
            speak("Click command not recognized.")

    elif "scroll" in command:
        if "up" in command:
            pyautogui.scroll(10)
            speak("Scrolled up.")
        elif "down" in command:
            pyautogui.scroll(-10)
            speak("Scrolled down.")
        else:
            speak("Scroll direction not recognized.")
    else:
        speak("Mouse command not recognized.")

def find_with_locate(name, search_type):
    """Search for a file or folder using the 'locate' command."""
    try:
        result = subprocess.run(["locate", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        matches = result.stdout.decode().splitlines()
        
        if matches:
            speak(f"I found {len(matches)} {search_type}(s). Listing the first few results:")
            for match in matches[:3]:  # Limit to the first 5 results
                print(match)
                speak(match)
        else:
            speak(f"No {search_type} named {name} was found.")
    except FileNotFoundError:
        speak("The 'locate' command is not installed. Please install it and try again.")

def wait_for_commands():
    """Pause the assistant for a few seconds."""
    speak("Alright, I will wait for your commands.")
    print("Waiting for 10 seconds...")
    time.sleep(10)  # Pause for 10 seconds
    speak("I'm ready for your commands now.")
    
def run_file(file_name):
    """Run a file based on its extension."""
    if not os.path.exists(file_name):
        speak(f"File {file_name} does not exist.")
        return
    
    extension = os.path.splitext(file_name)
    try:
        if extension == ".sh":
            subprocess.run(["bash", file_name])
            speak(f"Running Bash file {file_name}")
        elif extension == ".py":
            subprocess.run(["python3", file_name])
            speak(f"Running Python file {file_name}")
        elif extension == ".java":
            # Compile and run Java file
            compile_result = subprocess.run(["javac", file_name], stderr=subprocess.PIPE)
            if compile_result.returncode == 0:
                java_class = os.path.splitext(file_name)[0]
                subprocess.run(["java", java_class])
                speak(f"Running Java file {file_name}")
            else:
                speak(f"Compilation failed for Java file {file_name}")
        else:
            speak(f"Unsupported file type: {extension}")
    except Exception as e:
        speak(f"An error occurred while running the file: {e}")

def check_cpu():
    """Check and speak out the CPU usage level."""
    cpu_usage = psutil.cpu_percent(interval=1)
    speak(f"Your CPU usage is currently at {cpu_usage} percent.")

def check_disk():
    """Check disk usage."""
    disk_usage = psutil.disk_usage('/')
    speak(f"Your disk is {disk_usage.percent} percent full. You have {disk_usage.free // (1024 ** 3)} gigabytes free.")

def check_memory():
    """Check and speak out the memory usage level."""
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    speak(f"Your memory usage is currently at {memory_usage} percent.")

def check_network():
    """Check network speed and usage."""
    speak("Measuring network speed and usage. Please wait.")
    
    # Get initial data
    net1 = psutil.net_io_counters()
    
    net2 = psutil.net_io_counters()
    
    # Calculate speeds
    sent_speed = (net2.bytes_sent - net1.bytes_sent) / 1024  # KB/s
    recv_speed = (net2.bytes_recv - net1.bytes_recv) / 1024  # KB/s
    
    # Total data usage
    total_sent = net2.bytes_sent / (1024 ** 2)  # MB
    total_recv = net2.bytes_recv / (1024 ** 2)  # MB
    
    speak(f"Your network upload speed is {sent_speed:.2f} kilobytes per second, and your download speed is {recv_speed:.2f} kilobytes per second.")
    speak(f"So far, you've sent {total_sent:.2f} megabytes and received {total_recv:.2f} megabytes of data.")

def check_battery():
    """Check battery level."""
    battery = psutil.sensors_battery()
    if battery:
        speak(f"Your battery is at {battery.percent} percent.")
        if battery.power_plugged:
            speak("Your laptop is plugged in.")
        else:
            speak("Your laptop is running on battery.")
    else:
        speak("Battery status is not available on this device.")
    
def check_system_status():
    """Display system status information."""
    print("Gathering system information...")
    system_status = [
        check_cpu(),
        check_memory(),
        check_battery(),
        check_network(),
        get_weather("Madurai"),  # Change city as needed
    ]
   
def adjust_volume(direction):
    """Adjust system volume up or down."""
    try:
        if direction == "up":
            os.system("pactl set-sink-volume @DEFAULT_SINK@ +10%")
            speak("Volume increased.")
        elif direction == "down":
            os.system("pactl set-sink-volume @DEFAULT_SINK@ -10%")
            speak("Volume decreased.")
        elif direction == "mute":
            os.system("pactl set-sink-mute @DEFAULT_SINK@ toggle")
            speak("Volume Muted")
        else:
            speak("Invalid volume command.")
    except Exception as e:
        speak(f"Failed to adjust volume. {str(e)}")

def adjust_brightness(direction):
    """Adjust screen brightness using brightnessctl."""
    try:
        if direction == "up":
            os.system("sudo brightnessctl set +10%")
            speak("Brightness increased.")
        elif direction == "down":
            os.system("sudo brightnessctl set 10%-")
            speak("Brightness decreased.")
        else:
            speak("Invalid brightness command.")
    except Exception as e:
        speak(f"Failed to adjust brightness. {str(e)}")

def main():
    """Main logic for the assistant."""
    greet()
    speak(PREGENERATED_RESPONSES["greeting"], "greeting")
    while True:
        command = get_voice_input()
        if "volume up" in command:
            adjust_volume("up")
        elif "volume down" in command:
            adjust_volume("down")
        elif "volume mute" in command:
            adjust_volume("mute")
        elif "brightness up" in command:
            adjust_brightness("up")
        elif "brightness down" in command:
            adjust_brightness("down")
        elif "check my laptop status" in command:
            speak("wait for few seconds ,i will prepare for your system status now.")
            check_system_status()
            speak("System status check is complete sir")
        elif "exit" in command:
            speak("Goodbye sir!")
            return False
        elif "wait for my commands" in command:
            wait_for_commands()
        elif command:
            execute_command(command)

if __name__ == "__main__":
    try:
        cache_tts()  # Pre-cache responses
        main()
    except KeyboardInterrupt:
        logging.info("Voice assistant terminated by user.")
        print("\nGoodbye!")
