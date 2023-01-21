--[[
AdiBags - %FILTER_NAME% - Localization
by %FILTER_AUTHOR%
version: @project-version@
This file contains translations for this filter.
]]
local addonName, addon = ...

--<GLOBALS
local _G = _G
local GetLocale = _G.GetLocale
local pairs = _G.pairs
local rawset = _G.rawset
local setmetatable = _G.setmetatable
local tostring = _G.tostring
--GLOBALS>

local L = setmetatable({}, {
    __index = function(self, key)
        if key ~= nil then
            --@do-not-package@
            print(string.format('Missing translation for L["%s"]', key))
            --@end-do-not-package@
            rawset(self, key, tostring(key))
        end
        return tostring(key)
    end,
})
addon.L = L

L["AdiBags never intended to use icons, so they are glitchy. Make sure to disable prefix color, if you use an icon."] = true
L["Colored Categories"] = true
L["Colored Prefix"] = true
L["Custom Prefix"] = true
L["Enter a custom prefix for the categories."] = true
L["Filter version"] = true
L["General Settings"] = true
L["If you overwrite prefix or categorie color, you either need to toggle the color setting twice or reload."] = true
L["None"] = true
L["Prefix Categories"] = true
L["Prefix Color"] = true
L["Select a color for the prefix."] = true
L["Select a prefix for the categories, if you like."] = true
L["Settings affecting all categories."] = true
L["Should Categories be colored?"] = true
L["Should the prefix be colored to the filter color? (Only works for text-prefixes, for obvious reasons.)"] = true
L["These settings affect all categories of this filter."] = true
--
--!!BaseTranslation!!--

local locale = GetLocale()
if locale == 'frFR' then
    --@localization(locale="frFR", format="lua_additive_table", handle-unlocalized="blank")@
elseif locale == 'deDE' then
    --@localization(locale="deDE", format="lua_additive_table", handle-unlocalized="blank")@
elseif locale == 'ruRU' then
    --@localization(locale="ruRU", format="lua_additive_table", handle-unlocalized="blank")@
elseif locale == 'esES' then
    --@localization(locale="esES", format="lua_additive_table", handle-unlocalized="blank")@
elseif locale == 'zhTW' then
    --@localization(locale="zhTW", format="lua_additive_table", handle-unlocalized="blank")@
elseif locale == 'zhCN' then
    --@localization(locale="zhCN", format="lua_additive_table", handle-unlocalized="blank")@
elseif locale == 'koKR' then
    --@localization(locale="koKR", format="lua_additive_table", handle-unlocalized="blank")@
elseif locale == 'ptBR' then
    --@localization(locale="ptBR", format="lua_additive_table", handle-unlocalized="blank")@
elseif locale == 'itIT' then
    --@localization(locale="itIT", format="lua_additive_table", handle-unlocalized="blank")@
end

for k, v in pairs(L) do
    if v == true then
        L[k] = k
    end
end