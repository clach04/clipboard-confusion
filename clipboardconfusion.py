#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""View and change clipboard remotely

TODO Python3 support

TODO android support into xerox?

"""

import urllib  # FIXME py2 only
import os
import socket
import sys
try:
    if os.environ.get('LAUNCH_BROWSER'):
        import webbrowser
    else:
        raise ImportError
except ImportError:
    webbrowser = None
from wsgiref.simple_server import make_server
try:
    # py2
    from cgi import escape
    from cgi import parse_qs
    from urllib import quote, quote_plus
except ImportError:
    # Python 3.8 and later 
    # py3
    from html import escape
    from urllib.parse import quote, quote_plus
    from urllib.parse import parse_qs


try:
    import android
    droid = android.Android()
except ImportError:
    android = droid = None

try:
    import segno  # preferred - https://github.com/heuer/segno
except ImportError:
    segno = None

try:
    import pyqrcodeng  # https://github.com/pyqrcode/pyqrcodeNG
except ImportError:
    pyqrcodeng = None


def display_console_qrcode_pyqrcodeng(url):
    # NOTE pyqrcodeng could be used for desktop (maybe) web browser launching with locally generated SVG and/or PNG
    qr = pyqrcodeng.create(url)
    """
    print(qr.text())

    print('-' *65)
    text_scale_factor_width = 2
    white_char = u'\u2588'  # Full Block https://www.compart.com/en/unicode/U+2588
    #white_char = '#' # does not work with my phone qrcode scanner/reader
    #white_char = '*' # does not work with my phone qrcode scanner/reader
    black_char = ' '
    print(qr.text().replace('1', black_char * text_scale_factor_width).replace('0', white_char * text_scale_factor_width).encode('cp437'))
    print('-' *65)
    """
    qr.term()  # this "prints" to stdout/tty/console (works for win32)
    #print(qr.terminal())  # this generates ANSI/VT100 escape sequences (not suitable for win32)


def display_console_qrcode_segno(url):
    # NOTE segno could be used for desktop (maybe) web browser launching with locally generated SVG and/or PNG
    qr = segno.make(url)
    #print(dir(qr))
    #print(qr)
    qr.terminal()


display_console_qrcode = None
if pyqrcodeng: display_console_qrcode = display_console_qrcode_pyqrcodeng  # note officially unmaintained
if segno: display_console_qrcode = display_console_qrcode_segno

def gen_qrcode_url(url, image_size=547):
    """Construct QR generator google URL with max size, from:

    https://chart.googleapis.com/chart? - All infographic URLs start with this root URL, followed by one or more parameter/value pairs. The required and optional parameters are specific to each image; read your image documentation.
        chs - Size of the image in pixels, in the format <width>x<height>
        cht - Type of image: 'qr' means QR code.
        chl - The data to encode. Must be URL-encoded.

    See https://google-developers.appspot.com/chart/infographics/docs/overview
    """
    url = quote(url)
    #url = quote_plus(url)
    image_size_str = '%dx%d' % (image_size, image_size)
    result = 'https://chart.googleapis.com/chart?cht=qr&chs=%s&chl=%s' % (image_size_str, url)
    return result


# Utility function to guess the IP (as a string) where the server can be
# reached from the outside. Quite nasty problem actually.

def find_ip ():
   # we get a UDP-socket for the TEST-networks reserved by IANA.
   # It is highly unlikely, that there is special routing used
   # for these networks, hence the socket later should give us
   # the ip address of the default route.
   # We're doing multiple tests, to guard against the computer being
   # part of a test installation.

   candidates = []
   for test_ip in ["192.0.2.0", "198.51.100.0", "203.0.113.0"]:
      s = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
      s.connect ((test_ip, 80))
      ip_addr = s.getsockname ()[0]
      s.close ()
      if ip_addr in candidates:
         return ip_addr
      candidates.append (ip_addr)

   return candidates[0]

if android is None:
    try:
        import xerox  # NOTE use https://github.com/clach04/xerox/tree/win_no_crash until PR merged -- from https://github.com/kennethreitz/xerox
    except ImportError:
        if os.environ.get('FAKE_XEROX') is None:
            raise
        else:
            # no clipboard access, so store/cache locally
            class FakeXerox:
                def __init__(self):
                    self.txt = ''
                def copy(self, new_text):
                    self.txt = new_text
                def paste(self):
                    return self.txt
            xerox = FakeXerox()

def copy(new_text):
    if droid:
        droid.setClipboard(new_text)
    else:
        xerox.copy(new_text)

def paste():
    if droid:
        x = droid.getClipboard()
        result = x.result
    else:
        result = xerox.paste()
    return result

def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]
    # content length?

    path_info = environ['PATH_INFO']

    # Returns a dictionary in which the values are lists
    get_dict = parse_qs(environ['QUERY_STRING'])

    # POST values
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    # Read POST body
    request_body = environ['wsgi.input'].read(request_body_size)
    """
    print('DEBUG request_body_size', repr(request_body_size))
    if request_body_size:
        print('read with size')
        request_body = environ['wsgi.input'].read(request_body_size)
    else:
        print('read with NO size')
        request_body = environ['wsgi.input'].read()  # seen under Linux, if zero passed in, will read zero bytes!
    """
    print('DEBUG request_body', repr(request_body))
    sys.stdout.flush()  # DEBUG
    d = parse_qs(request_body.decode('utf-8'))
    print('DEBUG d', repr(d))
    new_clipboard_text = d.get('newtext')
    print('DEBUG new_clipboard_text %s' % repr(new_clipboard_text))
    if new_clipboard_text is not None:
        new_clipboard_text = ''.join(new_clipboard_text)
        new_clipboard_text = new_clipboard_text
        copy(new_clipboard_text)
    print('DEBUG new_clipboard_text', repr(new_clipboard_text))
    ###################################################

    clipboard_contents = paste()
    result = []
    result.append('<html>')
    result.append('<head>')
    result.append('<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
    result.append('</head>')
    print('DEBUG clipboard contents=',repr(clipboard_contents))
    x = escape(clipboard_contents)
    #'''
    result.append("""
    <pre>
        <code>""")
    result.append(x)
    result.append("""</code>
    </pre>
    """)
    #'''

    result.append("""
    <form accept-charset="utf-8" action="setclipboard" method="POST" id="myform" name="myform">
        <label>Current clipboard contents:</label>
        <br />
        <!-- TODO There is way to get textarea to be 100 percent via CSS and/or javascript, however most browsers allow manual resizing of text area. See http://stackoverflow.com/questions/271067/how-can-i-make-a-textarea-100-width-without-overflowing-when-padding-is-present (using a textwrapper div) -->
        <textarea rows="25" cols="80" name="newtext"  accept-charset="utf-8">""")
    result.append(x)
    result.append("""</textarea>
        <br />
        <input type="submit" value="Update clipboard"/>
    </form>
    """)
    result.append('</html>')
    #import pdb ; pdb.set_trace()
    start_response(status, response_headers)
    return [''.join(result).encode('utf-8')]


def doit():
    hostname = '0.0.0.0'
    #hostname = 'localhost'
    port = int(os.environ.get('PORT', 8000))
    print('Open http://%s:%d' % (hostname, port))
    print('Issue CTRL-C (Windows CTRL-Break instead) to stop')

    ip_addr = find_ip()
    url_str = "http://%s:%s/" % (ip_addr, port)
    print(url_str)
    #display_console_qrcode = webbrowser = None  # Quick disable launch browser and QRcode
    qrcode_url = gen_qrcode_url(url_str)
    print(qrcode_url)
    if display_console_qrcode:
        display_console_qrcode(url_str)
    if webbrowser:
        webbrowser.open(qrcode_url)

    httpd = make_server(hostname, port, application)
    httpd.serve_forever()


def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' % (sys.version, sys.platform))
    doit()

    return 0


if __name__ == "__main__":
    sys.exit(main())
