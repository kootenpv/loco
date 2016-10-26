## Loco

[![Build Status](https://travis-ci.org/kootenpv/loco.svg?branch=master)](https://travis-ci.org/kootenpv/loco)
[![PyPI](https://img.shields.io/pypi/v/loco.svg?style=flat-square)](https://pypi.python.org/pypi/loco/)
[![PyPI](https://img.shields.io/pypi/pyversions/loco.svg?style=flat-square)](https://pypi.python.org/pypi/loco/)

Share localhost through SSH. Also known as local ssh port forward. No strings attached.

### Features

- **Convenience**. Share whatever is happening on your localhost with someone else
- **Safety**. Nothing beats SSH. The only open port required is 22. Share your HTTP through SSH!
- **Containment**. Specifically creates an SSH user that can ONLY do port forwarding; nothing else.
- **Platforms**. Works on OSX and Linux in general.

### Story

`sender` wants to share his web app hosted at port 5000. `receiver` wants to see what the app is all about.

- `receiver` runs `loco pubkey` to copy their public SSH key to clipboard
- `receiver` sends pubkey to `sender` by chat, mail or pigeon.
- `sender` runs `loco create "RECEIVER_PUBKEY"`. This is [the interesting part](#the-interesting-part) :link:!
- `receiver` runs `loco listen SENDER_IP`

Receiver can now see what sender is seeing at `localhost:52222`

### Additional features

```
# No need to keep a terminal open
loco listen SENDER_IP --background

# kills a `loco listen` in the background
loco kill [optional: PORT]

# remove all settings for a user (by default loco0).
loco remove_user

# View how you can be accessed
loco list # outputs
user="loco0" port=62222 ssh_key=AAAAB3NzaC ..... joCyayMg+d account="pascal@T510"

# create specific user+port combination (don't forget to share this info with buddy)
loco create "PUBKEY" --user loco5 --port 60000

# NOTE: default is to serve at 52222, so can be viewed at 52222
loco listen IP --user loco5 --remote_port 60000

# Now receiver can locally view at 60000
loco listen IP --user loco5 --remote_port 60000 --local_port 60000
```

### The interesting part

`loco create` creates a restricted user on the senders' machine. This user (by default called `loco0`) can do nothing except for allow port forwarding at a given port (by default `62222`).
The receiver can use `loco listen SENDER_IP` to use SSH for portforwarding (again by default as `loco0`, port `62222`). The good thing is that you can now safely make a HTTP connection without allowing this user to do anything else.
Note that everything can be configured; the used username, the senders' port to be shared, and on which port it will be receivable by the receiver. To find these options, you can use `--help` using the CLI:

```bash
pascal@MBP:~ $ loco listen --help
Usage: loco listen [OPTIONS] [HOST]

  Listen on a remote localhost port and serve it locally

Options:
  --user TEXT
  --ip TEXT
  -b, --background
  --local_port INTEGER
  --remote_port INTEGER
  --help                 Show this message and exit.
```

Running it invalidly will show examples:

```bash
pascal@MBP:~ $ loco listen
Usage: loco listen [OPTIONS] [HOST]

Error: Provide either host or ip.
Examples:
loco receive USER@IP
loco receive mybuddy                # .ssh/config
loco receive --user loco0 --ip IP
loco receive --ip IP                # --user is given by default
```

You will have complete control over whether you want to allow sharing a single port with many users, or each user their own port.

### loco users are special

Any username starting with "loco" will be considered a loco user.
Apart from being restricted, the CLI tool also takes extra care for loco users. For example, it will warn you when you would try to remove non loco users. It will throw an exception when you try to delete yourself.
`loco list` also only lists the `loco` users.

### Contributing

Feel free to make suggestions.
