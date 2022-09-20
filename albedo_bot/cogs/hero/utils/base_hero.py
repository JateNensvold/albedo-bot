
from image_processing.processing.async_processing.processing_status import ProcessingStatus
import requests
from io import BytesIO

import jsonpickle
from discord import File
from discord.ext import commands
from image_processing.globals import IMAGE_PROCESSING_PORTRAITS
from image_processing.build_db import build_database
from image_processing.afk.hero.hero_data import HeroImage
from image_processing.processing.processing_server import (
    DATABASE_LOAD_MESSAGE, RELOAD_COMMAND_LIST)

import albedo_bot.config as config
from albedo_bot.cogs.utils.base_cog import BaseCog
from albedo_bot.database.schema.hero import Hero
from albedo_bot.database.schema.hero.hero import (
    HeroAscensionEnum, HeroClassEnum, HeroFactionEnum, HeroTypeEnum)
from albedo_bot.utils.errors import CogCommandError, RemoteProcessingError
from albedo_bot.utils.message.message_send import edit_message, send_embed, send_embed_exception
from albedo_bot.utils.embeds import EmbedField, EmbedWrapper
from albedo_bot.database.schema.hero.hero_portrait import HeroPortrait
from albedo_bot.config import AFK_HELPER_PATH
from albedo_bot.utils.git_helper.git_update import update_repo
from albedo_bot.utils.files.image_util import ContentType, valid_image
from albedo_bot.utils.hero_data import HeroData, JsonHero
from albedo_bot.utils.emoji import white_check_mark


