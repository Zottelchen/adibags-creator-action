# AdiBags Creator (by Zottelchen)

## What does it do?

It takes item IDs from lists in /items and creates an AdiBags Plugin from that. Just put your Blizzard API credentials into system variables BLIZZ_ID and BLIZZ_SECRET and run create.py.

## Environment Variables

* BLIZZARD_API_ID: Your Blizzard API ID
* BLIZZARD_API_SECRET: Your Blizzard API Secret
* BLIZZARD_API_REGION: Your Blizzard API Region (default: eu), only relevant for authentication
* GITHUB_GIST_ID: The GIST ID which contains item names (defaults to "[b86d83d7b11377fb4a143d9cb12aef64](https://gist.github.com/Zottelchen/b86d83d7b11377fb4a143d9cb12aef64)")
* GITHUB_TOKEN: Your GitHub Token for adding item names to the cache - not needed, the cache is read-only by default. Only use, if you setup your own item name cache.


* ADDON_VARIANT: The name/variant of the addon
* ADDON_COLOR: The color of the addon in the AdiBags Menu
* TOC_VERSION: The version of the addon

* CURSE_ID: The CurseForge Project ID
* WOW_INTERFACE_ID: The WoWInterface Project ID
* WAGO_ID: The Wago Project ID

* DEBUG: Set to 1 to disable fetching of item names

## ID Lists

The ID lists may contain some special symbols:

* \# - defines a comment for the generated Markdown file
* ! - defines a description for the AdiBags filter
* $ - defines a hex color for the AdiBags category
* \* - defines an override method to check against
* & - defines an additional method to check in addition to item ID (needs to return false)