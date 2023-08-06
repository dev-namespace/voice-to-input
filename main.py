#!/usr/bin/env python

import pyperclip, os, requests, time
from evdev import InputDevice, categorize, ecodes
from recorder import Recorder
from pynput.keyboard import Controller, Key
from pynput import keyboard
from docker_utils import is_whisper_running, run_whisper, stop_whisper

REC_KEYS = [keyboard.Key.pause, keyboard.Key.ctrl_l]
had_to_start_docker = False
recorder = None

# TODO: prefix and suffix (eg: i and enter+esc for vi input)

def setup():
    global recorder; recorder = Recorder()

    pressed_keys = []
    def on_press(key):
        nonlocal pressed_keys
        if key not in pressed_keys:
            pressed_keys.append(key)
            # print("pressed keys: %s" % pressed_keys)
        if all([k in pressed_keys for k in REC_KEYS]) and not recorder.is_recording:
            start_recording()

    def on_release(key):
        nonlocal pressed_keys
        if key in pressed_keys:
            pressed_keys.remove(key)

        if not any([k in pressed_keys for k in REC_KEYS]) and recorder.is_recording:
            stop_recording()

        if key == keyboard.Key.esc:
            # Stop listener
            return False

    try:
        with keyboard.Listener(
                on_press=on_press,
                on_release=on_release) as listener:
            listener.join()
    except Exception as e:
        print("[!] Audio could not be recorded")
        setup()

def start_recording():
    print('[*] Started recording')
    recorder.start()

def stop_recording():
    if os.path.exists('output.wav'):
        os.remove('output.wav')
    recorder.stop('output.wav')
    print('[*] Stopped recording')
    transcription = send_to_whisper('output.wav')
    trigger_text_input(transcription)

def trigger_text_input(text):
    pyperclip.copy(text)
    keyboard = Controller()
    with keyboard.pressed(Key.ctrl if not os.name == 'mac' else Key.cmd):
        keyboard.press('v')
        keyboard.release('v')
        time.sleep(0.3)

def send_to_whisper(filename):
    url = 'http://localhost:5000/transcribe'
    files = {'file': open(filename, 'rb')}
    response = requests.post(url, files=files)
    data = response.json()
    return data["text"]

def cleanup():
    print("Cleaning up...")
    if had_to_start_docker:
        stop_whisper()

if __name__ == '__main__':
    print("Checking if whisper-server is running...")
    print(is_whisper_running())
    if not is_whisper_running():
        run_whisper()
        had_to_start_docker = True

    try:
        setup()
    except KeyboardInterrupt:
        cleanup()
