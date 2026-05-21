# Samsung Galaxy Tab S9 FE — Dedicated Claude Tablet Setup Guide

This guide walks you through converting your out-of-warranty Samsung Galaxy Tab S9 FE
into a dedicated Jarvis/Claude device. Two paths are covered:

- **Path A (Recommended — No Rooting):** Run Jarvis inside Termux with a Chrome kiosk.
  Zero risk of bricking, works on stock One UI, preserves Samsung Pay.
- **Path B (Full Custom OS):** Unlock bootloader and flash a custom ROM for a truly
  dedicated OS. More involved, currently limited ROM support for this device.

---

## Your Device

| Field | Value |
|---|---|
| Model | Samsung Galaxy Tab S9 FE |
| Codename | gta9p |
| Chip | Samsung Exynos 1380 |
| Models | SM-X510 (Wi-Fi), SM-X516B (LTE) |
| Released | October 2023 |

---

## Path A — Termux Kiosk (Recommended)

### What you get
- Jarvis boots automatically when the tablet turns on
- Chrome opens fullscreen to the Jarvis interface
- Touch + voice input work out of the box
- No warranty impact, no risk of bricking
- Can still exit Jarvis if you need to use other apps

---

### Step 1 — Install Termux

> ⚠️ Do **not** install Termux from the Google Play Store — that version is outdated.
> Use F-Droid instead.

1. On the tablet, open Chrome and go to: `https://f-droid.org`
2. Download and install the F-Droid app
3. Open F-Droid → search for **Termux** → install it
4. Also install **Termux:Boot** from F-Droid (enables auto-start on reboot)

---

### Step 2 — Install Python and Jarvis

Open Termux and run these commands one by one:

```bash
# Update packages
pkg update && pkg upgrade -y

# Install Python and git
pkg install python git -y

# Clone the Jarvis repository (must specify the branch)
git clone -b claude/tablet-os-claude-communication-fszBz https://github.com/Call-OnDad/Jarvis Jarvis
cd Jarvis

# Run setup
chmod +x setup.sh
./setup.sh
```

---

### Step 3 — Add your API key

```bash
nano .env
```

Replace `your_key_here` with your actual key from https://console.anthropic.com

Save with `Ctrl+X → Y → Enter`

---

### Step 4 — Test it

```bash
./start.sh
```

Open Chrome on the tablet and navigate to: `http://localhost:5000`

You should see the Jarvis interface. Try typing or tapping the microphone.

---

### Step 5 — Make it a home-screen app (PWA)

1. With Jarvis running and Chrome open at `http://localhost:5000`
2. Tap the Chrome **⋮ menu** (three dots, top right)
3. Tap **"Add to Home screen"**
4. Name it "Jarvis" → tap **Add**

Now you have a dedicated app icon that opens Jarvis fullscreen.

---

### Step 6 — Auto-start on reboot

The `setup.sh` script already created a Termux:Boot script. You just need to:

1. Open **Termux:Boot** once (just launch it — it registers itself as a boot service)
2. Go to Android **Settings → Apps → Termux → Battery → Allow background activity**
3. Also do the same for **Termux:Boot**

On next reboot, Jarvis will start automatically in the background.
Open the Jarvis PWA icon and it will connect.

---

### Step 7 — Kiosk / Dedicated mode (optional)

To lock the tablet to only show Jarvis:

**Option A — Android Screen Pinning (built-in, no extra apps)**
1. Open the Jarvis PWA
2. Tap the square/recent-apps button
3. Tap the Jarvis app icon in the recent apps card
4. Tap **"Pin"** (or "Pin app")
5. The tablet is now locked to Jarvis — pressing Back/Home shows a PIN prompt

**Option B — Kiosk launcher app (more polished)**
1. Install **"Kiosk Browser"** or **"Fully Kiosk Browser"** from Play Store
2. Configure it to open `http://localhost:5000` on startup
3. Set it as your default launcher
4. It will auto-start and lock to Jarvis on every boot

---

## Path B — Custom ROM (Advanced)

