
from typing import TYPE_CHECKING

from albedo_bot.database.schema.checklist import ChecklistHero
from albedo_bot.database.schema.hero.hero_instance import (
    HeroInstance, HeroInstanceData, HeroList)
from albedo_bot.cogs.checklist.utils.missing_hero import MissingHero

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class ChecklistComparison:
    """_summary_
    """

    def __init__(self, bot: "AlbedoBot", checklist_heroes: list[ChecklistHero],
                 hero_instances: list[HeroInstance],
                 checklist_hero_prefix: str = "Required: ",
                 hero_instance_prefix: str = "Current: "):
        """ 
        A wrapper around hero comparisons when checking if a
        roster `HeroInstance` meets the requirements for a Hero Checklist

        Args:
            bot (AlbedoBot): The currently running bot instance
            checklist_heroes (list[ChecklistHero]): a list of hero requirements
                in a checklist
            hero_instances (list[HeroInstance]): a list of hero instances in a
                players roster
            checklist_hero_prefix (str, optional): prefix to add to the
                checklist_hero string. Defaults to None.
            hero_instance_prefix (str, optional): prefix to add to the
                hero_instance string. Defaults to None.
        """

        self.bot = bot
        self.checklist_heroes = checklist_heroes
        self.hero_instances = hero_instances

        self.checklist_hero_prefix = checklist_hero_prefix
        self.hero_instance_prefix = hero_instance_prefix

        self.hero_instance_dict: dict[int, HeroInstance] = {}

        for roster_hero in self.hero_instances:
            self.hero_instance_dict[roster_hero.hero_id] = roster_hero
        self.missing_heroes: list[MissingHero] = []

    async def check_missing_heroes(self):
        """_summary_
        """

        missing_heroes: list[MissingHero] = []

        for checklist_hero in self.checklist_heroes:

            checklist_hero_info = await HeroInstanceData.from_checklist_hero(
                self.bot, checklist_hero)

            if checklist_hero.hero_id in self.hero_instance_dict:
                hero_instance = self.hero_instance_dict[checklist_hero.hero_id]
                if not self.check_requirement(checklist_hero, hero_instance):
                    hero_instance_info = await HeroInstanceData.from_hero_instance(
                        self.bot, hero_instance)
                    missing_heroes.append(
                        MissingHero(checklist_hero_info[0],
                                    hero_instance_info[0]))
            else:
                missing_heroes.append(
                    MissingHero(checklist_hero_info[0], None))
        return missing_heroes

    async def format_heroes(self):
        """
        Generate a hero string with the attributes the the
            ChecklistHero and HeroInstance

        Returns:
            _type_: _description_
        """
        self.missing_heroes = await self.check_missing_heroes()

        hero_list = HeroList(self.bot, self.missing_heroes)
        output = await hero_list.format_heroes(
            self.checklist_hero_prefix, self.hero_instance_prefix)
        return output

    @staticmethod
    def check_requirement(checklist_hero: ChecklistHero, hero_instance: HeroInstance):
        """
        Check if a hero_instance meets the requirements of a checklist_hero

        Args:
            checklist_hero (ChecklistHero): _description_
            hero_instance (HeroInstance): _description_
        """
        if (checklist_hero.ascension_level.value >
                hero_instance.ascension_level.value):
            return False
        if (checklist_hero.engraving_level > hero_instance.engraving_level):
            return False
        if (checklist_hero.furniture_level > hero_instance.furniture_level):
            return False
        if (checklist_hero.signature_level > hero_instance.signature_level):
            return False
        return True
