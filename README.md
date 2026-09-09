# Water Buddy for Windows

Water Buddy is a lightweight Windows desktop hydration reminder built with PyQt6. It lives in the Windows notification area and periodically slides an animated buddy onto the screen to remind you to drink water. The reminder uses separate standing and drinking PNGs, customizable message text, and configurable reminder and snooze intervals.

## Screenshots

### Reminder window

![Water Buddy reminder window](Screenshot%202026-09-09%20204852.png)

### Settings

![Water Buddy settings](Screenshot%202026-09-09%20204641.png)

### Windows notification area

![Water Buddy in the Windows notification area](Screenshot%202026-09-09%20204721.png)

## Quick start

1. Install [Python for Windows](https://www.python.org/downloads/windows/) and select **Add Python to PATH** during setup.
2. Double-click `run_water_buddy.bat`.
3. The launcher installs the required PyQt6 dependency and starts Water Buddy.
4. Your buddy appears after one second. Use the water-drop icon in the Windows notification area to open Settings or preview it again.

The app requires Windows notification-area support. It runs in the background until you choose **Quit Water Buddy** from the tray menu.

## Add your own buddy

Place two transparent PNGs in the same folder as `water_buddy.py`:

- `buddy_idle.png` - standing pose
- `buddy_drink.png` - drinking pose

The app automatically loads these files at startup. Their alpha channel is preserved, so transparent PNG artwork blends into the transparent reminder window without a rectangular background. Images are scaled smoothly to fit the buddy area while preserving their aspect ratio.

You can also select other transparent PNG files from **Settings** in the tray menu. If an image is missing or cannot be loaded, the app uses a built-in placeholder character so the reminder still works.

## Features

- Slides in from the right and stays above other windows
- Animates from the standing image to the drinking image before showing the reminder
- Offers **Yes, drank it** and **Snooze** actions
- Reschedules the regular reminder after confirmation, or a shorter follow-up after snoozing
- Automatically snoozes if the reminder is left unanswered for 20 seconds
- Lets you customize reminder timing, snooze timing, and both lines of bubble text
- Saves settings between launches using Windows `QSettings`
- Provides a tray menu for showing the reminder, opening Settings, and quitting the app

Default values are a 30-minute reminder interval, a 5-minute snooze interval, and the message **Time to drink water!**

## Project files

- `water_buddy.py` - PyQt6 application and reminder logic
- `buddy_idle.png` - default transparent standing buddy image
- `buddy_drink.png` - default transparent drinking buddy image
- `requirements.txt` - Python dependencies
- `run_water_buddy.bat` - Windows launcher

