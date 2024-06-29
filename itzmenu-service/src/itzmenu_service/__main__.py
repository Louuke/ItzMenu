import uvicorn
import argparse

from itzmenu_service.config.settings import Settings


def main():
    parser = argparse.ArgumentParser(description='ItzMenu Service')
    for name, field in Settings.__fields__.items():
        parser.add_argument(
            f"--{name}",
            dest=name,
            type=field.annotation,
            default=field.default,
            help=field.description,
        )
    args = parser.parse_args()
    uvicorn.run('itzmenu_service.app:app', host=args.service_host, port=args.service_port, log_level=args.log)


if __name__ == '__main__':
    main()
