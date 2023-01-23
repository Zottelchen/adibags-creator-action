import os
import tomllib

from colorama import Fore

import blizzardapi
from helper import T, color_setgets, Helper


class AdiBagsAddon:
    def __init__(self, config_file_path: str, access_token: str, itemname_cache: dict):
        with open(config_file_path, "rb") as f:
            config = tomllib.load(f)
        self.filter_name = config["filter_name"]
        self.replacers = config["replacers"]  # key: string to replace, value: replacement
        self.prefixes = config["prefixes"]
        self._add_default_replacers(config)
        self.access_token = access_token
        self.itemname_cache = itemname_cache
        self.categories = set()
        self.lang = set()
        self._getforms({"main.lua": None, "toc.toc": None, "locale.lua": None})

    def get_item_name(self, itemid: int | str) -> str:
        itemid = str(itemid)
        if self.access_token == "DEBUG":
            return ""
        if self.itemname_cache is None:
            self.itemname_cache = {}
        if itemid in self.itemname_cache:  # Check if we have the name cached
            item_name = self.itemname_cache[itemid]
            print(f"{T(2)}{Fore.CYAN}Found Item in Item Cache: {itemid} ➡ {item_name}{Fore.RESET}")
            return item_name
        else:
            item_name = blizzardapi.fetch_itemname(itemid, self.access_token)
            self.itemname_cache[itemid] = item_name
        return item_name

    def add_category(self, config_file_path):
        category = AdiBagsCategory(config_file_path)
        self.categories.add(category)
        print(f"\n{category}")

    def build(self):
        print("Building AdiBags Addon.")
        print("Building Item Maps.")
        self._build_itemmaps()
        print("Building Partials.")
        self._getpartials()
        print("Saving Files.")
        self._save_files()

    def _build_itemmaps(self):
        all_items = {}
        for category in self.categories:
            for subcategory in category.subcategories:
                print(f"Getting Names for: {Fore.YELLOW}{category.name}/{subcategory.name}{Fore.RESET}")
                for item_id in subcategory.item_ids:
                    item_name = self.get_item_name(item_id)
                    subcategory.item_map[item_id] = item_name
                    if f"{item_id}/{item_name}" in all_items:
                        all_items[f"{item_id}/{item_name}"].append(f"{category.name}/{subcategory.name}")
                        print(f"{T(2)}{Fore.YELLOW}Duplicate Item: {item_id}/{item_name} in categories: {str(all_items[f'{item_id}/{item_name}'])}{Fore.RESET}")
                    else:
                        all_items[f"{item_id}/{item_name}"] = [f"{category.name}/{subcategory.name}"]


    def _replace(self, text: str, skip_translation: bool = False) -> str:
        for key in self.replacers:
            if not skip_translation:
                if f"L.REPLACE.{key}" in text:
                    text = text.replace(f"L.REPLACE.{key}", self.L(str(self.replacers[key])))
            text = text.replace(f"%{key}%", str(self.replacers[key]))
        return text

    def _save_files(self):
        # TOC
        print("Creating TOC file.")
        str_toc = self._replace(self.forms["toc.toc"])
        with open(f"out/AdiBags_{self.filter_name}.toc", "w", encoding="utf8") as f:
            f.write(str_toc)

        # Main Addon
        print("Creating Main Addon file.")
        str_main = self.forms["main.lua"]
        for partial in self.partials.keys():
            str_main = str_main.replace(f"--!!{partial}!!--", self.partials[partial])
        str_main = self._replace(str_main)

        with open(f"out/AdiBags_{self.filter_name}.lua", "w", encoding="utf8") as f:
            f.write(str_main)

        # Markdown
        print("Creating Markdown file.")
        str_md = "# How to Read this\n\nAll items are broken down into categories, with itemID followed by the Item name.\n\nLatest version: @project-version@\n\n"
        for category in sorted(self.categories):
            str_md += f"## {category.name}\n\n{category.markdown_description_overwrite or category.description}\n\n" \
                      f"Default Color: ![{category.color:06x}](https://via.placeholder.com/16/{category.color:06x}/{''.join(['{:x}'.format(15 - int(c, 16)) if c.isalnum() else c for c in str(f'{category.color:06x}')])}?text={category.color:06x})\n\n"
            for subcategory in sorted(category.subcategories):
                str_md += f"### {subcategory.name}\n\n{subcategory.markdown_description_overwrite or subcategory.description}\n\n" \
                          f"Default Color: ![{subcategory.color:06x}](https://via.placeholder.com/16/{subcategory.color:06x}/{''.join(['{:x}'.format(15 - int(c, 16)) if c.isalnum() else c for c in str(f'{subcategory.color:06x}')])}?text={subcategory.color:06x})\n\n"
                if subcategory.bonus_condition:
                    str_md += f"**Bonus Condition, which has to return false:** `{subcategory.bonus_condition}`\n\n"
                if subcategory.override_method:
                    str_md += f"**Override Method, which has to return true:** `{subcategory.override_method}`\n\n"
                for item_id in sorted(subcategory.item_map.keys()):
                    str_md += f"* {item_id} - {subcategory.item_map[item_id]}\n"
                str_md += "\n"
        with open("out/supported_items.md", "w", encoding="utf8") as f:
            f.write(str_md)

        with open("out/Localization.lua", "w", encoding="utf8") as f:
            str_locale = self.forms["locale.lua"]
            list_locale = ""
            print(f"{len(self.lang)} language strings detected. Make sure to put them on CurseForge!")
            for key in sorted(list(self.lang)):
                list_locale += f'L["{key}"] = true\n'
            str_locale = str_locale.replace("--!!BaseTranslation!!--", list_locale)
            str_locale = self._replace(str_locale, skip_translation=True)
            f.write(str_locale)

    def L(self, lang: str):
        self.lang.add(lang)
        return f"L['{lang}']"

    def _getpartials(self):
        self.partials = {"MatchIDs": "", "Matching": "", "DefaultOptions": "", "Prefixes": "", "ConfigMenu": "", "DefaultColors": ""}
        H = Helper()

        # Prefixes are defined on an addon base
        for prefix in self.prefixes:
            if prefix.startswith("icon:"):
                prefix = prefix.replace("icon:", "")
                self.partials["Prefixes"] += f'{T(6)}["|T{prefix}:" .. AdiBags.HEADER_SIZE .. ":" .. AdiBags.HEADER_SIZE .. ":-2:-10|t"] = "|T{prefix}:" .. AdiBags.HEADER_SIZE .. "|t",\n'
            else:
                self.partials["Prefixes"] += f'{T(6)}["{prefix}"] = "{prefix}",\n'

        # Working through the categories
        for category in sorted(self.categories):

            self.partials["ConfigMenu"] += (f'{T(2)}{category.simple_name}_config = {{\n'
                                            f'{T(3)}type = "group",\n'
                                            f'{T(3)}name = {self.L(category.name)},\n'
                                            f'{T(3)}desc = "", -- doesnt work,\n'
                                            f'{T(3)}inline = true,\n'
                                            f'{T(3)}order = {H.order()},\n'
                                            f'{T(3)}args = {{\n')
            self.partials["ConfigMenu"] += (f'{T(4)}Legendaries_desc = {{\n'
                                            f'{T(5)}type = "description",\n'
                                            f'{T(5)}name = {self.L(category.addon_description_overwrite or category.description)},\n'
                                            f'{T(5)}order = {H.order()},\n'
                                            f'{T(4)}}},\n')

            if category.mergeable:
                self.partials["DefaultOptions"] += f"{T(3)}moveMerged{category.simple_name} = {str(category.merged_by_default).lower()},\n"
                self.partials["DefaultColors"] += f'{T(4)}merged{category.simple_name} = converttorgb("{category.color:06x}", true),\n'
                self.partials["ConfigMenu"] += (f'{T(4)}moveMerged{category.simple_name} = {{\n'
                                                f'{T(5)}name = string.format({self.L("%sMerge %s%s")}, "|cffffd800", {self.L(category.name)}, "|r"),\n'
                                                f'{T(5)}desc = string.format({self.L("Merge all %s into a single category.")}, {self.L(category.name)}),\n'
                                                f'{T(5)}type = "toggle",\n'
                                                f'{T(5)}width = 1.5,\n'
                                                f'{T(5)}order = {H.order()}\n'
                                                f'{T(4)}}},\n')
                self.partials["ConfigMenu"] += (f'{T(4)}colorMerged{category.simple_name} = {{\n'
                                                f'{T(5)}name = {self.L("Color")},\n'
                                                f'{T(5)}desc = string.format({self.L("Select a color for the merged %s category.")}, {self.L(category.name)}),\n'
                                                f'{T(5)}type = "color",\n'
                                                f'{T(5)}order = {H.order()},\n'
                                                f'{T(5)}hasAlpha = false,\n'
                                                f'{T(5)}disabled = function() return not self.db.profile.moveMerged{category.simple_name} end,\n'
                                                f'{color_setgets(f"merged{category.simple_name}")}\n{T(4)}}},\n')
                self.partials["ConfigMenu"] += f'{H.seperator()}'

                subcategory_filters = ""
                for subcategory in sorted(category.subcategories):
                    subcategory_filters += f'{subcategory.simple_name}_IDs, '
                subcategory_filters = f'{"_IDs, ".join(sorted(category.subcategory_names)[:-1])}_IDs, {sorted(category.subcategory_names)[-1]}_IDs'
                self.partials["Matching"] += f'\n\tif self.db.profile.moveMerged{category.simple_name} then\n' \
                                             f'{T(2)}Result[formatBagTitle(self, {self.L(category.name)}, converttohex(self.db.profile.color.merged{category.simple_name}))] = AddToSet({subcategory_filters})\n' \
                                             f'\telse\n'

            for i, subcategory in enumerate(sorted(category.subcategories)):
                # List of IDs
                self.partials["MatchIDs"] += f"-- {subcategory.name}\nlocal {subcategory.simple_name}_IDs = {{\n"
                for item in sorted(subcategory.item_map.keys()):
                    self.partials["MatchIDs"] += f"{item}, -- {subcategory.item_map[item]}\n"
                self.partials["MatchIDs"] += "}\n\n"

                # Actual Matching
                self.partials["Matching"] += f'\n\tif self.db.profile.move{subcategory.simple_name} then\n' \
                                             f'{T(2)}Result[formatBagTitle(self, {self.L(subcategory.name)}, converttohex(self.db.profile.color.{subcategory.simple_name}))] = AddToSet({subcategory.simple_name}_IDs)\n'
                if subcategory.bonus_condition:
                    self.partials["Matching"] += f'{T(2)}Result[formatBagTitle(self, {self.L(subcategory.name)}, converttohex(self.db.profile.color.{subcategory.simple_name}))]["bonus_condition"] = {subcategory.bonus_condition}\n'
                if subcategory.override_method:
                    self.partials["Matching"] += f'{T(2)}Result[formatBagTitle(self, {self.L(subcategory.name)}, converttohex(self.db.profile.color.{subcategory.simple_name}))]["override"] = {subcategory.override_method}\n'
                self.partials["Matching"] += f'\tend'
                # Default Options
                self.partials["DefaultOptions"] += f"{T(3)}move{subcategory.simple_name} = {str(subcategory.enabled_by_default).lower()},\n"
                self.partials["DefaultColors"] += f'{T(4)}{subcategory.simple_name} = converttorgb("{subcategory.color:06x}", true),\n'
                # Config Menu
                self.partials["ConfigMenu"] += (f'{T(4)}move{subcategory.simple_name} = {{\n'
                                                f'{T(5)}name = {self.L(subcategory.name)},\n'
                                                f'{T(5)}desc = {self.L(subcategory.addon_description_overwrite or subcategory.description)},\n'
                                                f'{T(5)}type = "toggle",\n'
                                                f'{T(5)}width = 1.5,\n'
                                                f'{T(5)}order = {H.order()},\n'
                                                f'{f"{T(5)}disabled = function() return self.db.profile.moveMerged{category.simple_name} end" if category.mergeable else ""}'
                                                f'\n{T(4)}}},\n')
                self.partials["ConfigMenu"] += (f'{T(4)}color{subcategory.simple_name} = {{\n'
                                                f'{T(5)}name = {self.L("Color")},\n'
                                                f'{T(5)}desc = string.format({self.L("Select a color for %s.")}, {self.L(subcategory.name)}),\n'
                                                f'{T(5)}type = "color",\n'
                                                f'{T(5)}order = {H.order()},\n'
                                                f'{T(5)}disabled = function() return self.db.profile.moveMerged{category.simple_name} end,\n'
                                                f'{color_setgets(subcategory.simple_name)}\n{T(4)}}},\n')

                if i != len(category.subcategories) - 1:
                    self.partials["ConfigMenu"] += f'{H.seperator()}'

            # Close the category
            self.partials["ConfigMenu"] += f'{T(3)}}},\n{T(2)}}},\n'
            if category.mergeable:
                self.partials["Matching"] += "\n\tend"

        if os.environ.get("DEBUG") == "1":
            print(f"{Fore.RED}### DEBUG ###{Fore.RESET}")
            print(f"{Fore.BLUE}{self.partials['MatchIDs']}")
            print(f"{Fore.YELLOW}{self.partials['Matching']}")
            print(f"{Fore.GREEN}{self.partials['DefaultOptions']}")
            print(f"{Fore.MAGENTA}{self.partials['Prefixes']}")
            print(f"{Fore.CYAN}{self.partials['ConfigMenu']}")
            print(f"{Fore.BLACK}{self.partials['DefaultColors']}")
            print(f"{Fore.RED}### DEBUG ###{Fore.RESET}")

    def _getforms(self, forms: dict):
        self.forms = forms
        for form in self.forms.keys():
            with open(f"forms/{form}", "r", encoding="utf8") as f:
                self.forms[form] = f.read()

    def _add_default_replacers(self, config: dict):
        self.replacers["FILTER_NAME"] = self.filter_name
        self.replacers["FILTER_DESCRIPTION"] = config["filter_description"]
        self.replacers["FILTER_AUTHOR"] = config["filter_author"]
        self.replacers["ADDON_COLOR"] = f"{self.replacers['ADDON_COLOR']:06x}"


