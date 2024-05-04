#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""Pure Python 2 and 3 in-memory, single document pastebin, with optional clipboard support with some qrcode support
"""

version_tuple = __version_info__ = (0, 0, 2, 'git')
version = version_string = __version__ = '.'.join(map(str, __version_info__))

import logging
import os
import socket
import sys
import time

try:
    if os.environ.get('LAUNCH_BROWSER'):
        import webbrowser
    else:
        raise ImportError
except ImportError:
    webbrowser = None
from wsgiref.simple_server import make_server

try:
    # Python 3.8 and later
    # py3
    from html import escape
    from urllib.parse import quote, quote_plus
    from urllib.parse import parse_qs
except ImportError:
    # py2
    from cgi import escape
    from cgi import parse_qs
    from urllib import quote, quote_plus


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

try:
    import xerox  # NOTE use https://github.com/clach04/xerox/
except ImportError:
    xerox = None


log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(level=logging.INFO)
#log.setLevel(level=logging.DEBUG)

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
    # print(qr.terminal())  # this generates ANSI/VT100 escape sequences (not suitable for win32)


def display_console_qrcode_segno(url):
    # NOTE segno could be used for desktop (maybe) web browser launching with locally generated SVG and/or PNG
    qr = segno.make(url)
    # print(dir(qr))
    # print(qr)
    qr.terminal()


display_console_qrcode = None
if pyqrcodeng:
    display_console_qrcode = (
        display_console_qrcode_pyqrcodeng  # note officially unmaintained
    )
if segno:
    display_console_qrcode = display_console_qrcode_segno


def gen_qrcode_url(url, image_size=547):
    """Construct QR generator google URL with max size, from:

    https://chart.googleapis.com/chart? - All infographic URLs start with this root URL, followed by one or more parameter/value pairs. The required and optional parameters are specific to each image; read your image documentation.
        chs - Size of the image in pixels, in the format <width>x<height>
        cht - Type of image: 'qr' means QR code.
        chl - The data to encode. Must be URL-encoded.

    See https://google-developers.appspot.com/chart/infographics/docs/overview
    """
    url = quote(url)
    # url = quote_plus(url)
    image_size_str = '%dx%d' % (image_size, image_size)
    result = 'https://chart.googleapis.com/chart?cht=qr&chs=%s&chl=%s' % (
        image_size_str,
        url,
    )
    return result


# Utility function to guess the IP (as a string) where the server can be
# reached from the outside. Quite nasty problem actually.


def find_ip():
    # we get a UDP-socket for the TEST-networks reserved by IANA.
    # It is highly unlikely, that there is special routing used
    # for these networks, hence the socket later should give us
    # the ip address of the default route.
    # We're doing multiple tests, to guard against the computer being
    # part of a test installation.

    candidates = []
    for test_ip in ["192.0.2.0", "198.51.100.0", "203.0.113.0"]:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((test_ip, 80))
        ip_addr = s.getsockname()[0]
        s.close()
        if ip_addr in candidates:
            return ip_addr
        candidates.append(ip_addr)

    return candidates[0]

class FakeXerox:
    # store/cache locally - no clipboard access
    def __init__(self):
        self.txt = ''

    def copy(self, new_text):
        self.txt = new_text

    def paste(self):
        return self.txt

if xerox is None:
    # no clipboard access, so store/cache locally
    xerox = FakeXerox()


def clipboard_copy(new_text):
    if droid:
        droid.setClipboard(new_text)
    else:
        xerox.copy(new_text)


def clipboard_paste():
    if droid:
        x = droid.getClipboard()
        result = x.result
    else:
        result = xerox.paste()
    return result

def current_timestamp_for_header():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

"""
version:

commit 04f46c6a0708418cb7b96fc563eacae0fbf77674 (HEAD -> master, origin/master, origin/HEAD)
Merge: 540308a bd3de7f
Author: Sangmin, Shim <ssm0123@gmail.com>
Date:   Wed Nov 25 19:43:20 2015 +0900

    Merge pull request #63 from markvantilburg/patch-1

    Update README.md

NOTE .min.js version in that repo is from 2013-07-12
non-min is a litle over a year later. - Both work with clipboard confusion.

from https://github.com/davidshimjs/qrcodejs.git
MIT license

