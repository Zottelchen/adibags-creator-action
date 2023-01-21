from glob import glob

import github
from adibags import *


def main():
    access_token = "DEBUG"
    if os.environ.get("DEBUG") != "1":
        access_token = blizzardapi.auth()
    inital_item_cache = github.get_gist()
    addon = AdiBagsAddon(config_file_path="items/_addon.toml", access_token=access_token, itemname_cache=dict(inital_item_cache))
    print(f"{Fore.YELLOW}Detecting categories.{Fore.RESET}")
    for idfile in glob("items/*.toml"):
        if "_addon.toml" in idfile:
            continue
        print(f"{Fore.LIGHTBLACK_EX}{idfile}{Fore.RESET}")
        addon.add_category(idfile)
    addon.build()

    if addon.itemname_cache != inital_item_cache:
        github.update_gist(addon.itemname_cache)
    else:
        print("Item Cache unchanged, skipping updating online item cache.")


if __name__ == "__main__":
    main()
