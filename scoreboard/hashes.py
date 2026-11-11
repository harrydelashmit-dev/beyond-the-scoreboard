"""Portable hashes for versioned text; binary source hashes remain byte-exact."""
import hashlib


def text_sha256(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
