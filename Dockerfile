# NOTE this is expected to be behind a proxy server

# TODO try other bases, e.g. even Alpine as this needs no dependencies
FROM python:3.11

# no other dependencies, so no pip
# TODO consider alternative python web/wsgi server



ADD clipboardconfusion.py .
# TODO chmod a+x clipboardconfusion.py
# may need dos2unix
ADD qrcode.min.js .
ADD QR_icon.svg .

# TODO PORT environment variable, defaults to 8000
# Allow external connections
EXPOSE 8000

# TODO ENTRYPOINT
CMD ["python", "clipboardconfusion.py"]

# TODO healthcheck
