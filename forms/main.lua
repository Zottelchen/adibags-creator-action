--[[
AdiBags - %FILTER_NAME%
by %FILTER_AUTHOR%
version: @project-version@
%FILTER_DESCRIPTION%
]]

local addonName, addon = ...
local AdiBags = LibStub("AceAddon-3.0"):GetAddon("AdiBags")

local L = addon.L
local MatchIDs
local Result = {}

local function AddToSet(...)
    local Set = {}
    for _, l in ipairs({ ... }) do
        for _, v in ipairs(l) do
            Set[v] = true
        end
    end
    return Set
end

--!!MatchIDs!!--

local function converttohex(rgb)
    return string.format("%02x%02x%02x", rgb.r * 255, rgb.g * 255, rgb.b * 255)
end

local function converttorgb(hex, as_table)
    if as_table then
        return {
            r = tonumber("0x" .. strsub(hex, 1, 2)) / 255,
            g = tonumber("0x" .. strsub(hex, 3, 4)) / 255,
            b = tonumber("0x" .. strsub(hex, 5, 6)) / 255,
        }
    else
        -- as 3 values
        return tonumber("0x" .. hex:sub(1, 2)) / 255, tonumber("0x" .. hex:sub(3, 4)) / 255, tonumber("0x" .. hex:sub(5, 6)) / 255
    end
end

--@do-not-package@
local print = function(...)
    local str = ""
    for i = 1, select("#", ...) do
        str = str .. tostring(select(i, ...)) .. " "
    end
    DEFAULT_CHAT_FRAME:AddMessage("|cffff0000[AdiBagsDebug-%FILTER_NAME%]|r " .. str)
end
--@end-do-not-package@

local function formatBagTitle(self, title, hex)
    local prefix = ""
    if self.db.profile.prefixCategories then
        if self.db.profile.prefixCategories == "!CUSTOM" then
            prefix = self.db.profile.customPrefix
        else
            prefix = self.db.profile.prefixCategories
        end
    end
    if self.db.profile.coloredPrefix then
        prefix = "|cff" .. converttohex(self.db.profile.color.prefix) .. prefix .. "|r"
        if self.db.profile.coloredCategories then
            return prefix .. "|cff" .. hex .. title .. "|r"
        else
            return prefix .. title
        end
    else
        if self.db.profile.coloredCategories then
            return prefix .. "|cff" .. hex .. title .. "|r"
        else
            return prefix .. title
        end
    end
end

local function MatchIDs_Init(self)
    wipe(Result)

--!!Matching!!--

    return Result
end

local setFilter = AdiBags:RegisterFilter("%FILTER_NAME%", 98, "ABEvent-1.0")
setFilter.uiName = string.format("|cff%ADDON_COLOR%%s|r", L.REPLACE.FILTER_NAME)
setFilter.uiDesc = string.format("%s\n|cffffd800%s: @project-version@|r", L.REPLACE.FILTER_DESCRIPTION, L["Filter version"])

function setFilter:OnInitialize()
    self.db = AdiBags.db:RegisterNamespace("%FILTER_NAME%", {
        profile = {
            coloredCategories = true,
            prefixCategories = "",
            customPrefix = "",
            coloredPrefix = true,
--!!DefaultOptions!!--
            color = {
                prefix = converttorgb("%ADDON_COLOR%", true),
--!!DefaultColors!!--
            }
        }
    })
end

function setFilter:Update()
    MatchIDs = nil
    self:SendMessage("AdiBags_FiltersChanged")
end

function setFilter:OnEnable()
    AdiBags:UpdateFilters()
end

function setFilter:OnDisable()
    AdiBags:UpdateFilters()
end

function setFilter:Filter(slotData)
    MatchIDs = MatchIDs or MatchIDs_Init(self)
    for i, name in pairs(MatchIDs) do
        -- Override Method
        if MatchIDs[i]['override'] then
            slotData['loc'] = ItemLocation:CreateFromBagAndSlot(slotData.bag, slotData.slot)
            if slotData['loc'] and slotData['loc']:IsValid() then
                if MatchIDs[i]['override'](slotData.loc) then
                    return i
                end
            end

            -- Bonus Condition (triggers when bonus condition is not fulfilled)
        elseif MatchIDs[i]['bonus_condition'] then
            if name[slotData.itemId] then
                slotData['loc'] = ItemLocation:CreateFromBagAndSlot(slotData.bag, slotData.slot)
                if slotData['loc'] and slotData['loc']:IsValid() then
                    if not MatchIDs[i]['bonus_condition'](slotData.loc) then
                        -- THERE IS A NOT HERE!
                        return i
                    end
                end
            end

            -- Standard ID Matching
        elseif name[slotData.itemId] then
            return i
        end
    end
end

function setFilter:GetOptions()
    return {
        general_config = {
            type = "group",
            name = L["General Settings"],
            desc = L["Settings affecting all categories."],
            inline = true,
            order = 1,
            args = {
                description = {
                    type = "description",
                    name = string.format("%s |cffffd800%s |cff529F00%s|r", L["These settings affect all categories of this filter."], L["If you overwrite prefix or categorie color, you either need to toggle the color setting twice or reload."], L["AdiBags never intended to use icons, so they are glitchy. Make sure to disable prefix color, if you use an icon."]),
                    order = 1,
                },
                coloredCategories = {
                    name = string.format("|cffFDFD96%s|r", L["Colored Categories"]),
                    desc = L["Should Categories be colored?"],
                    width = "full",
                    type = "toggle",
                    order = 10
                },
                prefixCategories = {
                    name = L["Prefix Categories"],
                    desc = L["Select a prefix for the categories, if you like."],
                    type = "select",
                    order = 20,
                    values = {
                        [""] = L["None"],
                        ["!CUSTOM"] = L["Custom Prefix"],
--!!Prefixes!!--
                    },

                },
                customPrefix = {
                    name = L["Custom Prefix"],
                    desc = L["Enter a custom prefix for the categories."],
                    type = "input",
                    order = 30,
                    width = "full",
                    disabled = function()
                        return self.db.profile.prefixCategories ~= "!CUSTOM"
                    end,
                },
                coloredPrefix = {
                    name = string.format("|cffB9FFB9%s|r", L["Colored Prefix"]),
                    desc = L["Should the prefix be colored to the filter color? (Only works for text-prefixes, for obvious reasons.)"],
                    type = "toggle",
                    order = 40
                },
                prefixColor = {
                    name = L["Prefix Color"],
                    desc = L["Select a color for the prefix."],
                    type = "color",
                    order = 50,
                    hasAlpha = false,
                    disabled = function()
                        return not self.db.profile.coloredPrefix
                    end,
                    get = function()
                        local color = self.db.profile.color.prefix
                        AdiBags:UpdateFilters()
                        return color.r, color.g, color.b
                    end,
                    set = function(_, r, g, b)
                        local color = self.db.profile.color.prefix
                        color.r, color.g, color.b = r, g, b
                        AdiBags:UpdateFilters()
                    end,
                },
            },

        },
--!!ConfigMenu!!--
    },

    AdiBags:GetOptionHandler(self, false, function()
        return self:Update()
    end)
end
