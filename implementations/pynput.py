# pynput implementation
from pynput.keyboard import Key, Listener

def main_pynput(serial_port):
    """
    Main method for control using pynput
    :param serial_port:
    :return:
    """

    def on_press(key):
        print('{0} pressed'.format(key))

    def on_release(key):
        print('{0} release'.format(key))
        if key == Key.esc:
            # Stop listener
            return False

    # Collect events until released
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
