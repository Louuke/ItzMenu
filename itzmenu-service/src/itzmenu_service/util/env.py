import sys


def is_running_tests() -> bool:
    return 'pytest' in sys.modules or 'unittest' in sys.modules
