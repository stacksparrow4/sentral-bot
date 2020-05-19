sudo docker run -v $(pwd)/secrets:/root/bot/secrets -v $(pwd)/database:/root/bot/database --name bot -d --restart always bot
