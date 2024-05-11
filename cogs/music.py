import discord
from discord.ext import commands

import asyncio
import aiohttp
import yt_dlp

import re
import time
import math
import random

import hatsune_miku.helpers as helpers
import hatsune_miku.user_input as user_input

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
    def __init__(self, miku):
        self.miku = miku
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
                    message_content = f"downloading data for song {progress+2}/{total+2}, this might take a while..."
                    
                    if sent_messages[ctx.message.id] == None:
                        job = asyncio.run_coroutine_threadsafe(ctx.reply(mention_author=False, content=message_content), self.miku.loop)
                        sent_messages[ctx.message.id] = job.result()
                    
                    elif progress % 5 == 0 or progress == total:
                        job = asyncio.run_coroutine_threadsafe(sent_messages[ctx.message.id].edit(content=message_content), self.miku.loop)
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
                    self.miku.loop)
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
            duration = "unknown"
        
        # make sure that the progress is at the latest 1 second before the end of the song
        if type(duration) == int:
            progress = min(progress, duration * 1000 - 1000)
        else:
            progress -= 1000
        
        
        old_player = self.data[guild_id]["player"]
        old_options = self.data[guild_id]["ffmpeg_options"]["options"]
        start_time = time.time()
        
        self.data[guild_id]["ffmpeg_options"]["options"] = f"-vn -ss {progress/1000} -af 'loudnorm, volume=0.4 {filter}'"
        
        async def play_song_clear_seeking(self, ctx):
            # if the song played for a second, it probably had good ffmpeg arguments lol
            if time.time() - start_time > 1:
                self.data[ctx.guild.id]["seeking"] = False
                await self.play_song(ctx)
            else:
                await ctx.send(f"an error occured whilst changing filters, reseting them back")
                self.data[guild_id]["ffmpeg_options"]["options"] = old_options
                self.data[guild_id]["player"] = old_player
                ctx.voice_client.play(
                    self.data[guild_id]["player"],
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.play_song(ctx), self.miku.loop
                    )
                )
                
                self.data[guild_id]["progress"] = progress
                
        
        new_player = await YtDlpSource.get_player(self, guild_id, self.data[guild_id]["song"])
        ctx.voice_client.pause()
        self.data[guild_id]["player"] = new_player
        
        ctx.voice_client.play(
            self.data[guild_id]["player"],
            after=lambda e: asyncio.run_coroutine_threadsafe(
                play_song_clear_seeking(self, ctx), self.miku.loop
            )
        )
        
        self.data[guild_id]["progress"] = progress
        

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
            
            ctx.voice_client.play(
                self.data[guild_id]["player"],
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_song(ctx), self.miku.loop
                )
            )

            await self.send_now_playing_embed(ctx)


        except Exception as err:
            error = f"whoopsie, it looks like i encountered an error whilst trying to play your song\n{type(err)}:\n```{err}```"
            print(error)
            await ctx.send(error)


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
        embed.description = "Now Playing"

        embed = await self.add_embed_fields(embed, meta_data)

        await ctx.send(embed=embed)

    async def add_embed_fields(self, embed, meta_data):
            existing_field_count = len(embed.fields)
            
            try:
                # LIVE STATUS
                if meta_data["live_status"] == "is_live":
                    embed.add_field(
                        name = "Type",
                        value = "Livestream")

                # DURATION
                if "readable_duration" in meta_data and meta_data["readable_duration"] != "unknown":
                    embed.add_field(
                        name = "Duration",
                        value = meta_data["readable_duration"])

                # UPLOADER
                if meta_data["uploader"] != "unknown":
                    if meta_data["uploader_url"] in ["unknown", "None", None]:
                        embed.add_field(
                            name="Uploader",
                            value=meta_data['uploader'])
                    else:
                        embed.add_field(
                            name="Uploader",
                            value=f"[{meta_data['uploader']}]({meta_data['uploader_url']})")


                # LIKE DISLIKE RATIO
                if meta_data["dislikes"] != "unknown":
                    embed.add_field(
                        name="Likes / Dislikes",
                        value=f"{meta_data['likes']} / {meta_data['dislikes']}",
                    )


                # VIEW COUNT
                if meta_data["views"] != "unknown":
                    embed.add_field(
                        name="views",
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
                    name="an error occured - a field is missing :(",
                    value=e
                )


            return embed

    async def send_queue_finished_embed(self, ctx):
        embed = helpers.create_embed(ctx)

        embed.title = "Queue Finished"
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
        name="play",
        aliases=["sing"],
        bfier="play a song",
        description="accepts any URL, direct attatchments, and keywords to search for")
    async def play_command(self, ctx, *, search_query = None):
        if search_query == None:
            if len(ctx.message.attachments) == 0:
                await ctx.send("sorry, that's not a valid search query")
                return

            search_query = ctx.message.attachments[0].url
            
        try:
            voice_channel = ctx.author.voice.channel

        except AttributeError as e:
            await ctx.send("couldn't find the voice channel you're in, perhaps you're not in a voice channel?")
            return

        except Exception as e:
            await ctx.send(f"an exception was thrown:\n{e}")
            return

        voice_client = discord.utils.get(self.miku.voice_clients, guild=ctx.guild) # This allows for more functionality with voice channels
        guild_id = ctx.guild.id

        if voice_client != None:
            if voice_client.channel != voice_channel:
                await ctx.send("sorry, i'm already busy playing bangers somewhere else in this guild")
                return


        await self.ensure_valid_data(guild_id)
        await ctx.message.add_reaction("✅")
        
        song_data = await self.download_song(search_query, ctx)

        # with open ("example_data.json", "w") as f:
        #     import json
        #     json.dump(song_data, f)

        async def add_playlist(ctx, song_data):
            if len(song_data["entries"]) == 0:
                return
            
            for entry in song_data["entries"]:
                self.data[guild_id]["queue"].append(
                    {"data": entry,
                    "ctx": ctx}
                )

            if len(song_data["entries"]) > 2:
                embed = helpers.create_embed(ctx)
                embed.title = f"Added {len(song_data['entries']) + 2} songs to queue"

                await ctx.send(embed = embed)


        async def add_song(ctx, song_data):
            if "entries" in song_data:
                song_data = song_data["entries"][0]

            self.data[guild_id]["queue"].append(
                {"data": song_data,
                "ctx": ctx}
            )

            if self.data[guild_id]["playing"]:
                meta_data = await self.get_meta_data(song_data)
                embed = helpers.create_embed(ctx)
                embed.title = "Added song to queue"
                embed.description = meta_data["title"]

                embed = await self.add_embed_fields(embed, meta_data)

                await ctx.send(embed = embed)


        add_full_playlist = False
        playlist_download_count = 50
        if "entries" in song_data and len(song_data["entries"]) > 1:
            await ctx.reply(f"hey, would you like to play the entire playlist instead of just the first track?\n\nautomatically adding first track: <t:{round(time.time()) + 15}:R>")
            add_full_playlist = await user_input.get_consent(self.miku, ctx, 17, ", adding the first track only")

            if add_full_playlist:
                await add_playlist(ctx, song_data)
                
                if ctx.author.id in self.miku.config["TRUSTED_IDS"]:
                    await ctx.reply(f"how many songs would you like to add?")
                    response = await user_input.get_input(self.miku, ctx, 10, f", deafaulting to {playlist_download_count}")
                    try:
                        response = int(response.content)
                        playlist_download_count = response
                    except:
                        await ctx.send(f"sorry, that doesn't seem like a valid integer, defaulting to {playlist_download_count}")

            # take first item from a playlist
            else:
                await add_song(ctx, song_data)

        else:
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
        brief="apply an ffmpeg filter",
        description="quite a complicated command, for technical reasons it's given to ffmpeg as `-af 'loudnorm, volume=0.4 {filter}'`, so your filter will need to start with a leading comma"
        )
    async def filter_command(self, ctx, filter = ""):
        voice_channel = ctx.author.voice.channel

        if voice_channel is not None:
            voice = discord.utils.get(self.miku.voice_clients, guild=ctx.guild)
            if voice is not None:
                await self.change_ffmpeg_filter(ctx, filter)
            else:
                await ctx.send("uhhh, some error happen :( - sozzy")
        else: 
            await ctx.send("it doesn't seem like you're in a voice channel")


    @commands.hybrid_command(
        name="now-playing", aliases=["nowplaying", "np"],
        description="In case you're wondering what song i'm playing")
    async def nowplaying_command(self, ctx):
        guild_id = ctx.guild.id
        if not guild_id in self.data or self.data[guild_id]["playing"] == False:
            await ctx.send("sorry, i'm currently not playing any songs within this server")
            return

        if "meta_data" not in self.data[guild_id]:
            return

        meta_data = self.data[guild_id]["meta_data"]

        embed = helpers.create_embed(ctx)
        embed.title = "Currently Playing"
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
            name="Progress",
            value=embed_value,
            inline=False
        )

        embed = await self.add_embed_fields(embed, meta_data)

        await ctx.send(embed = embed)


    @commands.hybrid_command(name="queue", aliases=["q"])
    async def queue_command(self, ctx, page = 1):
        if type(page) != int:
            return await ctx.send(f"{page} is not a valid page number")

        guild_id = ctx.guild.id
        if not guild_id in self.data or self.data[guild_id]["playing"] == False:
            return await ctx.send("sorry, i'm currently not playing any songs within this server")


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
                value=f"The queue is currently empty, go ahead and add some songs with `{ctx.prefix}play`",
                inline=False
            )

        await ctx.send(embed=embed)


    @commands.command(name="move", aliases=["psps"])
    async def move_command(self, ctx):
        voice_channel = ctx.author.voice.channel

        if voice_channel is not None:
            voice = discord.utils.get(self.miku.voice_clients, guild=ctx.guild)
            voice.pause()
            await ctx.send(f"oke, moving to {voice_channel.name}")
            await voice.move_to(voice_channel)
            await asyncio.sleep(2)
            voice.resume()
        else:
            await ctx.send("it doesn't seem like you're in a voice channel")


    @commands.command(
        name="shuffle",
        brief="shuffle the playlist",
        description="shuffle the currently playing music playlist")
    async def shuffle_command(self, ctx):
        if ctx.guild.id in self.data:
            random.shuffle(self.data[ctx.guild.id]["queue"])
        else:
            await ctx.send("there's currently no queue in this server")


    @commands.command(
        name="leave", aliases=["disconnect"],
        description="Leave the VC and stop playing music")
    async def leave_command(self, ctx):
        voice = discord.utils.get(self.miku.voice_clients, guild=ctx.guild)

        if ctx.guild.id in self.data:
            del self.data[ctx.guild.id]

        if voice:
            await voice.disconnect()
            await ctx.message.add_reaction("✅")
        else:
            await ctx.send("sorry, i don't seem to be in any voice channels at the moment")


    @commands.hybrid_command(
        name="skip",
        description="skipero!")
    async def skip_command(self, ctx):
        try:
            # this stops the song, making the next song automatically start
            discord.utils.get(self.miku.voice_clients, guild=ctx.guild).stop()
        except:
            await ctx.send("an error has occured")


    @commands.hybrid_command(
        name="stop",
        description="Stop playing music")
    async def stop_command(self, ctx):
        if ctx.guild.id in self.data:
            del self.data[ctx.guild.id]
            await ctx.message.add_reaction("✅")
        else:
            await ctx.send("sorry, i don't seem to be playing anything right now")


    @commands.command(
        name="join",
        description="make me psps myself over to you")
    async def join_command(self, ctx):
        try:
            voice_channel = ctx.author.voice.channel
            await voice_channel.connect(self_deaf=True)

        except AttributeError as e:
            await ctx.send("couldn't find the voice channel you're in, perhaps you're not in a voice channel?")

        except Exception as e:
            await ctx.send(f"an exception was thrown:\n{e}")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None:
            channel = before.channel
            if len(channel.members) == 1:
                if channel.guild.id in self.data:
                    voice = discord.utils.get(self.miku.voice_clients, guild=channel.guild)

                    self.data[channel.guild.id]["queue"] = []

                    if voice:
                        await voice.disconnect()

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
