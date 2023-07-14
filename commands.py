from discord.ext.commands import Cog, Bot, Context, command, Command
from discord import Intents
from discord import app_commands
from discord.ext import commands
import discord
import sqlite3
from discord.ext import commands
from math import ceil
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO
import discord


global cur, con
con = sqlite3.connect('Main_Data_Base.db')
con.row_factory = sqlite3.Row
cur = con.cursor()
class Commands(Cog):
  
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def points(self, ctx: Context,a:str,b:int,member:discord.Member = None):
            guildid=ctx.guild.id
            if member == None:
                await ctx.send("Wrong command! Please use ``!points add/remove <value> <@username>``")
            elif a == "add":
                cur.execute("SELECT points FROM users WHERE id=? AND guildid=?", (ctx.author.id, guildid))
                user_points = cur.fetchone()[0]
                user_points_after = user_points + b
                cur.execute("UPDATE users SET points=? WHERE id=? AND guildid=?", (user_points_after, ctx.author.id, guildid))
                con.commit()
            elif a == "remove":
                cur.execute("SELECT points FROM users WHERE id=? AND guildid=?", (ctx.author.id,guildid))
                user_points = cur.fetchone()[0]
                user_points_after = user_points - b 
                cur.execute("UPDATE users SET points=? WHERE id=? AND guildid=?", (user_points_after, ctx.author.id, guildid))
                con.commit()
    @points.error
    async def on_points_error(self, ctx: Context, error: commands.MissingRequiredArgument) -> None:
        await ctx.send("Wrong command! Please use ``!points add/remove <value> <@username>``")

    
    
    @command() #will make shop and economy system soon
    async def shop(self, ctx):
        file = discord.File("seks.png")
        embed=discord.Embed(title="Welcome to the shop!", description="Here you can buy some stuff!", color=discord.Color.yellow())
        embed.set_author(name="")
        embed.set_thumbnail(url="")
        embed.add_field(name="How do I buy something?", value="You may use command: `!shop buy [id]` or contact moderators. (COMMAND IN DEVELOPMENT)", inline=True)
        embed.add_field(name="How do I collect points?", value='Giveaways, leveling, collecting them from moderators. For more information type `/help` and choose `Economy`')
        embed.add_field(name="How do I sell or give someone recently bought things?", value="To sell use `!shop sell [your equipment id]`, to hand over use `!equipment-give @member [your equipment id]`", inline=False)
        embed.add_field(name="", value= "", inline=True)
        embed.add_field(name="", value= "", inline=True)
        embed.add_field(name="", value= "", inline=True)
        embed.set_image(url="attachment://seks.png")
        embed.set_footer(text="Thank you for using Aurora!")
        await ctx.send(embed=embed, file=file)
        
    @command()
    async def profile(self, ctx, member:discord.Member = None):
        if member == None:
            member = ctx.author
        guildid=ctx.guild.id
        cur.execute("SELECT levelid FROM users WHERE id=? AND guildid=?", (member.id,guildid))
        level_id = cur.fetchone()[0]            #gets user's level
        cur.execute("SELECT min_exp FROM level WHERE id=?", (level_id + 1,))
        minimal_exp = cur.fetchone()[0]         #gets minimal exp to achieve user's level+1
        cur.execute("SELECT exp FROM users WHERE id=? AND guildid=?", (member.id,guildid))
        user_exp = cur.fetchone()[0]            #gets current user's exp
        cur.execute("SELECT min_exp FROM level WHERE id=?", (level_id,))
        prev_min_exp = cur.fetchone()[0]        #gets minimal exp to achieve user's current level
        exp_perc = minimal_exp - prev_min_exp           
        user_exp_perc = user_exp - prev_min_exp         
        user_perc = user_exp_perc / exp_perc                 
        level_progress = round(user_exp_perc / exp_perc, 2)        
        green = ceil(level_progress * 10)           
        gray = 10 - green           
        exp_progress_string = green * ":purple_square:" + gray * ":white_large_square:"
        embed=discord.Embed(title="Level: {}            Total exp: {}".format(level_id, user_exp), description=exp_progress_string)
        embed.set_author(name=member.display_name)
        embed.set_thumbnail(url=member.avatar.url)
        number_len = len("{} / {} exp".format(user_exp_perc, exp_perc))
        print(number_len)
        embed.add_field(name="{} / {} exp                   :mag_right: {}%".format(user_exp_perc, exp_perc, round(user_perc*100)),value="", inline=True)
        embed.add_field(name="Number of your messages:", value="You have written {} messages so far!".format(user_exp), inline=False)
        cur.execute("SELECT points FROM users WHERE id=? AND guildid=?",(member.id,guildid))
        points = str(cur.fetchone()[0])
        embed.add_field(name="Current points:", value= "Local: "+points+"\n Global: Soon!", inline=True)
        embed.add_field(name="Equipment:", value= "Nothin's here! For now...", inline=True)
        embed.add_field(name="Warns:", value= "Placeholder", inline=True)
        embed.set_footer(text="Thanks for using Aurora!")
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

    

    class HelpSelect(discord.ui.Select):
        def __init__(self):
            # Set the options that will be presented inside the dropdown
            options = [
                discord.SelectOption(label='Economy', description='Introduction and help abouts points, shop etc.', emoji='🪙'),
                discord.SelectOption(label='Level', description='Raise with each message and conquer rankings!', emoji='👑'),
                discord.SelectOption(label='Moderation', description='Learn how to punish bad kittens!', emoji='⚖️'),
                discord.SelectOption(label='Developer', description="Some info about me, Aurora's creator", emoji='🐸'),
                discord.SelectOption(label='Setting up', description='Description of how to set up Aurora for your server', emoji='⚙️')
            ]
            super().__init__(placeholder='Choose your topic...', min_values=1, max_values=1, options=options)
        
        #will make further help menus 
        async def callback(self,interaction: discord.Interaction):
            if self.values[0]=="Level":
                embed=discord.Embed(title="Level info",color=0xffff00)
                embed.add_field(name="How does it work?", value="For every message on selected (by moderation) channels you will get few exp points.\
                                \nBy collecting those points you can get higher levels")
                embed.add_field(name="Commands", value="`!exp` **[for mods]** - allows to add/remove chosen amount of user's exp\
                                \n`!profile` - shows the most important info about you")
                await interaction.response.send_message(embed=embed)
            if self.values[0]=="Economy":
                embed=discord.Embed(title="Economy info",color=0xffff00)
                embed.add_field(name="How do I get points?", value="- Winning giveaways (amount is chosen by moderators)\
                                \n- Receiving it via mod commands (amount is chosen by moderators)\
                                \n- Leveling up (constant value)")
                embed.add_field(name="Commands", value="`!points` [for mods] - allows to add/remove chosen amount of user's points")
                await interaction.response.send_message(embed=embed)
            if self.values[0]=="Developer":
                embed=discord.Embed(title="Developer", color=0x008000)
                embed.add_field(name="My socials", value="[GitHub](https://github.com/CediDev)\
                                \n[Aurora Support Server](https://discord.gg/mcnpFgqg)")
                embed.add_field(name="Contact me", value="`Discord:` cedisz\
                                \n`Email:` c3disz@gmail.com")
                embed.add_field(name="About me", value="I am a Polish student currently learning to code, especially using python.\
                                \nFeel free to contact me if needed.", inline=False)
                embed.add_field(name="Support me", value="Coming soon!")
                embed.set_footer(text="Thank you for using Aurora! <3")          
                await interaction.response.send_message(embed=embed)
            if self.values[0]=="Setting up":
                if interaction.user.guild_permissions.administrator:
                    embed = discord.Embed(title="Setting up Aurora", description="Most important commands to make it work!")
                    embed.add_field(name="Few steps to setup your server:", value="`Step 1:` Use `!create_data_base` command to make a place\
                                    for your data in Aurora's DataBase.\n`Step 2:` Use `!set_greeting_channel id` to, obviously, set\
                                    a channel where Aurora will greet new users.\n`Step 3:` Use `!set_help_channel id` to choose\
                                    a channel on which threads with anonymous help will be made. For more info type `!ahelp`\
                                    \n`Step 4:` Now, you have to choose a muted role for your server. This role will be given to anyone\
                                    who will get Time-Outed. `!set_muted_role id`")
                    await interaction.response.send_message("Hello! At first I'd like to thank you and your community for using Aurora.\
                                                            I'll do my best to keep y'all satisfied with Aurora's work.\n`~Cedi, Aurora's creator`", embed=embed)
                    
                else:
                    await interaction.response.send_message("This category is for administrators only!", ephemeral=True)

    @command()
    async def ahelp(ctx, self):
        embed=discord.Embed(title="Anonymous chat", description="")
        embed.add_field(name="Anonymous chat is a project based on my idea to create a safe-place for talking about your and our problems e.g. suggestions, resolving conflicts, complaining anonymously or just talking about your bothers", value=" It works\
                            quite simple - users press the button, which makes a new thread (in the chosen by moderation channel) which \
                            can be seen only by mods. Then, Aurora sends a short message with few instructions to the user \
                            who pressed the button. From now on, the user can DM Aurora, and it will copy and post each of user's messages \
                            in the previosly created thread. What's more, every mods' message in that thread will also be copied \
                            and then sent to said user.")
        embed.set_footer(text="Thanks for using Aurora!")
        await self.send(embed=embed)
    
    ### SETTING UP ###
    @command()
    async def create_data_base(self, ctx):
        global serverid
        serverid = ctx.message.guild.id
        print(serverid)
        values = (int(serverid), 0,0)
        try:
            cur.execute("INSERT INTO guild VALUES(?,?,?)", values)
            con.commit()
        except sqlite3.IntegrityError:
            await ctx.send("This server is `already in the database!`")
        
    @command()  #sets channel used to greet new members
    async def set_greeting_channel(self, ctx, id):
        cur.execute("UPDATE guild SET greet_ch=? WHERE id=?", (id, ctx.message.guild.id))
        con.commit()
        await ctx.send("Greeting channel successfully updated!")
    @set_greeting_channel.error
    async def on_set_greeting_channel_error(self, ctx, error:commands.MissingRequiredArgument):
        await ctx.send("Something went wrong! Please provide your chosen `channel id`.")

    @command()  #sets channel for anonymous help threads
    async def set_help_channel(self, ctx, id):
        cur.execute("UPDATE guild SET help_ch=? WHERE id=?",(id,ctx.message.guild.id))
        con.commit()
        await ctx.send("Help channel successfully updated!")
    @set_help_channel.error
    async def on_set_help_channel_error(self, ctx, error:commands.MissingRequiredArgument):
        await ctx.send("Something went wrong! Please provide your chosen `channel id`.")
        
    
    @command() #sets up a role for muted users
    async def set_mute_role(self, ctx, id):
        cur.execute("UPDATE guild SET muted_role=? WHERE id=?",(id,ctx.message.guild.id))
        con.commit()
        await ctx.send("Mute role successfully updated!")
    @set_mute_role.error
    async def on_set_muted_role_error(self, ctx, error:commands.MissingRequiredArgument):
        await ctx.send("Something went wrong! Please provide your chosen `role id`.")
        
    
    
    class HelpSelectView(discord.ui.View):
        def __init__(self):
            super().__init__()

            # Adds the dropdown to our view object.
            self.add_item(Commands.HelpSelect())
    
    @app_commands.command(name="help", description="Help & Info categories")
    async def self(self,interaction: discord.Interaction):
        view = Commands.HelpSelectView()
        await interaction.response.send_message(view=view)

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
        cur.execute(f"SELECT id FROM users WHERE thread={id}")
        threadauthor=cur.fetchone()[0]
        print(threadauthor)
        cur.execute(f"UPDATE users SET thread=? WHERE id=?", (0, threadauthor))
        con.commit()
        

    

async def setup(bot: Bot):
        await bot.add_cog(Commands(bot))
    