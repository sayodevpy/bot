import discord
from discord.ext import commands
import json
import os

# Définition du chemin du fichier de configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
REPS_PATH = os.path.join(BASE_DIR, "reps.json")


# Chargement des données
try:
    with open(REPS_PATH, "r") as f:
        reps = json.load(f)
except FileNotFoundError:
    reps = {}

# Chargement du token depuis config.json
try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    TOKEN = config["TOKEN"]
except FileNotFoundError:
    print("❌ Fichier config.json introuvable ! Assurez-vous qu'il est dans BOT SAYO.")
    exit()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="+", intents=intents)

AUTHORIZED_REP_CHANNEL = 1349074046616211571
AUTHORIZED_SCORE_CHANNEL = 1349448275383685231

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

@bot.command()
async def rep(ctx, user: discord.Member, quantity: str, *, message: str):
    if ctx.channel.id != AUTHORIZED_REP_CHANNEL:
        return
    
    if not quantity.startswith("x") or not quantity[1:].isdigit():
        await ctx.send("❌ Format incorrect. Utilisation : +rep @user xN message", delete_after=5)
        return
    
    quantity = int(quantity[1:])
    
    if str(user.id) not in reps:
        reps[str(user.id)] = {"name": user.name, "count": 0}
    reps[str(user.id)]["count"] += quantity
    
    with open(REPS_PATH, "w") as f:
        json.dump(reps, f, indent=4)
    
@bot.command()
@commands.has_permissions(administrator=True)
async def repscore(ctx):
    if ctx.channel.id != AUTHORIZED_SCORE_CHANNEL:
        return
    
    sorted_reps = sorted(reps.items(), key=lambda x: x[1]["count"], reverse=True)
    total_rep = sum(user["count"] for _, user in sorted_reps)
    
    embed = discord.Embed(title="🏆 Classement des Vendeurs", color=discord.Color.gold())
    emojis = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    
    for i in range(5):
        if i < len(sorted_reps):
            user_id, data = sorted_reps[i]
            embed.add_field(name=f"{emojis[i]} {data['name']} : {data['count']} Reps", value="\u200b", inline=False)
        else:
            embed.add_field(name=f"{emojis[i]} None : 0 Reps", value="\u200b", inline=False)
    
    embed.set_footer(text=f"Total de reps: {total_rep}")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def represet(ctx, user: discord.Member = None, amount: int = None):
    if user is None:
        reps.clear()
    else:
        user_id = str(user.id)
        if user_id in reps:
            if amount is None or amount >= reps[user_id]["count"]:
                del reps[user_id]
            else:
                reps[user_id]["count"] -= amount
    
    with open(REPS_PATH, "w") as f:
        json.dump(reps, f, indent=4)
    
    await ctx.send("✅ Réinitialisation des reps effectuée.")

@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount: int = None):
    if amount is None:
        await ctx.channel.purge()
    else:
        await ctx.channel.purge(limit=amount + 1)

@bot.command()
@commands.has_permissions(administrator=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)

@bot.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def addrole(ctx, user: discord.Member, role: discord.Role):
    await user.add_roles(role)

@bot.command()
@commands.has_permissions(administrator=True)
async def removerole(ctx, user: discord.Member, role: discord.Role = None):
    if role is None:
        await user.edit(roles=[])
    else:
        await user.remove_roles(role)

@bot.command()
async def aide(ctx):
    embed = discord.Embed(title="📜 Liste des Commandes", color=discord.Color.blue())
    embed.add_field(name="+rep @user xN message", value="Ajoute N reps à l'utilisateur mentionné.", inline=False)
    embed.add_field(name="+repscore", value="Affiche le classement des vendeurs.", inline=False)
    embed.add_field(name="+represet [@user] [N]", value="Réinitialise les reps de tout le monde ou de l'utilisateur spécifié.", inline=False)
    embed.add_field(name="+clear [N]", value="Supprime N messages du salon (tous si non spécifié).", inline=False)
    embed.add_field(name="+lock", value="Verrouille le salon en empêchant les messages.", inline=False)
    embed.add_field(name="+unlock", value="Déverrouille le salon et permet les messages.", inline=False)
    embed.add_field(name="+addrole @user @role", value="Ajoute un rôle à un utilisateur.", inline=False)
    embed.add_field(name="+removerole @user [@role]", value="Enlève un rôle à un utilisateur (tous si aucun rôle spécifié).", inline=False)
    embed.set_footer(text="Utilisation réservée aux administrateurs sauf pour +rep.")
    await ctx.send(embed=embed)

bot.run(TOKEN)