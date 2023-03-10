from common_imports import *
from PermissionHandler import PermissionHandler as PM
import ConfigHandler

config = configparser.ConfigParser()
PermissionHandler = PM
config_handler = ConfigHandler.ConfigChk()
config_handler.check_config()

# Read config and set links / regex format
config.read('config.ini')
ELEVATED = config['DISCORD']['roles'].split(",")
TOKEN = config['DISCORD']['token']
GROUP_ID = config['WEBSITE']['group_id']
API_KEY = config['WEBSITE']['api_key']
API_ENDPOINT = 'https://templeosrs.com/api/'
COMPETITIONS_URL = "https://templeosrs.com/groups/competitions.php?id=" + GROUP_ID
OVERVIEW_URL = "https://templeosrs.com/groups/overview.php?id=" + GROUP_ID
MEMBER_URL = "https://templeosrs.com/groups/members.php?id=" + GROUP_ID
regex = r"^[A-Za-z0-9 ]{0,12}(,[A-Za-z0-9 ]{0,12})*$"

def debug(Input):
    if not os.path.exists("debug_output.md"):
        open("debug_output.txt", "w").close()
        with open("debug_output.txt", "a") as debug_file:
            timestamp = str(datetime.datetime.now())
            debug_file.write(f"{timestamp}: {Input}\n")

#Initiate Bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), case_insensitive=True)
permission_handler = PermissionHandler(bot)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
        
@bot.command(aliases=["ar", "adr"])
@permission_handler.has_roles()
async def addrole(ctx, arg):
    config.read("config.ini")
    if len(arg) > 1:
        role = arg
        roles = config.get("DISCORD", "ROLES")
        if role not in roles:
            roles += ", " + role
            config.set("DISCORD", "ROLES", roles)
            with open("config.ini", "w") as config_file:
                config.write(config_file)
                guild = ctx.guild
                existing_role = discord.utils.get(guild.roles, name=role)
                if existing_role is None:
                    await guild.create_role(name=role)
                    await ctx.send(f"Role {role} added to the server and the config file.")
        else:
            guild = ctx.guild
            existing_role = discord.utils.get(guild.roles, name=role)
            if existing_role is None:
                await guild.create_role(name=role)
                await ctx.send(f"Role {role} added to the server.")
            else:
                await ctx.send(f"Role {role} already exists.")
    else:
        await ctx.send("Invalid command. Use the format !addrole role.")

@bot.command(aliases=["gi"])
async def groupinfo(ctx):
    # Make a request to the API
    response = requests.get(API_ENDPOINT + f'group_info.php?id={GROUP_ID}', headers={'Authorization': f'Bearer {API_KEY}'})

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract the 'info' dictionary
        info = data['data']['info']

        # Extract the values from the 'info' dictionary
        group_id = info['id']
        group_name = info['name']
        total_xp = info['total_xp']
        average_xp = round(info['average_xp'], 2)
        total_ehp = round(info['total_ehp'],2 )
        average_ehp = round(info['average_ehp'], 2)
        total_ehb = round(info['total_ehb'], 2)
        average_ehb = round(info['average_ehb'], 2)
        clan_type = info['clan_type']
        #clan_type_id = info['clan_type_id']
        member_count = info['member_count']

        # Calculate the value in millions
        total_xp_millions = total_xp / 1000000
        average_xp_millions = average_xp / 1000000

        # Format the value as a string with two decimal places
        formatted_total_xp = '{:,.2f}'.format(total_xp_millions)
        formatted_average_xp = '{:,.2f}'.format(average_xp_millions)

        # Create an embed
        embed = discord.Embed(title='Group Info', color=discord.Color.dark_green(), url=OVERVIEW_URL)

        # Set the fields of the embed to the values of the data
        embed.add_field(name='ID', value=group_id)
        embed.add_field(name='Name', value=group_name)
        embed.add_field(name='Total XP', value=formatted_total_xp + "M")
        embed.add_field(name='Average XP', value=formatted_average_xp + "M")
        embed.add_field(name='Total EHP', value=total_ehp)
        embed.add_field(name='Average EHP', value=average_ehp)
        embed.add_field(name='Total EHB', value=total_ehb)
        embed.add_field(name='Average EHB', value=average_ehb)
        embed.add_field(name='Clan type', value=clan_type)
        #embed.add_field(name='Clan type ID', value=clan_type_id)
        embed.add_field(name='Member count', value=member_count)

        # Send the embed to discord
        await ctx.send(embed=embed)
    else:
        # Send an error message if the request was unsuccessful
        await ctx.send('An error occurred while trying to get the data. Please try again later.')

