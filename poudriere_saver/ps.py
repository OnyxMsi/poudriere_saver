import argparse
import sys
import subprocess
import os
from poudriere_saver import api
import logging.config
import yaml


LOGGER = logging.getLogger("pty")
LOGLEVELS = (logging.WARNING, logging.INFO, logging.DEBUG)


def get_lvl_from_int(value):
    return LOGLEVELS[min(len(LOGLEVELS) - 1, max(value, 0))]


def configure_logger(args):
    data = {
        "version": 1,
        "formatters": {
            "formatter": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "formatter",
            }
        },
        "loggers": {
            "pty": {"handlers": ["console"], "level": get_lvl_from_int(args.verbose)},
            "pty.parser": {
                "handlers": ["console"],
                "level": get_lvl_from_int(args.verbose - 1),
            },
        },
    }
    logging.config.dictConfig(data)


def parse_args():
    parser = argparse.ArgumentParser("poudsaver")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    subparsers = parser.add_subparsers(required=True, dest="command")
    to_yaml_parser = subparsers.add_parser("export")
    to_yaml_parser.add_argument("directory", help="Directory to read")
    to_yaml_parser.add_argument("configuration", help="File to generate")
    to_yaml_parser.add_argument("set", help="Sets", type=str, nargs="+")
    to_yaml_parser.set_defaults(func=export)
    to_directory_parser = subparsers.add_parser("import")
    to_directory_parser.add_argument("directory", help="Directory to create")
    to_directory_parser.add_argument("configuration", help="Configuration to read")
    to_directory_parser.set_defaults(func=_import)
    clean_parser = subparsers.add_parser("clean")
    clean_parser.add_argument("directory", help="Directory to clean in")
    clean_parser.set_defaults(func=clean)
    args = parser.parse_args()
    return args


def poudriere_command(cmd):
    final_cmd = ("poudriere", "-N") + tuple(cmd.split())
    process = subprocess.run(
        final_cmd, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE, encoding="utf-8"
    )
    lines = process.stdout.splitlines()
    # Drop first line
    for line in lines[1:]:
        yield tuple(line.split())


def get_poudriere_jails():
    for columns in poudriere_command("jail -l"):
        yield api.Jail(columns[0], columns[1], columns[2])


def get_poudriere_ports():
    for columns in poudriere_command("ports -l"):
        yield api.Port(columns[0], columns[4])


def _import(args):
    LOGGER.debug("Generate from %s to directory %s", args.configuration, args.directory)
    with open(args.configuration) as conf_fd:
        conf = yaml.load(conf_fd, Loader=yaml.FullLoader)
    api.write_options(conf["options"], args.directory)
    api.write_make_conf(conf["make"], args.directory)
    return 0


def export(args):
    LOGGER.info("Generate %s from directory %s", args.configuration, args.directory)
    if not os.path.isdir(args.directory):
        LOGGER.error("%s : no such directory", args.directory)
        return 1
    jails = tuple(get_poudriere_jails())
    ports = tuple(get_poudriere_ports())
    conf = {
        "make": api.load_make_conf_files(args.directory, jails, ports, args.set),
        "options": api.load_options(args.directory, jails, ports, args.set),
    }
    LOGGER.debug("Write into %s", args.configuration)
    with open(args.configuration, "w") as fd:
        fd.write(yaml.dump(conf))
    return 0


def clean(args):
    LOGGER.info("Clean configuration in %s", args.directory)
    if not os.path.isdir(args.directory):
        LOGGER.error("%s : no such directory", args.directory)
        return 1
    api.clean_directory(args.directory)
    return 0


def main():
    args = parse_args()
    configure_logger(args)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
