import os
import sys
from glob import glob
from json import JSONDecodeError
from pathlib import Path
from colorama import Fore
import requests

import blizzardapi
import github
from adibags import *

SIGN_REPLACER = {"➡": "{", "⬅": "}", "↔": "{}"}
OUTDIR = "out/"


def main():
    access_token = "DEBUG"
    if os.environ.get("DEBUG") != "1":
        access_token = blizzardapi.auth()
    addon = AdiBagsAddon(config_file_path="items/_addon.toml", access_token=access_token, itemname_cache=github.get_gist())
    print(f"{Fore.YELLOW}Detecting categories.{Fore.RESET}")
    for idfile in glob("items/*.toml"):
        if "_addon.toml" in idfile:
            continue
        print(f"{Fore.LIGHTBLACK_EX}{idfile}{Fore.RESET}")
        addon.add_category(idfile)
    addon.build()

    github.update_gist(addon.itemname_cache)


def create_markdown(itemdict):
    print("Creating Markdown file.")
    str_markdown = "# How to Read this\n\nAll items are broken down into categories, with itemID followed by the Item name.\n\nLatest version: @project-version@\n\n"
    for key in itemdict:
        post_title = ""
        if itemdict[key]["disabled_by_default"]:
            post_title = "(Disabled by default)"
        str_markdown += "## {} {}\n\n".format(key, post_title)
        if itemdict[key]["comment"] != "":
            str_markdown += itemdict[key]["comment"] + "\n\n"
        for i in itemdict[key]["items"]:
            str_markdown += " * {} - {}\n".format(i["id"], i["name"])
        str_markdown += "\n"
        with open(OUTDIR + "addon_supported_items.md", "w", encoding="utf8") as f:
            f.write(str_markdown)


# TODO: implement this into adibags.py
#
#         if itemdict[key]["bonus_condition"] != "":
#             filter_addition = '\n\t\t\tResult["{0}"]["bonus_condition"] = true\n\t\t\tResult["{0}"]["bonus_condition_method"] = {1}'.format(
#                 colorkey, itemdict[key]["bonus_condition"]
#             )
#             filter_addition_colorless = '\n\t\t\tResult[unescape("{0}")]["bonus_condition"] = true\n\t\t\tResult[unescape("{0}")]["bonus_condition_method"] = {1}'.format(
#                 colorkey, itemdict[key]["bonus_condition"]
#             )
#         elif itemdict[key]["override_method"] != "":
#             filter_addition = '\n\t\t\tResult["{0}"]["override"] = true\n\t\t\tResult["{0}"]["override_method"] = {1}'.format(
#                 colorkey, itemdict[key]["override_method"]
#             )
#             filter_addition_colorless = '\n\t\t\tResult[unescape("{0}")]["override"] = true\n\t\t\tResult[unescape("{0}")]["override_method"] = {1}'.format(
#                 colorkey, itemdict[key]["override_method"]
#             )
#
#         filters += '\tif self.db.profile.{0} then\n\t\tif self.db.profile.showcoloredCategories then\n\t\t\tResult["{1}"] = AddToSet({2}){3}\n\t\telse\n\t\t\tResult[unescape("{1}")] = AddToSet({2}){4}\n\t\tend\n\tend\n\n'.format(
#             "move" + key_clean,
#             colorkey,
#             key_clean + "IDs",
#             filter_addition,
#             filter_addition_colorless,
#         )



if __name__ == "__main__":
    main()
