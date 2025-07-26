# PlayaTewsIdentityMasker UI Launcher Guide

## Quick Start - Recommended

**For most users, use the OBS-style interface (default):**

```bash
python launch_obs_ui.py
```

This launches the modern, streaming-focused OBS-style interface that's optimized for live streaming and content creation.

## Available UI Options

### 1. OBS-Style UI (Default & Recommended)
- **File:** `launch_obs_ui.py`
- **Command:** `python launch_obs_ui.py`
- **Features:**
  - Modern streaming-focused interface
  - OBS-style controls and layout
  - Optimized for live streaming
  - Clean, intuitive design
  - Built-in streaming output controls

### 2. Traditional UI (Legacy)
- **File:** `launch_traditional_ui.py`
- **Command:** `python launch_traditional_ui.py`
- **Features:**
  - Traditional panel-based layout
  - All controls visible at once
  - Advanced user interface
  - Legacy compatibility

### 3. Main Launcher (Advanced)
- **File:** `main.py`
- **Commands:**
  ```bash
  # OBS-style (default)
  python main.py run PlayaTewsIdentityMasker
  
  # Traditional
  python main.py run PlayaTewsIdentityMasker --traditional
  
  # Legacy traditional
  python main.py run PlayaTewsIdentityMaskerTraditional
  ```

## Why Does the UI Keep Reverting?

The UI might revert to traditional if:

1. **Wrong launcher used:** You're using `launch_traditional_ui.py` instead of `launch_obs_ui.py`
2. **Command line flags:** You're using `--traditional` flag
3. **Legacy command:** You're using `PlayaTewsIdentityMaskerTraditional` instead of `PlayaTewsIdentityMasker`
4. **Settings persistence:** The app remembers your last choice

## Making OBS-Style UI the Permanent Default

To ensure you always get the OBS-style UI:

1. **Use the dedicated launcher:**
   ```bash
   python launch_obs_ui.py
   ```

2. **Or use the main launcher without flags:**
   ```bash
   python main.py run PlayaTewsIdentityMasker
   ```

3. **Avoid these commands:**
   ```bash
   # These will give you traditional UI
   python launch_traditional_ui.py
   python main.py run PlayaTewsIdentityMasker --traditional
   python main.py run PlayaTewsIdentityMaskerTraditional
   ```

## Troubleshooting

### UI Still Reverting?
1. Check which launcher you're using
2. Clear any saved settings in your workspace
3. Make sure you're not using any `--traditional` flags

### Performance Issues?
- The OBS-style UI is optimized for performance
- If you experience issues, try the traditional UI as a fallback

### Need Help?
- OBS-style UI is recommended for most users
- Traditional UI is available for advanced users who prefer the legacy layout