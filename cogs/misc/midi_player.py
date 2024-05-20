import discord
from discord.ext import commands

import subprocess
import os
from ffmpeg import FFmpeg

import librosa
import sound_to_midi

import hatsune_miku.ffmpeg_handler as ffmpeg_handler


class MidiPlayer(commands.Cog):
    def __init__(self, miku):
        self.miku = miku


    async def midifiy_audio(self, input_filename, identifier):
        # soundfont = "assets/misc/hatsune-miku-soundfont.sf2"
        soundfont = "assets/misc/miku.sf2"

        command = f"fluidsynth -nli -r 48000 -o synth.cpu-cores=2 -T oga -F temp/step1-{identifier}.ogg {soundfont} {input_filename}"
        command_array = command.split(" ")

        call = subprocess.run(command_array, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

        if isinstance(call, subprocess.CompletedProcess):
            if not await ffmpeg_handler.apply_ffmpeg_audio_filter(
                f"temp/step1-{identifier}.ogg", f"temp/step2-{identifier}.mp3",
                {},
                [],
                "loudnorm, volume=3.5"
            ): return False

            return f"temp/step2-{identifier}.mp3"

    @commands.command(
        name="midify",
        brief="hatsune miku-ify your audio files!")
    async def midify_command(self, ctx):
        file_in = "bwaa.mp3"
        file_out = "bwaa.mid"
        y, sr = librosa.load(file_in, sr=None)
        print(y)
        print("--")
        print(sr)
        print("Audio file loaded!")
        midi = sound_to_midi.monophonic.wave_to_midi(y, srate=sr)
        print("Conversion finished!")
        with open (file_out, 'wb') as f:
            midi.writeFile(f)
        print("Done. Exiting!")

        midi_filename = "bwaa.mid"

        mp3_filename = await self.midifiy_audio(midi_filename, ctx.guild.id)

        if mp3_filename:
            await ctx.send(file=discord.File(mp3_filename))
        else:
            await ctx.send("an error occured, sozzy :(")




async def setup(miku):
    await miku.add_cog(MidiPlayer(miku))
