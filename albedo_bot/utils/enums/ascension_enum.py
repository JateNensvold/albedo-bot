from albedo_bot.cogs.utils.mixins.enum_mixin import EnumMixin


ascension_values = {"E": 1,
                    "E+": 2,
                    "L": 3,
                    "L+": 4,
                    "M": 5,
                    "M+": 6,
                    "A": 7,
                    "A1": 8,
                    "A2": 9,
                    "A3": 10,
                    "A4": 11,
                    "A5": 12}

# pylint: disable=unexpected-keyword-arg
AscensionValues = EnumMixin(value="AscensionValues", names=ascension_values)
