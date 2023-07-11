import os
import subprocess
import time

PROCESS = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':

        PROCESS.append(subprocess.Popen([
            'gnome-terminal',
            "--disable-factory",
            "--",
            "python",
            "./server.py",
        ])
        )

        time.sleep(0.1)

        PROCESS.append(subprocess.Popen([
            'gnome-terminal',
            "--disable-factory",
            "--",
            "python",
            "./client.py",
            "-n",
            "test1",

        ])
        )
        time.sleep(0.1)

        PROCESS.append(subprocess.Popen([
            'gnome-terminal',
            "--disable-factory",
            "--",
            "python",
            "./client.py",
            "-n",
            "test2",

        ])
        )

        time.sleep(0.1)

        PROCESS.append(subprocess.Popen([
            'gnome-terminal',
            "--disable-factory",
            "--",
            "python",
            "./client.py",
            "-n",
            "test3",
        ])
        )

        time.sleep(0.1)
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
