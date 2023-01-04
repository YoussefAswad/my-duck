#!/usr/bin/python

from requests import request
from time import sleep
import os
import getopt
import sys
import traceback


def CheckConnection(host='http://google.com'):
    try:
        request("GET", host)  # Python 3.x
        return True
    except:
        return False


def ReadConfig(path):
    conf = {}
    try:
        with open(path) as fp:
            for line in fp:
                if line.startswith('#'):
                    continue
                key, val = line.strip().split('=', 1)
                conf[key] = val
        return conf
    except:
        return None


def ParseArgs():
    argument_list = sys.argv[1:]
    options = "hi:f:a:l"
    long_options = ["help", "interval=",
                    "file=", "account=", "config=", "loop"]
    config_args = {}
    try:
        arguments, values = getopt.getopt(argument_list, options, long_options)
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--help"):
                print("Help")  # TODO
                raise SystemExit(0)
            elif currentArgument in ("-i", "--interval"):
                config_args["INTERVAL"] = currentValue
                try:
                    int(currentValue)
                except ValueError:
                    print("option " + currentArgument + " requires an integer")
                    raise SystemExit(0)
            elif currentArgument in ("-f", "--file"):
                config_args["FILE"] = currentValue
            elif currentArgument in ("-a", "--account"):
                config_args["ACCOUNT"] = currentValue
            elif currentArgument in ("--config"):
                config_args["PATH"] = os.path.expanduser(currentValue)
            elif currentArgument in ("-l", "--loop"):
                config_args["LOOP"] = True
    except getopt.error as err:
        print(str(err))
        raise SystemExit(0)
    if "INTERVAL" in config_args and "LOOP" not in config_args:
        print("option -i/--interval can only be used with option -l/--loop")
        raise SystemExit(0)
    if "FILE" in config_args and "ACCOUNT" in config_args:
        print(
            "options -f/--file and -a/--account cannot be used together, please use only one")
        raise SystemExit(0)
    return config_args


def ReadAccount(file_path):
    account = ReadConfig(file_path)
    if account is None:
        print(os.path.basename(file_path) +
              " is not formatted properley or it does not exist")
    if "TOKEN" in account:
        if "DOMAINS" in account:
            return account
        else:
            print(os.path.basename(file_path) +
                  " does not contain a Domains field!")
            return None
    else:
        print(os.path.basename(file_path) + " does not contain a Token field!")
        return None


def ReadAccounts(config):
    account_path = config["PATH"] + "/accounts"
    accounts = []
    for file in os.listdir(account_path):
        if file.endswith(".conf"):
            account = ReadAccount(account_path + '/' + file)
            if (account is None):
                continue
            accounts.append(account)
    return accounts


def Update(accounts):
    for account in accounts:
        res = request(method='GET', url="https://www.duckdns.org/update?domains=" +
                      account["DOMAINS"] + "&token=" + account["TOKEN"] + "&ip=&verbose=true")
        res = res.content.decode("utf-8").split("\n")
        res = {
            "Success": True if res[0] == "OK" else False,
            "IPV4": res[1],
            "IPV6": res[2],
            "Changed": True if res[3] == "UPDATED" else False
        }
        if res["Success"]:
            print("Domain(s) " + account["DOMAINS"] +
                  (" of account " + account["EMAIL"] if "EMAIL" in account else "") + " were" + (" not" if not res["Changed"] else "") + " updated." + " Current IP:" + res["IPV4"])
        else:
            print("connection to duckdns.org failed!")


def CreateConfig():
    is_windows = True if os.name == 'nt' else False
    home = os.path.expanduser("~")

    config = {
        "INTERVAL": 600
    }
    # Determine appropriate config path
    # Parse arguments
    config_args = ParseArgs()
    if "PATH" in config_args:
        config["PATH"] = config_args["PATH"]
    else:
        if is_windows:
            config["PATH"] = home + "/AppData/Roaming/multi-duck"
        else:
            try:
                config["PATH"] = os.environ['XDG_CONFIG_HOME'] + "/multi-duck"
            except:
                config["PATH"] = home + '/.config/multi-duck'

    # Try reading config file
    try:
        config_file = ReadConfig(config["PATH"] + "/multi-duck.conf")
        # Apply values from config (if available)
        for key in config_file:
            if key in config:
                config[key] = config_file[key]
    except:
        print("no config file detected, using default vales")

    # Override with command line values
    for key in config_args:
        if key in config:
            config[key] = config_args[key]
    return config


def Loop(accounts, interval):
    while (True):
        if (CheckConnection()):
            Update(accounts)
        else:
            print("No Internet!")
        sleep(interval)


def SetAccount(config, config_args):
    if "FILE" in config_args:
        return [ReadAccount(os.path.expanduser(config_args["FILE"]))]
    elif "ACCOUNT" in config_args:
        return [ReadAccount(
            config["PATH"] + "/accounts/" + config_args["ACCOUNT"] + ".conf")]
    else:
        return ReadAccounts(config)


def Run(config_args):
    config = CreateConfig()
    # Check if any account if avialable
    config["ACCOUNTS"] = SetAccount(config, config_args)
    if "LOOP" in config_args:
        if (config["ACCOUNTS"]):
            print("Loop interval set to " +
                  str(config["INTERVAL"]) + " seconds.")
            Loop(config["ACCOUNTS"], int(config["INTERVAL"]))
        else:
            print(
                "no account configs were detected!. Try adding an account and try again")
    else:
        Update(config["ACCOUNTS"])


def main():
    try:
        Run(ParseArgs())
    except KeyboardInterrupt:
        print("Exiting")
    except Exception:
        traceback.print_exc(file=sys.stdout)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
