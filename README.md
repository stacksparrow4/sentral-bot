# sentral-bot

A bot that can send sentral notifications to specified discord channels.

## Usage

1. Download/clone this repository
2. Open terminal in the folder where you downloaded to, and run `mkdir secrets database`
2. Install docker
3. While docker is installing, open a web browser and go to [https://discord.com/developers/applications](https://discord.com/developers/applications)
4. Create a new application, give it a name (eg sentral bot)
5. Go to the bot tab on the left and create a bot for the application
6. Copy the token, and run the command in the terminal: `echo "YOUR_TOKEN_HERE" > secrets/.token`
7. Back in the discord bot page click OAuth2 on the left
8. Copy the client id
9. Insert the client id into this url (replacing CLIENT_ID with your bots client id):
  https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=18432&scope=bot
10. Go to that url, and add a bot to a server you have the manage server permission on
11. Run the following line in the terminal: `read user && read pass && echo -e "${user}\n${pass}" > secrets/.creds`
  Now type your sentral username and press enter
  Now type your sentral password and press enter
12. Open line 75 of discordclient.py. It should say something like
  ```python
  if message.author.id != 485713672161722379 and message.author.id != 232767987843727361:
  ```
  Make sure that you have developer mode enabled in discord settings, and right click any of your messages in any server and click copy id to get your discord user_id.
  Replace line 75 with the following:
  ```python
  if message.author.id != ENTER_YOUR_USER_ID_HERE:
  ```
  This ensures only you can use this bot.
  (Also, depending on which school you are in, you may need to change all occurances of https://web3.girraween-h.schools.nsw.edu.au/ in getmessages.py)
  
13. In the terminal type `./build.sh`
14. Then type `./run.sh`
15. If you want the bot to start automatically when the system reboots, type `sudo systemctl enable docker`
16. Go to the discord server where the bot is in and find an appropriate channel
17. Type `$subchannel` in the chat.
18. The bot should now say "this channel is now subscribed to updates on sentral". If it doesn't, you messed something up.
