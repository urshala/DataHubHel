import argparse
import logging
import sys

from . import initialize_services, open311_consumer, sample_producer

COMMAND_MAP = {
    "init": initialize_services.main,
    "produce-sample-data": sample_producer.produce_sample_data,
    "consume-open311": open311_consumer.listen_open311,
}


def main(argv=sys.argv):
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    func = COMMAND_MAP[args.command]
    func()


def parse_args(argv):
    parser = argparse.ArgumentParser(prog=argv[0])
    subparsers = parser.add_subparsers(
        title="command", dest="command", required=True
    )
    for (name, module) in COMMAND_MAP.items():
        subparsers.add_parser(name)
    return parser.parse_args(argv[1:])


if __name__ == "__main__":
    main()
