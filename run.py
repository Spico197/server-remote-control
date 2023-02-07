import json
import logging
import argparse

from backend.interfaces import API_MAP


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server_run")


def get_args():
    parser = argparse.ArgumentParser("Control servers in a convenient way")
    parser.add_argument(
        "method",
        choices=(
            "get_power_status",
            "power_on",
            "power_off",
            "power_reset",
            "ssh_ping",
            "get_gpu_num",
        ),
    )
    parser.add_argument("-c", "--config-filepath", default="conf/server.json")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    servers = json.load(open(args.config_filepath, "rt"))
    for server in servers:
        memo = server.pop("memo")
        manage_type = server.pop("manage_type")
        api = API_MAP[manage_type](**server)
        _method = getattr(api, args.method)
        try:
            res = _method()
            logger.info(f"server: {server['ssh_ip']}, action: {args.method}, result: {res}")
        except Exception as err:
            logger.error(f"server: {server['ssh_ip']}, action: {args.method}, err: {type(err)}, memo: {memo}")


if __name__ == "__main__":
    main()
