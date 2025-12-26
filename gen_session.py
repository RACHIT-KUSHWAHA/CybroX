from pyrogram import Client
import asyncio

async def main():
    print("--- Legendbot Session Generator ---")
    print("Go to https://my.telegram.org to get API ID and API HASH.")
    
    try:
        api_id = int(input("Enter API ID: "))
        api_hash = input("Enter API HASH: ")
    except ValueError:
        print("Invalid API ID. It must be an integer.")
        return

    print("\nLogging in... (Check your Telegram for the code)")
    
    # Using a file-based session to avoid Windows :memory: SQLite errors
    app = Client("temp_login", api_id=api_id, api_hash=api_hash)
    
    try:
        await app.start()
        session_string = await app.export_session_string()
        me = await app.get_me()
        
        print("\n" + "="*50)
        print(f"Successfully logged in as: {me.first_name} (@{me.username})")
        print("Here is your SESSION_STRING (Copy all of it):")
        print("="*50 + "\n")
        print(session_string)
        print("\n" + "="*50)
        
        await app.stop()
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(main())
