import os
import requests
import json
from datetime import datetime, timedelta
from threading import Thread
import asyncio

notificationEvents = []
postEvents = []

class Element:
    def __init__(self, sessID="Anon", parse_mode="Markdown", Logs=False):
        self.old_domain = "https://elemsocial.com"
        self.domain = "https://api.elemsocial.com"
        self.Logs = Logs
        self.s_key = False
        self.sessID = sessID
        self.post_blacklist = []
        self.postDateFormat = "%Y-%m-%d %H:%M:%S"
        self.headers = {"S-KEY": self.s_key, 'User-Agent':'ElementAPI'}
        
    async def send_post(self, text:str, Censoring:bool=False, clearMetaData:bool=True):
        response = requests.post(f"{self.old_domain}/System/API/AddPost.php", headers=self.headers, data={"Text": text, "ClearMetadataIMG": clearMetaData, "CensoringIMG": Censoring})
        if not response.status_code == 200:
            return False
        return True
        
    async def load_posts(self, F:str="LATEST", start_index:int=0):
        response = requests.post(f"{self.old_domain}/System/API/LoadPosts.php?F={F}", headers=self.headers, data={"StartIndex": start_index})
        if not response.status_code == 200:
            return False
        
        return response.json

    def on_notification(self, action=False):
        def decorator(func):
            global notificationEvents
            notificationEvents.append({"Action": action, "callback": func})

        return decorator
    
    def on_post(self, type="LATEST"):
        def decorator(func):
            global postEvents
            postEvents.append({"Type": type, "callback": func})

        return decorator

    async def init(self):
        async def notifications_update(self):
            while True:
                try:
                    req = requests.post(f"{self.old_domain}/System/API/Notifications.php?F=CHECK", data={"StartIndex": "0"}, headers={"S-KEY": self.s_key, 'User-Agent':'ElementAPI'})
                except:
                    await asyncio.sleep(1)
                    continue
                if not req.text == "" and int(req.text) >= 1:
                    всеУведы = requests.post(f"{self.old_domain}/System/API/Notifications.php?F=GET", data={"StartIndex": "0"}, headers={"S-KEY": self.s_key, 'User-Agent':'ElementAPI'}).json()
                    for i in range(0, int(req.text)):
                        for event in notificationEvents:
                            class res:
                                def __init__(self, tak):
                                    self.notify = всеУведы[i]
                                    self.self2 = tak
                                
                                async def reply(self, text):
                                    if not всеУведы[i]["Action"] == "PostComment": return False
                                    Content = json.loads(всеУведы[i]["Content"])
                                    try:
                                        comments = requests.post(f"{self.self2.old_domain}/System/API/PostInteraction.php?F=LOAD_COMMENTS", headers={"S-KEY": self.self2.s_key, 'User-Agent':'ElementAPI'}, data={"PostID": Content["PostID"]}).json()
                                    except:
                                        await asyncio.sleep(3)
                                        await res.reply(self, text)
                                    for comment in comments:
                                        if comment["Name"] == всеУведы[i]["Name"] and comment["Text"] == Content["Text"] and comment["Date"] == всеУведы[i]["Date"]:
                                            response = requests.post(f"{self.self2.old_domain}/System/API/PostInteraction.php?F=POST_COMMENT", headers={"S-KEY": self.self2.s_key, 'User-Agent':'ElementAPI'}, data={"Text": text, "PostID": Content["PostID"], "Reply": comment["ID"]})
                                            if not response.status_code == 200:
                                                return False
                                            return True
                                
                                async def send(self, text):
                                    if not всеУведы[i]["PostComment"]: return False
                                    Content = json.loads(всеУведы[i]["PostComment"]["Content"])
                                    response = requests.post(f"{self.old_domain}/System/API/PostInteraction.php?F=POST_COMMENT", headers={"S-KEY": self.s_key, 'User-Agent':'ElementAPI'}, data={"Text": text, "PostID": Content["PostID"]})
                                    if not response.status_code == 200:
                                        return False
                                    return True

                            if event["Action"] == False:
                                await event["callback"](res(self))
                            elif event["Action"] == всеУведы[i]["Action"]:
                                await event["callback"](res(self))
                await asyncio.sleep(8)

        async def posts_update(self):
            while True:
                for event in postEvents:
                    try:
                        response = requests.post(f"{self.old_domain}/System/API/LoadPosts.php?F={event['Type']}", headers={"S-KEY": self.s_key, 'User-Agent':'ElementAPI'}, data={"StartIndex": 0})
                    except:
                        await asyncio.sleep(4)
                        continue
                    if not response.status_code == 200:
                        await asyncio.sleep(4)
                        continue
                    response = response.json()[0]
                    time = datetime.now() - datetime.strptime(response["Date"], "%Y-%m-%d %H:%M:%S")
                    if time <= timedelta(seconds=30):
                        flag = True
                        for post in self.post_blacklist:
                            if str(post) == str(response):
                                flag = False
                        if flag:
                            await event["callback"](response)
                            self.post_blacklist.append(response)
                await asyncio.sleep(10)

        functions = [asyncio.create_task(notifications_update(self)), asyncio.create_task(posts_update(self))]
        await asyncio.gather(*functions)

    def run(self, *args):
        if len(args) == 0:
            with open(f"{self.sessID}.session", "r", -1, "UTF-8") as f:
                print(f.read())
                self.s_key = json.loads(f.read())["S-Key"]
            Element.write_log(self, "INFO", "Authorization success")
            asyncio.run(Element.init(self))
            return True
        
        if len(args) == 1:
            if os.path.exists(f"{self.sessID}.json"): Element.run(self); return
            response = requests.post(f"{self.old_domain}/System/API/Connect.php", headers={'User-Agent':'ElementAPI', "S-KEY": args[0]})
            if not response.status_code == 200:
                Element.write_log(self, "ERROR", "Server unavailable")
                print(f'{datetime.now().strftime("%H:%M-%d.%m.%Y")} [WARN] Server unavailable')
                return False

            elif response.text == '"Error"':
                Element.write_log(self, "ERROR", "Session key expired")
                raise ValueError("Session key expired")
            
            with open(f"{self.sessID}.session", "w") as f:
                f.write(json.dumps({"S-Key": args[0]}))

            asyncio.run(Element.init(self))
            return True

        if len(args) > 2 and "@" in args[0] and "." in args[0]:
            if os.path.exists(f"{self.sessID}.json"): Element.run(self); return

            response = requests.post(f"{self.domain}/auth/login", headers={'User-Agent':'ElementAPI'}, data={"email": args[0], "password": args[1], "device_type": "Browser", "device": args[2]})
            if not response.status_code == 200:
                Element.write_log(self, "ERROR", "Server unavailable")
                print(f'{datetime.now().strftime("%H:%M-%d.%m.%Y")} [WARN] Server unavailable')
                return False
            response = response.json()

            if response["status"] == "error":
                Element.write_log(self, "ERROR", response["text"])
                print(f'{datetime.now().strftime("%H:%M-%d.%m.%Y")} [ERROR] {response["text"]}')
                return False
            if response["status"] == "success":
                Element.write_log(self, "INFO", "Authorization success")
                self.s_key = response["S_KEY"]
                with open(f"{self.sessID}.session", "w") as f:
                    f.write(json.dumps({"S-Key": response["S_KEY"]}))

                asyncio.run(Element.init(self))
                return True
        
    def write_log(self, type, text):
        if self.Logs:
            if not os.path.exists("Logs"):
                os.mkdir("Logs")
            with open(f'Logs/{datetime.now().strftime("%d.%m.%Y")} Log.log', mode="a") as f:
                f.write(f'{datetime.now().strftime("%H:%M-%d.%m.%Y")} [{type}] {text}\n')