class AdiBagsCategory:
    def __init__(self, config_file_path: str):
        self.subcategories = set()
        with open(config_file_path, "rb") as f:
            config = tomllib.load(f)
        for key, value in config.items():
            if type(value) is dict and key != "category_description":
                self.subcategories.add(AdiBagsSubCategory(value))

        self.name = config["category_name"].replace("'", "\\'")
        self.simple_name = ''.join(e for e in self.name if e.isalnum())
        self.color = config["category_color"]
        description = config["category_description"]
        self.description = description.get("_", None).replace("'", "\\'")
        self.markdown_description_overwrite = description.get("markdown", None)
        self.addon_description_overwrite = description.get("addon", "").replace("'", "\\'")
        self.mergeable = config.get("mergeable", False)
        self.merged_by_default = config.get("merged_by_default", True)
        self.item_map = {}

    @property
    def item_ids(self):
        item_ids = set()
        for subcategory in self.subcategories:
            item_ids.update(subcategory.item_ids)
        return item_ids

    @property
    def subcategory_names(self):
        return [subcategory.simple_name for subcategory in self.subcategories]

    def __str__(self):
        return f"""Category '{self.name}' (with {len(self.subcategories)} subcategories) with a total of {len(self.item_ids)} items.
        Color: {hex(self.color)}
        Markdown Description: {self.markdown_description_overwrite or self.description}
        Addon Description: {self.addon_description_overwrite or self.description}
        Mergeable: {self.mergeable} / Merged by default: {self.merged_by_default}
        """

    def __lt__(self, other):
        return self.name < other.name


class AdiBagsSubCategory:
    def __init__(self, subcategory_config: dict):
        self.name = subcategory_config["name"].replace("'", "\\'")
        self.simple_name = ''.join(e for e in self.name if e.isalnum())
        self.color = subcategory_config["color"]
        self.enabled_by_default = subcategory_config.get("enabled_by_default", True)
        description = subcategory_config["description"]
        self.description = description.get("_", None).replace("'", "\\'")
        self.markdown_description_overwrite = description.get("markdown", None)
        self.addon_description_overwrite = description.get("addon", "").replace("'", "\\'")
        self.item_ids = set(subcategory_config.get("items", []))
        self.item_map = {}
        self.bonus_condition = subcategory_config.get("bonus_condition", False)
        self.override_method = subcategory_config.get("override_method", False)

    def __str__(self):
        return f"""SubCategory '{self.name}' with {len(self.item_ids)} items.
        Color: {hex(self.color)}
        enabled_by_default: {self.enabled_by_default}
        Markdown Description: {self.markdown_description_overwrite or self.description}
        Addon Description: {self.addon_description_overwrite or self.description}
        Bonus Condition: {self.bonus_condition}
        Override Method: {self.override_method}
        """

    def __lt__(self, other):
        return self.name < other.name
