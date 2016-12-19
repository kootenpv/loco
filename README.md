## Loco

[![Build Status](https://travis-ci.org/kootenpv/loco.svg?branch=master)](https://travis-ci.org/kootenpv/loco)
[![PyPI](https://img.shields.io/pypi/v/loco.svg?style=flat-square)](https://pypi.python.org/pypi/loco/)
[![PyPI](https://img.shields.io/pypi/pyversions/loco.svg?style=flat-square)](https://pypi.python.org/pypi/loco/)

Share localhost through SSH. Making local/remote port forwarding easy and safe.

### Story

`sender` wants to share his web app hosted at port 52222. `receiver` wants to see what the app is all about.

- `receiver` runs `loco pubkey` to copy their public SSH key to clipboard
- `receiver` sends pubkey to `sender` by chat, mail or pigeon.
- `sender` runs `loco create "RECEIVER_PUBKEY"`. This is [the interesting part](#the-interesting-part)!
- `receiver` runs `loco listen SENDER`, where sender is ssh config such as user@ip

Receiver can now see what sender is seeing at `localhost:52222`

When you are behind a (company) firewall/router, then there are 3 possible solutions.

- You can use a "shared" area (such as a cloud instance).
- You can do remote forwarding instead of local forwarding. Basically, as long as 1 of the 2 parties is not within a firewall, it'll work.
- You can open up port 22 (SSH).

### Features

- **Convenience**. Share whatever is happening on your localhost with someone else
- **Safety**. Nothing beats SSH. The only open port required is 22. Share your HTTP through SSH!
- **Containment**. Specifically creates an SSH user that can ONLY do port forwarding; nothing else.
- **Cross-platform**. Works on OSX and Linux in general.
- **No 3rd party**. Unlike `ngrok`, you won't need to rely on a third party.

### Installation

Works using both Python 2.7+ and Python 3+:

    pip install loco

### Functionality

```bash
# cast your localhost to someone else
loco cast RECEIVER

# No need to keep a terminal open
loco listen SENDER --background

# Kills a `loco listen` in the background
loco kill [optional: PORT, default=52222]

# Remove all settings for a user (by default loco0).
loco remove_user

# View how you can be accessed
loco ls # outputs
user="loco0" port=52222 ssh_key=AAAAB3NzaC ..... joCyayMg+d account="pascal@T510"

# Create specific user+port combination (don't forget to share this info with buddy)
# And don't forget the quotes
loco create "PUBKEY" loco5@someip --port 5000

# NOTE: default is to serve at 52222, so can be viewed at 52222
loco listen loco5@someip --remote_port 5000

# Now receiver can locally view at 5000
loco listen loco5@someip --remote_port 5000 --local_port 5000

# push your content to someone who created a loco user for you
loco cast loco5@someip --remote_port 5000 --local_port 5000
```

For issues, such as both parties being within a firewall, you can use a server in between (e.g. some cloud instance).
If just one party is within firewall, then you can use either cast/listen.

In case of using an inbetween server:

```bash
# on server:
loco create "PUBKEY_RECEIVER"
loco create "PUBKEY_SENDER"
# on sender:
loco cast loco0@server
# on receiver
loco listen loco0@server
```

### The interesting part

`loco create` creates a restricted user on the senders' machine. This user (by default called `loco0`) can do nothing except for allow port forwarding at a given port (by default `52222`).
The receiver can use `loco listen SENDER_IP` to use SSH for portforwarding (again by default as `loco0`, port `52222`). The good thing is that you can now safely make a HTTP connection without allowing this user to do anything else.
Note that everything can be configured; the used username, the senders' port to be shared, and on which port it will be receivable by the receiver.

To find out more possibilities, you can use `--help` using the CLI:

```bash
pascal@MBP:~ $ loco listen --help
Usage: loco listen [OPTIONS] HOST

  Listen on a remote localhost port and serve it locally.

  Provide host.

 Example: loco listen USER@IP

Options:
  -b, --background
  --local_port INTEGER
  --remote_port INTEGER
  --browse TEXT
  --help                 Show this message and exit.
```

You will have complete control over whether you want to allow sharing a single port with many users, or each user their own port.

### loco users are special

Any username starting with "loco" will be considered a loco user.
Apart from being restricted, the CLI tool also takes extra care for loco users. For example, it will warn you when you would try to remove non loco users. It will throw an exception when you try to delete yourself.
`loco ls` also only lists the `loco` users.

### Contributing

Feel free to make suggestions.
