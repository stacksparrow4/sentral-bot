import discord, sqlite3, asyncio, hashlib, datetime
from getmessages import get_messages

DELAY = 60*30 # = 30 minutes
# DELAY = 5

conn = sqlite3.connect('./database/database.db')

c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS channels (id TEXT UNIQUE)')
c.execute('CREATE TABLE IF NOT EXISTS messagehashes (hash TEXT UNIQUE)')
conn.commit()

def shahash(s):
    m = hashlib.sha256()
    m.update(s.encode())
    return m.hexdigest()

def generate_color(author):
    # For fun, generate a colour seeded by the author, so each author will have the same colour.
    return int(shahash(author), 16) % 0xffffff

def gen_msg_string(msg):
    return msg[0]+msg[1]+''.join(msg[2])+msg[3]

def query(*args):
    c = conn.cursor()
    c.execute(*args)
    return c.fetchall()

# Update db version
if query('SELECT name FROM sqlite_master WHERE type="table" AND name="messages"'):
    textcontents = query('SELECT textcontent FROM messages')

    for row in textcontents:
        txt = row[0]
        hashed = shahash(txt)
        query('INSERT INTO messagehashes VALUES (?)', [hashed])
    
    query('DROP TABLE messages')

    conn.commit()

def clip_string(s):
    if len(s) >= 1020:
        return s[:1020] + '...'
    return s

class MyClient(discord.Client):
    def __init__(self):
        super().__init__()

        self.bg_task = self.loop.create_task(self.background_task())

    async def on_ready(self):
        print("Logged on!")

    def create_msg_embed(self, msg):
        title, body, imgs, author = msg

        embed = discord.Embed(title=title, color=generate_color(author))

        clipped_body = clip_string(body)
        if clipped_body:
            embed.add_field(name="Body", value=clipped_body, inline=False)

        embed.set_author(name=author)
        
        return embed

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.author.id != 485713672161722379 and message.author.id != 232767987843727361:
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

                if len(msgs) == 0:
                    await message.channel.send("There are no messages currently.")
                else:
                    for msg in msgs:
                        await message.channel.send(embed=self.create_msg_embed(msg))

            elif command == 'issubbed':
                if len(query("SELECT id FROM channels WHERE id=?", [str(message.channel.id)])) > 0:
                    await message.channel.send("This channel is subscribed.")
                else:
                    await message.channel.send("This channel is not yet subscribed.")
            
            elif command == 'logdb':
                db_content = query("SELECT hash FROM messagehashes")

                await message.channel.send('\n'.join([i[0] for i in db_content]))

    async def background_task(self):
        await self.wait_until_ready()
        
        await asyncio.sleep(10)

        while True:
            print("Checked sentral at ", datetime.datetime.now())

            try:
                msgs = get_messages()
                
            except Exception as e:
                print("--- RECIEVED ERROR GETTING MESSAGES! ---")
                print(e)
                print()

            try:
                for msg in msgs:
                    string_msg = gen_msg_string(msg)
                    hashed_msg = shahash(string_msg)

                    matches = query("SELECT hash FROM messagehashes WHERE hash=?", [hashed_msg])

                    if len(matches) == 0:
                        print('New message:', string_msg[:20])

                        subbed_channels = query("SELECT id FROM channels")

                        for channel in subbed_channels:
                            try:
                                channel_ref = self.get_channel(int(channel[0]))

                                await channel_ref.send(embed=self.create_msg_embed(msg))
                            except Exception as e:
                                print("--- Recieved exception for channel {}! ---".format(channel), e)
                        
                        try:
                            query("INSERT INTO messagehashes VALUES (?)", [hashed_msg])
                        except:
                            print("--- RECIEVED ERROR SENDING HASH TO DB! ---")
                            print(e)
                            print()

            except Exception as e:
                print("--- RECIEVED ERROR DISTRIBUTING MESSAGES! ---")
                print(e)
                print()

            conn.commit()

            await asyncio.sleep(DELAY)



with open('./secrets/.token', 'r') as f:
    token = f.read()

client = MyClient()
client.run(token)
