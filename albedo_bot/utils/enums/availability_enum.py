import datetime

from albedo_bot.cogs.utils.mixins.enum_mixin import EnumMixin


NORMAL_TIME_FORMAT = "%I:%M:%S %p"
MILITARY_TIME_FORMAT = "%H:%M:%S"

availability_enum_values: dict[str, datetime.datetime] = {}

for availability_offset in range(0, 24):
    timestamp = datetime.datetime(
        1, 1, 1, availability_offset)
    availability_enum_values[str(availability_offset)] = timestamp

# pylint: disable=unexpected-keyword-arg
AVAILABILITY_ENUM = EnumMixin(
    value="AvailabilityEnum", names=availability_enum_values)
