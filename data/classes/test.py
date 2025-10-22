from Frostlightbot.data.classes.dbRequests import dbRequests
from Frostlightbot.data.classes.database import Member, Config

def main():
    db = dbRequests()

    print("=== CREATE ENTRIES ===")
    # Members erstellen
    db.create_entry(Member, id=20251022000001, name="Max", coins=100, candy=5, level=2, xp=50)
    db.create_entry(Member, id=20251022000002, name="Lisa")  # Defaults für Coins, Candy, Level, XP

    # Configs erstellen
    db.create_entry(Config, id=1, name="ServerName")
    db.create_entry(Config, id=2, name="Prefix")

    print("\n=== SELECT ALL ===")
    members = db.select_entry(Member)
    print("Alle Mitglieder:")
    for m in members:
        print(m)

    configs = db.select_entry(Config)
    print("\nAlle Configs:")
    for c in configs:
        print(c)

    print("\n=== SELECT FILTERED ===")
    member_max = db.select_entry(Member, id=20251022000001)
    print("Mit id=20251022000001:")
    print(member_max)

    print("\n=== UPDATE ENTRY ===")
    updated = db.update_entry(Member, 20251022000001, coins=500, level=5)
    if updated:
        print("Update erfolgreich!")
        member_max = db.select_entry(Member, id=20251022000001)
        print(member_max)
    else:
        print("Update fehlgeschlagen!")

    print("\n=== ERROR CASES ===")
    # Eintrag existiert nicht
    result = db.select_entry(Member, id=999)
    if not result:
        print("Keine Einträge gefunden, wie erwartet.")

    # Update auf nicht existierendem Eintrag
    updated = db.update_entry(Member, 999, coins=50)
    if not updated:
        print("Update auf nicht vorhandenen Eintrag korrekt fehlgeschlagen.")

    print("\n=== CREATE ENTRY MIT WENIGEN PARAMETERN (Defaults) ===")
    db.create_entry(Member, id=20251022000003, name="Tom")
    member_tom = db.select_entry(Member, id=20251022000003)
    print(member_tom)

if __name__ == "__main__":
    main()