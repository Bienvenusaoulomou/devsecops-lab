import subprocess

user_input = input("Command: ")

subprocess.run(["echo", user_input], shell=False)
