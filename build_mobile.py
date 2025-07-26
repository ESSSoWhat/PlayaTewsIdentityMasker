#!/usr/bin/env python3
"""
PlayaTewsIdentityMasker Mobile Application Builder
Packages the application into Android APK using Kivy and Buildozer
"""

import os
import sys
import subprocess
from pathlib import Path

def install_buildozer():
    """Install Buildozer for Android packaging"""
    try:
        import buildozer
        print("Buildozer already installed")
    except ImportError:
        print("Installing Buildozer...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "buildozer"])

def create_mobile_main():
    """Create mobile-optimized main file using Kivy"""
    mobile_main = '''#!/usr/bin/env python3
"""
PlayaTewsIdentityMasker Mobile Application
Kivy-based mobile interface for face swapping
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import numpy as np
from pathlib import Path

class PlayaTewsIdentityMaskerMobile(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Initialize camera
        self.camera = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Create UI elements
        self.create_ui()
        
    def create_ui(self):
        # Title
        title = Label(text='PlayaTewsIdentityMasker Mobile', size_hint_y=None, height=50)
        self.add_widget(title)
        
        # Camera preview
        self.camera_preview = Image(size_hint_y=0.6)
        self.add_widget(self.camera_preview)
        
        # Control buttons
        button_layout = BoxLayout(size_hint_y=None, height=100, spacing=10)
        
        self.start_btn = Button(text='Start Camera', on_press=self.start_camera)
        self.stop_btn = Button(text='Stop Camera', on_press=self.stop_camera)
        self.swap_btn = Button(text='Face Swap', on_press=self.toggle_face_swap)
        
        button_layout.add_widget(self.start_btn)
        button_layout.add_widget(self.stop_btn)
        button_layout.add_widget(self.swap_btn)
        
        self.add_widget(button_layout)
        
        # Status label
        self.status_label = Label(text='Ready', size_hint_y=None, height=30)
        self.add_widget(self.status_label)
        
    def start_camera(self, instance):
        """Start camera capture"""
        try:
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                Clock.schedule_interval(self.update_camera, 1.0/30.0)
                self.status_label.text = 'Camera started'
            else:
                self.status_label.text = 'Failed to start camera'
        except Exception as e:
            self.status_label.text = f'Camera error: {str(e)}'
    
    def stop_camera(self, instance):
        """Stop camera capture"""
        if self.camera:
            self.camera.release()
            self.camera = None
            Clock.unschedule(self.update_camera)
            self.status_label.text = 'Camera stopped'
    
    def toggle_face_swap(self, instance):
        """Toggle face swap mode"""
        self.face_swap_enabled = not getattr(self, 'face_swap_enabled', False)
        self.swap_btn.text = 'Face Swap: ON' if self.face_swap_enabled else 'Face Swap: OFF'
    
    def update_camera(self, dt):
        """Update camera frame"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Process frame
                if getattr(self, 'face_swap_enabled', False):
                    frame = self.process_face_swap(frame)
                
                # Convert to Kivy texture
                buf = cv2.flip(frame, 0)
                buf = buf.tostring()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.camera_preview.texture = texture
    
    def process_face_swap(self, frame):
        """Simple face detection and highlighting"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, 'Face Detected', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        
        return frame

class PlayaTewsIdentityMaskerMobileApp(App):
    def build(self):
        return PlayaTewsIdentityMaskerMobile()

if __name__ == '__main__':
    PlayaTewsIdentityMaskerMobileApp().run()
'''
    
    with open('mobile_main.py', 'w') as f:
        f.write(mobile_main)
    
    print("Created mobile_main.py")

def create_buildozer_spec():
    """Create Buildozer specification file"""
    buildozer_spec = '''[app]

# (str) Title of your application
title = PlayaTewsIdentityMasker Mobile

# (str) Package name
package.name = playatewsidentitymasker

# (str) Package domain (needed for android/ios packaging)
package.domain = org.playatews

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,opencv-python,numpy,plyer

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info

# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 1.9.1

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
#android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 29

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 20

# (str) Android NDK version to use
android.ndk = 19b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.renpy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
# use that parameter together with android.entrypoint to set custom Java class instead of PythonActivity
#android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml to write directly inside the <manifest> element of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_xml = ./src/android/extra_manifest.xml

# (str) Extra xml to write directly inside the <manifest><application> tag of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML arguments:
#android.extra_manifest_application_arguments = ./src/android/extra_manifest_application_arguments.xml

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (list) Android AAR archives to add
#android.add_aars =

# (list) Put these files or directories in the apk assets directory.
# Either form may be used, and assets need not be in 'source.include_exts'.
# 1) android.add_assets = source_asset_relative_path
# 2) android.add_assets = source_asset_path:target_asset_relative_path
#android.add_assets =

# (list) Put these files or directories in the apk res directory.
# The option may be used in three ways, the value may contain one or zero ':'
# Some examples:
# 1) A file to add to resources, legal resource names contain ['a-z','0-9','_']
# android.add_resources = my_icons/all-inclusive.png:drawable/all_inclusive.png
# 2) A directory, here  'legal_icons' must contain resources of one kind
# android.add_resources = legal_icons:drawable
# 3) A directory, here 'legal_resources' must contain one or more directories, 
# each of a resource kind
# android.add_resources = legal_resources
#android.add_resources =

# (list) Put these files or directories in the apk libs/armeabi directory
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_mips = libs/android-mips/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
# android.wakelock = False

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the
# project.properties automatically.)
#android.library_references =

# (list) Android shared libraries which will be added to AndroidManifest.xml using <uses-library> tag
#android.uses_library =

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for activity's pid
#android.logcat_pid_only = False

# (str) Android additional adb arguments
#android.adb_args = -H host.docker.internal

# (bool) Copy library instead of making a libs symlink
#android.copy_libs = 1

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, was `android.arch` as we weren't supporting builds for multiple archs at the same time.
android.archs = arm64-v8a, armeabi-v7a

# (int) overrides automatic versionCode computation (used in build.gradle)
# this is not the same as app version and should only be edited if you know what you're doing
# android.numeric_version = 1

#
# Python for android (p4a) specific
#

# (str) python-for-android URL to use for checkout
#p4a.url =

# (str) python-for-android fork to use in case if p4a.url is not specified, defaults to upstream (kivy)
#p4a.fork = kivy

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android specific commit to use, defaults to HEAD, must be within p4a.branch
#p4a.commit = HEAD

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#p4a.port =

#
# iOS specific
#

# (str) Path to your iOS developer identity
#ios.codesign.identity = iPhone Developer: <lastname> <firstname> (<hexstring>)

# (str) The display name of the application (can be changed during packaging)
#ios.display_name = My First Application

# (str) The name of your application's main folder (e.g. 'MyApp')
#ios.app_name = MyApp

# (str) Path to the Kivy icon
#ios.icon.filename = %(source.dir)s/data/icon.png

# (str) Path to the iOS static libs that will be used in the project
#ios.static_libs = %(source.dir)s/libs

# (list) iOS application plist files to merge
#ios.info_plist = %(source.dir)s/Info.plist

# (list) iOS additional plist files to merge
#ios.extra_plist = %(source.dir)s/extra.plist

# (list) iOS external frameworks to add
#ios.frameworks = AudioToolbox, ImageIO, SystemConfiguration

# (list) iOS weak frameworks to add
#ios.weak_frameworks = Contacts, Social, iAd

# (list) iOS libraries to add
#ios.libraries = iconv, sqlite3

# (list) iOS plugins to add
#ios.plugins = MyPlugin

# (list) Preinstall plugins that are not needed in this plugin
#ios.preinstall_plugins =

# (list) Plugin codesign_identity
#ios.plugin_codesign_identity = iPhone Developer: <lastname> <firstname> (<hexstring>)

# (list) Development team (iOS)
#ios.development_team = <hexstring>

# (str) The display name of the application (can be changed during packaging)
#ios.display_name = %(title)s

# (str) Path to your iOS developer identity
#ios.codesign.identity = iPhone Developer: <lastname> <firstname> (<hexstring>)

# (str) Path to your iOS developer identity
#ios.codesign.identity = iPhone Developer: <lastname> <firstname> (<hexstring>)

# (str) The name of your application's main folder (e.g. 'MyApp')
#ios.app_name = %(title)s

# (str) Path to the Kivy icon
#ios.icon.filename = %(source.dir)s/data/icon.png

# (str) Path to the iOS static libs that will be used in the project
#ios.static_libs = %(source.dir)s/libs

# (list) iOS application plist files to merge
#ios.info_plist = %(source.dir)s/Info.plist

# (list) iOS additional plist files to merge
#ios.extra_plist = %(source.dir)s/extra.plist

# (list) iOS external frameworks to add
#ios.frameworks = AudioToolbox, ImageIO, SystemConfiguration

# (list) iOS weak frameworks to add
#ios.weak_frameworks = Contacts, Social, iAd

# (list) iOS libraries to add
#ios.libraries = iconv, sqlite3

# (list) iOS plugins to add
#ios.plugins = MyPlugin

# (list) Preinstall plugins that are not needed in this plugin
#ios.preinstall_plugins =

# (list) Plugin codesign_identity
#ios.plugin_codesign_identity = iPhone Developer: <lastname> <firstname> (<hexstring>)

# (list) Development team (iOS)
#ios.development_team = <hexstring>

#
# Apple TV specific
#

# (str) Path to the icon
#tvos.icon.filename = %(source.dir)s/data/icon.png

# (str) Path to the top level app directory
#tvos.app_dir = %(source.dir)s

# (str) Application name
#tvos.app_name = %(title)s

# (str) Application bundle identifier
#tvos.bundle_identifier = %(package.domain)s.%(package.name)s

# (str) Path to the entitlements file
#tvos.entitlements = %(source.dir)s/entitlements.plist

# (str) Path to the Info.plist file
#tvos.info_plist = %(source.dir)s/Info.plist

# (str) Path to the main file
#tvos.main_file = %(source.dir)s/main.py

# (str) Path to the provisioning profile
#tvos.provisioning_profile = %(source.dir)s/profile.mobileprovision

# (str) Path to the certificate
#tvos.certificate = %(source.dir)s/cert.p12

# (str) Certificate password
#tvos.certificate_password = password

# (str) Team identifier
#tvos.team_identifier = team_identifier

# (str) Apple TV platform to build for
#tvos.platform = appletvos

# (int) Apple TV SDK version to build for
#tvos.deployment_target = 9.1

#
# tvOS specific
#

# (str) Path to the icon
#tvos.icon.filename = %(source.dir)s/data/icon.png

# (str) Path to the top level app directory
#tvos.app_dir = %(source.dir)s

# (str) Application name
#tvos.app_name = %(title)s

# (str) Application bundle identifier
#tvos.bundle_identifier = %(package.domain)s.%(package.name)s

# (str) Path to the entitlements file
#tvos.entitlements = %(source.dir)s/entitlements.plist

# (str) Path to the Info.plist file
#tvos.info_plist = %(source.dir)s/Info.plist

# (str) Path to the main file
#tvos.main_file = %(source.dir)s/main.py

# (str) Path to the provisioning profile
#tvos.provisioning_profile = %(source.dir)s/profile.mobileprovision

# (str) Path to the certificate
#tvos.certificate = %(source.dir)s/cert.p12

# (str) Certificate password
#tvos.certificate_password = password

# (str) Team identifier
#tvos.team_identifier = team_identifier

# (str) Apple TV platform to build for
#tvos.platform = appletvos

# (int) Apple TV SDK version to build for
#tvos.deployment_target = 9.1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#[app]
#source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
#    This can be translated into:
#
#[app:source.exclude_patterns]
#license
#data/audio/*.wav
#data/images/original/*
#

#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#[app@demo]
#title = My Application (demo)
#
#[app:source.exclude_patterns@demo]
#images/hd/*
#
#    Then, invoke the command line with the "demo" profile:
#
#buildozer --profile demo android debug
'''
    
    with open('buildozer.spec', 'w') as f:
        f.write(buildozer_spec)
    
    print("Created buildozer.spec")

def build_apk():
    """Build Android APK"""
    print("Building Android APK...")
    
    # Initialize buildozer
    subprocess.check_call(['buildozer', 'init'])
    
    # Build APK
    subprocess.check_call(['buildozer', 'android', 'debug'])
    
    print("APK build completed!")

def main():
    """Main mobile build process"""
    print("PlayaTewsIdentityMasker Mobile Application Builder")
    print("=" * 50)
    
    # Install buildozer
    install_buildozer()
    
    # Create mobile main file
    create_mobile_main()
    
    # Create buildozer spec
    create_buildozer_spec()
    
    # Build APK
    build_apk()
    
    print("\nMobile build completed!")
    print("APK location: bin/playatewsidentitymasker-0.1-debug.apk")

if __name__ == "__main__":
    main()