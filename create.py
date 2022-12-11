import os
import sys
from glob import glob
from json import JSONDecodeError
from pathlib import Path
from colorama import Fore
import requests

import blizzardapi
import github

REPLACERS = {
    "%ADDON_VARIANT%": os.environ.get("ADDON_VARIANT"),
    "%ADDON_COLOR%": os.environ.get("ADDON_COLOR"),
    "%TOC_VERSION%": os.environ.get("TOC_VERSION"),
    "%CURSE_ID%": os.environ.get("CURSE_ID"),
    "%WOW_INTERFACE_ID%": os.environ.get("WOW_INTERFACE_ID"),
    "%WAGO_ID%": os.environ.get("WAGO_ID"),
}
SIGN_REPLACER = {"➡": "{", "⬅": "}", "↔": "{}"}
OUTDIR = "out/"


def main():
    all_item_dict = {}
    access_token = "DEBUG"
    if os.environ.get("DEBUG") != "1":
        access_token = blizzardapi.auth()
    itemname_cache = github.get_gist()
    for idfile in glob("items/*.txt"):
        groupname = Path(idfile).stem
        disabled = False
        if "#" in groupname:
            disabled = True
            groupname = groupname.replace("#", "")
        group = {
            "disabled_by_default": disabled,
            "comment": "",
            "adibagsdesc": "",
            "adibagscolor": "",
            "bonus_condition": "",
            "override_method": "",
        }
        items = []
        with open(idfile, "r") as f:
            print("Getting Names for:", groupname)
            for line in f:
                if "#" in line:
                    group["comment"] = line.strip().replace("#", "")
                    print("\tFound Markdown Comment:", group["comment"])
                elif "!" in line:
                    group["adibagsdesc"] = (
                        line.strip().replace("!", "").replace('"', "'")
                    )
                    print("\tFound AdiBags Description:", group["adibagsdesc"])
                elif "$" in line:
                    group["adibagscolor"] = "ff" + line.strip().replace("$", "").lower()
                    print("\tFound AdiBags Color:", group["adibagscolor"])
                elif "&" in line:
                    group["bonus_condition"] = line.strip().replace("&", "")
                    print("\tFound Bonus Condition:", group["bonus_condition"])
                elif "*" in line:
                    group["override_method"] = line.strip().replace("*", "")
                    print("\tFound Override Method:", group["override_method"])
                else:
                    itemname, itemname_cache = get_item_name(line.strip(), access_token, itemname_cache)
                    items.append(
                        {
                            "id": line.strip(),
                            "name": itemname,
                        }
                    )
        group["items"] = items
        all_item_dict[groupname] = group

    github.update_gist(itemname_cache)
    create_markdown(all_item_dict)
    create_lua(all_item_dict)
    create_toc()


def get_item_name(itemid, access_token: str, itemname_cache: dict = None) -> (str, dict):
    if access_token == "DEBUG":
        return ""
    if itemname_cache is None:
        itemname_cache = {}
    if itemid in itemname_cache:  # Check if we have the name cached
        item_name = itemname_cache[itemid]
        print(f"\t\t{Fore.CYAN}Found Item in Item Cache:  {itemid} {item_name}{Fore.RESET}")
        return item_name, itemname_cache
    else:
        item_name = blizzardapi.fetch_itemname(itemid, access_token)
        itemname_cache[itemid] = item_name
    return item_name, itemname_cache


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


