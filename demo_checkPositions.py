import hkptrc_ibapi
import queue

if __name__ == '__main__':
    app = hkptrc_ibapi.hkptrc_ibApp('127.0.0.1', 7496, 1)

    app.get_positions()                                     # Prepare position data in app.position_data

    keep_loop = True
    while keep_loop:
        try:
            position_data = app.position_data.get(timeout=1)
            print(position_data)
        except queue.Empty:
            keep_loop = False

    app.disconnect()

