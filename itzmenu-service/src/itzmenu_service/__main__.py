import uvicorn
import argparse


def main():
    parser = argparse.ArgumentParser(description='ItzMenu Service')
    parser.add_argument('-port',  '-p', type=int, default=8000, help='port to run the service on')
    parser.add_argument('-host',  '-ht', type=str, default='127.0.0.1', help='host to run the service on')
    parser.add_argument('-log',  '-l', type=str, default='info', help='log level')
    args = parser.parse_args()
    uvicorn.run('itzmenu_service.app:app', host=args.host, port=args.port, log_level=args.log)


if __name__ == '__main__':
    main()
