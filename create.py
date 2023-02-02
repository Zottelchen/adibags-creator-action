import json
from glob import glob

import apprise

import github
from adibags import *


def main():
    access_token = "DEBUG"
    if os.environ.get("DEBUG") != "1":
        access_token = blizzardapi.auth()
    inital_item_cache = github.get_gist()
    addon = AdiBagsAddon(config_file_path="items/_addon.toml", access_token=access_token,
                         itemname_cache=dict(inital_item_cache))
    print(f"{Fore.YELLOW}Detecting categories.{Fore.RESET}")
    for idfile in glob("items/*.toml"):
        if "_addon.toml" in idfile:
            continue
        print(f"{Fore.LIGHTBLACK_EX}{idfile}{Fore.RESET}")
        addon.add_category(idfile)
    addon.build()

    if addon.itemname_cache != inital_item_cache:
        success = github.update_gist(addon.itemname_cache)
    else:
        print("Item Cache unchanged, skipping updating online item cache.")
        success = "The item cache did not change."

    with open("itemcache.json", "w") as f:
        json.dump(addon.itemname_cache, f, sort_keys=True, indent=2)

    with open("out/Localization.lua", "r") as f:
        localization = f.read()

    with open("locale.lua", "w") as f:
        for l in localization.split("\n"):  # this is a very cheap solution, but it works
            if l.startswith('L["'):
                f.write(l + "\n")

    if os.environ.get("APPRISE_ITEM_CACHE"):
        print("Sending item cache to Apprise service.")

        apobj = apprise.Apprise()
        apobj.add(os.environ.get("APPRISE_ITEM_CACHE"))
        apobj.notify(
            title=f"**Item Cache ({addon.filter_name})**",
            body=success,
            attach="itemcache.json",
        )

    if os.environ.get("APPRISE_ADDON_LOCALE"):
        print("Sending locale to Apprise service.")

        apobj = apprise.Apprise()
        apobj.add(os.environ.get("APPRISE_ADDON_LOCALE"))
        apobj.notify(
            title=f"**Locale (of {addon.filter_name})**",
            body="Here are the current strings to localize. Don't forget to upload these to Curseforge!",
            attach="locale.lua",
        )


if __name__ == "__main__":
    main()
