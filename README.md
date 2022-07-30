# clipboard-confusion

Pure Python 2 and 3 in-memory, single document pastebin, with optional clipboard support with some qrcode support

## Setup

To get started, *optionally*:

    python -m pip install git+https://github.com/clach04/xerox.git

xerox is NOT required for simple in-mempry pastebin suppport. xerox is only needed to update the server clipboard, see https://github.com/clach04/xerox/ for potential additional requirements per platform.

To run, issue:

    python3 clipboardconfusion.py
    py -3 clipboardconfusion.py

or

    python2 clipboardconfusion.py
    py -2 clipboardconfusion.py

Issue CTRL-Break on Windows to stop/kill and CTRL-C under Linux/Unix.

Also runs under Jython 2.5+ (2.2 doesn't ship wsgi support out of box), IronPython untested.

## History

Based on https://github.com/clach04/toys4droids/blob/master/remote_clipboard.py
