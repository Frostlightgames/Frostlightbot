from data.classes.database import DATABASE
class Member:
    def __init__(self, uid, name):
        self.uid = uid
        self.name = name
        self.coins = DATABASE.get_member_value(uid,"coins") or 0
        self.candy = DATABASE.get_member_value(uid,"candy") or 0
        self.level = DATABASE.get_member_value(uid,"level") or 0
        self.xp = DATABASE.get_member_value(uid,"xp") or 0

        DATABASE.set_member_value(uid,"name", self.name)

    @property
    def coins(self):
        coins = DATABASE.get_member_value(self.uid, "coins")
        return coins
    
    @coins.setter
    def coins(self, value):
        DATABASE.set_member_value(self.uid,"coins",value)

    @property
    def candy(self):
        candy = DATABASE.get_member_value(self.uid, "candy")
        return candy
    
    @candy.setter
    def candy(self, value):
        DATABASE.set_member_value(self.uid,"candy",value)

    @property
    def level(self):
        level = DATABASE.get_member_value(self.uid, "level")
        return level
    
    @level.setter
    def level(self, value):
        DATABASE.set_member_value(self.uid,"level",value)
    
    @property
    def xp(self):
        xp = DATABASE.get_member_value(self.uid, "xp")
        return xp
    
    @xp.setter
    def xp(self, value):
        DATABASE.set_member_value(self.uid,"xp",value)
