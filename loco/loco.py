import hashlib
import re
import os
import webbrowser
import click

from .utils import write_to_clipboard
from .utils import platform_fn
from .utils import is_on_apple

USER = "loco0"


@click.group()
def main():
    return "OK"


@main.command()
@click.argument("pubfile", default=None, required=False)
@click.option("--cat", default=False, is_flag=True)
def pubkey(pubfile, cat):
    """ Copies your pubkey to clipboard"""
    if pubfile is None:
        pubfile = "id_rsa.pub"

    with open(os.path.expanduser("~/.ssh/" + pubfile)) as f:
        public_key = f.read().strip()
    if not cat:
        print("Copied pubkey to clipboard")
        write_to_clipboard(public_key)
    else:
        print(public_key)


def get_user_dir(user):
    home = "/Users" if is_on_apple() else "/home"
    return os.path.join(home, user)


def get_random_uid():
    import random
    return random.randint(1000, 3000)


def get_restriction_line(port=52222,
                         public_key=None,
                         denied_msg="'Loco account only allows port forwarding.'",
                         denies="no-X11-forwarding,no-agent-forwarding,no-pty"):
    if not public_key:
        raise ValueError("public_key should be set? or password method (TODO)")
    permit_open = 'permitopen="localhost:{0}",permitopen="127.0.0.1:{0}"'.format(port)
    restriction = 'command="echo {0}",{1},{2} {3}'.format(
        denied_msg, denies, permit_open, public_key)
    return restriction


def read_restrictions(authorized_keys_file):
    restrictions = ""
    if os.path.isfile(authorized_keys_file):
        with open(authorized_keys_file) as f:
            restrictions = f.read()
    return restrictions


def ensure_rbash_osx():
    rbash = '#!/bin/bash\nexec /bin/bash -r "$@"'
    rbash_file = "/usr/local/rbash"
    if not os.path.isfile(rbash_file):
        with open(rbash_file, "w") as f:
            f.write(rbash)
        os.system("sudo chmod +x {}".format(rbash_file))


def create_user_osx(user=USER):
    user_dir = get_user_dir(user)
    uid = get_random_uid()
    ensure_rbash_osx()
    os.system("sudo dscl . -create /groups/loco && sudo dscl . -append /groups/loco gid 622")
    cmds = ['sudo dscl . -create /Users/{0} UniqueID "{1}"',
            'sudo dscl . -create /Users/{0}',
            'sudo dscl . -create /Users/{0} RealName "Lo Co"',
            # eventually remove this one below
            'sudo dscl . -create /Users/{0} UserShell /usr/local/rbash',
            'sudo dscl . -create /Users/{0} PrimaryGroupID 20',
            # home dir does not work yet
            'sudo dscl . -create /Users/{0} NFSHomeDirectory /Users/{0}']
    cmd = " && ".join(cmds).format(user, uid)
    os.system(cmd)
    os.system("sudo mkdir {}".format(user_dir))
    return user


def create_user_linux(user=USER):
    return os.system("sudo useradd -m {}".format(user))


def remove_user_osx(user):
    user_dir = get_user_dir(user)
    os.system('sudo /usr/bin/dscl . -delete "{0}" && sudo rm -rf {0}'.format(user_dir))


def remove_user_linux(user):
    user_dir = get_user_dir(user)
    os.system("sudo userdel -r -f {}".format(user))
    os.system("sudo rm -rf {}".format(user_dir))


def create_user(user):
    os_dependent_functions = {"Darwin": create_user_osx, "Linux": create_user_linux}
    create_user_fn = platform_fn(**os_dependent_functions)
    create_user_fn(user)


@main.command()
@click.argument("user", default=USER)
def remove_user(user):
    """ Used to remove a loco user """
    if user in os.path.expanduser("~"):
        raise Exception("Cannot delete self")
    if not user.startswith("loco"):
        inp = input("Are you sure you want to delete user '{}' [y/N]: ".format(user))
        if inp.lower() != "y":
            print("Aborting.")
            return
    os_dependent_functions = {"Darwin": remove_user_osx, "Linux": remove_user_linux}
    remove_user_fn = platform_fn(**os_dependent_functions)
    donotrun(remove_user_fn, user)


def public_port_exists(rline, authorized_keys_file, restrictions, public_key, port):
    port = str(port)
    new_restrictions = []
    replaced = False
    for restriction in restrictions.split("\n"):
        if public_key in restriction:
            if ":" + port + '"' not in restriction:
                new_opens = 'no-pty,permitopen="localhost:{0}",permitopen="127.0.0.1:{0}",'
                restriction = restriction.replace("no-pty,", new_opens.format(port))
                replaced = True
            else:
                print("public_key and port already exists in", authorized_keys_file)
                return
        new_restrictions.append(restriction)
    print("Adding key+port rule to file")
    if replaced:
        result = "\n".join(new_restrictions)
    else:
        result = rline
    with open(authorized_keys_file, "w") as f:
        f.write(result + "\n")


