from albedo_bot.cogs.utils.mixins.enum_mixin import StrEnum


# Timezone values are pulled from the following website
#   https://www.opentext.com/support/time-zones
timezone_enum_values = {
    "GMT-12": "Anywhere on Earth",
    "GMT-11": "Samoa Standard Time",
    "GMT-10": "Hawaii Standard Time",
    "GMT-9": "Alaska Standard Time",
    "GMT-8": "Pacific Standard Time",
    "GMT-7": "Mountain Standard Time",
    "GMT-6": "Central Standard Time",
    "GMT-5": "Eastern Standard Time",
    "GMT-4": "Atlantic Standard Time",
    "GMT-3": "Argentina Time",
    "GMT-2": "South Georgia Time",
    "GMT-1": "Central African Time",
    "GMT+0": "Greenwich Mean Time",
    "GMT+1": "European Central Time",
    "GMT+2": "Eastern European Time",
    "GMT+3": "Eastern Africa Time",
    "GMT+4": "Near East Time",
    "GMT+5": "Pakistan Standard Time",
    "GMT+6": "Bangladesh Standard Time",
    "GMT+7": "Indochina Time",
    "GMT+8": "China Taiwan Time",
    "GMT+9": "Japan Standard Time",
    "GMT+10": "Australia Eastern Time",
    "GMT+11": "Solomon Standard Time",
    "GMT+12": "New Zealand Standard Time"
}

# pylint: disable=unexpected-keyword-arg
TIMEZONE_ENUM = StrEnum(value="TimeZoneEnum",
                        names=timezone_enum_values)
