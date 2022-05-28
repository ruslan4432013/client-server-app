import os
import subprocess
import time

PROCESS = []

while True:
    ACTION = input('Select action: q - exit, s - start server and clients, x - close all windows: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        catalog = os.getcwd()
        p = f'python3 "{catalog}/server.py"'
        PROCESS.append(subprocess.Popen([
            'konsole',
            '-e',
            p])
        )
        print(p)
        time.sleep(3)
        for i in range(2):
            p = f'python3 "{catalog}/client.py" -m send -u userS{i}'
            PROCESS.append(subprocess.Popen([
                'konsole',
                '-e',
                p])
            )
            print(p)
            time.sleep(0.1)
        for i in range(5):
            p = f'python3 "{catalog}/client.py" -m listen -u userL{i}'
            PROCESS.append(subprocess.Popen([
                'konsole',
                '-e',
                p])
            )
            print(p)
            time.sleep(0.1)
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()