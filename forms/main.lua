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

local function AddToSet(List)
    local Set = {}
    for _, v in ipairs(List) do
        Set[v] = true
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
        print("PrefixCategories:", self.db.profile.prefixCategories, "CustomPrefix:", self.db.profile.customPrefix)
        print("Adibags Header Height:" .. AdiBags.HEADER_SIZE)
        if self.db.profile.prefixCategories == "!CUSTOM" then
            print("If", self.db.profile.customPrefix)
            prefix = self.db.profile.customPrefix
        else
            print("Else", self.db.profile.prefixCategories)
            prefix = self.db.profile.prefixCategories
        end
    end
    if self.db.profile.coloredPrefix then
        prefix = "|cff" .. converttohex(self.db.profile.prefixColor) .. prefix .. "|r"
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
setFilter.uiName = "|cff%ADDON_COLOR%%FILTER_NAME%|r"
setFilter.uiDesc = "%FILTER_DESCRIPTION%\n|cffFFD800Filter version: @project-version@|r"

function setFilter:OnInitialize()
    self.db = AdiBags.db:RegisterNamespace("%FILTER_NAME%", {
        profile = {
            coloredCategories = true,
            prefixCategories = "",
            customPrefix = "",
            coloredPrefix = true,
            prefixColor = converttorgb("%ADDON_COLOR%", true),
            --!!DefaultOptions!!--
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
                if MatchIDs[i]['override_method'](slotData.loc) then
                    return i
                end
            end

            -- Bonus Condition (triggers when bonus condition is not fulfilled)
        elseif MatchIDs[i]['bonus_condition'] then
            if name[slotData.itemId] then
                slotData['loc'] = ItemLocation:CreateFromBagAndSlot(slotData.bag, slotData.slot)
                if slotData['loc'] and slotData['loc']:IsValid() then
                    if not MatchIDs[i]['bonus_condition_method'](slotData.loc) then
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
            name = "General Settings",
            desc = "Settings affecting all categories.",
            inline = true,
            order = 1,
            args = {
                description = {
                    type = "description",
                    name = "These settings affect all categories of this filter. |cffFFD800If you overwrite prefix or categorie color, you either need to toggle the color setting twice or reload.|r",
                    order = 1,
                },
                coloredCategories = {
                    name = "|cffFDFD96Colored Categories|r",
                    desc = "Should Categories be colored?",
                    width = "full",
                    type = "toggle",
                    order = 10
                },
                prefixCategories = {
                    name = "Prefix Categories",
                    desc = "Select a prefix for the categories, if you like.",
                    type = "select",
                    order = 20,
                    values = {
                        [""] = "None",
                        ["!CUSTOM"] = "Custom Prefix",
                        --!!Prefixes!!--
                    },

                },
                customPrefix = {
                    name = "Custom Prefix",
                    desc = "Enter a custom prefix for the categories.",
                    type = "input",
                    order = 40,
                    width = "full",
                    disabled = function()
                        return self.db.profile.prefixCategories ~= "!CUSTOM"
                    end,
                },
                coloredPrefix = {
                    name = "|cffB9FFB9Color Prefix|r",
                    desc = "Should the prefix be colored to the filter color? (Only works for text-prefixes, for obvious reasons.)",
                    type = "toggle",
                    order = 50
                },
                prefixColor = {
                    name = "Prefix Color",
                    desc = "Select a color for the prefix.",
                    type = "color",
                    order = 60,
                    hasAlpha = false,
                    disabled = function()
                        return not setFilter.db.profile.coloredPrefix
                    end,
                    get = function()
                        local color = setFilter.db.profile.prefixColor
                        AdiBags:UpdateFilters()
                        return color.r, color.g, color.b
                    end,
                    set = function(_, r, g, b)
                        local color = setFilter.db.profile.prefixColor
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
