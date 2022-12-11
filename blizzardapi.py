import os
from colorama import Fore
import requests



def auth():
    """Get an access token from Blizzard
    Required environment variables:
        BLIZZARD_API_ID
        BLIZZARD_API_SECRET
    Optional environment variables:
        BLIZZARD_API_REGION (defaults to "eu")"""
    print("Getting Access Token from Blizzard")
    r = requests.post(
        f"https://{os.environ.get('BLIZZARD_API_REGION', 'eu')}.battle.net/oauth/token",
        data={
            "grant_type": "client_credentials",
        },
        auth=(os.environ.get('BLIZZARD_API_ID'), os.environ.get('BLIZZARD_API_SECRET')),
    )
    return r.json()["access_token"]


def fetch_itemname(itemid, access_token):
    r = requests.get(
        "https://us.api.blizzard.com/data/wow/item/"
        + itemid
        + "?namespace=static-us&locale=en_us&access_token="
        + access_token
    )
    try:
        item_name = r.json()["name"]
        print(f"\t\t{Fore.GREEN}Found Item in API: {itemid} {item_name}{Fore.RESET}")
        return item_name
    except KeyError as e:
        print(
            f"\t\t{Fore.RED}KeyError at ID {itemid}: {e}\t||\tJSON: {r.text}{Fore.RESET}"
        )
        return "ERROR1"
    except requests.JSONDecodeError as e:
        print(
            f"\t\t{Fore.RED}JSONDecodeError at ID {itemid}: {e}\t||\tJSON: {r.text}{Fore.RESET}"
        )
        return "ERROR2"
