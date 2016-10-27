import platform
import subprocess


def write_to_clipboard(output):
    system = platform.system()
    if system == "Darwin":
        cmd = ['pbcopy']
    else:
        cmd = ["xclip", "-selection", "clipboard"]
        subprocess.Popen(cmd, stdin=subprocess.PIPE).communicate(output.encode('utf-8'))
        cmd = ["xclip", "-selection", "primary"]
    subprocess.Popen(cmd, stdin=subprocess.PIPE).communicate(output.encode('utf-8'))


def platform_fn(**kwargs):
    """ Helper function for os dependent implementations """
    operating_system = platform.system()
    return kwargs[operating_system]


def is_on_apple():
    return platform.system() == "Darwin"