def create_lua(itemdict):
    print("Creating LUA file.")
    itemlist, profiledefaults, filters, settings = "", "", "", ""
    order_counter = 0
    for key in itemdict:
        key_clean = key.replace(" ", "").replace("'", "").replace("-", "")

        # ITEM LISTE
        itemlist += "\n -- {}\nlocal {} = ➡".format(key, key_clean + "IDs")
        for i in itemdict[key]["items"]:
            itemlist += "\n{}, -- {}".format(i["id"], i["name"])
        itemlist += "\n}\n"

        # DEFAULT PROFIL
        enabled = "true"
        if itemdict[key]["disabled_by_default"]:
            enabled = "false"
        profiledefaults += "\n            {} = {},".format("move" + key_clean, enabled)

        # ADD TO FILTERS (MatchIDs)
        colorkey = key
        if itemdict[key]["adibagscolor"] != "":
            colorkey = "|c" + itemdict[key]["adibagscolor"] + key + "|r"

        filter_addition = ""  # i present to you: spaghetti
        filter_addition_colorless = ""
        if itemdict[key]["bonus_condition"] != "":
            filter_addition = '\n\t\t\tResult["{0}"]["bonus_condition"] = true\n\t\t\tResult["{0}"]["bonus_condition_method"] = {1}'.format(
                colorkey, itemdict[key]["bonus_condition"]
            )
            filter_addition_colorless = '\n\t\t\tResult[unescape("{0}")]["bonus_condition"] = true\n\t\t\tResult[unescape("{0}")]["bonus_condition_method"] = {1}'.format(
                colorkey, itemdict[key]["bonus_condition"]
            )
        elif itemdict[key]["override_method"] != "":
            filter_addition = '\n\t\t\tResult["{0}"]["override"] = true\n\t\t\tResult["{0}"]["override_method"] = {1}'.format(
                colorkey, itemdict[key]["override_method"]
            )
            filter_addition_colorless = '\n\t\t\tResult[unescape("{0}")]["override"] = true\n\t\t\tResult[unescape("{0}")]["override_method"] = {1}'.format(
                colorkey, itemdict[key]["override_method"]
            )

        filters += '\tif self.db.profile.{0} then\n\t\tif self.db.profile.showcoloredCategories then\n\t\t\tResult["{1}"] = AddToSet({2}){3}\n\t\telse\n\t\t\tResult[unescape("{1}")] = AddToSet({2}){4}\n\t\tend\n\tend\n\n'.format(
            "move" + key_clean,
            colorkey,
            key_clean + "IDs",
            filter_addition,
            filter_addition_colorless,
        )

        # SETTINGS SCREEN
        order_counter += 10
        settings += '\t\t{} = ➡\n\t\t\tname = "{}",\n\t\t\tdesc = "{}",\n\t\t\ttype = "toggle",\n\t\t\torder = {}\n\t\t⬅,\n\n'.format(
            "move" + key_clean, key, itemdict[key]["adibagsdesc"], order_counter
        )

    # CATEGORYCOLOR SETTING
    settings += '\t\t{} = ➡\n\t\t\tname = "{}",\n\t\t\tdesc = "{}",\n\t\t\ttype = "toggle",\n\t\t\torder = {}\n\t\t⬅,\n\n'.format(
        "showcoloredCategories",
        r"|cffff98abC|cffffa094o|cffffa77el|cffffaf67o|cfffebf71r|cfffecf7be|cfffddf85d|cffe0d988 |cffc3d38bC|cffa6cd8ea|cff9bccaet|cff8fcbcde|cff95bad2g|cff9aa9d7o|cffa098dcr|cffae98dci|cffbd98dce|cffcb98dcs|r",
        "Should Categories be colored?",
        order_counter + 10,
    )
    profiledefaults += "\n            {} = {},".format("showcoloredCategories", "true")
    # putting it all together
    str_lua = get_form("lua.lua")
    str_lua = mass_replace(str_lua, SIGN_REPLACER, reverse=True)
    str_lua = str_lua.replace("--!!PH", "{}")
    str_lua = mass_replace(str_lua, REPLACERS)
    str_lua = str_lua.format(itemlist, filters, profiledefaults, settings)
    str_lua = mass_replace(str_lua, SIGN_REPLACER)
    str_lua = str_lua.replace("\t", "    ")

    with open(
            OUTDIR + f"AdiBags_{REPLACERS['%ADDON_VARIANT%']}.lua", "w", encoding="utf8"
    ) as f:
        f.write(str_lua)


def create_toc():
    print("Creating TOC file.")
    str_toc = get_form("toc.toc")
    str_toc = mass_replace(str_toc, REPLACERS)
    with open(
            OUTDIR + f"AdiBags_{REPLACERS['%ADDON_VARIANT%']}.toc", "w", encoding="utf8"
    ) as f:
        f.write(str_toc)


def mass_replace(file_str: str, replacers: dict, reverse: bool = False) -> str:
    for key in replacers.keys():
        value = replacers[key]
        if not reverse:
            file_str = file_str.replace(key, value)
        else:
            file_str = file_str.replace(value, key)
    return file_str


def get_form(form):
    content = Path("forms/" + form).read_text(encoding="utf-8")
    return content


if __name__ == "__main__":
    main()
