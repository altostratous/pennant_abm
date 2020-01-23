from arabic_reshaper import reshape as _reshape


def reshape(s):
    return ''.join(reversed(_reshape(s)))