@bot.command(aliases=["ach", "recents", "recent", "latestpogs"])
async def achievements(ctx, num:int=5):
    # Make a request to the API
    response = requests.get(API_ENDPOINT + 'group_achievements.php', params={'id': GROUP_ID})
    if num < 1 or num > 20:
        await ctx.send('Please enter a number between 1 and 20')
        return
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()['data']

        # Create an embed object
        embed = discord.Embed(title='Group achievements')

        # Add the achievements to the embed object as fields
        for achievement in data[:num]:
            xp = achievement['Xp']
            if xp >= 1000000:
                xp = f'{xp // 1000000}M'
            type_ = achievement['Type']
            if type_ == 'Pvm':
                xp = f'{xp}kc'
            embed.add_field(name=achievement['Username'], value=f'{achievement["Skill"]} {xp} {achievement["Date"]}', inline=False)

        # Send the embed object to discord
        await ctx.send(embed=embed)
    else:
        # Send an error message if the request was unsuccessful
        await ctx.send('An error occurred while trying to get the data. Please try again later.')

@bot.command(aliases=["leaders", "staff", "admins", "cl"])
async def clanleaders(ctx):
    # Make a request to the API
    response = requests.get(API_ENDPOINT + f'group_info.php?id={GROUP_ID}', headers={'Authorization': f'Bearer {API_KEY}'})

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract the values from the 'info' dictionary
        leaders = data['data']['leaders']

        # Create an embed object
        embed = discord.Embed(title="Clan Leaders", description=", ".join(leaders), color=discord.Color.dark_green(), url=MEMBER_URL)

        # Send the embed to discord
        await ctx.send(embed=embed)
    else:
        # Send an error message if the request was unsuccessful
        await ctx.send('An error occurred while trying to get the data. Please try again later.')

@bot.command(aliases=["rm", "del", "delete", "remove", "deletemember", "removemember"])
@permission_handler.has_roles()
async def delmem(ctx, *, player_names):
    if not re.match(regex, player_names):
        await ctx.send("Error: player names must contain only letters, digits, and spaces, and have a maximum of 12 characters.")
        return

    # Make a request to the API
    response = requests.post(API_ENDPOINT + 'remove_group_member.php', data={'id': GROUP_ID, 'key': API_KEY, 'players': player_names})

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Send a message to discord with the data
        await ctx.send(f'Removed: {player_names} from group: {GROUP_ID}')
    else:
        # Send an error message if the request was unsuccessful
        await ctx.send('An error occurred while trying to remove the players. Please try again later.')

@bot.command(aliases=["addm", "add", "addmember"])
@permission_handler.has_roles()
async def addmem(ctx, *, player_names):
    if not re.match(regex, player_names):
        await ctx.send("Error: player names must contain only letters, digits, and spaces, and have a maximum of 12 characters.")
        return
        
    # Make a request to the API
    response = requests.post(API_ENDPOINT + 'add_group_member.php', data={'id': GROUP_ID, 'key': API_KEY, 'players': player_names})

        # Check if the request was successful
    if response.status_code == 200:
            # Send a message to discord with the data
            await ctx.send(f'Added: {player_names} to group: {GROUP_ID}')
    else:
            # Send an error message if the request was unsuccessful
        await ctx.send('An error occurred while trying to add the players. Please try again later.')





bot.run(TOKEN)
