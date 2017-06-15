# No unicode_literals
import sys, os, json, unicodedata, locale
from binascii import hexlify, unhexlify
from twisted.python import log

def to_bytes(u):
    return unicodedata.normalize("NFC", u).encode("utf-8")
def bytes_to_hexstr(b):
    assert isinstance(b, type(b""))
    hexstr = hexlify(b).decode("ascii")
    assert isinstance(hexstr, type(u""))
    return hexstr
def hexstr_to_bytes(hexstr):
    assert isinstance(hexstr, type(u""))
    b = unhexlify(hexstr.encode("ascii"))
    assert isinstance(b, type(b""))
    return b
def dict_to_bytes(d):
    assert isinstance(d, dict)
    b = json.dumps(d).encode("utf-8")
    assert isinstance(b, type(b""))
    return b
def bytes_to_dict(b):
    assert isinstance(b, type(b""))
    d = json.loads(b.decode("utf-8"))
    assert isinstance(d, dict)
    return d

def estimate_free_space(target):
    # f_bfree is the blocks available to a root user. It might be more
    # accurate to use f_bavail (blocks available to non-root user), but we
    # don't know which user is running us, and a lot of installations don't
    # bother with reserving extra space for root, so let's just stick to the
    # basic (larger) estimate.
    try:
        s = os.statvfs(os.path.dirname(os.path.abspath(target)))
        return s.f_frsize * s.f_bfree
    except AttributeError:
        return None

# encoding routines copied from Tahoe

def _canonical_encoding(encoding):
    if encoding is None:
        log.msg("Warning: falling back to UTF-8 encoding.", level=log.WEIRD)
        encoding = 'utf-8'
    encoding = encoding.lower()
    if encoding == "cp65001":
        encoding = 'utf-8'
    elif encoding == "us-ascii" or encoding == "646" or encoding == "ansi_x3.4-1968":
        encoding = 'ascii'

    return encoding

def _check_encoding(encoding):
    # sometimes Python returns an encoding name that it doesn't support for
    # conversion fail early if this happens
    try:
        u"test".encode(encoding)
    except (LookupError, AttributeError):
        raise AssertionError("The character encoding '%s' is not supported for conversion." % (encoding,))

def get_io_encoding():
    if sys.platform == 'win32':
        # # On Windows we install UTF-8 stream wrappers for sys.stdout and
        # # sys.stderr, and reencode the arguments as UTF-8 (see
        # # scripts/runner.py).
        #
        # Note: tahoe does that, but we don't. Set to UTF-8 and hope.
        io_encoding = 'utf-8'
    else:
        ioenc = None
        if hasattr(sys.stdout, 'encoding'):
            ioenc = sys.stdout.encoding
        if ioenc is None:
            try:
                ioenc = locale.getpreferredencoding()
            except Exception:
                pass  # work around <http://bugs.python.org/issue1443504>
        io_encoding = _canonical_encoding(ioenc)

    _check_encoding(io_encoding)
    return io_encoding
