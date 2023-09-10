# clipboard-confusion

Pure Python 2 and 3 in-memory, single document pastebin, with optional clipboard support with some qrcode support

## Setup

To get started, *optionally* enable (server) clipboard support:

    python -m pip install git+https://github.com/clach04/xerox.git

xerox is NOT required for simple in-memory pastebin support. xerox is only needed to update the server clipboard, see https://github.com/clach04/xerox/ for potential additional requirements per platform.

*Optionally* enable (local) QRcode support:

    python -m pip install segno


To run, issue:

    python3 clipboardconfusion.py
    py -3 clipboardconfusion.py

or

    python2 clipboardconfusion.py
    py -2 clipboardconfusion.py

Issue CTRL-Break on Windows to stop/kill and CTRL-C under Linux/Unix.

Also runs under Jython 2.5+ (2.2 doesn't ship wsgi support out of box), IronPython untested.

## Docker

    #docker build -t clipboardconfusion .
    docker build -f Dockerfile_alpine -t clipboardconfusion .
    docker run -p 8000:8000 --name clipboardconfusion --hostname clipboardconfusion --restart=unless-stopped clipboardconfusion


## History

Based on https://github.com/clach04/toys4droids/blob/master/remote_clipboard.py
