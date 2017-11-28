"""cloud_bot.handler"""

import os
import random
import tweepy
from cloud_bot import utils


def handler(event, context):
    """Tweet the image
    """
    consumer_key = os.environ['C_KEY']
    consumer_secret = os.environ['C_SECRET']
    access_key = os.environ['A_KEY']
    access_secret = os.environ['A_SECRET']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    is_full = bool(random.getrandbits(1))
    scene, im, info = utils.create_img(highres=is_full)
    place = info.get('name', '')

    tweet_content = f'{place}\n #Landsat #clouds\n https://viewer.remotepixel.ca/?sceneid={scene}'
    api.update_with_media(f'{scene}_cloud.jpg', status=tweet_content, file=im)

    return True


def handler_fullcloud(event, context):
    """Tweet the image
    """
    consumer_key = os.environ['C_KEY']
    consumer_secret = os.environ['C_SECRET']
    access_key = os.environ['A_KEY']
    access_secret = os.environ['A_SECRET']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    is_full = bool(random.getrandbits(1))
    scene, im, info = utils.create_img(highres=is_full, min_cloud=99)
    place = info.get('name', '')

    tweet_content = f'{place}\n #Landsat #clouds\n https://viewer.remotepixel.ca/?sceneid={scene}'
    api.update_with_media(f'{scene}_cloud.jpg', status=tweet_content, file=im)

    return True
