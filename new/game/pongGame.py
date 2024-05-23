from .models import ball, pad
import asyncio

class pongGame :

    def __init__(self, room_name, pongConsumer) :
        self.room_name = room_name
        self.room_group_name = f'game_{self.room_name}'
        self.player_number = 1
        self.pongConsumer = pongConsumer
        self.game_state = False
        #self.ids = [pongConsumer.player]
        #self.players = [player_name]
        print("YO!")
        
        
    async def launchGame(self) :
        print("WESH")
        self.game_task = None
        self.ball = ball(400, 300, 10)
        self.leftPad = pad(0, 260, 10, 80, ball, 2, None)
        self.rightPad = pad(790, 260, 10, 80, ball, 2, self.leftPad)
        self.score = [0, 0]
        self.player_number = 2
        self.game_state = True
        self.game_task = asyncio.create_task(self.start_countdown())

    async def start_countdown(self):
        for i in range(3, 0, -1):
            await self.pongConsumer.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'countdown',
                    'countdown': i
                }
            )
            await asyncio.sleep(1)
        await self.pongConsumer.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'countdown',
                'countdown': "Go!"
            }
        )
        await asyncio.sleep(1)
        await self.pongConsumer.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'countdown',
                'countdown': ""
            }
        )
        await self.game_loop()

    async def game_loop(self):
        while True:
            #self.update_ball_position()
            #print("1")
            self.ball.move()
            #print("2")
            self.leftPad.move()
            #print("3")
            self.rightPad.move()
            #print("4")
            self.update_ball_position()
            #print("5")
            self.collisions(self.ball, self.leftPad, self.rightPad)
            #print("6")
            await self.send_game_state()
            await asyncio.sleep(0.01)

    def collisions(self ,ball, leftPad, rightPad):
        if (ball.y + ball.rad >= 600) or (ball.y - ball.rad <= 0) :
            ball.ySpeed *= -1
        if ball.xSpeed < 0 :
            if ball.y >= leftPad.y and ball.y <= leftPad.y + leftPad.height:
                if ball.x - ball.rad <= leftPad.x + leftPad.width :
                    ball.xSpeed *= -1
                    if ball.xSpeed < 8.1 :
                        ball.xSpeed += 0.05
                    midPad = leftPad.y + leftPad.height / 2
                    diff = midPad - ball.y
                    reduc = (leftPad.height / 2) / ball.maxSpeed
                    ball.ySpeed = diff / reduc
        elif ball.xSpeed > 0 :
            if ball.y >= rightPad.y and ball.y <= rightPad.y + rightPad.height:
                if ball.x + ball.rad >= rightPad.x :
                    ball.xSpeed *= -1
                    if ball.xSpeed > -8.1 :
                        ball.xSpeed += -0.05
                    midPad = rightPad.y + rightPad.height / 2
                    diff = midPad - ball.y
                    reduc = (leftPad.height / 2) / ball.maxSpeed
                    ball.ySpeed = diff / reduc

    def update_ball_position(self):
        if self.ball.x <= 0:
            self.score[1] += 1
            self.reset_all()
        if self.ball.x >= 800:
            self.score[0] += 1
            self.reset_all()

    def reset_all(self):
        #self.ball.x, ball.y = [400, 300]
        #self.ball.xSpeed, ball.ySpeed = [0, 0]
        self.ball.reset()
        self.rightPad.y = 260
        self.leftPad.y = 260

    async def send_game_state(self):
        game_state = {
            'ball_position': [self.ball.x, self.ball.y],
            'paddle1_position': (self.leftPad.y),
            'paddle2_position': (self.rightPad.y),
            'score': self.score,
        }
        #print(self.leftPad.y)
        #print(game_state)
        await self.pongConsumer.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_state',
                'game_state': game_state
            }
        )
