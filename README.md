# 1. clone the repo
git clone https://github.com/ivszabolcs/NetRadio.git \
cd NetRadio

# 2. creates a new virtual environment
python -m venv venv \
source venv/bin/activate    # macOS/Linux \
venv\Scripts\activate.bat   # Windows 

# 3. install dependencies
pip install -r requirements.txt


# 1. What does the program do?
The program displays an icon in the system tray.

By clicking the icon, a menu appears where you can:

<li>Start radio playback</li>

<li>Stop the radio</li>

<li>Exit the program</li>

The radio plays an internet stream in the background using the VLC Python bindings.

The program is minimalist — it has no separate window, only a tray icon and menu.

# 2. Adding a New Stream
The program functions as an internet radio player and plays streaming URLs.

To add a new "song" or station, simply provide a new internet radio stream URL.

<strong>What kind of link can you use?</strong>

The URL must be a live streaming link (e.g., MP3 or AAC stream).

Examples:

<li>http://stream.srg-ssr.ch/m/rsp/mp3_128</li>

<li>http://26343.live.streamtheworld.com/SAM10AAC139.mp3</li>

These are usually .mp3, .aac, or other live stream formats.

# 3. Settings
<li>You can change the window size.</li>

<li>You can switch between light and dark themes.</li>
