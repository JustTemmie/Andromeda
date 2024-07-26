import discord
from discord.ext import commands

import asyncio
import aiohttp
import yt_dlp

import re
import time
import math
import random

import modules.helpers as helpers
import modules.user_input as user_input
import config
from launcher import lang

ytdlp_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": False,
    "playlist_items": "1:50",
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0", # bind to ipv4 since ipv6 addresses cause issues sometimes
    "retries": "infinite"
}

default_ffmpeg_options = {
    "options": "-vn -af 'loudnorm, volume=0.4'",
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

sent_messages = {}


# insane regex https://stackoverflow.com/a/14693789
remove_colour = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # parameter bytes
        [ -/]*  # intermediate bytes
        [@-~]   # final byte
    )
''', re.VERBOSE)

class TrackedFFmpegPCMAudio(discord.FFmpegPCMAudio):
    def __init__(self, player, guild_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = player
        self.guild_id = guild_id

    # read is called every 20 miliseconds, overwrite the read function to increase a counter by 20
    def read(self, *args, **kwargs):
        ret = super().read()
        if ret:
            self.player.data[self.guild_id]["progress"] += 20
        return ret

class YtDlpSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")


    @classmethod
    async def get_player(cls, player, guild_id, song):
        data = song["data"]

        filename = data["url"]

        player.data[guild_id]["meta_data"] = await player.get_meta_data(data)
        player.data[guild_id]["meta_data"]["ctx"] = song["ctx"]
        player.data[guild_id]["progress"] = 0

        return cls(TrackedFFmpegPCMAudio(player, guild_id, filename, **player.data[guild_id]["ffmpeg_options"]), data=data)

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = {}
    

    async def download_song(self, url, ctx, playlist_items = "1:2"):

        options = ytdlp_format_options.copy()
        sent_messages[ctx.message.id] = None
        
        class YTDLPProgressUpdater:
            def debug(log):
                if not log.startswith("[download] "):
                    return
                if "Downloading item " not in log:
                    return

                log = remove_colour.sub('', log)
                items = log.split("Downloading item ")[1]
                progress = int(items.split(" ")[0])
                total = int(items.split(" ")[-1])

                if total > 2:
                    message_content = lang.tr("music_downloading_queue_progress", userID=ctx.author.id, progress=progress+2, total=total+2)
                    
                    if sent_messages[ctx.message.id] == None:
                        job = asyncio.run_coroutine_threadsafe(ctx.reply(mention_author=False, content=message_content), self.bot.loop)
                        sent_messages[ctx.message.id] = job.result()
                    
                    elif progress % 5 == 0 or progress == total:
                        job = asyncio.run_coroutine_threadsafe(sent_messages[ctx.message.id].edit(content=message_content), self.bot.loop)
                        job.result()
                
                if progress == total:
                    del sent_messages[ctx.message.id] 

            def info(log):
                pass

            def warning(log):
                pass

            def error(log):
                log = remove_colour.sub('', log)
                job = asyncio.run_coroutine_threadsafe(ctx.reply(
                    mention_author=False,
                    content=f"```{log}```"),
                    self.bot.loop)
                job.result()


        options["logger"] = YTDLPProgressUpdater
        options["playlist_items"] = playlist_items

        with yt_dlp.YoutubeDL(options) as ytdlp:
            data = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdlp.extract_info(url, download=False))

        return data
    
    async def change_ffmpeg_filter(self, ctx, filter):
        guild_id = ctx.guild.id
        
        self.data[guild_id]["seeking"] = True
        progress = self.data[guild_id]["progress"]
        try:
            duration = self.data[guild_id]["meta_data"]["duration"]
        except:
            duration = lang.tr("generic_unknown", userID=ctx.author.id)
        
        # make sure that the progress is at the latest 1 second before the end of the song
        if type(duration) == int:
            progress = min(progress, duration * 1000 - 1000)
        else:
            progress -= 1000
        
        
        # old_player = self.data[guild_id]["player"]
        # old_options = self.data[guild_id]["ffmpeg_options"]["options"]
        # start_time = time.time()
        
        self.data[guild_id]["ffmpeg_options"]["options"] = f"-vn -ss {progress/1000} -af 'loudnorm, volume=0.4 {filter}'"
        
        
        new_player = await YtDlpSource.get_player(self, guild_id, self.data[guild_id]["song"])
        ctx.voice_client.pause()
        self.data[guild_id]["player"] = new_player
        
        if ctx.voice_client:
            ctx.voice_client.play(
                self.data[guild_id]["player"],
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_song(ctx), self.bot.loop
                )
            )
        
            self.data[guild_id]["progress"] = progress
            self.data[guild_id]["ffmpeg_options"]["options"] = f"-vn -af 'loudnorm, volume=0.4 {filter}'"
        
        else:
            self.play_song(ctx)
        

    async def play_song(self, ctx):
        try:
            guild_id = ctx.guild.id
            if guild_id not in self.data or self.data[guild_id]["seeking"]:
                return

            if len(self.data[guild_id]["queue"]) == 0:
                await self.send_queue_finished_embed(ctx)
                self.data[guild_id]["playing"] = False
                self.data[guild_id]["progress"] = 0
                return
            
            self.data[guild_id]["song"] = self.data[guild_id]["queue"].pop(0)
            self.data[guild_id]["playing"] = True
            
            self.data[guild_id]["player"] = await YtDlpSource.get_player(self, guild_id, self.data[guild_id]["song"])
            
            if ctx.voice_client:
                ctx.voice_client.play(
                    self.data[guild_id]["player"],
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.play_song(ctx), self.bot.loop
                    )
                )

                await self.send_now_playing_embed(ctx)

            else:
                await lang.tr_send(ctx, "error_music_start_playing", song=self.data[guild_id]['song'])
                self.play_song(ctx)

        except Exception as err:
            await lang.tr_send(ctx, "error_music_generic_playing", error_type=type(err), error=err)


    async def get_like_dislike_ratio(self, video_id):
        if video_id == "unknown":
            return {}

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://returnyoutubedislikeapi.com/votes?videoId={video_id}") as r:
                if r.status == 200:
                    data = await r.json()
                    meta_data = {
                        "likes": data["likes"],
                        "dislikes": data["dislikes"],
                        "views": data["viewCount"],
                    }
                else:
                    meta_data = {
                        "likes": "unknown",
                        "dislikes": "unknown",
                        "views": "unknown",
                    }

        return meta_data

    async def ensure_valid_data(self, guild_id):
        # make sure there's actually usable data in the data dictionary
        if guild_id not in self.data:
            self.data[guild_id] = {}
            self.data[guild_id]["playing"] = False
            self.data[guild_id]["meta_data"] = {}
            self.data[guild_id]["queue"] = []
            self.data[guild_id]["progress"] = 0
            self.data[guild_id]["ffmpeg_options"] = default_ffmpeg_options.copy()
            self.data[guild_id]["player"] = None
            self.data[guild_id]["seeking"] = False
            self.data[guild_id]["song"] = None

    async def send_now_playing_embed(self, ctx):
        meta_data = self.data[ctx.guild.id]["meta_data"]

        embed = helpers.create_embed(meta_data["ctx"])
        embed.title = meta_data["title"]
        embed.description = lang.tr("music_embed_now_playing", userID=ctx.author.id)

        embed = await self.add_embed_fields(embed, meta_data, ctx.author.id)

        await ctx.send(embed=embed)

    async def add_embed_fields(self, embed, meta_data, authorID):
            existing_field_count = len(embed.fields)
            
            try:
                # LIVE STATUS
                if meta_data["live_status"] == "is_live":
                    embed.add_field(
                        name = lang.tr("music_embed_livestream_type_title", userID=authorID),
                        value = lang.tr("music_embed_livestream_type_title", userID=authorID))

                # DURATION
                if "readable_duration" in meta_data and meta_data["readable_duration"] != "unknown":
                    embed.add_field(
                        name = lang.tr("music_embed_duration", userID=authorID),
                        value = meta_data["readable_duration"])

                # UPLOADER
                if meta_data["uploader"] != "unknown":
                    if meta_data["uploader_url"] in ["unknown", "None", None]:
                        embed.add_field(
                            name=lang.tr("music_embed_uploader", userID=authorID),
                            value=meta_data['uploader'])
                    else:
                        embed.add_field(
                            name=lang.tr("music_embed_uploader", userID=authorID),
                            value=f"[{meta_data['uploader']}]({meta_data['uploader_url']})")


                # LIKE DISLIKE RATIO
                if meta_data["dislikes"] != "unknown":
                    embed.add_field(
                        name=lang.tr("music_embed_likes_and_dislikes", userID=authorID),
                        value=f"{meta_data['likes']} / {meta_data['dislikes']}",
                    )


                # VIEW COUNT
                if meta_data["views"] != "unknown":
                    embed.add_field(
                        name=lang.tr("music_embed_views", userID=authorID),
                        value=meta_data["views"])
                    

                # THUMBNAIL
                if meta_data["thumbnail"] != "unknown":
                    embed.set_thumbnail(url = meta_data["thumbnail"])

                new_field_count = len(embed.fields)

                for i in range(new_field_count - 2, max(0, existing_field_count - 1), -2):
                    embed.insert_field_at(
                        i,
                        name="\t",
                        value="\t",
                        inline=False
                    )
            
            except Exception as e:
                embed.add_field(
                    name=lang.tr("error_generic", userID=authorID),
                    value=e
                )


            return embed

    async def send_queue_finished_embed(self, ctx):
        embed = helpers.create_embed(ctx)

        embed.title = lang.tr("music_embed_queue_finished")
        await ctx.send(embed = embed)

    async def get_meta_data(self, data, fetch_like_dislike_ratio = True):
        video_id = data["id"]
        if video_id == None: video_id = "unknown"
        if fetch_like_dislike_ratio:
            meta_data = await self.get_like_dislike_ratio(video_id)
        else:
            meta_data = {}

        data_points = ["title", "duration", "live_status", "upload_date",
                    "uploader", "uploader_url", "thumbnail", "original_url"]

        for entry in data_points:
            if entry in data:
                meta_data[entry] = data[entry]
            else:
                meta_data[entry] = "unknown"

        try:
            meta_data["readable_duration"] = helpers.format_time(data["duration"])
        except:
            meta_data["readable_duration"] = "unknown"

        return meta_data

    @commands.command(
        name="playnext",
        brief="command_brief_playnext",
        description="command_description_playnext",
        extras={"page": "main", "category":"music"}
    )
    @commands.cooldown(6, 7200, commands.BucketType.member)
    async def playnext_command(self, ctx, *, search_query = None):
        await self.play_command(ctx, search_query, mode = list.insert)
        
    @commands.command(
        name="play",
        aliases=["sing"],
        brief="command_brief_play",
        description="command_description_play",
        extras={"page": "main", "category":"music"}
    )
    async def play_command_register(self, ctx, *, search_query = None):
        await self.play_command(ctx, search_query, mode = list.append)
    
    async def play_command(self, ctx, search_query, mode):
        try:
            voice_channel = ctx.author.voice.channel

        except AttributeError as e:
            await lang.tr_send(ctx, "music_no_voice_channel_found")
            return

        except Exception as e:
            await lang.tr_send(ctx, "error_generic_with_error_passthru", error=e)
            return

        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild) # This allows for more functionality with voice channels
        guild_id = ctx.guild.id

        if voice_client != None:
            if voice_client.channel != voice_channel:
                await lang.tr_send(ctx, "music_playing_in_different_voice_channel")
                return


        await self.ensure_valid_data(guild_id)
        await ctx.message.add_reaction("✅")
        
        def add_entry(entry):
            if mode == list.insert:
                self.data[guild_id]["queue"].insert(0,
                    {"data": entry,
                    "ctx": ctx}
                )
                
            else:
                self.data[guild_id]["queue"].append(
                    {"data": entry,
                    "ctx": ctx}
                )
        
        async def add_playlist(ctx, song_data):
            if len(song_data["entries"]) == 0:
                return
            
            for entry in song_data["entries"]:
                add_entry(entry)

            if len(song_data["entries"]) > 2:
                embed = helpers.create_embed(ctx)
                embed.title = lang.tr("music_embed_added_songs_to_queue", userID=ctx.author.id, song_count=len(song_data['entries']) + 2)

                await ctx.send(embed = embed)


        async def add_song(ctx, song_data):
            if "entries" in song_data:
                song_data = song_data["entries"][0]
            
            add_entry(song_data)
            
            if self.data[guild_id]["playing"]:
                meta_data = await self.get_meta_data(song_data)
                embed = helpers.create_embed(ctx)
                embed.title = lang.tr("music_embed_added_song_to_queue", userID=ctx.author.id)
                embed.description = meta_data["title"]

                embed = await self.add_embed_fields(embed, meta_data, ctx.author.id)

                await ctx.send(embed = embed)

        
        if search_query == None:
            if len(ctx.message.attachments) == 0:
                await lang.tr_send(ctx, "music_generic_invalid_search_query")
                return
            
            song_data = await self.download_song(ctx.message.attachments[0].url, ctx)
            
            
        else:
            song_data = await self.download_song(search_query, ctx)

        # with open ("example_data.json", "w") as f:
        #     import json
        #     json.dump(song_data, f)


        add_full_playlist = False
        playlist_download_count = 50
        if "entries" in song_data and len(song_data["entries"]) > 1:
            await lang.tr_reply(ctx, "music_question_add_playlist", time=round(time.time()) + 15)
            add_full_playlist = await user_input.get_consent(self.bot, ctx, 17, ", adding the first track only")

            if add_full_playlist:
                await add_playlist(ctx, song_data)
                
                if ctx.author.id in config["TRUSTED_IDS"]:
                    await ctx.reply(lang.tr("music_question_add_song_amount"))
                    response = await user_input.get_input(
                        self.bot, ctx, 10,
                        lang.tr(
                            "music_question_no_reply",
                            userID=ctx.author.id,
                            default=playlist_download_count
                        )
                    )
                    
                    try:
                        response = int(response.content)
                        playlist_download_count = response
                    except:
                        await lang.tr_send(ctx, "music_question_invalid_reply", default=playlist_download_count)

            # take first item from a playlist
            else:
                await add_song(ctx, song_data)

        elif song_data != None:
            await add_song(ctx, song_data)


        if voice_client == None:
            await voice_channel.connect(self_deaf=True)
            await self.play_song(ctx)

        if self.data[guild_id]["playing"] == False:
            await self.play_song(ctx)
        
        if add_full_playlist:
            song_data = await self.download_song(search_query, ctx, f"3:{playlist_download_count}")
            await add_playlist(ctx, song_data)

    @commands.cooldown(1, 4, commands.BucketType.guild)
    @commands.command(
        name="filter",
        brief="command_brief_filter",
        description="command_description_filter",
        extras={"page": "main", "category":"music"}
    )
    async def filter_command(self, ctx, filter = ""):
        voice_channel = ctx.author.voice.channel

        if voice_channel is not None:
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice is not None:
                await self.change_ffmpeg_filter(ctx, filter)
            else:
                await lang.tr_send(ctx, "error_generic")
        else: 
            await lang.tr_send(ctx, "music_no_voice_channel_found")


    @commands.hybrid_command(
        name="now-playing", aliases=["nowplaying", "np"],
        brief="command_brief_nowplaying",
        extras={"page": "main", "category":"music"}
    )
    async def nowplaying_command(self, ctx):
        guild_id = ctx.guild.id
        if not guild_id in self.data or self.data[guild_id]["playing"] == False:
            await lang.tr_send(ctx, "music_not_playing")
            return

        if "meta_data" not in self.data[guild_id]:
            return

        meta_data = self.data[guild_id]["meta_data"]

        embed = helpers.create_embed(ctx)
        embed.title = lang.tr("music_embed_currently_playing", userID=ctx.author.id)
        if meta_data["original_url"] != "unknown":
            embed.description = f"[{meta_data['title']}]({meta_data['original_url']})"
        else:
            embed.description = meta_data["title"]
            

        progress = self.data[guild_id]["progress"] / 1000
        embed_value = f"{progress}/?"
        try:
            progress_bar = helpers.getProgressBar(progress, meta_data["duration"], 23)
            embed_value = f"{round((progress / meta_data['duration']) * 100)}% - {progress_bar}"
        except:
            pass
        
        embed.add_field(
            name=lang.tr("music_embed_progress", userID=ctx.author.id),
            value=embed_value,
            inline=False
        )

        embed = await self.add_embed_fields(embed, meta_data, ctx.author.id)

        await ctx.send(embed = embed)


    @commands.hybrid_command(
        name="queue", aliases=["q"],
        extras={"page": "main", "category":"music"}
    )
    async def queue_command(self, ctx, page = 1):
        if type(page) != int:
            return await lang.tr_send(ctx, "music_invalid_queue_page_number", page=page)

        guild_id = ctx.guild.id
        if not guild_id in self.data or self.data[guild_id]["playing"] == False:
            return await lang.tr_send(ctx, "music_not_playing")


        queue = self.data[guild_id]["queue"]
        raw_queue_data = []

        for song in queue:
            if song["data"] not in [None, "pending"]:
                song_data = await self.get_meta_data(song["data"], False)
                raw_queue_data.append(song_data)
            else:
                raw_queue_data.append({
                    "title": "Fetching...",
                    "readable_duration": "N/A"
                })

        total_pages = math.ceil(len(raw_queue_data) / 10)
        if page > total_pages:
            page = total_pages

        embed = helpers.create_embed(ctx)
        embed.title = "Queue"
        embed.set_footer(text=f"{embed.footer.text} - page {page}/{total_pages}", icon_url=ctx.author.display_avatar.url)
        thumbnail_url = self.data[guild_id]["meta_data"]["thumbnail"]
        if "https://" in thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        if len(raw_queue_data) > 0:
            field_start = round((page - 1) * 10)
            field_end = round(min(len(raw_queue_data), page * 10))
            for i in range(field_start, field_end):
                song_data = raw_queue_data[i]
                embed.add_field(
                    name=song_data["title"],
                    value=song_data["readable_duration"],
                    inline=False
                )

        else:
            embed.add_field(
                name="None",
                value=lang.tr("music_embed_empty_queue", userID=ctx.author.id, prefix=ctx.prefix),
                inline=False
            )

        await ctx.send(embed=embed)


    @commands.command(
        name="move", aliases=["psps"],
        extras={"page": "main", "category":"music"}
    )
    async def move_command(self, ctx):
        voice_channel = ctx.author.voice.channel

        if voice_channel is not None:
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            voice.pause()
            await lang.tr_send(ctx, "voice_channel_name", voice_channel_name=voice_channel.name)
            await voice.move_to(voice_channel)
            await asyncio.sleep(2)
            voice.resume()
        else:
            await lang.tr_send(ctx, "music_no_voice_channel_found")


    @commands.command(
        name="shuffle",
        brief="command_brief_shuffle",
        description="command_description_shuffle",
        extras={"page": "main", "category":"music"}
    )
    async def shuffle_command(self, ctx):
        if ctx.guild.id in self.data:
            random.shuffle(self.data[ctx.guild.id]["queue"])
        else:
            await lang.tr_send(ctx, "music_not_playing")


    @commands.command(
        name="leave", aliases=["disconnect"],
        brief="command_brief_leave",
        extras={"page": "main", "category":"music"}
    )
    async def leave_command(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if ctx.guild.id in self.data:
            del self.data[ctx.guild.id]

        if voice:
            await voice.disconnect()
            await ctx.message.add_reaction("✅")
        else:
            await lang.tr_send(ctx, "music_not_playing")


    @commands.hybrid_command(
        name="skip",
        brief="command_brief_skip",
        extras={"page": "main", "category":"music"}
    )
    async def skip_command(self, ctx):
        try:
            # this stops the song, making the next song automatically start
            discord.utils.get(self.bot.voice_clients, guild=ctx.guild).stop()
        except:
            await lang.tr_send(ctx, "error_generic")


    @commands.hybrid_command(
        name="stop",
        brief="command_brief_stop",
        extras={"page": "main", "category":"music"}
    )
    async def stop_command(self, ctx):
        if ctx.guild.id in self.data:
            del self.data[ctx.guild.id]
            await ctx.message.add_reaction("✅")
        else:
            await lang.tr_send(ctx, "music_not_playing")


    @commands.command(
        name="join",
        extras={"page": "main", "category":"music"}
    )
    async def join_command(self, ctx):
        try:
            voice_channel = ctx.author.voice.channel
            await voice_channel.connect(self_deaf=True)

        except AttributeError as e:
            await lang.tr_send(ctx, "music_no_voice_channel_found")

        except Exception as e:
            await lang.tr_send(ctx, "error_generic_with_error_passthru", error=e)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None:
            channel = before.channel
            voice = discord.utils.get(self.bot.voice_clients, guild=channel.guild)
            
            if not voice:
                return
            
            if len(channel.members) == 1:
                if channel.guild.id in self.data:
                    self.data[channel.guild.id]["queue"] = []

                if voice:
                    await voice.disconnect()
    
async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
