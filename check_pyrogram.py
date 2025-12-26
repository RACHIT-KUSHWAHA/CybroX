from pyrogram import types
print(dir(types))
try:
    from pyrogram.types import ChatAdministratorRights
    print("ChatAdministratorRights found")
except ImportError:
    print("ChatAdministratorRights NOT found")
