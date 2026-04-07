import discord
from discord import app_commands
from discord.ext import commands

from config import DISCORD_BOT_TOKEN
from db import init_db, save_message, build_context, get_recent_messages
from ai_service import ask_ai, rewrite_ai, summarize_ai

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def safe_send(interaction: discord.Interaction, content: str):
    if len(content) > 1900:
        chunks = [content[i:i + 1900] for i in range(0, len(content), 1900)]
        if interaction.response.is_done():
            await interaction.followup.send(chunks[0])
        else:
            await interaction.response.send_message(chunks[0])

        for chunk in chunks[1:]:
            await interaction.followup.send(chunk)
    else:
        if interaction.response.is_done():
            await interaction.followup.send(content)
        else:
            await interaction.response.send_message(content)


@bot.event
async def on_ready():
    init_db()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Command sync failed: {e}")

    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.content and message.guild is not None:
        save_message(
            user_name=message.author.name,
            user_id=str(message.author.id),
            channel_id=str(message.channel.id),
            content=message.content
        )

    await bot.process_commands(message)


@bot.tree.command(name="ask", description="Ask the AI a question")
@app_commands.describe(question="Your question for the AI")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)

    try:
        context = build_context(str(interaction.channel.id), limit=15)
        answer = ask_ai(question, context)
        await safe_send(interaction, answer)
    except Exception as e:
        await safe_send(interaction, f"Error while generating answer: {e}")


@bot.tree.command(name="rewrite", description="Rewrite text professionally")
@app_commands.describe(text="The text you want rewritten")
async def rewrite(interaction: discord.Interaction, text: str):
    await interaction.response.defer(thinking=True)

    try:
        rewritten = rewrite_ai(text)
        await safe_send(interaction, rewritten)
    except Exception as e:
        await safe_send(interaction, f"Error while rewriting text: {e}")


@bot.tree.command(name="summarize", description="Summarize recent messages in this channel")
async def summarize(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    try:
        rows = get_recent_messages(str(interaction.channel.id), limit=25)

        if not rows:
            await safe_send(interaction, "No recent messages found in this channel.")
            return

        chat_text = "\n".join([f"{user}: {content}" for user, content, _ in rows])
        summary = summarize_ai(chat_text)
        await safe_send(interaction, summary)
    except Exception as e:
        await safe_send(interaction, f"Error while summarizing chat: {e}")


@bot.tree.command(name="helpbot", description="Show available bot commands")
async def helpbot(interaction: discord.Interaction):
    help_text = (
        "**Available Commands**\n"
        "/ask - Ask the AI a question\n"
        "/rewrite - Rewrite text more clearly/professionally\n"
        "/summarize - Summarize recent channel messages\n"
        "/helpbot - Show this help message"
    )
    await interaction.response.send_message(help_text)


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)