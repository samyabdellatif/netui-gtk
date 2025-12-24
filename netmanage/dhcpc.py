import subprocess


def lease(ifacename):
    shellcommand = r"sudo dhcpcd "+ifacename
    process = subprocess.run(shellcommand, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = list(filter(None,map(str.strip, process.stdout.split("\n"))))
    return output
