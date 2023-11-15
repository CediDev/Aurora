from discord.ext.commands import Cog, Bot, Context, command, Command
from discord import Intents
from discord import app_commands
from discord.ext import commands, tasks
import discord
import sqlite3
from discord.ext import commands
from math import ceil
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO
import discord
from typing import Literal
import math
import datetime
import asyncio

global cur, con
con = sqlite3.connect('Main_Data_Base.db')
con.row_factory = sqlite3.Row
cur = con.cursor()
class Moderation(Cog):
  
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def warn(ctx, self, user:discord.Member, *reason:str):
        reasonstring= ' '.join(reason)
        date=datetime.datetime.now()
        d = str(date.date())
        id = self.guild.id
        values=(id, user.id, reasonstring,d,self.author.name)
        cur.execute("INSERT INTO warns(guildid,userid,reason,date,warnedby) VALUES(?,?,?,?,?)", (values))
        con.commit()
        await user.send("You've been warned.")
            
    class WarnsButton(discord.ui.View):
        def __init__(self, member, id):
            self.page = 1
            member=member
            id=id
            cur.execute(f"SELECT * FROM warns WHERE guildid=? AND userid=?",(id,member.id))
            self.items = cur.fetchall()
            self.pages = math.ceil(len(self.items) / 6)
            super().__init__()

        @discord.ui.button(label='', style=discord.ButtonStyle.green, emoji='◀️')              
        async def receive2(self, interaction:discord.Interaction, button1: discord.ui.Button):
            if self.page==1:
                self.page=self.pages
            elif self.page==None:
                self.page=self.pages
            else:
                self.page-=1
            e=discord.Embed(title=f"{name}'s warns", description="",color=discord.Color.red())
            for row in self.items[(self.page-1)*6:6*(self.page)]:
                        column1_value = row[5]
                        column3_value = row[3]
                        column4_value = row[4]
                        e.add_field(name="", value=f"Warned by: **{column1_value}**\n{column4_value}\nReason: *{column3_value}*", inline=False)
                        e.set_footer(text=f"Page {self.page}/{self.pages}")
            await interaction.response.edit_message(content="",embed=e,attachments="")
        
        @discord.ui.button(label='', style=discord.ButtonStyle.green, emoji="▶️")
        async def receive(self, interaction: discord.Interaction,button: discord.ui.Button):    
            if self.page==self.pages:
                self.page=self.pages-(self.pages-1)
            else:
                self.page+=1
            e=discord.Embed(title=f"{name}'s warns", description="",color=discord.Color.red())
            for row in self.items[(self.page-1)*6:6*(self.page)]:
                    column1_value = row[5]
                    column3_value = row[3]
                    column4_value = row[4]
                    e.add_field(name="", value=f"Warned by: **{column1_value}**\n{column4_value}\nReason: *{column3_value}*", inline=False)
                    e.set_footer(text=f"Page {self.page}/{self.pages}")
            await interaction.response.edit_message(embed=e, view=self, attachments="")
            
    @command()
    async def warns(self, ctx, member:discord.Member):
        global ids, userid,name
        ids=ctx.guild.id
        name=member.name
        userid=member.id
        cur.execute(f"SELECT * FROM warns WHERE guildid=? AND userid=?",(ids,userid))
        items = cur.fetchall()
        pages = math.ceil(len(items) / 6)
        e=discord.Embed(title=member.name+"'s warns", description="", color=discord.Color.red())
        for row in items[0:6]:
                        column1_value = row[5]
                        column3_value = row[3]
                        column4_value = row[4]
                        e.add_field(name="", value=f"Warned by: **{column1_value}**\n{column4_value}\nReason: *{column3_value}*", inline=False)
                        e.set_footer(text=f"Page 1/{pages}")
        await ctx.send(embed=e, view=Moderation.WarnsButton(member,ids))

    @command()
    async def mute(ctx, self, member:discord.Member, time, *reason:str):
        reasonstring= ' '.join(reason)
        date=datetime.datetime.now()
        d = str(date.date())
        id = self.guild.id
        values=(id, member.id, reasonstring,time,d,self.author.name)
        print(values)
        cur.execute("INSERT INTO mutes(guildid,userid,reason,duration,date,mutedby) VALUES(?,?,?,?,?,?)", (values))
        con.commit()
        cur.execute(f"SELECT muted_role FROM guild WHERE id=?",(id,))
        role = cur.fetchone()[0]
        for char in time:
            if char.isdigit():
                digit = int(char)
        for i, char in enumerate(time):
            if char == "m" or "M":
                mutetime=digit*60
            elif char == "h" or "H":
                mutetime=digit*3600
        role1=self.guild.get_role(role)
        await member.add_roles(role1)
        await asyncio.sleep(mutetime)
        await member.remove_roles(role1, reason="Mute ended")

    class MutesButton(discord.ui.View):
        def __init__(self, member, id):
            self.page = 1
            member=member
            id=id
            cur.execute(f"SELECT * FROM mutes WHERE guildid=? AND userid=?",(id,member.id))
            self.items = cur.fetchall()
            self.pages = math.ceil(len(self.items) / 6)
            super().__init__()

        @discord.ui.button(label='', style=discord.ButtonStyle.green, emoji='◀️')              
        async def receive2(self, interaction:discord.Interaction, button1: discord.ui.Button):
            if self.page==1:
                self.page=self.pages
            elif self.page==None:
                self.page=self.pages
            else:
                self.page-=1
            e=discord.Embed(title=f"{name}'s mutes", description="",color=discord.Color.red())
            for row in self.items[(self.page-1)*6:6*(self.page)]:
                        column1_value = row[6]
                        column3_value = row[3]
                        column4_value = row[4]
                        column5_value = row[5]
                        e.add_field(name="", value=f"Muted by: **{column1_value}**\n{column5_value}\nDuration: {column4_value}\nReason: *{column3_value}*", inline=False)
                        e.set_footer(text=f"Page {self.page}/{self.pages}")
            await interaction.response.edit_message(content="",embed=e,attachments="")
        
        @discord.ui.button(label='', style=discord.ButtonStyle.green, emoji="▶️")
        async def receive(self, interaction: discord.Interaction,button: discord.ui.Button):    
            if self.page==self.pages:
                self.page=self.pages-(self.pages-1)
            else:
                self.page+=1
            e=discord.Embed(title=f"{name}'s mutes", description="",color=discord.Color.red())
            for row in self.items[(self.page-1)*6:6*(self.page)]:
                        column1_value = row[6]
                        column3_value = row[3]
                        column4_value = row[4]
                        column5_value = row[5]
                        e.add_field(name="", value=f"Muted by: **{column1_value}**\n{column5_value}\nDuration: {column4_value}\nReason: *{column3_value}*", inline=False)
                        e.set_footer(text=f"Page {self.page}/{self.pages}")
            await interaction.response.edit_message(embed=e, view=self, attachments="")

    @command()
    async def mutes(self, ctx, member:discord.Member):
        cur.execute(f"SELECT * FROM mutes WHERE guildid=? AND userid=?",(ctx.guild.id, member.id))
        items = cur.fetchall()
        id = ctx.guild.id
        pages = math.ceil(len(items) / 6)
        e=discord.Embed(title=member.name+"'s mutes", description="", color=discord.Color.red())
        for row in items[0:6]:
                        column1_value = row[6]
                        column3_value = row[3]
                        column4_value = row[4]
                        column5_value = row[5]
                        e.add_field(name="", value=f"Muted by: **{column1_value}**\n{column5_value}\nDuration: {column4_value}\nReason: *{column3_value}*", inline=False)
                        e.set_footer(text=f"Page 1/{pages}")
        await ctx.send(embed=e, view=Moderation.MutesButton(member,id))   

async def setup(bot: Bot):
        await bot.add_cog(Moderation(bot))
    