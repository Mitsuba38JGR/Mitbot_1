import os
import random
import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ====== レベル用データ（簡易メモリ保存） ======
levels = {}

def add_xp(user_id):
    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 1}
    levels[user_id]["xp"] += 10
    if levels[user_id]["xp"] >= levels[user_id]["level"] * 100:
        levels[user_id]["xp"] = 0
        levels[user_id]["level"] += 1
        return True
    return False

# ====== 起動時 ======
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} でログインしました")

# ====== メッセージで経験値 ======
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    leveled_up = add_xp(message.author.id)
    if leveled_up:
        await message.channel.send(
            f"{message.author.mention} レベルアップ！ Lv.{levels[message.author.id]['level']} 🎉"
        )

    await bot.process_commands(message)

# ====== ① スラッシュコマンド ======
@bot.tree.command(name="ping", description="Pingを確認する")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓")

# ====== ② レベル確認コマンド ======
@bot.tree.command(name="level", description="自分のレベルを見る")
async def level(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 1}

    xp = levels[user_id]["xp"]
    lv = levels[user_id]["level"]

    await interaction.response.send_message(
        f"📊 {interaction.user.display_name} のレベル\nLv.{lv} | XP {xp}/{lv*100}"
    )

# ====== ③ ミニゲーム（じゃんけん） ======
@bot.tree.command(name="janken", description="じゃんけんする")
@app_commands.describe(hand="グー　/ チョキ / パー")
async def janken(interaction: discord.Interaction, hand: str):
    choices = ["グー", "チョキ", "パー"]

    if hand not in choices:
        await interaction.response.send_message("ぐー / ちょき / ぱー で入力してね！")
        return

    bot_hand = random.choice(choices)

    result = "引き分け！"
    if hand == "グー" and bot_hand == "チョキ":
        result = "あなたの勝ち！"
    elif hand == "チョキ" and bot_hand == "パー":
        result = "あなたの勝ち！"
    elif hand == "パー" and bot_hand == "グー":
        result = "あなたの勝ち！"
    elif hand != bot_hand:
        result = "あなたの負け！"

    await interaction.response.send_message(
        f"あなた：{hand}\nBot：{bot_hand}\n結果：{result}"
    )

bot.run(os.getenv("TOKEN"))
