from dotenv import load_dotenv
import os
from telethon import TelegramClient, events, sync
import requests


def get_message(message):
  message_result = {
      'text': message.text,
      'id': message.id,
      'date': message.date.isoformat(),
  }
  if message.reply_to_msg_id:
    message_result['reply_to_msg_id'] = message.reply_to_msg_id
  return message_result

load_dotenv()

webhook_url =os.getenv('WEBHOOK_URL')
# Créer un client avec les paramètres de l'API
client = TelegramClient('session', api_id=os.getenv('TELEGRAM_API_ID'), api_hash=os.getenv('TELEGRAM_API_HASH'))
peerId = os.getenv('TELEGRAM_PEER_ID')
# Se connecter à l'API
client.start(os.getenv('TELEGRAM_PHONE')) # Remplacer par votre numéro de téléphone

# Récupérer la liste des canaux auxquels on est abonné
chats = client.get_dialogs(limit=100)

# Filtrer les chats de type canal
channels = [chat for chat in chats if chat.is_channel]

channel = None
for channelCurrent in channels:
  print('channelCurrent.id', channelCurrent.name, channelCurrent.id)
  if str(channelCurrent.id) == str(peerId):
    channel = channelCurrent

if channel is None:
  print('PeerId invalide invalide')
  exit()

# Récupérer les messages du canal
# messages = client.get_messages(channel, limit=10)
# messages.reverse()

# # Afficher les messages du canal
# print(f'Voici les messages du canal {channel.name} :')
# for message in messages:
#   if message.reply_to_msg_id:
#     print(f'{message.date}: {message.text} {message.reply_to_msg_id}')

# S'abonner aux mises à jour des nouveaux messages du canal
@client.on(events.NewMessage(chats=channel))
async def new_message_handler(event):
  # Afficher le nouveau message
  print(f'{event.message.date}: {event.message.text}')
  try:
    requests.post(webhook_url, json = {
      'message': get_message(event.message),
      'type': 'new_message'
    })
  except:
    print('Webhook invalide')
    
@client.on(events.NewMessage(chats=channel))
async def new_message_handler(event):
    # Afficher le nouveau message
    print(f'{event.message.date}: {event.message.text}')
    print('Message added', event.id, 'changed at', event.date)
    try:
        requests.post(webhook_url, json={
            'message': get_message(event.message),
            'type': 'new_message'
        })
    except:
        print('Webhook invalide')

@client.on(events.MessageEdited(chats=channel))
async def on_message_updated(event):
    # Log the date of new edits
    print('Message edited', event.id, 'changed at', event.date)
    requests.post(webhook_url, json = {
      'message': get_message(event.message),
      'type': 'update_message'
    })

@client.on(events.MessageDeleted(chats=channel))
async def on_message_deleted(event):
    # Log the date of new edits
    print('Message deleted', event.deleted_id)
    requests.post(webhook_url, json = {
      'message': {
        'id': event.deleted_id,
      },
      'type': 'delete_message'
    })

# Indiquer que le programme est en attente de nouveaux messages
print('En attente de nouveaux messages...')
# Garder le programme en marche
client.run_until_disconnected()