> Browser Compatibility
>
> IE6~10, Chrome, Firefox, Safari, Opera, Mobile Safari, Android, Windows Mobile, ETC.
"""
qr_code_js_filename = 'qrcode.min.js'
#qr_code_js_filename = 'qrcode.js'
f = open(qr_code_js_filename, 'rb')
qrcode_js_bytes = f.read()
f.close()

# TODO consider using PNG instead?
qr_code_svg_filename = 'QR_icon.svg'
f = open(qr_code_svg_filename, 'rb')
qrcode_svg_bytes = f.read()
f.close()

def application(environ, start_response):
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html'),
        ('Cache-Control', 'no-cache'),
        ('X-Content-Type-Options', 'nosniff'),  # no-sniff
    ]
    # content length?

    path_info = environ['PATH_INFO']
    print('DEBUG entry path_info %r' % path_info) ; sys.stdout.flush()
    if path_info == '/qrcode.min.js':
        response_headers = [
            ('Content-Type', 'text/javascript'),
            ('Cache-Control', 'no-cache'),  # revisit this
            ('X-Content-Type-Options', 'nosniff'),  # no-sniff
        ]
        start_response(status, response_headers)
        return [qrcode_js_bytes]
    elif path_info == '/QR_icon.svg':
        response_headers = [
            ('Content-Type', 'image/svg+xml'),
            #('Cache-Control', 'no-cache'),  # revisit this
            ('X-Content-Type-Options', 'nosniff'),  # no-sniff
        ]
        start_response(status, response_headers)
        return [qrcode_svg_bytes]
    elif path_info == '/download':
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition
        result = clipboard_paste().encode('utf-8')
        response_headers = [
            ('Content-Type', 'text/plain'), # TODO? + '; charset=utf-8'
            ('Content-Disposition', 'attachment; filename="clipboard_utf8.txt"'),
            #('Cache-Control', 'no-cache'),  # revisit this
            ('X-Content-Type-Options', 'nosniff'),  # no-sniff
            ('Last-Modified', current_timestamp_for_header()),  # TODO could use time of last paste...
            ('Content-Length', '%d' % len(result)),
        ]
        start_response(status, response_headers)
        return [result]
    # else assume update/view clipboard

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
    log.debug('request_body_size %r', request_body_size)
    if request_body_size:
        print('read with size')
        request_body = environ['wsgi.input'].read(request_body_size)
    else:
        print('read with NO size')
        request_body = environ['wsgi.input'].read()  # seen under Linux, if zero passed in, will read zero bytes!
    """
    log.debug('request_body %r', request_body)
    sys.stdout.flush()  # DEBUG
    d = parse_qs(request_body.decode('utf-8'))
    log.debug('d %r', d)
    new_clipboard_text = d.get('newtext')
    log.debug('new_clipboard_text %sr' % new_clipboard_text)
    if new_clipboard_text is not None:
        new_clipboard_text = ''.join(new_clipboard_text)
        new_clipboard_text = new_clipboard_text
        clipboard_copy(new_clipboard_text)
    log.debug('new_clipboard_text %r', new_clipboard_text)
    ###################################################

    clipboard_contents = clipboard_paste()
    log.debug('clipboard contents=%r', clipboard_contents)
    character_count = len(clipboard_contents)
    character_count_str = "{:,} characters".format(character_count)  # NOTE py2.7+ and requires locale to be setup
    character_count_str += " (%d characters)" % character_count
    # TODO stats; byte size/count, line count, word count?
    x = escape(clipboard_contents)

    result = []
    # DOCTYPE and html lang="en" - break the 50% screen height in the textarea, only works with plain old html tag
    #result.append('<!DOCTYPE html>')
    #result.append('<html lang="en">')
    result.append('<html>')
    result.append('<head>')
    result.append('<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
    result.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    result.append('<title>Clipboard Confusion</title>')
    result.append(
        """<script type="text/javascript">
function form_setfocus() {document.myform.newtext.focus();}
/*
** form_setfocus() works with:
**   * GNU IceCat 31.6.0
** and fails with:
**   * Firefox 16.0.1
*/

function init() {

    form_setfocus();

    document.addEventListener('keydown', (event) => {
        if(event.ctrlKey && event.key == "Enter") {
            //document.forms[0].submit();
            document.myform.submit();
        }
    });
    /*
    ** ctrl-enter works with:
    **   * GNU IceCat 31.6.0
    ** and fails with:
    **   * Chromium  12.0.742.112
    **   * Firefox 3.6.18, 16.0.1
    **   * Konqueror 4.5.5 (KDE 4.5.5)
    */

}

    function fallbackCopyTextToClipboard(text) {
        var textArea = document.createElement("textarea");
        textArea.value = text;

        // Avoid scrolling to bottom
        textArea.style.top = "0";
        textArea.style.left = "0";
        textArea.style.position = "fixed";

        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            var successful = document.execCommand('copy');
            var msg = successful ? 'successful' : 'unsuccessful';
            console.log('Fallback: Copying text command was ' + msg);
        } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
        }

        document.body.removeChild(textArea);
    }
    function copyTextToClipboard(text) {
        if (!navigator.clipboard) {
            fallbackCopyTextToClipboard(text);
            return;
        }
        navigator.clipboard.writeText(text).then(function() {
            console.log('Async: Copying to clipboard was successful!');
        }, function(err) {
            console.error('Async: Could not copy text: ', err);
        });
    }

window.onload=init; /* <body onload="init()"> */
</script>
    """
    )

    # <script src="https://cdn.jsdelivr.net/gh/davidshimjs/qrcodejs@gh-pages/qrcode.min.js"></script>
    # <script src="./qrcode.min.js"></script>
    result.append("""
<script src="./qrcode.min.js"></script>
<script>
    // Show the QR-Code of a "value" attribute (when the QR-Code icon is clicked).
    /*
        Where the parent node of the caller will have the qr code appended too - TODO consider using node directly?
        value is used as string value to generate qrcode, if missing use parent with .value, or parent with .innerText
        if parent_node is passed in, use that as place to put qrcode, else parent of caller
    */
    function showQrCode(caller, value, parent_node)
    {
        parent_node = parent_node || caller.parentNode;
        // Remove previous qrcode if present.
        removeQrcode();

        // Build the div which contains the QR-Code:
        var element = document.createElement('div');
        element.id = 'permalinkQrcode';

        // Make QR-Code div commit sepuku when clicked:
        if ( element.attachEvent ){
            element.attachEvent('onclick', 'this.parentNode.removeChild(this);' );

        } else {
            // Damn IE
            element.setAttribute('onclick', 'this.parentNode.removeChild(this);' );
        }

        element.innerHTML += "<br>Click to close";
        parent_node.appendChild(element);
        new QRCode(document.getElementById(element.id), value || caller.value || caller.innerText);
        qrcodeImage = document.getElementById(element.id);
        // make sure QR code is actually shown - Workaround to deal with newly created element lag for transition.
        window.getComputedStyle(qrcodeImage).opacity;
        qrcodeImage.className = 'show';
        return false;
    }

    // Remove any displayed QR-Code
    function removeQrcode()
    {
        var elem = document.getElementById('permalinkQrcode');
        if (elem) {
            elem.parentNode.removeChild(elem);
        }
        return false;
    }
</script>
""")
    result.append('</head>')
    # result.append("""<body onload="init()">""")
    result.append("""<body>""")

    result.append("""<button class="js-copy-to-clipboard" id="js-copy-to-clipboard">Copy Text Entry Field to (browser) clipboard</button>""")
    result.append(' <a href="/download">Download</a>')  # TODO styled button
    result.append("""<br />""")
    result.append("""<div><div class="qrcode_window" id="qrcode_window" name="qrcode_window"></div></div>""")

    # qrcode for Text Entry Form
    result.append(
        """
        <a href="#" onclick="showQrCode(newtext, null, qrcode_window); return false;" class="qrcode">
            <img src="./QR_icon.svg" class="linklist-plugin-icon" title="Show QRCode for Text Entry Field" alt="data form QR-Code">
            <!-- qricon.png is converted from https://commons.wikimedia.org/wiki/File:QR_icon.svg -->
        </a>
    """
    )

    # qrcode for code tag/pastebin
    result.append(
        """
        <a href="#" onclick="showQrCode(clipboard_contents, null, qrcode_window); return false;" class="qrcode">
            <img src="./QR_icon.svg" class="linklist-plugin-icon" title="Show QRCode for clipboard_contents" alt="data QR-Code">
            <!-- qricon.png is converted from https://commons.wikimedia.org/wiki/File:QR_icon.svg -->
        </a>
    """
    )

    # qrcode for Window URL
    result.append(
        """
        <a href="#" onclick="showQrCode(qrcode_window, window.location.href); return false;" class="qrcode">
            <img src="./QR_icon.svg" class="linklist-plugin-icon" title="Show QRCode for URL" alt="URL QR-Code">
            <!-- qricon.png is converted from https://commons.wikimedia.org/wiki/File:QR_icon.svg -->
        </a>
    """
    )
    # TODO server static version of qrcode icon and source code, above requires internet access
    #         <img src="/static/qricon.png" class="linklist-plugin-icon" title="QR-Code" alt="QRCode">

    if isinstance(xerox, FakeXerox):
        # TODO make pretty/styled
        result.append(
        """<br /><b>Native clipboard support missing</b>, install xerox (or Android support lib), using non-persistent/temporary memory.
        <br />
    """
        )

    result.append(
        """
    <form accept-charset="utf-8" action="setclipboard" method="POST" id="myform" name="myform">
        <label for="newtext">Current clipboard contents:</label>"""
    )
    result.append(character_count_str)  # stats
    result.append("""
        <br />
        <!-- TODO There is way to get textarea to be 100 percent via CSS and/or javascript, however most browsers allow manual resizing of text area. See http://stackoverflow.com/questions/271067/how-can-i-make-a-textarea-100-width-without-overflowing-when-padding-is-present (using a textwrapper div) -->
        <textarea id="newtext" name="newtext" accept-charset="utf-8" style="width:100%;height:50%">"""
    )
    result.append(x)
    result.append(
        """</textarea>
        <br />
        <input type="submit" value="Update"/>
        <a href="/download">Download</a>
    </form>
    """
    )

    result.append(character_count_str)  # stats
    result.append('<hr>')
    result.append(
        """
    <pre><code id="clipboard_contents">"""
    )
    result.append(x)
    result.append(
        """</code>
    </pre>
    """
    )
    result.append('<hr>')

    result.append(
        """    <a href="https://github.com/clach04/clipboard-confusion/">
    Clipboard Confusion - a single file, in-memory pastebin
    </a>
    """
    )
    result.append(
        """
    <script>

    //var copyClipBtn = document.querySelector('button.js-copy-to-clipboard');
    var copyClipBtn = document.getElementById("js-copy-to-clipboard");

    copyClipBtn.addEventListener('click', function(event) {
        /*
        ** Works/Tested with:
        **    * Chromium 79.0.3945.79
        **    * FireFox 46.0, 86.0
        **
        ** Fails with:
        **    * Chromium  12.0.742.112 (Developer Build 90304) Ubuntu 10.10 -  WebKit  534.30 (trunk@84325)
        **    * Firefox 3.6.18, 16.0.1
        **    * GNU IceCat 31.6.0 (Developer Build 144678) Built on  Lubuntu 12.04
        **    * Konqueror 4.5.5 (KDE 4.5.5)
        */
        var text_entry_field = document.getElementById("newtext");

        text_entry_field.select();
        text_entry_field.setSelectionRange(0, 99999); /* For mobile devices */
        copyTextToClipboard(text_entry_field.value);
    });
    </script>
    """
    )
    result.append("""</body>""")

    result.append('</html>')
    # import pdb ; pdb.set_trace()
    print('DEBUG path_info %r pre start_response' % path_info) ; sys.stdout.flush()
    start_response(status, response_headers)
    print('DEBUG path_info %r pre return' % path_info) ; sys.stdout.flush()
    return [''.join(result).encode('utf-8')]


def doit(filename=None):
    hostname = '0.0.0.0'  # allow any client
    # hostname = 'localhost'  # limit to local only
    port = int(os.environ.get('PORT', 8000))

    if filename:
        print('Using file %s as initial clipboard contents' % (filename, ))
        f = open(filename, 'r')  # assume locale encoding...
        clipboard_copy(f.read())
        f.close()

    print('Attempting to listen on http://%s:%d' % (hostname, port))
    print('Issue CTRL-C (Windows CTRL-Break instead) to stop')

    ip_addr = find_ip()
    print("http://%s:%s/" % ('localhost', port))
    url_str = "http://%s:%s/" % (ip_addr, port)
    print(url_str)
    # display_console_qrcode = webbrowser = None  # Quick disable launch browser and QRcode
    qrcode_url = gen_qrcode_url(url_str)
    print(qrcode_url)
    if display_console_qrcode:
        display_console_qrcode(url_str)
    else:
        print('console qrcode support missing, install segno or pyqrcodeng')
    if isinstance(xerox, FakeXerox):
        print('clipboard support missing, install xerox (or Android support lib)')
    if webbrowser:
        webbrowser.open(qrcode_url)

    httpd = make_server(hostname, port, application)
    httpd.serve_forever()


def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' % (sys.version, sys.platform))
    print('Clipboard Confusion v%s' % __version__)
    try:
        filename = argv[1]
    except IndexError:
        filename = None
    doit(filename=filename)

    return 0


if __name__ == "__main__":
    sys.exit(main())
