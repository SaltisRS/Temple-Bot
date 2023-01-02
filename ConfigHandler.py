from common_imports import *

class ConfigChk:
    def __init__(self):
        self.config = configparser.ConfigParser()

    def check_config(self):
        # Check if the config.ini file exists
        if not os.path.exists("config.ini"):
            # Create the config.ini file if it does not exist
            self.create_config()
            return

        # Read in the config.ini file
        self.config.read("config.ini")

        # Iterate through the sections and entries in the config.ini file
        for section, entries in self.config.items():
            for entry, value in entries.items():
                # Check if the value is empty or 0
                if not value or value == "0":
                    # Prompt the user for the missing value
                    value = input(f"Enter a value for {entry} in section {section}: ")
                    # Update the value in the config.ini file
                    self.config.set(section, entry, value)

    def create_config(self):
        # Prompt the user for the values for each section and entry
        TOKEN = input("Enter a value for TOKEN in section DISCORD: (bot token)")
        ROLES = input("Enter a name for ROLES in section DISCORD: (case sensitive)")
        API_KEY = input("Enter a value for API_KEY in section WEBSITE: (edit code)")
        GROUP_ID = input("Enter a value for GROUP_ID in section WEBSITE: ")

        # Add the values to the config.ini file
        self.config.add_section("DISCORD")
        self.config.set("DISCORD", "TOKEN", TOKEN)
        self.config.set("DISCORD", "ROLES", ROLES)
        self.config.set("DISCORD", "error_message", "Sorry, you do not have the required elevation to use this command.")
        self.config.add_section("WEBSITE")
        self.config.set("WEBSITE", "API_KEY", API_KEY)
        self.config.set("WEBSITE", "GROUP_ID", GROUP_ID)

        # Save the config.ini file
        with open("config.ini", "w") as config_file:
            self.config.write(config_file)

