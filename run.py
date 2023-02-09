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
            "ssh_run",
            "get_gpu_process",
            "who",
        ),
        help="Operation to execute.",
    )
    parser.add_argument(
        "-c",
        "--config-filepath",
        default="conf/server.json",
        help="Server configurations, examples are in `conf/server.json.example`.",
    )
    parser.add_argument("-s", "--shell-command", help="Linux commands to execute.")
    parser.add_argument(
        "-i",
        "--ip",
        nargs="+",
        help=(
            "Default operation is applied across all servers, "
            "you may want to specify IP address to execute operation "
            "on certain servers. "
            "e.g. python run.py ssh_ping -i 192.168.1.2 192.168.1.3",
        ),
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    servers = json.load(open(args.config_filepath, "rt"))
    for server in servers:
        memo = server.pop("memo")
        manage_type = server.pop("manage_type")
        if args.ip and server["ssh_ip"] not in args.ip:
            continue
        api = API_MAP[manage_type](**server)
        _method = getattr(api, args.method)
        try:
            if args.method == "ssh_run":
                res = _method(args.shell_command)
            else:
                res = _method()
            logger.info(
                f"server: {server['ssh_ip']}, action: {args.method}, result: {res}"
            )
        except Exception as err:
            logger.error(
                f"server: {server['ssh_ip']}, action: {args.method}, err: {type(err)}, memo: {memo}"
            )


if __name__ == "__main__":
    main()
