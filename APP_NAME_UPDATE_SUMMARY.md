# App Name Update Summary

## Overview
Successfully updated the application name from "DeepFaceLive" to "PlayaTewsIdentityMasker" throughout the codebase and GitHub repository.

## Changes Made

### 1. Core Application Files
- **`README.md`**: Created new README with updated app name and local development path
- **`main.py`**: Updated CLI parser to use "PlayaTewsIdentityMasker" as the command name
- **`apps/DeepFaceLive/DeepFaceLiveApp.py`**: Updated app_name parameter from 'DeepFaceLive' to 'PlayaTewsIdentityMasker'

### 2. Build Configuration Files

#### Desktop Build (`build_desktop.py`)
- Updated application name in PyInstaller spec
- Updated executable name to "PlayaTewsIdentityMasker"
- Updated Windows installer (NSIS) script:
  - Installer filename: `PlayaTewsIdentityMasker-Setup.exe`
  - Install directory: `$PROGRAMFILES\PlayaTewsIdentityMasker`
  - Start menu shortcuts: `PlayaTewsIdentityMasker`
  - Desktop shortcuts: `PlayaTewsIdentityMasker`
  - Registry entries: Updated uninstall information

#### Mobile Build (`build_mobile.py`)
- Updated mobile app title to "PlayaTewsIdentityMasker Mobile"
- Updated package name: `playatewsidentitymasker`
- Updated package domain: `org.playatews`
- Updated Buildozer specification

### 3. Dependencies and Configuration
- **`requirements_minimal.txt`**: Updated header comment
- **`requirements_packaging.txt`**: Updated header comment

### 4. Test and Optimization Files
- **`run_optimized_tests.py`**: Updated all references to use "PlayaTewsIdentityMasker"

### 5. GitHub Repository
- **Remote URL**: Updated from `ESSSoWhat/PlayaTews-Anonomiser` to `ESSSoWhat/PlayaTewsIdentityMasker`

## Local Development Path
- **Specified Path**: `C:\Users\son-l\Desktop\PlayaTewsIdentityMasker\PlayaTewsIdentityMasker-master`

## Usage Commands Updated
- **Run Application**: `python main.py run PlayaTewsIdentityMasker`
- **Build Desktop**: Creates `PlayaTewsIdentityMasker.spec` and `PlayaTewsIdentityMasker-Setup.exe`
- **Test Runner**: Updated to reference "PlayaTewsIdentityMasker" in all output

## Note
The internal application structure under `apps/DeepFaceLive/` was preserved to maintain compatibility with existing code dependencies and imports. Only the user-facing application name and external references were updated.

## Status
✅ **COMPLETE** - All app name references have been updated successfully.