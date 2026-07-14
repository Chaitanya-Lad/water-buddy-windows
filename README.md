# Water Buddy for Windows

An animated hydration reminder inspired by the attached Water Buddy guide, rebuilt for Windows with PyQt6.

## Quick start

1. Install [Python for Windows](https://www.python.org/downloads/windows/) and select **Add Python to PATH** during setup.
2. Double-click `run_water_buddy.bat`.
3. Your buddy appears after one second. Use the water-drop icon in the Windows notification area to open Settings or preview it again.

## Add your own buddy

Place two transparent PNGs in this folder:

- `buddy_idle.png` — standing pose
- `buddy_drink.png` — drinking pose

The app automatically uses them. You can also select PNGs elsewhere from **Settings** in the tray menu.

## Included behavior

- Slides in from the right and stays above other windows
- Changes from standing to drinking pose, then asks you to hydrate
- **Yes, drank it** schedules the regular reminder interval (30 minutes by default)
- **Snooze** and no response schedule a 5-minute follow-up
- Settings save automatically between launches

Until custom PNGs are added, Water Buddy shows a simple built-in placeholder character so you can test everything immediately.
