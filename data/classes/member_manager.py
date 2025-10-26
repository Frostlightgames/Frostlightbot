import discord

from main import *
from data.classes.member import Member

class MemberManager:
    def __init__(self, bot:FrostlightBot):
        self.bot = bot
        self.member_list: dict[str,Member] = {}

        self.scan_for_member()

    def scan_for_member(self):
        for member in self.bot.get_all_members():
            self.member_list[member.id] = Member(member.id,member.name)

    def get(self,uid=None, name=None, member:discord.Member=None):
        self.scan_for_member()
        member_uid = uid or member.id if member else None
        if member_uid in self.member_list:
            return self.member_list[member_uid]
        else:
            for member in self.member_list:
                if self.member_list[member].name == name:
                    return self.member_list[member]
        raise ValueError("Member cloud not be found")