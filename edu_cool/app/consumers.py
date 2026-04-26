
import json

from channels.generic.websocket import AsyncWebsocketConsumer

from channels.exceptions import DenyConnection

from app.models import Course

from get_docker_secret import get_docker_secret


class ChatConsumer(AsyncWebsocketConsumer):

    sfu_group = "sfu_group"

    async def connect(self):

        self.room_name = self.scope["url_route"]["kwargs"].get("room_name", None)
        
        if self.room_name is None and self.scope['user'].is_superuser and self.scope['user'].username == get_docker_secret('server_cred_username', 'admin'):
            
            self.scope['is_sfu'] = True

            await self.channel_layer.group_add(self.sfu_group, self.channel_name)
            
            await self.accept()

            return

        if self.room_name is None:

            raise DenyConnection("permission denied")

        try:

            course = await Course.objects.select_related('tutor').aget(id = self.room_name)

        except:

            raise DenyConnection('404: room not found')

        if self.scope['user'] != course.tutor and not await self.scope['user'].enrolled_courses.filter(course = course).aexists():
            # print('erooooooor hereeeeeeeee')

            # print( self.scope['user'].enrolled_courses.objects.filter())
            raise DenyConnection('only tutors and students could join this rrom')

        await self.channel_layer.group_add(self.room_name, self.channel_name)

        await self.accept()


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.sfu_group, self.channel_name)


    async def receive(self, text_data):
        
        text_data_json = json.loads(text_data)
        
        message = text_data_json["message"]

        message['sender_channel'] = self.channel_name


        if not self.scope.get('is_sfu', None):

            message['user_name'] = self.scope['user'].username

            message['room'] = self.room_name

            await self.channel_layer.group_send(
                self.sfu_group, {"type": "chat.message", "message": message}
            )

            return

        if message.get('receiver_channel', None) != None:

            await self.channel_layer.send(
                message['receiver_channel'], {"type": "chat.message", "message": message}
            )

        elif message.get('group', None) != None:

            await self.channel_layer.group_send(
                message['group'], {"type": "chat.message", "message": message}
            )


    async def chat_message(self, event):
        
        message = event["message"]
        
        await self.send(text_data=json.dumps({"message": message}))