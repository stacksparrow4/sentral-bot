import discord, sqlite3, asyncio, hashlib
from getmessages import get_messages

DELAY = 60*30 # = 30 minutes
# DELAY = 3

conn = sqlite3.connect('./database/database.db')

c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS channels (id TEXT UNIQUE)')
c.execute('CREATE TABLE IF NOT EXISTS messages (textcontent TEXT UNIQUE)')
conn.commit()

def generate_color(author):
    # For fun, generate a colour seeded by the author, so each author will have the same colour.
    m = hashlib.sha256()
    m.update(author.encode())
    return int(m.hexdigest(), 16) % 0xffffff

def gen_msg_string(msg):
    return msg[0]+msg[1]+''.join(msg[2])+msg[3]

def query(*args):
    c = conn.cursor()
    c.execute(*args)
    return c.fetchall()

class MyClient(discord.Client):
    def __init__(self):
        super().__init__()

        self.bg_task = self.loop.create_task(self.background_task())

    async def on_ready(self):
        print("Logged on!")

    def create_msg_embed(self, msg):
        title, body, imgs, author = msg

        embed = discord.Embed(title=title, color=generate_color(author))
        embed.add_field(name="Body", value=body, inline=False)
        embed.set_author(name=author)

        if len(imgs) > 0:
            embed.set_image(url=imgs[0])
        
        return embed

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.startswith('$'):
            command = message.content[1:]
            if command == 'subchannel':
                query("INSERT INTO channels VALUES (?)", [str(message.channel.id)])

                conn.commit()

                await message.channel.send("This channel is now subscribed to updates on sentral.")

            elif command == 'unsubchannel':
                if len(query("SELECT id FROM channels WHERE id=?", [str(message.channel.id)])) > 0:
                    query("DELETE FROM channels WHERE id=?", [str(message.channel.id)])

                    conn.commit()

                    await message.channel.send("This channel is now unsubscribed.")
                else:
                    await message.channel.send("But this channel isn't subscribed...")
            
            elif command == 'logmessages':
                msgs = get_messages()

                for msg in msgs:
                    await message.channel.send(embed=self.create_msg_embed(msg))

    async def background_task(self):
        await self.wait_until_ready()

        while True:
            print("YES")

            msgs = get_messages()

            for msg in msgs:
                string_msg = gen_msg_string(msg)

                matches = query("SELECT textcontent FROM messages WHERE textcontent=?", [string_msg])

                if len(matches) == 0:
                    subbed_channels = query("SELECT id FROM channels")

                    for channel in subbed_channels:
                        channel_ref = self.get_channel(int(channel[0]))

                        await channel_ref.send(embed=self.create_msg_embed(msg))
            
            query("DELETE FROM messages")

            for msg in msgs:
                query("INSERT INTO messages VALUES (?)", [gen_msg_string(msg)])
            
            conn.commit()
            
            await asyncio.sleep(DELAY)



with open('./secrets/.token', 'r') as f:
    token = f.read()

client = MyClient()
client.run(token)
