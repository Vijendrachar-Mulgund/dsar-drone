import socket
import pickle
import time

import cv2
import sys

from config import (SERVER_ADDRESS, IMAGE_ENCODE_DECODE_FORMAT, SOCKET_TRANSMISSION_SIZE,
                    VIDEO_IMAGE_ENCODE_DECODE_FORMAT, VIDEO_SOURCE)


def video_capture(client_conn, vid_source=None):
    cap = cv2.VideoCapture(vid_source if vid_source is not None else VIDEO_SOURCE)

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        ret, buffer = cv2.imencode(VIDEO_IMAGE_ENCODE_DECODE_FORMAT, frame)
        if not ret:
            continue

        data = buffer.tobytes()
        length = len(data)
        client_conn.sendall(str(length).ljust(SOCKET_TRANSMISSION_SIZE).encode(IMAGE_ENCODE_DECODE_FORMAT))
        client_conn.sendall(data)

        if frame is not None:
            cv2.imshow('Client Video', frame)

        data = client_conn.recv(SOCKET_TRANSMISSION_SIZE).decode(IMAGE_ENCODE_DECODE_FORMAT)

        if data == "NEXT_FRAME":
            print("Requested next frame")
            pass
        elif data == "LOCATION_COORDINATES":
            print("Requested location coordinates")
            location_coordinates = get_location()
            location_data = pickle.dumps(location_coordinates)
            client_conn.sendall(location_data)
            print("Requested location coordinates sent")
            time.sleep(15)
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    client_conn.close()
    cv2.destroyAllWindows()

def get_location():
    return [-3.937610, 52.644903]


def init_client():
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(SERVER_ADDRESS)
    return client_socket


def get_params(cmd_params):
    params_dict = {}
    for i in range(1, len(cmd_params), 2):
        params_dict[cmd_params[i]] = cmd_params[i + 1]
    return params_dict


if __name__ == "__main__":
    try:
        params = get_params(sys.argv)
        socket_connection = init_client()
        if params["-source"]:
            video_capture(socket_connection, params["-source"])
        else:
            video_capture(socket_connection)
    except KeyboardInterrupt:
        print("Client shutting down 🛑")
    except Exception as e:
        print("An error occurred: {}".format(e))
