import discord
from discord.ext import commands, tasks
from yt_dlp import YoutubeDL
import asyncio
import tomllib
from random import choice
from e621 import E621
from rule34Py import rule34Py

with open("config.toml", "rb") as f:
    data = tomllib.load(f)

TOKEN = data['disc_token']
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=';', intents=intents)
client.remove_command('help')

##############################

@client.event
async def on_ready():
    change_status.start()
    print("=========================")
    print(f" Running Shikinha...")
    print(f" Ping {round(client.latency * 1000)}ms")
    print("=========================")

@tasks.loop(minutes=4)
async def change_status():
    sts = {1:[discord.ActivityType.playing, ";help 📜"],
        2:[discord.ActivityType.watching, "a vida passar 🍃"],
        3:[discord.ActivityType.watching, "A Revolução das maquinas 🤖"], 
        4:[discord.ActivityType.watching, "o mundo queimar 🔥"],
        5:[discord.ActivityType.listening, "RADIOHEAD 🎵🔥"],
        6:[discord.ActivityType.playing, "SNAKE 🐍"],
        7:[discord.ActivityType.playing, "o lixo fora 🚮"]}
    chosen_state = sts[choice(range(1, len(sts) + 1))]
    
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=chosen_state[0], name=chosen_state[1]))

async def main():
    await client.start(TOKEN)

############ REGULAR STUFF #############

@client.command(aliases=["h"])
async def help(ctx):
    embed = discord.Embed(
        title = ":sparkles: COMANDOS :sparkles: ",
        description=" (Meu prefixo é ';')",
        colour = discord.Colour.from_rgb(177, 164, 154)
    )
    embed.set_footer(text=f"Shikinha")

    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/767002076257452053/758bef70a617ebb543bcf154341a5e5a.png?size=1024")
    embed.add_field(name="help", value="● Retorna a minha lista de Comandos.", inline=False)
    embed.add_field(name="ping", value="● Retorna a latência em milissegundos.", inline=False)
    embed.add_field(name="play <link>", value="● Busca no Youtube pelo áudio desejado (<link>).", inline=False)
    embed.add_field(name="skip", value="● Pula para o próximo áudio.", inline=False)
    embed.add_field(name="pause", value="● Pausa o áudio atual.", inline=False)
    embed.add_field(name="resume", value="● Retoma o áudio atual.", inline=False)
    embed.add_field(name="leave", value='● Desconecta o bot do canal de voz.', inline=False)
    embed.add_field(name="rule34 <tags>   (NSFW)", value="● Pesquisa um post aleatório no Rule34 que possua as tags <tags>.", inline=False)
    embed.add_field(name="e621 <tags>     (NSFW)", value="● Pesquisa um post aleatório no E621 que possua as tags <tags>.", inline=False)

    await ctx.message.add_reaction("📜")
    await ctx.send(embed=embed)

@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! **{round(client.latency * 1000)}ms**")

############## NSFW ##################

@client.command(aliases=["e621"])  # NSFW
async def e6(ctx, *, tags):
    api = E621()

    posts = api.posts.search(f"{str(tags)} -webm")
    post = choice(posts)
    img = post.file_obj.url
    
    tags_obj = post.tags
    tags = tags_obj.general + tags_obj.species + tags_obj.character + tags_obj.copyright + tags_obj.invalid + tags_obj.lore + tags_obj.artist
    tags = " ".join(tags)

    embed = discord.Embed(colour = discord.Colour.from_rgb(2, 54, 102))
    embed.set_image(url=f"{img}")
    embed.set_footer(text=f"Tags: {tags}")

    await ctx.send(embed=embed)

@client.command(aliases=["rule34", "r3"])  # NSFW
async def r34(ctx, *, tags):
    tags = tags.split()

    while("video" in tags):
        tags.remove("video")
    tags.append("-video")
    
    r34Py = rule34Py()

    result_random = r34Py.random_post(tags)
    img = result_random.image
    tags = result_random._tags   
    tags = " ".join(tags)

    embed = discord.Embed(colour = discord.Colour.from_rgb(170, 229, 164))
    embed.set_image(url=f"{img}")
    embed.set_footer(text=f"Tags: {tags}")
    
    await ctx.send(embed=embed)
    

########### MUSIC COMMANDS #############

# configs do yt_dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'extractaudio': True,
    'audioformat': 'mp3',
    'default_search': 'ytsearch',  # Busca no YouTube se não for URL
    'max_downloads': 1,  # Limita a busca ao primeiro resultado
}

# dict para armazenar filas de músicas por servidor (guild.id)
queues = {}
queue_locks = {}


async def play_next(ctx):
    # Verifica se há músicas na fila
    if ctx.guild.id in queues and len(queues[ctx.guild.id]) > 0:
        song = queues[ctx.guild.id].pop(0)  # Pega a próxima música na fila
        url2 = song['url']
        channel = ctx.author.voice.channel

        if not ctx.voice_client:
            vc = await channel.connect()
        else:
            vc = ctx.voice_client

        try:
            vc.play(discord.FFmpegPCMAudio(url2, 
                before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -loglevel warning', 
                options='-maxrate 1M -bufsize 1M'), 
                after=lambda e: client.loop.create_task(play_next(ctx))
            )
        except Exception as e:
            print(e)
            await vc.disconnect()
    else:
        await ctx.voice_client.disconnect()

@client.command(aliases=["p", "tocar"])
async def play(ctx, *, url):
    # Inicializa a fila e o lock para o servidor se não existirem
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    if ctx.guild.id not in queue_locks:
        queue_locks[ctx.guild.id] = asyncio.Lock()

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except:
            await ctx.reply(f"❌ Ocorreu um erro ao buscar o vídeo.")
            return
        
        if 'entries' in info:
            info = info['entries'][0]

        url2 = info['url']
        title = info.get('title', 'Título não encontrado')
    
    async with queue_locks[ctx.guild.id]:
        queues[ctx.guild.id].append({
            'title': title,
            'url': url2
        })

    if not ctx.voice_client:
        embed = discord.Embed(
            title="🎙️ 🎶 Tocando agora...",
            description=f"{title}",
            colour=discord.Colour.from_rgb(93, 173, 236))
        await ctx.message.add_reaction("🎶")
        await ctx.reply(embed=embed)
        await play_next(ctx)

    else:
        embed = discord.Embed(
            title="✋ Na fila...",
            description=f"{title}",
            colour=discord.Colour.from_rgb(255, 220, 93))
        await ctx.message.add_reaction("🎶")
        await ctx.reply(embed=embed)

@client.command()
async def leave(ctx):
    if ctx.voice_client:

        async with queue_locks[ctx.guild.id]:
            queues[ctx.guild.id].clear()

        await ctx.voice_client.disconnect()
    else:
        await ctx.reply("O bot não está em um canal de voz.")

@client.command(aliases=['s', 'pular'])
async def skip(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.message.add_reaction("👍")
        await play_next(ctx)
    else:
        await ctx.reply("Não há música tocando no momento.")

@client.command(aliases=['pausa', 'stop'])
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.message.add_reaction("⏸️")
    else:
        await ctx.reply("Não há música tocando no momento.")

@client.command(aliases=['unpause'])
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.message.add_reaction("▶️")
    else:
        await ctx.reply("Não há música pausada no momento.")

######################################

asyncio.run(main())