> ⚠️ **This permanently trips Knox** (e0000001 in download mode). Samsung Pay,
> Samsung Health secure features, and some banking apps will stop working.
> The device will still function fully for Jarvis use. Only proceed if you accept this.

---

### Custom ROM Availability (as of 2025)

The Tab S9 FE (gta9p) is a relatively new device. Official support status:

| ROM | Status |
|---|---|
| LineageOS official | Not yet available for gta9p |
| LineageOS unofficial | Check XDA: https://xda-developers.com (search "SM-X510 LineageOS") |
| crDroid / PixelExperience | Check XDA for unofficial ports |
| Stock One UI (recommended) | Always available from Samsung |

**If no ROM is available** for your exact model, stick with Path A.

---

### Step 1 — Enable Developer Options

1. **Settings → About tablet → Software information**
2. Tap **Build number** 7 times rapidly
3. Enter your PIN when prompted
4. You'll see "Developer mode has been enabled"

---

### Step 2 — Enable OEM Unlock

1. **Settings → Developer options**
2. Toggle **OEM unlocking** ON
3. Confirm when prompted
4. This requires the device to have been activated with a Samsung account

---

### Step 3 — Set up ADB on your PC

On your computer:

```bash
# Install Android platform tools
# Windows: download from https://developer.android.com/tools/releases/platform-tools
# macOS:   brew install android-platform-tools
# Linux:   sudo apt install adb

# Verify ADB is working
adb version
```

On the tablet:
1. **Settings → Developer options → USB debugging** → ON
2. Connect tablet to PC via USB
3. On PC: `adb devices` — accept the prompt on the tablet, verify it shows

---

### Step 4 — Unlock the bootloader

```bash
# On your PC:
adb reboot bootloader

# Tablet will enter Download Mode. Then:
fastboot flashing unlock

# Confirm on tablet screen with Volume Up
# Device will factory reset automatically
```

---

### Step 5 — Flash a custom recovery (TWRP / OrangeFox)

Check XDA Developers for your exact model (SM-X510 or SM-X516B) for a compatible recovery image.

```bash
# Once you have a recovery image:
fastboot flash recovery recovery.img
fastboot reboot recovery
```

---

### Step 6 — Flash the ROM

From recovery:
1. Wipe → Format Data
2. Wipe → Dalvik/ART Cache
3. Install → select your ROM zip
4. Reboot System

---

### Step 7 — Install Jarvis on the custom ROM

Follow **Path A Steps 1–7** above — Termux works the same way on any Android.

---

## ADB Kiosk Mode (Advanced — requires PC)

This locks the tablet into the Jarvis PWA with no way to exit without ADB.
Run from your PC with the tablet connected:

```bash
# Put Chrome into kiosk mode for the Jarvis URL
adb shell am start -n com.android.chrome/com.google.android.apps.chrome.Main \
  --data-uri "http://localhost:5000" \
  --es "android.intent.extra.REFERRER_NAME" "android-app://com.android.chrome"

# Enable immersive mode (hides status/nav bars)
adb shell settings put global policy_control immersive.full=*

# Lock screen timeout to never (keeps display on)
adb shell settings put system screen_off_timeout 2147483647

# Keep screen on while charging
adb shell svc power stayon true
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Jarvis won't start | Check `.env` has a valid `ANTHROPIC_API_KEY` |
| "Address already in use" | `pkill -f app.py` then restart |
| Voice input not working | Must use Chrome browser; Firefox does not support Web Speech API |
| Voice output sounds robotic | In the app, the quality depends on voices installed — Chrome on Android uses Google TTS |
| Termux auto-start not working | Open Termux:Boot once; disable battery optimization for Termux and Termux:Boot |
| Screen dims/sleeps | Developer options → Stay awake (when charging) |

---

## Quick Reference

| Task | Command |
|---|---|
| Start Jarvis | `cd ~/Jarvis && ./start.sh` |
| View logs | `tail -f ~/Jarvis/jarvis.log` |
| Stop Jarvis | `pkill -f app.py` |
| Update Jarvis | `cd ~/Jarvis && git pull && pip3 install -r requirements.txt` |
| Open in browser | `http://localhost:5000` |