@main.command()
@click.argument("public_key")
@click.option("--user", default=USER)
@click.option("--port", default=52222)
def create(public_key, user, port):
    """ Creates exception at a port for a user for local tunnelling. Creates user if not existing. """
    # has to be done in two, hideous but don't try to be the wise guy
    # dirname is not actually dirname, it means path up
    user_dir = get_user_dir(user)
    if not os.path.isdir(user_dir):
        print("Creating user", user)
        create_user(user)
    ssh_path = os.path.join(user_dir, ".ssh")
    # allow for easier editing
    try:
        os.system("sudo chown -R $USER {}".format(user_dir))
        if not os.path.isdir(ssh_path):
            print("Create the .ssh path for user")
            os.system("mkdir {}".format(ssh_path))
        rline = get_restriction_line(port, public_key)
        authorized_keys_file = os.path.join(ssh_path, "authorized_keys")
        restrictions = read_restrictions(authorized_keys_file)
        public_port_exists(rline, authorized_keys_file, restrictions, public_key, port)
    finally:
        # disable editing
        os.system("sudo chown -R {0} {1}".format(user, user_dir))


@main.command()
@click.argument("port", default=52222)
def kill(port=52222):
    """ Kill the local server at a given port """
    cmd = "kill $(ps aux | grep " + str(port) + " | grep -v grep | awk '{print $2}')"
    os.system(cmd)


@main.command()
@click.argument("host", default=None, required=True)
@click.option("--background", "-b", default=False, is_flag=True)
@click.option("--expose", "-e", default=False, is_flag=True)
@click.option("--local_port", default=52222)
@click.option("--remote_port", default=52222)
@click.option("--browse", default=False, is_flag=True)
def listen(host, background, expose, local_port, remote_port, browse):
    """ Listen on a remote localhost port and serve it locally.

    Provide host.

    \bExample:
    loco listen USER@IP
    """
    listening = True
    norm_args = communicate(host, background, expose, local_port, remote_port, listening, browse)


@main.command()
@click.argument("host", default=None, required=True)
@click.option("--background", "-b", default=False, is_flag=True)
@click.option("--expose", "-e", default=False, is_flag=True)
@click.option("--local_port", default=None)
@click.option("--remote_port", default=None)
def cast(host, background, expose, local_port, remote_port):
    """ Cast to a remote localhost port from a local port.

    Provide host.

    \b
    Examples:
    loco cast USER@IP
    """
    communicate(host, background, expose, local_port, remote_port, listening=False, browse=False)


def communicate(host, background, expose, local_port, remote_port, listening, browse=False):
    host = host.split(":")[0]

    interface = "0.0.0.0" if expose else "localhost"
    if listening:
        action = "LOCALLY available at"
        RorL = "-L"
        cmd = "ssh {host} {bg} -N {RorL} {interface}:{local_port}:localhost:{remote_port}"
    else:
        action = "CASTING from"
        RorL = "-R"
        cmd = "ssh {host} {bg} -N {RorL} {interface}:{remote_port}:localhost:{local_port}"

    local_port = local_port if local_port is not None else remote_port
    remote_port = remote_port if remote_port is not None else local_port

    local_port = local_port if local_port is not None else 52222
    remote_port = remote_port if remote_port is not None else 52222

    background = "-f" if background else ""
    normalized_args = {"host": host, "bg": background, "local_port": local_port,
                       "remote_port": remote_port, "RorL": RorL,
                       "interface": interface}

    msg = "Connecting with {}:{}, {} localhost:{} in_background={}"
    connect_str = msg.format(host, remote_port, action, local_port, bool(background))
    print(connect_str)

    cmd = cmd.format(**normalized_args)
    if browse:
        webbrowser.open("localhost:{}".format(local_port), new=True)
    os.system(cmd)
    return normalized_args


def list_user(user, user_dir):
    auth_keys_file = os.path.join(user_dir, ".ssh/authorized_keys")
    with open(auth_keys_file) as f:
        for line in f:
            line = line.strip()
            for port in re.findall(r"127.0.0.1:(\d+)", line):
                if "ssh-rsa" not in line:
                    print(line)
                    m = "Please post an issue with above line on https://github.com/kootenpv/loco"
                    raise Exception(m)
                key, account = line.split("ssh-rsa")[1].split()
                repr_key = key[:10] + " ..... " + key[-10:]
                tmpl = 'user="{}" port={} ssh_key={} account="{}"'
                print(tmpl.format(user, port, repr_key, account))


@main.command()
def ls():
    """ List all allowed connections """
    # e.g. /Users and /home
    home_not_user_folder = get_user_dir("")
    on_apple = is_on_apple()
    if not on_apple:
        print("To read loco folder you need root on linux.")
    for user in os.listdir(home_not_user_folder):
        if not user.startswith("loco"):
            continue
        user_dir = os.path.join(home_not_user_folder, user)
        if not on_apple:
            try:
                os.system("sudo chown -R $USER {}".format(user_dir))
                list_user(user, user_dir)
            finally:
                os.system("sudo chown -R {0} {1}".format(user, user_dir))
        else:
            list_user(user, user_dir)


def get_hash_port(word):
    h = str(int(hashlib.sha1(word.encode("utf8")).hexdigest(), 16))
    port = None
    for i in range(len(h) - 5):
        tmp = int(h[i:i + 5])
        if 3000 < tmp < 65536:
            port = tmp
            break
    return port
