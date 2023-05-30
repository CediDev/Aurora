import discord
from discord.ext import commands
from discord.ext.commands import Cog, Bot, Context, command, Command
import discord.ext.commands
from discord import app_commands
import asyncio
import sqlite3
from math import ceil
from discord import Button, ButtonStyle
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO





class Events(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    global cur, con
    con = sqlite3.connect('Main_Data_Base.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()    
    
    
    class ThreadButton(discord.ui.View):
        @discord.ui.button(label='Click', style=discord.ButtonStyle.danger)
        async def receive(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message("We made a ticket for you " + str(interaction.user), ephemeral=True)
            global user
            user = (interaction.user)
            y=0
            while discord.utils.get(threadname.threads, name=(f"Help{y}")) is not None:
                y += 1
            else:
                await threadname.create_thread(name=f"Help{y}")
                thread = discord.utils.get(threadname.threads, name=f"Help{y}")
                print(thread)
                cur.execute(f"UPDATE user SET thread={thread.id} WHERE id={interaction.user.id}")
                global afterthread
                afterthread = discord.utils.get(threadname.threads, name=(f"Help{y}"))
                await user.send("Hello! You can write something here, admins and mods will see your message copied and sent by bot, so don't worry - you are completely anonymous.")
    
    @command()  #setting channel for help tickets
    async def thread(self, ctx, id:int):
        global threadid
        print(int(id))
        threadid=int(id)
        print(threadid)
        global threadname
        threadname = self.bot.get_channel(threadid)
    
    
    
    @command() #makes a button used to create anonymous tickets
    async def Help(self,ctx: commands.Context):
        await ctx.send('In need of anonymous help?', view=Events.ThreadButton())  
        print(self)
    
    @Cog.listener("on_message")     
    async def listener_two(self, message):
        channel = self.bot.get_channel(threadid)
        if message.author.id != 1060907451878211624:    #checks if the message's author is a bot
            if message.guild is None:
                cur.execute(f"SELECT thread FROM user where id={message.author.id}")
                dm_to_thread = cur.fetchone()[0]
                print(dm_to_thread)
                if dm_to_thread is not None:
                    channel1 = discord.utils.get(channel.threads, id=dm_to_thread)
                    await channel1.send("Anonymous said: " + message.content)
            else:
                channel_threads = [thread.id for thread in channel.threads]
                if message.channel.id in channel_threads:
                    cur.execute(f"SELECT id FROM user WHERE thread={message.channel.id}")
                    anon_user_id = cur.fetchone()
                    if anon_user_id is not None:
                        anon_user_id1 = anon_user_id[0]
                        anon_user = self.bot.get_user(anon_user_id1) 
                        await anon_user.send(message.content)


    @Cog.listener("on_message")        #exp and levels system
    async def listener_one(self, message):
      if message.content.startswith("!"):
          print("Detected a command!")
      else:    
        if message.author.id == 1060907451878211624:   #checks if the message's author is a bot
            print("Detected a bot's message!")
        else:
            cur.execute("SELECT level_id FROM user WHERE id=?", (message.author.id,))
            level_id = cur.fetchone()[0] +1
            cur.execute("SELECT min_exp FROM level WHERE id=?", (level_id,))
            minimal_exp = cur.fetchone()[0]
            cur.execute("SELECT exp FROM user WHERE id=?", (message.author.id,))
            user_exp = cur.fetchone()[0]
            wynik_exp = user_exp + 1
            if wynik_exp < minimal_exp:
                cur.execute("UPDATE user SET exp=? WHERE id=?", (wynik_exp, message.author.id))
                con.commit()
            elif wynik_exp == minimal_exp:
                cur.execute("UPDATE user SET exp=? WHERE id=?", (wynik_exp, message.author.id))
                cur.execute("UPDATE user SET level_id=? WHERE id=?", (level_id, message.author.id))
                con.commit()
                embed=discord.Embed(title="Level up!",description=f"Congratulations {user.display_name}, you achieved {level_id} level!")
                channel = self.bot.get_channel(message.channel.id)
                await channel.send(embed=embed)
    
    
    @Cog.listener()          #listener greets new members and adds them to mySQL data base.
    async def on_member_join(self, member:discord.Member):    
        channel = self.bot.get_channel(greetings_channel)
        embed=discord.Embed(title=f"Welcome!",description=f"{member.mention} have just joined to our server!")
        print(member.id)
        user_stats = (int(member.id), member.display_name,1,1)
        cur.execute('INSERT INTO user VALUES(?, ?, ?)', user_stats)
        con.commit()
        if sqlite3.IntegrityError:
            print("Record Already Exists")
        await channel.send(embed=embed)

    @command()  #sets channel used to greet new members
    async def set_greeting_channel(self, id):
        global greetings_channel
        greetings_channel = id


async def setup(bot: Bot):
    await bot.add_cog(Events(bot))
 