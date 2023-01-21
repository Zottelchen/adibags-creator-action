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
			rawset(self, key, tostring(key))
		end
		return tostring(key)
	end,
})
addon.L = L

--!!BaseTranslation!!--

local locale = GetLocale()
if locale == 'frFR' then
--@localization(locale="frFR", format="lua_additive_table")@
elseif locale == 'deDE' then
--@localization(locale="deDE", format="lua_additive_table")@
elseif locale == 'ruRU' then
--@localization(locale="ruRU", format="lua_additive_table")@
elseif locale == 'esES' then
--@localization(locale="esES", format="lua_additive_table")@
elseif locale == 'zhTW' then
--@localization(locale="zhTW", format="lua_additive_table")@
elseif locale == 'zhCN' then
--@localization(locale="zhCN", format="lua_additive_table")@
elseif locale == 'koKR' then
--@localization(locale="koKR", format="lua_additive_table")@
elseif locale == 'ptBR' then
--@localization(locale="ptBR", format="lua_additive_table")@
elseif locale == 'itIT' then
--@localization(locale="itIT", format="lua_additive_table")@
end

