import requests

from discord import File
from discord.ext import commands
import image_processing.globals as GV

from albedo_bot.cogs.utils.base_cog import BaseCog
from albedo_bot.database.schema.hero import Hero
from albedo_bot.database.schema.hero.hero import (
    HeroAscensionEnum, HeroClassEnum, HeroFactionEnum, HeroTypeEnum)
from albedo_bot.utils.errors import CogCommandError
from albedo_bot.utils.message import EmbedField, EmbedWrapper, send_embed
from albedo_bot.database.schema.hero.hero_portrait import HeroPortrait


class BaseHeroCog(BaseCog):
    """_summary_
    """

    # pylint: disable=no-member
    @BaseCog.admin.group(name="hero")
    async def hero_admin(self, ctx: commands.Context):
        """
        A group of players commands that require elevated permissions to run

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

    async def _find_hero(self, hero_name: Hero):
        """
        Search for a hero with the name 'hero_name' in the database. Return true if
        there is a match, return False otherwise

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero_name ([type]): name of hero to look for

        Returns:
            [type]: Return 'hero_object' if found in the heroes table,
                None otherwise
        """

        hero_select = self.db_select(Hero).where(
            Hero.name == hero_name)
        hero_object = await self.db_execute(hero_select).first()

        return hero_object

    async def _add_hero(self, ctx: commands.Context,
                        hero_name: str,
                        hero_faction: HeroFactionEnum,
                        hero_class: HeroClassEnum,
                        hero_type: HeroTypeEnum,
                        ascension_tier: HeroAscensionEnum):
        """
        Add a hero to the hero database

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero_name (str): name of hero to add
        """
        hero_object: Hero = await self._find_hero(hero_name)
        if hero_object is None:
            new_hero = Hero(name=hero_name, hero_faction=hero_faction,
                            hero_class=hero_class, hero_type=hero_type,
                            ascension_tier=ascension_tier)
            await self.db_add(new_hero)

            await send_embed(ctx, embed_wrapper=EmbedWrapper(
                description=(f"Added new hero `{hero_name}` as `{new_hero}`")))
        else:

            embed_wrapper = EmbedWrapper(
                title="Hero Already Registered",
                description=(
                    f"A hero with the name `{hero_name}` has already been "
                    f"registered as `{hero_object}`"))
            raise CogCommandError(embed_wrapper=embed_wrapper)

    async def _remove_hero(self, ctx: commands.Context, hero_object: Hero):
        """
        Remove a hero from the database

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero_object (Hero): Hero getting removed
        """
        await self.db_delete(hero_object)

        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            description=(f"Removed hero `{hero_object}` from hero database")))

    async def _add_image(self, ctx: commands.Context, hero: Hero,
                         image_index: int):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            image_index (int): _description_
        """

        portrait_attachment = ctx.message.attachments[0]
        if len(ctx.message.attachments) == 0:
            embed_wrapper = EmbedWrapper(
                title="No Hero portrait found",
                description=(
                    "To add a hero portrait to the database ensure that an "
                    "image has been attached to this command"))
            raise CogCommandError(embed_wrapper=embed_wrapper)
        elif len(ctx.message.attachments) > 1:
            embed_wrapper = EmbedWrapper(
                title="Too many Hero portraits found",
                description=(
                    "To add a hero portrait to the database ensure that only a "
                    "single image has been attached to this command"))
            raise CogCommandError(embed_wrapper=embed_wrapper)
        file_types: list[str] = ["jpg", "jpeg", "png"]
        if portrait_attachment.content_type.lower() not in file_types:
            embed_wrapper = EmbedWrapper(
                title="Invalid file type",
                description=(
                    f"The following attachment is invalid "
                    f"{portrait_attachment.url}, Hero portraits only support "
                    f"the following file types {', '.join(file_types)}"))
            raise CogCommandError(embed_wrapper=embed_wrapper)

        portraits_select = self.db_select(
            HeroPortrait).where(hero.id == HeroPortrait.id)

        hero_portraits = await self.db_execute(portraits_select).all()

        required_portraits: list[HeroPortrait] = []
        optional_portraits: list[HeroPortrait] = []

        for hero_portrait in hero_portraits:
            if hero_portrait.required:
                required_portraits.append(hero_portrait)
            else:
                optional_portraits.append(hero_portrait)

        optional_portraits.sort(key=lambda portrait: portrait.image_index)

        update_portraits: list[HeroPortrait] = []

        if image_index < 0:
            image_index = len(optional_portraits)
        elif image_index > len(optional_portraits):
            image_index = len(optional_portraits)
        else:
            for hero_portrait in optional_portraits:
                if hero_portrait.image_index >= image_index:
                    hero_portrait.image_index += 1
                    update_portraits.append(hero_portrait)

        new_portrait = HeroPortrait()
        portrait_name = f"{hero.name}_{len(optional_portraits)}"
        portrait_directory_path = GV.IMAGE_PROCESSING_PORTRAITS

        new_portrait.image_index = len(optional_portraits)
        new_portrait.required = False
        new_portrait.image_directory = portrait_directory_path
        new_portrait.image_name = portrait_name
        new_portrait.id = hero.id

        full_portrait_path = portrait_directory_path.joinpath(
            portrait_name)
        if not portrait_directory_path.exists():
            embed_wrapper = EmbedWrapper(
                title="Portrait Path Failure",
                description=(
                    "The following path does not exist "
                    f"{portrait_directory_path}.\n"
                    f"Contact an admin or {self.bot.owner_string} with the "
                    "above error"))
            raise CogCommandError(embed_wrapper=embed_wrapper)
        elif full_portrait_path.exists():
            embed_wrapper = EmbedWrapper(
                title="Portrait Path Failure",
                description=(
                    "The following path already exists"
                    f"{full_portrait_path}.\n"
                    f"Contact an admin or {self.bot.owner_string} with the "
                    "above error"))
            raise CogCommandError(embed_wrapper=embed_wrapper)

        attachment_data = requests.get(portrait_attachment.url).content
        with open(full_portrait_path, 'wb') as file:
            file.write(attachment_data)

        await self.db_add(new_portrait)

        for hero_portrait_update in update_portraits:
            await self.db_add(hero_portrait_update)

        portrait_image = File(full_portrait_path,
                              filename=hero_portrait.image_name)
        embed_wrapper = EmbedWrapper(
            title="Image added successfully",
            description=(
                f"The following image {hero_portrait.image_name} has been "
                f"successfully added for hero `{hero.name}`"),
            image=portrait_image)
        await send_embed(ctx, embed_wrapper=embed_wrapper)

    async def _remove_image(self, ctx: commands.Context, hero: Hero,
                            image_index: int):
        """
        Remove an image from the hero portrait database

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            image_index (int): _description_
        """

        portraits_select = self.db_select(
            HeroPortrait).where(hero.id == HeroPortrait.id)

        hero_portraits = await self.db_execute(portraits_select).all()

        required_portraits: list[HeroPortrait] = []
        optional_portraits: list[HeroPortrait] = []

        for hero_portrait in hero_portraits:
            if hero_portrait.required:
                required_portraits.append(hero_portrait)
            else:
                optional_portraits.append(hero_portrait)

        optional_portraits.sort(key=lambda portrait: portrait.image_index)

        if len(optional_portraits) == 0:
            embed_wrapper = EmbedWrapper(
                title="No images found",
                description=(
                    "There are currently no optional images available "
                    "to remove"))
            raise CogCommandError(embed_wrapper=embed_wrapper)

        try:
            old_portrait = optional_portraits[image_index]
            await self.db_delete(old_portrait)

            old_portrait.full_path().unlink()

            embed_wrapper = EmbedWrapper(
                title="Image removed successfully",
                description=(
                    f"Image `{old_portrait.image_name}` for hero `{hero.name}` "
                    "has been successfully deleted."))
            await send_embed(ctx, embed_wrapper=embed_wrapper)
        except IndexError as exception:
            embed_wrapper = EmbedWrapper(
                title="Image index out of bounds",
                description=(
                    f"The image index provided `({image_index})` is out of "
                    "bounds, enter an index in the following range "
                    f"`(0 - {len(optional_portraits) -1}`"))
            raise CogCommandError(embed_wrapper=embed_wrapper) from exception
        except FileNotFoundError as exception:
            embed_wrapper = EmbedWrapper(
                title="Missing file",
                description=(
                    "Unable to find a file to delete for image "
                    f"`{old_portrait.image_name}`.\n Contact an admin or "
                    f"{self.bot.owner_string} for assistance"))
            raise CogCommandError(embed_wrapper=embed_wrapper) from exception

    async def _show_image(self, ctx: commands.Context, hero: Hero):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        portraits_select = self.db_select(
            HeroPortrait).where(hero.id == HeroPortrait.id)

        hero_portraits = await self.db_execute(portraits_select).all()

        required_portraits: list[HeroPortrait] = []
        optional_portraits: list[HeroPortrait] = []

        for hero_portrait in hero_portraits:
            if hero_portrait.required:
                required_portraits.append(hero_portrait)
            else:
                optional_portraits.append(hero_portrait)

        optional_portraits.sort(key=lambda portrait: portrait.image_index)

        embed_wrapper_list = self.build_display(hero, [*required_portraits,
                                                       *optional_portraits])
        await send_embed(ctx, embed_wrapper=embed_wrapper_list)

    def build_display(self, hero: Hero,
                      portrait_list: list[HeroPortrait]):
        """
        Build a list of EmbedWrappers for a list of portraits

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero (Hero): Hero to display build display for
            portrait_list (list[HeroPortrait]): list of portraits to build a
                display around
        """

        embed_wrapper_list: list[EmbedWrapper] = []

        for portrait_iter_index, hero_portrait in enumerate(portrait_list):
            embed_field_list: list[EmbedField] = []

            embed_field_list.append(EmbedField(
                name="Required", value=f"{hero_portrait.required}"))
            if hero_portrait.required:
                portrait_index = "-"
            else:
                portrait_index = hero_portrait.image_index
            embed_field_list.append(EmbedField(
                name="Index", value=f"{portrait_index}"))
            embed_field_list.append(EmbedField(
                name="Name", value=f"{hero_portrait.image_name}"))

            image = File(hero_portrait.full_path(),
                         filename=hero_portrait.image_name)

            if hero_portrait.required:
                required_status = "Required"
            else:
                required_status = "Optional"

            embed_wrapper = EmbedWrapper(
                title=f"{hero.name} {required_status} portrait",
                description=(f"Image {portrait_iter_index}/"
                             f"{len(portrait_list)}"),
                embed_fields=embed_field_list,
                image=image)
            embed_wrapper_list.append(embed_wrapper)
        return embed_wrapper_list
