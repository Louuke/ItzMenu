import argparse

from itzmenu_extractor.jobs import Executor


def main():
    parser = argparse.ArgumentParser(description='ItzMenuExtractor')
    parser.add_argument('--preload', '-p', type=lambda s: [item for item in s.split(',')], default=[],
                        help='detect and save menus from images')
    parser.add_argument('--log',  '-l', type=str, default='info', help='log level')
    executor = Executor(parser.parse_args())
    executor.start()


if __name__ == '__main__':
    main()
