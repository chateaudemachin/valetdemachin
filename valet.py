import os, slackclient, time
import random


SOCKET_DELAY = 1

VALET_SLACK_NAME = os.environ.get('VALET_SLACK_NAME')
VALET_SLACK_TOKEN = os.environ.get('VALET_SLACK_TOKEN')
VALET_SLACK_ID = os.environ.get('VALET_SLACK_ID')

valet_slack_client = slackclient.SlackClient(VALET_SLACK_TOKEN)


# TODO SLACK Specific
def is_private(event):
    """Checks if on a private slack channel"""
    channel = event.get('channel')
    return channel.startswith('D')


def post_message(message, channel):
    valet_slack_client.api_call('chat.postMessage', channel=channel,
                          text=message, as_user=True)


# how the bot is mentioned on slack
def get_mention(user):
    return '<@{user}>'.format(user=user)

valet_slack_mention = get_mention(VALET_SLACK_ID)


# TODO Language Specific
def is_for_me(event):
    """Know if the message is dedicated to me"""
    # check if not my own event
    type = event.get('type')
    if type and type == 'message' and not(event.get('user')==VALET_SLACK_ID):
        if is_private(event):
            return True
        text = event.get('text')
        channel = event.get('channel')
        if valet_slack_mention in text.strip().split():
            return True


def say_hi(user_mention):
    """Say Hi to a user by formatting their mention"""
    response_template = random.choice(['Sup, {mention}...',
                                       'Yo!',
                                       'Hola {mention}',
                                       'Bonjour!'])
    return response_template.format(mention=user_mention)


def say_bye(user_mention):
    """Say Goodbye to a user"""
    response_template = random.choice(['see you later, alligator...',
                                       'adios amigo',
                                       'Bye {mention}!',
                                       'Au revoir!'])
    return response_template.format(mention=user_mention)


def is_hi(message):
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens
               for g in ['hello', 'bonjour', 'hey', 'hi', 'sup', 'morning', 'hola', 'ohai', 'yo'])


def is_bye(message):
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens
               for g in ['bye', 'goodbye', 'revoir', 'adios', 'later', 'cya'])


def handle_message(message, user, channel):
    if is_hi(message):
        user_mention = get_mention(user)
        post_message(message=say_hi(user_mention), channel=channel)
    elif is_bye(message):
        user_mention = get_mention(user)
        post_message(message=say_bye(user_mention), channel=channel)


# Bot Specific
def run():
    if valet_slack_client.rtm_connect():
        print('[.] Valet de Machin is ON...')
        while True:
            event_list = valet_slack_client.rtm_read()
            if len(event_list) > 0:
                for event in event_list:
                    print(event)
                    # print (event)
                    if is_for_me(event):
                        handle_message(message=event.get('text'), user=event.get('user'), channel=event.get('channel'))
            time.sleep(SOCKET_DELAY)
    else:
        print('[!] Connection to Slack failed! (Have you sourced the environment variables?)')

if __name__=='__main__':
    run()
