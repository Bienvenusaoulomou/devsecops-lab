import subprocess

command = input("Command: ")

subprocess.call(command, shell=False)
