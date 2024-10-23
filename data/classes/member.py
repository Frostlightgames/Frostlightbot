class MemberManager:
    def __init__(self,bot):
        self.bot = bot
        self.member_list = []

    async def check(self):
        for member in self.bot.get_all_members():
            self.load(member)

    def find(self,discord_member):
        found = False
        for member in self.member_list:
            if member.id == discord_member.id:
                found = True
                return member
        if not found:
            new_member = Member(self.bot,discord_member.id,discord_member.name)
            self.member_list.append(new_member)
            return new_member

    def save(self,discord_member):
        member = self.find(discord_member)
        self.bot.database.save_member(member)

    def load(self,discord_member):
        member = self.find(discord_member)
        data = self.bot.database.load_member(member)
        member.name = data[0]
        member.id = data[1]
        member.coins = data[2]
        member.candy = data[3]
        member.level = data[4]
        member.xp = data[5]
        return member

class Member:
    def __init__(self,bot,id=0,name=""):
        self.bot = bot
        self.id = id
        self.name = name
        self.coins = 0
        self.candy = 0
        self.level = 0
        self.xp = 0