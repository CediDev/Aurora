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
import time





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
            global user, guildid2, threadid, threadname
            user = (interaction.user)
            y=0
            guildid2=interaction.user.guild.id
            cur.execute(f"SELECT help_ch FROM users WHERE id={self.message.guild.id}")
            threadid=cur.fetchone()[0]
            threadname=self.bot.get_channel(threadid)
            while discord.utils.get(threadname.threads, name=(f"Help{y}")) is not None:
                y += 1
            else:
                await threadname.create_thread(name=f"Help{y}")
                thread = discord.utils.get(threadname.threads, name=f"Help{y}")
                cur.execute(f"UPDATE users SET thread={thread.id} WHERE id={interaction.user.id} AND guildid={guildid2}")
                global afterthread
                afterthread = discord.utils.get(threadname.threads, name=(f"Help{y}"))
                await user.send("Hello! You can write something here, admins and mods will see your message copied and sent by bot, so don't worry - you are **completely anonymous**. Their replies will show up here.")

    
    @command() #makes a button used to create anonymous tickets
    async def Help(self,ctx: commands.Context):
        await ctx.send('In need of anonymous help?', view=Events.ThreadButton())  
        print(self)
    
    @Cog.listener("on_message")     
    async def listener_two(self, message):
        try:
            channel = self.bot.get_channel(threadid)
            guildid=message.guild.id
            if channel.threads is not None and message.author.id != 1060907451878211624:    #checks if the message's author is a bot
                if message.guild is None:
                    cur.execute(f"SELECT thread FROM users where id=? AND guildid=?",(message.author.id,guildid2))
                    dm_to_thread = cur.fetchone()[0]
                    if dm_to_thread is not None:
                        channel1 = discord.utils.get(channel.threads, id=dm_to_thread)
                        await channel1.send("Anonymous said: " + message.content)
                else:
                    channel_threads = [thread.id for thread in channel.threads]
                    if message.channel.id in channel_threads:
                        cur.execute(f"SELECT id FROM users WHERE thread={message.channel.id} AND guildid={guildid}")
                        anon_user_id = cur.fetchone()
                        if anon_user_id is not None:
                            anon_user_id1 = anon_user_id[0]
                            anon_user = self.bot.get_user(anon_user_id1) 
                            await anon_user.send(message.content)
        except NameError:
            pass

    @Cog.listener("on_message")        #exp and levels system
    async def listener_one(self, message):
        guildid=message.guild.id
        if not message.content.startswith("!") and message.author.id != 1060907451878211624:
            cur.execute("SELECT mtime FROM users WHERE id=? AND guildid=?", (message.author.id,guildid))
            last_message_time = cur.fetchone()[0]
            current_message_time = time.time()
            if last_message_time == None:
                cur.execute("UPDATE users SET mtime=? WHERE id=? AND guildid=?", (current_message_time, message.author.id, guildid))
                con.commit()
            else:               
                if current_message_time - last_message_time >=30:
                    cur.execute("UPDATE users SET mtime=? WHERE id=? AND guildid=?", (current_message_time, message.author.id, guildid))
                    con.commit()
                    cur.execute("SELECT levelid FROM users WHERE id=? AND guildid=?", (message.author.id,guildid))
                    level_id = cur.fetchone()[0] +1
                    cur.execute("SELECT min_exp FROM level WHERE id=?", (level_id,))
                    minimal_exp = cur.fetchone()[0]
                    cur.execute("SELECT exp FROM users WHERE id=? AND guildid=?", (message.author.id,guildid))
                    user_exp = cur.fetchone()[0]
                    xr = random.randint(3, 5)
                    wynik_exp = user_exp + xr
                    if wynik_exp < minimal_exp:
                        cur.execute("UPDATE users SET exp=? WHERE id=? AND guildid=?", (wynik_exp, message.author.id, guildid))
                        con.commit()
                    elif wynik_exp == minimal_exp:
                        cur.execute("UPDATE users SET exp=? WHERE id=? AND guildid=?", (wynik_exp, message.author.id, guildid))
                        cur.execute("UPDATE users SET level_id=? WHERE id=? AND guildid=?", (level_id, message.author.id, guildid))
                        con.commit()
                        embed=discord.Embed(title="Level up!",description=f"Congratulations {user.display_name}, you achieved {level_id} level!")
                        channel = self.bot.get_channel(message.channel.id)
                        await channel.send(embed=embed)
    
    
    @Cog.listener()          #listener greets new members and adds them to mySQL data base.
    async def on_member_join(ctx, member:discord.Member):    
        cur.execute(f"SELECT greet_ch FROM guild WHERE id={int(member.guild.id)}")
        greetings_channel = cur.fetchone()[0]
        channel = ctx.bot.get_channel(greetings_channel)    
        embed=discord.Embed(title=f"Welcome!",description=f"{member.mention} have just joined to our server!")
        user_stats = (int(member.id),int(member.guild.id),member.name,0,0,0,0,0)
        cur.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?,?)', user_stats)
        con.commit()
        if sqlite3.IntegrityError:
            print("Record Already Exists")
        await channel.send(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(Events(bot))
 