from websocket import WebSocketApp
from datetime import datetime
from threading import Thread
from colorama import init
from platform import system
from time import sleep

import keyboard
import json
import os

class log:
    def __init__(self, message) -> None:
        self.message = message
        self.WHITE: str = "\u001b[37m"
        self.MAGENTA: str = "\033[38;5;97m"
        self.YELLOW: str = "\033[38;5;220m"
        self.RED: str = "\033[38;5;196m"
        self.GREEN: str = "\033[38;5;40m"
        self.PINK: str = "\033[38;5;176m"
        init(autoreset=True)

    def getTime(self) -> str:
        return datetime.now().strftime("%H:%M:%S")
    
    def input(self) -> None:
        return f"{self.PINK}[{self.MAGENTA}VOICECORD{self.PINK}] {self.PINK}[{self.MAGENTA}INP{self.PINK}] {self.PINK}[{self.MAGENTA}{self.getTime()}{self.PINK}]{self.WHITE} |{self.WHITE} {self.message}: "
    
    def success(self) -> None:
        print(f"{self.PINK}[{self.MAGENTA}VOICECORD{self.PINK}] {self.PINK}[{self.MAGENTA}SUC{self.PINK}] {self.PINK}[{self.MAGENTA}{self.getTime()}{self.PINK}]{self.WHITE} |{self.GREEN} {self.message}")
    
    def info(self) -> None:
        print(f"{self.PINK}[{self.MAGENTA}VOICECORD{self.PINK}] {self.PINK}[{self.MAGENTA}INF{self.PINK}] {self.WHITE}{self.PINK}[{self.MAGENTA}{self.getTime()}{self.PINK}]{self.WHITE} |{self.YELLOW} {self.message}")

    def error(self) -> None:
        print(f"{self.PINK}[{self.MAGENTA}VOICECORD{self.PINK}] {self.PINK}[{self.MAGENTA}ERR{self.PINK}] {self.PINK}[{self.MAGENTA}{self.getTime()}{self.PINK}]{self.WHITE} |{self.RED} {self.message}")

class openWebsocket(WebSocketApp):
    def __init__(self, token: str, guild_id: int, voice_channel_id: int) -> None:
        self.token = token
        self.guild = guild_id
        self.vc = voice_channel_id

        self.connect = {"op": 4, "d": {"guild_id": self.guild, "channel_id": self.vc, "self_mute": True, "self_deaf": True}}
        self.disconnect = {"op": 4, "d": {"guild_id": guild_id, "channel_id": None}}

        self.heartbeatInterval = None
        self.websocketAddress: str = "wss://gateway.discord.gg/?v=10&encoding=json"

        super().__init__(self.websocketAddress,
                         on_open=self.handleOpen,
                         on_message=self.handleMessage,
                         on_close=self.handleClose)
        
    def handleOpen(self, ws) -> None:
        self.send(json.dumps({
            "op": 2,
            "d": {
                "intents": 7,
                "token": self.token,
                "properties": {
                    "$os": system(),
                    "$browser": "Chrome",
                    "$device": "Desktop"
                }
            }
        }))
        log("Authentication payload sent").info()
        self.send(json.dumps(self.connect))
        
    def handleMessage(self, ws, message: str) -> None:
        message = json.loads(message)
        event: str = message['t']
        data: dict = message['d']
        op: int = message['op']
        
        if op == 10:
            self.heartbeatInterval = int(data["heartbeat_interval"]) / 1000
            log("Heartbeat interval: {}".format(self.heartbeatInterval)).info()
            Thread(target=self.heartbeatCycle).start()
        elif event == "READY":
            log("Succesfully logged in").success()
        
    def handleClose(self, ws, status: int, message: str) -> None:
        if status == 4004:
            log("Token invalid").error()
            os._exit(1)
        else:
            os.system("cls")
            self.close()
            self.run_forever()

    def handleQuit(self) -> None:
        self.send(json.dumps(self.disconnect))
        os._exit(1)
    
    def heartbeatCycle(self) -> None:
        while True:
            self.send(json.dumps({"op": 1, "d": "null"}))
            sleep(self.heartbeatInterval)

if __name__ == "__main__":
    try:
        token = str(input(log("Enter your token").input()))
        guild = int(input(log("Enter guild ID").input()))
        channel = int(input(log("Enter channel ID").input()))
        websocket = openWebsocket(token, guild, channel)
        keyboard.add_hotkey("ctrl+q", websocket.handleQuit)
        websocket.run_forever()
    except ValueError:
        log('Invalid input').error()
        os._exit(1)
