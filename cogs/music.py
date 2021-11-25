import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
    
        #all the music related stuff
        self.is_playing = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = ""

     #searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

     #searching the playlist on youtube
    def search_pl_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                infos =  ydl.extract_info(item, download=False)['entries']
            except Exception: 
                return False

        songlist = list()
        
        for info in infos:
          songlist.append({'source': info['formats'][0]['url'], 'title': info['title']})

        return songlist

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # infinite loop checking 
    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            
            #try to connect to voice channel if you are not already connected

            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])
            
            print(self.music_queue)
            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
            await self.vc.disconnect()

    @commands.command(name="help",alisases=['ajuda'],help="Central tu é burro.")
    async def help(self,ctx):
        helptxt = ''
        for command in self.client.commands:
            helptxt += f'**{command}** - {command.help}\n'
        embedhelp = discord.Embed(
            colour = 1646116,#grey
            title=f'Comandos do {self.client.user.name}',
            description = helptxt
        )
        embedhelp.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embedhelp)


    @commands.command(name="play", help="Se pah toca uma música do YouTube.",aliases=['p','tocar'])
    async def p(self, ctx, *args):
        query = " ".join(args)
        
        try:
            voice_channel = ctx.author.voice.channel
        except:
        #if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Tu é burro né irmão, entra num canal ai antes.'
            )
            await ctx.send(embed=embedvc)
            return
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                embedvc = discord.Embed(
                    colour= 12255232,#red
                    description = 'Tu cago tudo! Escreve o nome da musica direito, se mesmo assim não der certo tu se fudeu irmão, não tem como toca essa porra ai.'
                )
                await ctx.send(embed=embedvc)
            else:
                embedvc = discord.Embed(
                    colour= 32768,#green
                    description = f"Irmão tu ponho a música **{song['title']}** na fila."
                )
                await ctx.send(embed=embedvc)
                self.music_queue.append([song, voice_channel])
                
                if self.is_playing == False:
                    await self.play_music()

    @commands.command(name="playlist", help="Se pah adiciona varias música de uma playlist do Youtube na fila.", aliases=['pli'])
    async def pl(self, ctx, *args):
        query = " ".join(args)
        
        try:
            voice_channel = ctx.author.voice.channel
        except:
        #if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Tu é burro né irmão, entra num canal ai antes.'
            )
            await ctx.send(embed=embedvc)
            return
        else:
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Irmão perai, to puxando os cabo da quebrada pra baixa no aries tudo essas musica ai que tu boto. Se travar a musica que ta tocando o problema é teu, burro.'
            )
            await ctx.send(embed=embedvc)

            songlist = self.search_pl_yt(query)

            if type(songlist) == type(True):
                embedvc = discord.Embed(
                    description = 'Tu cago tudo! Copia o link da playlist direito, se mesmo assim não der certo tu se fudeu irmão, não tem como toca essa porra ai.'
                )
                await ctx.send(embed=embedvc)
            else:
                for song in songlist:                  
                  self.music_queue.append([song, voice_channel])
                
                embedvc = discord.Embed(
                    colour= 32768,#green
                    description = f'Irmão tu ponho uma playlist INTEIRA com FUCKING {len(songlist)} MUSICAS na fila, espero que esteja satisfeito.'
                )
                await ctx.send(embed=embedvc)

                if self.is_playing == False:
                    await self.play_music()

    @commands.command(name="queue", help="Explana as músicas da fila.",aliases=['q','fila'])
    async def q(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f'**{i+1} - **' + self.music_queue[i][0]['title'] + "\n"

        print(retval)
        if retval != "":
            embedvc = discord.Embed(
                colour= 12255232,
                description = f"{retval}"
            )
            await ctx.send(embed=embedvc)
        else:
            embedvc = discord.Embed(
                colour= 1646116,
                description = 'Irmão não tem nada pra toca aqui, se toca.'
            )
            await ctx.send(embed=embedvc)

    @commands.command(name="skip", help="Pula a atual música de bosta que está tocando.",aliases=['pular'])
    @commands.has_permissions(manage_channels=True)
    async def skip(self, ctx):
        if self.vc != "" and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music()
            embedvc = discord.Embed(
                colour= 1646116,#ggrey
                description = f"Você pulou essa porcaria que colocaram e chamam de música."
            )
            await ctx.send(embed=embedvc)

    @commands.command(name="clear", help="Limpa todas as musicas pq um merda fez cagada.", aliases=['limpar','cl'])
    @commands.has_permissions(manage_channels=True)
    async def clear(self, ctx):
        if self.vc != "" and self.vc:
            self.music_queue = []
            embedvc = discord.Embed(
                colour= 1646116,#ggrey
                description = f"Ja era tudo as musica que tava na fila, perdeu playboy."
            )
            await ctx.send(embed=embedvc)

    @skip.error #Erros para kick
    async def skip_error(self,ctx,error):
        if isinstance(error, commands.MissingPermissions):
            embedvc = discord.Embed(
                colour= 12255232,
                description = f"Irmão tu não pode pula música, tu é um merda meu irmão. Só quem pode **Gerenciar canais** pode pular músicas."
            )
            await ctx.send(embed=embedvc)     
        else:
            raise error

def setup(client):
    client.add_cog(music(client))