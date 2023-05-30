from discord.ext.commands import Cog, Bot, Context, command
from discord import Intents
from discord import app_commands
import discord
import sqlite3
from discord.ext import commands
from math import ceil
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO

global cur, con
con = sqlite3.connect('Main_Data_Base.db')
con.row_factory = sqlite3.Row
cur = con.cursor()
class Commands(Cog):
  
  def __init__(self, bot: Bot):
    self.bot = bot

  @command()
  async def points(self, ctx: Context,a:str,b:int,member:discord.Member = None):
        if member == None:
            await ctx.send("Wrong command! Please use ``!points add/remove <value> <@username>``")
        elif a == "add":
            cur.execute("SELECT points FROM user WHERE id=?", (ctx.author.id,))
            user_points = cur.fetchone()[0]
            user_points_after = user_points + b
            cur.execute("UPDATE user SET points=? WHERE id=?", (user_points_after, ctx.author.id))
            con.commit()
        elif a == "remove":
            cur.execute("SELECT points FROM user WHERE id=?", (ctx.author.id,))
            user_points = cur.fetchone()[0]
            user_points_after = user_points - b 
            cur.execute("UPDATE user SET points=? WHERE id=?", (user_points_after, ctx.author.id))
            con.commit()
  @points.error
  async def on_points_error(self, ctx: Context, error: commands.MissingRequiredArgument) -> None:
    await ctx.send("Wrong command! Please use ``!points add/remove <value> <@username>``")

  @command() #will make shop and economy system soon
  async def shop(self, ctx):
      embed=discord.Embed(title="Shop page x", description="Here you can buy some stuff!", color=discord.Color.yellow())
      embed.set_author(name="")
      embed.set_thumbnail(url="")
      embed.add_field(name="[1] TimeOut someone!", value="You can mute someone for 6 hours :)", inline=True)
      embed.add_field(name="[2] Gamba!", value="Use Wheel of Fortune! Disclaimer: you can win temporary ban :flushed:", inline=False)
      embed.add_field(name="", value= "", inline=True)
      embed.add_field(name="", value= "", inline=True)
      embed.add_field(name="", value= "", inline=True)
      embed.set_footer(text="BOT made by Cedi!")
      await ctx.send(embed=embed)
  
  @command()
  async def profile(self, ctx, member:discord.Member = None):
      if member == None:
          member = ctx.author
      cur.execute("SELECT level_id FROM user WHERE id=?", (member.id,))
      level_id = cur.fetchone()[0]            #gets user's level
      cur.execute("SELECT min_exp FROM level WHERE id=?", (level_id + 1,))
      minimal_exp = cur.fetchone()[0]         #gets minimal exp to achieve user's level+1
      cur.execute("SELECT exp FROM user WHERE id=?", (member.id,))
      user_exp = cur.fetchone()[0]            #gets current user's exp
      cur.execute("SELECT min_exp FROM level WHERE id=?", (level_id,))
      prev_min_exp = cur.fetchone()[0]        #gets minimal exp to achieve user's current level
      exp_perc = minimal_exp - prev_min_exp           
      user_exp_perc = user_exp - prev_min_exp         
      guwno = user_exp_perc / exp_perc                 
      level_progress = round(user_exp_perc / exp_perc, 2)        
      green = ceil(level_progress * 10)           
      gray = 10 - green           
      exp_progress_string = green * ":purple_square:" + gray * ":white_large_square:"
      embed=discord.Embed(title="Level: {}            Total exp: {}".format(level_id, user_exp), description=exp_progress_string)
      embed.set_author(name=member.display_name)
      embed.set_thumbnail(url=member.avatar.url)
      number_len = len("{} / {} exp".format(user_exp_perc, exp_perc))
      print(number_len)
      embed.add_field(name="{} / {} exp                   :mag_right: {}%".format(user_exp_perc, exp_perc, round(guwno*100)),value="", inline=True)
      embed.add_field(name="Number of your messages:", value="You have written {} messages so far!".format(user_exp), inline=False)
      embed.add_field(name="Current points:", value= "Local: \n Global: ", inline=True)
      embed.add_field(name="Equipment:", value= "Nothin's here! For now...", inline=True)
      embed.add_field(name="Warns:", value= "Placeholder", inline=True)
      embed.set_footer(text="BOT made by Cedi!")
      await ctx.send(embed=embed)

  @command()
  async def embed(self, ctx ,title:str, message:str, color:str, field_name:str, field_value:str, thumbnail, img:str):
      colors = {"green": 0x00ff00, "red": 0xff0000, "blue": 0x0000ff}
      embed=discord.Embed(title=title, description=message,color=colors[color])
      if thumbnail != "0":
          embed.set_thumbnail(url=thumbnail)
      if img != "0":
          embed.set_image(url=img)
      embed.add_field(name=field_name, value=field_value)
      await ctx.send(embed=embed)
  @embed.error
  async def on_embed_error(self,ctx, error: commands.MissingRequiredArgument) -> None:
      await ctx.send("Unknown command! Please use `!embed 'title' 'description' 'color'[blue, red, green] 'field name' 'field value' 'thumbnail (write 0 if none)' 'img (write 0 if none)'` ")

  @app_commands.command(name="example", description="Description")
  async def hello(self, interaction: discord.Interaction)-> None:
      await interaction.response.send_message("Hi!")

  @command()
  async def sync(self, ctx):
        await ctx.bot.tree.sync()
        print("done")

  @command() #will use it for img generation
  async def image(self, message, text:str):
      channel = message.channel
      base = Image.open("img.png").convert("RGBA")

      # make a blank image for the text, initialized to transparent text color
      txt = Image.new("RGBA", base.size, (255,255,255,0))

      # get a font
      fnt = ImageFont.truetype("AGENCYR.TTF", 360)
      # get a drawing context
      d = ImageDraw.Draw(txt)

      # draw text, full opacity
      d.text((500,60), f"{text}", font=fnt, fill=(255,255,255,255))

      out = Image.alpha_composite(base, txt)
      with BytesIO() as file:
        out.save(file, format="PNG")
        file.seek(0)
        discord_file = discord.File(file, filename="image.png")
        await channel.send(file=discord_file)

  @command()
  async def thread_del(self, ctx, id):
    cur.execute(f"SELECT id FROM user WHERE thread={id}")
    threadauthor=cur.fetchone()[0]
    print(threadauthor)
    cur.execute(f"UPDATE user SET thread=? WHERE id=?", (0, threadauthor))
    con.commit()
     
 

async def setup(bot: Bot):
  await bot.add_cog(Commands(bot))
 