from common_imports import *

class PermissionHandler:
    def __init__(self, bot):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.bot = bot
        self.error_message = config['DISCORD']['error_message']

    def check_roles(self, ctx):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.required_roles = config['DISCORD']['roles'].split(',')

        if ctx.author.id == self.bot.owner_id:
            return True

        roles = [role.name.lower().strip() for role in ctx.author.roles]
        required_roles = [role.lower().strip() for role in self.required_roles]
        if any(role in roles for role in required_roles) or ctx.author.guild_permissions.administrator:
            return True
        return False


    def has_roles(self):
        async def predicate(ctx):
            if not self.check_roles(ctx):
                await ctx.send(self.error_message)
                return False
            return True
        return commands.check(predicate)