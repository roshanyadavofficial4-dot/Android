[app]

# (str) Title of your application
title = A.R.Y.A. OS

# (str) Package name
package.name = arya_os

# (str) Package domain (needed for android packaging)
package.domain = org.arya

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,db,json,wav,mp3

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,kivymd,pillow,requests,beautifulsoup4,google-genai,plyer,pyjnius,websockets,pyaudio,SpeechRecognition,gTTS,pypdf2,psutil

# (str) Custom source folders for requirements
# Custom architectures should be handled by p4a or buildozer automatically
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
# Valid values are: landscape, portrait, portrait-upside-down, landscape-left, landscape-right
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA,RECORD_AUDIO,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,SYSTEM_ALERT_WINDOW,BIND_ACCESSIBILITY_SERVICE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 33

# (str) Android NDK version to use
#android.ndk = 25b

# (list) Android architectures to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >= 23)
android.allow_backup = True

# (str) The Android logcat filters to use
#android.logcat_filters = *:S python:D

# (str) The Android white list of page to copy to the project
#android.whitelist =

# (str) Bootstrap to use for android
#android.bootstrap = sdl2

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add kivy-android.jar or python-android.jar, they are
# already added.
#android.add_jars = foo.jar,bar.jar,path/to/baz.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (list) Android AAR archives to add
#android.add_aars =

# (list) Gradle dependencies
#android.gradle_dependencies =

# (list) add java compile options
# this can for example be used to enable the desugar jdk libs
#android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

# (list) Packaging options to pass to Gradle
#android.packaging_options = "exclude 'META-INF/LICENSE.txt'", "exclude 'META-INF/NOTICE.txt'"

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (str) OUYA Console category. Should be one of GAME or APP
#android.ouya.category = APP

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
#android.manifest.intent_filters =

# (str) launch_mode extension of the main activity
#android.manifest.launch_mode = standard

# (list) Android additional libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android-v8/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_mips = libs/android-mips/*.so

# (bool) Copy library instead of making a lib dir. This is typically needed with
# older NDKs or if you want to use the same library for all architectures.
#android.copy_libs = 1

# (str) The name of the main entry point, default is main.py
#android.entrypoint = main.py

# (list) Android app theme, default is ok for Kivy
#android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Screen orientation, default is portrait
#android.orientation = portrait

# (list) Android additional activities
#android.add_activities = com.example.ExampleActivity

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Android use build-tools from the SDK
#android.use_build_tools = True

# (str) Android NDK directory (if empty, it will be downloaded)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be downloaded)
#android.sdk_path =

# (str) ANT directory (if empty, it will be downloaded)
#android.ant_path =

# (str) python-for-android branch to use, default is master
#p4a.branch = master

# (str) python-for-android git repository to use, default is the one from kivy
#p4a.source_dir =

# (list) python-for-android whitelist
#p4a.whitelist =

# (bool) If True, then skip the compilation of the application
#p4a.skip_build = False

# (list) List of extra p4a arguments
#p4a.extra_args =

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use, default is master
#p4a.branch = master

# (str) python-for-android git repository to use, default is the one from kivy
#p4a.source_dir =

# (str) The directory where the p4a recipes are located
#p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Port number to use for the p4a web server
#p4a.port = 8000


#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios

# (str) Name of the certificate to use for signing the debug version
#ios.codesign.debug = "iPhone Developer: <firstname> <lastname> (<identifier>)"

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = "iPhone Distribution: <firstname> <lastname> (<identifier>)"


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifacts directory, if empty, it will be the directory
# where buildozer.spec is located.
#build_dir = ./.buildozer

# (str) Path to bin directory, if empty, it will be the directory where
# buildozer.spec is located.
#bin_dir = ./bin