class BaseHeroCog(BaseCog):
    """
    A discord.py cog that contains all the helper functions for the `Hero` Cog
    """

    @BaseCog.admin.group(name="hero")
    async def hero_admin(self, ctx: commands.Context):
        """
        A group of hero commands that require elevated permissions to run

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

    async def _auto_load(self, ctx: commands.Context):
        """
        Attempt to automatically load hero updates from
        https://github.com/Dae314/AFKBuilder/blob/main/src/stores/HeroData.js
        and then rebuild/reload the hero database for image recognition

        Args:
            ctx (commands.Context): _description_
        """
        embed_list: list[EmbedWrapper] = []

        holdover_wrapper = EmbedWrapper(
            title="Auto Loading hero updates... ",
            description=(
                f"Currently detecting updates for `AFK_Helper`..."))
        holdover_message_list = await send_embed(
            ctx, embed_wrapper=holdover_wrapper)
        holdover_message = holdover_message_list[0]

        try:
            repo_update = update_repo(AFK_HELPER_PATH)

            if len(repo_update.commit_info) == 0:
                embed_wrapper = EmbedWrapper(
                    title="No updates detected",
                    description=(
                        f"No hero updates were detected in `AFK_Helper`"))
                await send_embed(ctx, embed_wrapper=embed_wrapper)
                await holdover_message.delete()
                return

            repo_update_list: list[str] = []
            for commit_info in repo_update.commit_info:
                repo_update_list.append(f"```\n{commit_info.message}\n```")

            embed_wrapper = EmbedWrapper(title="AFK Helper changelog",
                                         description=("\n".join(repo_update_list)))
            embed_list.append(embed_wrapper)

            # removed_heroes: list[JsonHero] = []
            added_heroes: list[JsonHero] = []
            modified_heroes: list[JsonHero] = []

            hero_dict: dict[str, JsonHero] = {}
            for hero_entry in config.hero_data:
                hero_dict[hero_entry.hero_name] = hero_entry

            new_hero_data = HeroData.parse_file(
                self.bot, config.AFK_HELPER_HERO_DATA_PATH)

            for new_hero_dict in new_hero_data:
                new_json_hero = JsonHero(new_hero_dict)
                if new_json_hero.hero_name in hero_dict:
                    if not hero_dict[new_json_hero.hero_name
                                     ].hero_dict == new_json_hero.hero_dict:
                        modified_heroes.append(new_json_hero)
                    del hero_dict[new_json_hero.hero_name]
                else:
                    added_heroes.append(new_json_hero)
        except Exception as exception:
            await holdover_message.delete
            await send_embed_exception(ctx, exception, description=(
                "An error occurred while attempting to fetch hero updates ",
                "command is being aborted..."))

        # Any heroes leftover in the hero_dict are heroes that have
        #   been removed.

        holdover_wrapper.title = "Updating hero information... "
        holdover_wrapper.description += (
            f"{white_check_mark}\nUpdating hero information in database...")
        holdover_message = await edit_message(ctx, message=holdover_message,
                                              embed_wrapper=holdover_wrapper)
        # Flush hero config to database
        config.hero_data._db = new_hero_data
        await config.hero_data.save()

        for json_hero in modified_heroes:
            modified_hero = await json_hero.build(self.bot.session)
            hero_portrait = await HeroPortrait.get_portrait(modified_hero,
                                                            self.bot.session)
            modified_hero_embed = self.build_display(
                modified_hero, [hero_portrait])[0]
            modified_hero_embed.title = f"Modified hero - {modified_hero.name}"
            modified_hero_embed.description = (
                f"`{modified_hero.name}` has been modified in the Hero "
                "Database")
            embed_list.append(modified_hero_embed)

        for json_hero in added_heroes:
            added_hero = await json_hero.build(self.bot.session)
            hero_portrait = await HeroPortrait.get_portrait(added_hero,
                                                            self.bot.session)
            added_hero_embed = self.build_display(
                added_hero, [hero_portrait])[0]
            added_hero_embed.title = f"Added hero - {added_hero.name}"
            added_hero_embed.description = (
                f"`{added_hero.name}` has been added to the Hero Database")
            embed_list.append(added_hero_embed)

        holdover_wrapper.title = "Auto Loading hero updates... "
        holdover_wrapper.description += (
            f"{white_check_mark}\n"
            f"Rebuilding Hero Database in `afk_image_processing`...")
        holdover_message = await edit_message(ctx, message=holdover_message,
                                              embed_wrapper=holdover_wrapper)

        base_hero_list: list[HeroImage] = []

        hero_portrait_select = self.db_select(HeroPortrait)

        hero_portrait_objects = await self.db_execute(
            hero_portrait_select).all()

        for hero_portrait_object in hero_portrait_objects:
            hero_image = await hero_portrait_object.build_hero_image(
                self.bot.session)
            base_hero_list.append(hero_image)

        # Rebuild here
        build_database(enriched_db=True, base_images=base_hero_list)
        holdover_wrapper.title = "Auto Loading hero updates... "
        holdover_wrapper.description += (
            f"{white_check_mark}\n"
            f"Refreshing Hero Database in remote process, if others are "
            f"using the bot this could take a while...")
        holdover_message = await edit_message(ctx, message=holdover_message,
                                              embed_wrapper=holdover_wrapper)

        # Refresh here
        await self.remote_reload_database(ctx)

        await send_embed(ctx, embed_list)
        await holdover_message.delete()

    async def remote_reload_database(self, ctx: commands.Context):
        """
        Refresh/reload the database on the remote process

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        Returns:
            (ProcessingResult): the response from calling the remote 
                processing server
        """
        command_list: list[str] = RELOAD_COMMAND_LIST
        # processing_result = ProcessingClient().remote_compute_results(
        #     config.PROCESSING_SERVER_ADDRESS,
        #     config.PROCESSING_SERVER_TIMEOUT_MILLISECONDS,
        #     command_list)

        processing_result = await config.processing_client.async_compute(
            command_list,
            config.PROCESSING_SERVER_ADDRESS,
            config.PROCESSING_SERVER_TIMEOUT_MILLISECONDS,
        )

        if processing_result.status == ProcessingStatus.reload:
            if processing_result.message != DATABASE_LOAD_MESSAGE:
                raise RemoteProcessingError(
                    (f"{error_message}\nExpected \n"
                     f"```{DATABASE_LOAD_MESSAGE}```\nfound\n"
                     f"```{ processing_result.message}```\n instead"))
        else:
            error_message = (
                f"Unable to refresh database on the remote process due to"
                f"\n```\n{processing_result.message}\n```\nContact an "
                f"admin or `{self.bot.owner_string}` for more information")
            raise RemoteProcessingError(error_message)
        return processing_result

    async def _add_image(self, ctx: commands.Context, hero: Hero,
                         image_index: int):
        """
        Add an image to the hero portrait database for `hero`

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero (Hero): hero to add portrait for
            image_index (int): index to add portrait at

        Raises:
            CogCommandError: When no image was attached to the 
                command invocation
            CogCommandError: When more than one image was attached to the
                command invocation
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

        content_type = ContentType.from_str(portrait_attachment.content_type)

        valid_image(portrait_attachment.url, content_type)

        new_portrait = await HeroPortrait.add_optional(
            self.bot, hero, IMAGE_PROCESSING_PORTRAITS,
            content_type, image_index)

        attachment_data = requests.get(portrait_attachment.url).content
        buffered_data = BytesIO(attachment_data)
        portrait_image = File(buffered_data,
                              filename=new_portrait.image_name)

        with open(new_portrait.full_path(), 'wb') as file_pointer:
            file_pointer.write(attachment_data)

        embed_wrapper = EmbedWrapper(
            title="Image added successfully",
            description=(
                f"The following image `{new_portrait.image_name}` has been "
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
            hero (Hero): _description_
            image_index (int): _description_

        Raises:
            CogCommandError: When no optional portraits are found for a `hero`
            CogCommandError: When `image_index` is out of bounds
            CogCommandError: When the image location in the database points to
                a non existent file
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
        """
        Show all the portraits for `hero` 

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero (Hero): hero to show portraits for
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

        required_portraits_list = self.build_display(
            hero, [*required_portraits])
        optional_portraits_list = self.build_display(
            hero, [*optional_portraits])
        await send_embed(ctx, embed_wrapper=[*required_portraits_list,
                                             *optional_portraits_list])

    def build_display(self, hero: Hero,
                      portrait_list: list[HeroPortrait]):
        """
        Build a list of EmbedWrappers for `portrait_list`

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
                name="Name", value=f"`{hero_portrait.image_name}`"))

            image = File(hero_portrait.full_path(),
                         filename=hero_portrait.image_name)

            if hero_portrait.required:
                required_status = "Required"
            else:
                required_status = "Optional"

            embed_wrapper = EmbedWrapper(
                title=f"{hero.name} portraits - {required_status}",
                description=(f"Image {portrait_iter_index+1}/"
                             f"{len(portrait_list)}"),
                embed_fields=embed_field_list,
                image=image)
            embed_wrapper_list.append(embed_wrapper)
        return embed_wrapper_list
