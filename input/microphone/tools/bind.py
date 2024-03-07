from __future__ import annotations

import time

from pynput import keyboard


def on_release(key: keyboard.Key | keyboard.KeyCode):
    match type(key):
        case keyboard.Key:
            number = key.value.vk
        case keyboard.KeyCode:
            number = key.vk
        case _:
            number = None

    print(f': The key pressed has a vk value of {number}.')


if __name__ == "__main__":
    listener = keyboard.Listener(on_release=on_release)
    listener.start()

    while True:
        time.sleep(1)
