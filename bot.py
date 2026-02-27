import logging
import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys

# Enable logging
logging.basicConfig(level=logging.INFO)

# ---------------- Discord bot token ----------------
TOKEN = "MTQ3NzA0NzMzMzg1MzMzNTY1Nw.G6xc6w.U8lMlnwZqTefOmDOKAlEaQU84vijcbXkVtLRnI"  # <-- replace with your regenerated token

# ---------------- Google Sheets API setup ----------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client_sheet = gspread.authorize(creds)
    sheet = client_sheet.open("Qatar Airways Personnel Database").sheet1
except Exception as e:
    print("❌ Google Sheets connection failed:")
    print(e)
    sys.exit(1)

# ---------------- Discord bot intents ----------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- Event: on_ready ----------------
@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

# ---------------- Flight logging command ----------------
@bot.command()
async def log(ctx, member: discord.Member):
    try:
        user_id = str(member.id)

        # ---------------- Load records ----------------
        # Header row is row 4
        records = sheet.get_all_records(head=4)
        print("DEBUG: Loaded records from sheet:", records)

        for i, row in enumerate(records, start=5):  # data starts at row 5
            print(f"DEBUG: Checking row {i}: {row}")
            if str(row["Discord ID"]) == user_id:
                # Handle empty or invalid Flights cells
                try:
                    current_flights = int(row["Flights"])
                except:
                    current_flights = 0

                points = current_flights + 1
                sheet.update_cell(i, 7, points)  # Column G = Flights
                await ctx.send(f"{member.mention} now has {points} flight(s)!")
                return

        # ---------------- Add new user if not found ----------------
        new_row = ["", member.name, user_id, "", "", "", 1, "", ""]
        sheet.append_row(new_row)
        await ctx.send(f"{member.mention} added with 1 flight!")

    except Exception as e:
        await ctx.send("❌ Failed to log flight points.")
        print("ERROR in !log command:", e)

# ---------------- Run bot ----------------
try:
    bot.run(TOKEN)
except discord.LoginFailure:
    print("❌ Invalid Discord token. Regenerate it in Developer Portal and update bot.py")
except Exception as e:
    print("❌ Bot failed to start:")
    print(e)