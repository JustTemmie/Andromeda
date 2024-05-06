import discord
from discord.ext import commands

import asyncio
import aiohttp
import math
import yt_dlp

import hatsune_miku.helpers as helpers

ytdlp_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'retries': "infinite"
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdlp = yt_dlp.YoutubeDL(ytdlp_format_options)

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
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')


    @classmethod
    async def next_song(cls, player, guild_id):
        song = player.data[guild_id]["queue"].pop(0)
        
        if song["data"] == None:
            data = await player.download_song(song["url"])
        # elif song["data"] == "pending":
        #     await song["data"] != "pending":
        #         data = song["data"]
        else:
            data = song["data"]
        
        filename = data['url']
        
        player.data[guild_id]["meta_data"] = await player.get_meta_data(data)
        player.data[guild_id]["meta_data"]["ctx"] = song["ctx"]
        player.data[guild_id]["progress"] = 0        
        
        return cls(TrackedFFmpegPCMAudio(player, guild_id, filename, **ffmpeg_options), data=data)

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.miku = bot
        self.data = {}
    
    async def download_song(self, url):
        data = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdlp.extract_info(url, download=False))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        
        return data
    
    async def cache_song(self, guild_id, index = 0):
        if len(self.data[guild_id]["queue"]) == 0:
            return
        
        self.data[guild_id]["next_up"] = "pending"
        
        url = self.data[guild_id]["queue"][index]["url"]
        data = await self.download_song(url)
        
        self.data[guild_id]["queue"][index]["data"] = data
        # print(f"finished downloading cache for {url}")
    
    async def play_song(self, ctx):
        try:
            if len(self.data[ctx.guild.id]["queue"]) == 0:
                await self.send_queue_finished_embed(ctx)
                self.data[ctx.guild.id]["playing"] = False
                return
            
            self.data[ctx.guild.id]["playing"] = True
            
            
            player = await YtDlpSource.next_song(self, ctx.guild.id)
            
            ctx.voice_client.play(
                player,
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
        
    async def ensure_valid_data(self, player, guild_id):
        # make sure there's actually usable data in the data dictionary
        if guild_id not in player.data:
            player.data[guild_id] = {}
            player.data[guild_id]["playing"] = False
            player.data[guild_id]["meta_data"] = {}
            player.data[guild_id]["settings"] = {}
            player.data[guild_id]["queue"] = []
            player.data[guild_id]["progress"] = 0

    async def send_now_playing_embed(self, ctx):
        meta_data = self.data[ctx.guild.id]["meta_data"]
        
        embed = helpers.create_embed(meta_data["ctx"])
        embed.title = meta_data["title"]
        embed.description = "Now Playing"

        embed = await self.add_embed_fields(embed, meta_data)
        
        await ctx.send(embed=embed)

    async def add_embed_fields(self, embed, meta_data):
            existing_field_count = len(embed.fields)
            
            # LIVE STATUS
            if meta_data["live_status"] == "is_live":
                embed.add_field(
                    name = "Type",
                    value = "Livestream")
            
            # DURATION
            if meta_data["readable_duration"] != "unknown":
                embed.add_field(
                    name = "Duration",
                    value = meta_data["readable_duration"])
            
            # UPLOADER
            if meta_data["uploader"] != "unknown":
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
        
        data_points = ["title", "duration", "live_status", "upload_date", "uploader", "uploader_url", "thumbnail"]

        for entry in data_points:
            if entry in data:
                meta_data[entry] = data[entry]
            else:
                meta_data[entry] = "unknown"
        
        if "duration" in data:
            meta_data["readable_duration"] = helpers.format_time(data["duration"])
        else:
            meta_data["readable_duration"] = "unknown"
        
        return meta_data
    
    
    @commands.command(
        name="play",
        description="plays a song")
    async def play_command(self, ctx, *, song):
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
        
        await self.ensure_valid_data(self, guild_id)
        self.data[guild_id]["queue"].append(
            {"url": song, "data": None, "ctx": ctx}
        )

        await ctx.message.add_reaction("✅")
        
        if voice_client == None:
            await voice_channel.connect(self_deaf=True)
            await self.play_song(ctx)
        
        else:
            if voice_client.channel != voice_channel:
                await ctx.send("sorry, i'm already busy playing another banger in this guild")
                return
            
            queue = self.data[guild_id]["queue"]
            index = len(queue) - 1
            
            if self.data[guild_id]["playing"] == False:
                await self.play_song(ctx)
            else:
                await self.cache_song(guild_id, index)
                data = await self.get_meta_data(queue[index]["data"])
                
                embed = helpers.create_embed(ctx)
                embed.title = "Added song to queue"
                embed.description = data["title"]

                embed = await self.add_embed_fields(embed, data)
                
                await ctx.send(embed = embed)

    
    @commands.command(
        name="nowplaying", aliases=["now-playing", "np"],
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
        embed.description = meta_data["title"]
        
        progress = self.data[guild_id]["progress"] / 1000
        progress_bar = helpers.getProgressBar(progress, meta_data["duration"], 23)
        embed.add_field(
            name="Progress",
            value=f"{round((progress / meta_data['duration']) * 100)}% - {progress_bar}",
            inline=False
        )

        embed = await self.add_embed_fields(embed, meta_data)
        
        await ctx.send(embed = embed)

    @commands.command(name="queue", aliases=["q"])
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
        embed.set_footer(text=f"page {page}/{total_pages}", icon_url=ctx.author.display_avatar.url)
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
        name="skip",
        description="pikmin!")
    async def skip_command(self, ctx):
        # this stops the song, making the next song automatically start
        discord.utils.get(self.miku.voice_clients, guild=ctx.guild).stop()
    
    @commands.hybrid_command(
        name="stop", aliases=["leave", "disconnect"],
        description="Pikmin :(")
    async def stop_command(self, ctx):
        voice = discord.utils.get(self.miku.voice_clients, guild=ctx.guild)
        
        if ctx.guild.id in self.data:
            self.data[ctx.guild.id]["queue"] = []
            
        if voice:
            await voice.disconnect()
            await ctx.send("okay, i'll stop")
        else:
            await ctx.send("sorry, i don't seem to be in any voice channels at the moment")
        del self.data[ctx.guild.id]
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None:
            channel = before.channel
            if len(channel.members) == 1:
                if channel.guild.id in self.data:
                    voice = discord.utils.get(self.miku.voice_clients, guild=channel.guild)
        
                    self.data[channel.guild.id]["queue"] = []
                    
                    await voice.disconnect()

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
