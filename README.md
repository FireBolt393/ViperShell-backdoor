
![vipershell1](https://github.com/user-attachments/assets/04248384-6e9b-40ee-95e7-768cf8ae0ee9)

# ViperShell Backdoor

**ViperShell** is a Python-based backdoor designed for remote control over a victim's machine, featuring a terminal interface styled to mimic the look and feel of Kali Linux. This tool offers a variety of features to manage and monitor the system from a distance, ranging from capturing webcam images to running Python scripts on the victim's machine.

## Features

### General Commands:
- `-h`, `--HELP`: Displays the help menu.
- `-ip`, `--IP`: Returns the IP address of the victim.
- `-l`, `--LOCATION`: Returns the location of the victim.
- `-m`, `--MACHINE`: Shows whether the backdoor is running on a physical or virtual machine.

### File Management:
- `-feu <path>`, `--FILE-EU <path>`: Upload executable files to the startup folder of the victim’s machine.
- `-fd <path>`, `--FILE-D <path>`: Download files from the victim’s machine.

### Key Interaction:
- `-k <key>`, `--KEY <key>`: Triggers the specified key on the victim’s machine.
- `-k -h`, `--KEY -h`: Opens the help menu for key triggers.

### Popups:
- `-pop`, `--POPUP`: Displays a custom popup message on the victim's machine.

### Code Execution:
- `-scr`, `--SCRIPT`: Executes custom Python or batch code on the victim’s machine.
- Code can be loaded from `.py` and `bat` files only.
- All `print` outputs are sent back to the user and are not shown on the victim's machine.

### Camera and Screenshot:
- `-cam`, `-CAMERAS`: Dumps all cameras connected to the victim's machine.
- `-img <cam no>`, `--IMAGE <cam no>`: Captures an image using the specified camera number (default is `0`).
  - Some webcams have activation indicators, so use this command with caution.
  - If no image is captured, the webcam may be disabled via a keyboard hotkey.
  - Use `systeminfo` on the command prompt to get the device model and find the camera toggle hotkey.
  - Use the `-k` command to trigger the hotkey.

- `-ss`, `--SCREENSHOT`: Captures a screenshot.
- `-sstr`, `--SCRSTREAM`: Starts streaming the victim's screen.

### Audio Recording:
- `-recr <secs>`, `--RECORD <secs>`: Records audio for the specified number of seconds (default: `5`).

### To access command prompt:
-`-cmd`, `--COMMAND`: Gives access to the victim's command prompt.
-MULTIPLE line batch code cannot be executed on the command prompt. Use `-scr` or `-SCRIPT` command to load and execute batch scripts.

### Session Control:
- `-sus`, `--SUSPEND`: Temporarily suspends the connection from the host.
- `-rec`, `--RECONNECT`: Reconnects back to the host after suspension.
- `-e`, `--EXIT`: Terminates the backdoor (requires the victim to manually restart it).

## Usage
To execute any command, run:
-`-<command> <argument>` OR `--<COMMAND> <argument>`

**Example:**
To record the audio:
`-recr 10`. Captures the audio for 10 seconds.

## External Libraries used:
Check requirements.txt

run command: `pip install -r requirements.txt`, to install the dependencies.

## Disclaimer:
This tool is meant for educational purposes only. The developer is not responsible for any misuse of this software. Always ensure you have proper authorization before accessing any system.

## Contributions:
We welcome contributions to ViperShell! If you'd like to contribute.

## License:
This project is licensed under the MIT License - see the LICENSE file for details.




