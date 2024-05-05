# clipboard-confusion

Pure Python 2 and 3 in-memory, single document pastebin, with optional clipboard support with some qrcode support

## Setup

To get started, *optionally* enable (server) clipboard support:

    python -m pip install git+https://github.com/clach04/xerox.git

xerox is NOT required for simple in-memory pastebin support. xerox is only needed to update the server clipboard, see https://github.com/clach04/xerox/ for potential additional requirements per platform.

*Optionally* enable (local) QRcode support:

    python -m pip install segno

## Running

### Natively

To run, issue:

    python3 clipboardconfusion.py
    py -3 clipboardconfusion.py
    py -3 clipboardconfusion.py clipboardconfusion.py  # start with source code for this tool in clipboard

or

    python2 clipboardconfusion.py
    py -2 clipboardconfusion.py
    py -2 clipboardconfusion.py clipboardconfusion.py  # start with source code for this tool in clipboard

Issue CTRL-Break on Windows to stop/kill and CTRL-C under Linux/Unix.

Also runs under Jython 2.5+ (2.2 doesn't ship wsgi support out of box), IronPython untested.

#### Serving a file

    clipboardconfusion.py /etc/os-release

NOTE file is assumed to be text (utf-8) and **not** binary.

#### OpenSSL encrypted AES-256-CBC with PBKDF2

You can serve an encrypted file using bash shell [process substitution](http://www.tldp.org/LDP/abs/html/process-sub.html):

    cat /etc/os-release | \
        openssl enc -e -aes-256-cbc -in - -out - -base64 -salt -pbkdf2 -iter 10000  -pass pass:password | \
        ./clipboardconfusion.py /dev/stdin

Windows alternative example:

    "C:\Program Files\Git\mingw64\bin\openssl.exe"  enc -e -aes-256-cbc -in README.md -out README.md.enc -base64 -salt -pbkdf2 -iter 10000  -pass pass:password
    py -3 clipboardconfusion.py README.md.enc

The web interface has a work-in-progress support for decrypting (only) the contents of the textentry field in the form.
It ONLY supports openssl encrypted with:
  * aes-256-cbc
  * salt
  * PBKDF2 with itereration count of 10000 (10,000, i.e. 10K). NOTE in 2023 this iteration count is considered too small

### Docker

    #docker build -t clipboardconfusion .
    docker build -f Dockerfile_alpine -t clipboardconfusion .

    #docker run -p 8000:8000 --name clipboardconfusion --hostname clipboardconfusion --restart=unless-stopped clipboardconfusion
    docker run -p 1234:8000 --name clipboardconfusion --hostname clipboardconfusion --restart=unless-stopped clipboardconfusion
    echo Open http://localhost:1234/


## History

Based on https://github.com/clach04/toys4droids/blob/master/remote_clipboard.py
