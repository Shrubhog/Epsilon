"""
The Epsilon code.
"""
import json
import hashlib
import requests
import discord

with open('config/config.json', 'r') as f:
    CONFIG = json.load(f)

# config stuff
PREFIX = CONFIG['prefix']
CLIENT = discord.Client()
ROOT = CONFIG['root']

# helper functions


def represents_int(string):
    """
    Checks whether a string is an integer
    """
    try:
        int(string)
        return True
    except ValueError:
        return False


def wikipedia(wiki_args):
    """
    Get Wikipedia information and infobox photo URL.
    """

    # Search Wikipedia for page.
    # Explained here: https://stackoverflow.com/questions/27457977/searching-wikipedia-using-api
    # And here:
    # https://stackoverflow.com/questions/1565347/get-first-lines-of-wikipedia-article/19781754
    wiki_page = requests.get(
        ("https://en.wikipedia.org/w/api.php?action=opensearch"
         "&search={0}&limit=1&namespace=0&format=json")
        .format(wiki_args)
    ).json()
    
    # Get the infobox photo from Wikidata
    # Process explained here:
    # https://stackoverflow.com/questions/36813352/how-to-reliably-get-the-image-used-in-the-wikipedia-infobox
    embed_photo = requests.get(
        ("https://www.wikidata.org/w/api.php?action=wbgetentities"
         "&format=json&sites=enwiki&props=claims&titles={}")
        .format(wiki_page[1][0])).json()
    # Get the WikiData object code by getting the first result key.
    photo_id = next(iter(embed_photo["entities"]))
    # Get the page of that object.
    photo_values = requests.get(
        ("https://www.wikidata.org/w/api.php?action=wbgetclaims"
         "&entity={}&property=P18&format=json")
        .format(photo_id))
    # Take the image name from the first image on the page (images are P18s) and get rid of spaces.
    photo_name = photo_values.json()["claims"]["P18"][0] \
        ["mainsnak"]["datavalue"]["value"].replace(" ", "_")
    # Get the hash of that name and use it to get the URL in WikiMedia's upload format.
    photo_hash = hashlib.md5(photo_name.encode('utf-8')).hexdigest()
    photo_url = "https://upload.wikimedia.org/wikipedia/commons/{}/{}/{}".format(
        photo_hash[0], photo_hash[:2], photo_name)
    # Return the page and the photo.
    return wiki_page, photo_url

# bot functions
@CLIENT.event
async def on_ready():
    """
    Callback for when the client is ready
    """

    print('Logged on as {0}!'.format(CLIENT.user))


@CLIENT.event
async def on_message(message):
    """
    Callback for when a message is sent.
    """

    if message.author == CLIENT.user:
        # Don't talk to yourself. This can lead to infinite loops.
        return
    if message.content.startswith(PREFIX):
        command = message.content[len(PREFIX):]
        if command.startswith('ping'):
            await message.channel.send('pong!')
        elif command.startswith('stop') and message.author.id == ROOT:
            # Only stop for the root user
            await message.channel.send('Logging out...')
            await CLIENT.logout()
        elif command.startswith('stop') and message.author.id != ROOT:
            await message.channel.send('You have to be root to stop.')
        elif command.startswith('wikipedia '):
            args = command[len("wikipedia "):]
            wiki_page, photo_url = wikipedia(args)
            try:
                embed = discord.Embed(
                    title="Wikipedia", description=wiki_page[1][0], color=0xeeeeee)
                embed.add_field(
                    name="Page", value=wiki_page[2][0], inline=True)
                embed.set_thumbnail(url=photo_url)
                embed.add_field(name="URL", value=wiki_page[3][0], inline=True)
                await message.channel.send(embed=embed)
            except IndexError:
                await message.channel.send(
                    message.channel,
                    "No results for search: {}".format(args)
                )
        elif command.startswith('xkcd'):
            args = command[len('xkcd'):].split(" ")

            # sanitize spaces
            while "" in args:
                args.remove("")

            if args[0] is None:
                # get latest
                pass
            elif args[0] == 'random':
                # get random
                pass
            elif represents_int(args[0]):
                # get comic by id
                pass

TOKEN = CONFIG['token']
CLIENT.run(TOKEN)
