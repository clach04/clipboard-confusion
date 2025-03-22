-*- coding: utf-8 -*-

# clipboard-confusion

Home page https://github.com/clach04/clipboard-confusion/

  * [Overview](#overview)
  * [Setup](#setup)
  * [Running](#running)
    + [Natively](#natively)
      - [Serving a file](#serving-a-file)
    + [Docker](#docker)
  * [History](#history)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

## Overview

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

### Docker

    #docker build -t clipboardconfusion .
    docker build -f Dockerfile_alpine -t clipboardconfusion .

    #docker run -p 8000:8000 --name clipboardconfusion --hostname clipboardconfusion --restart=unless-stopped clipboardconfusion
    docker run -p 1234:8000 --name clipboardconfusion --hostname clipboardconfusion --restart=unless-stopped clipboardconfusion
    echo Open http://localhost:1234/


## qrcodes

  * zxing for Android is a good free qrcode scanner https://play.google.com/store/apps/details?id=com.google.zxing.client.android
  * https://www.irfanview.com/ has a qrcode scanner/reader plugin for Microsoft Windows
  * https://github.com/zxing-js/library
      * https://github.com/zxing-js/browser

## History

Based on https://github.com/clach04/toys4droids/blob/master/remote_clipboard.py

## also see

  * https://github.com/Tanq16/local-content-share
  * https://github.com/jon6fingrs/ghostboard
  * https://github.com/jedisct1/piknik
  * https://github.com/shrimqy/Sefirah-Android
  * https://github.com/Sathvik-Rao/ClipCascade - maybe possible to support api that this uses?
