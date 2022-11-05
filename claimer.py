import threading, requests, json, ctypes, sys, random, time, os

lock = threading.Lock()
config = json.load(open("config.json"))
proxyless = config["proxyless"]
threads = config["threads"]
promotion_id = config["promotion_id"]

tokens = open("input/tokens.txt", "r").read().splitlines()
codes = open(f"output/{promotion_id}.txt", 'a')

class data:
    success = 0
    locked = 0
    no_nitro = 0
    errors = 0
    em_locked = 0

def error(*kwargs):
    t = time.strftime("%H:%M:%S")
    if len(kwargs) == 1: sys.stdout.write("[{}] {}{}{}\n".format(f"\033[1;34;40m{t}\x1b[0m", "\033[1;31;40m", kwargs[0], "\x1b[0m"))
    else: sys.stdout.write("[{}] - ({}) {}{}{}\n".format(f"\033[1;34;40m{t}\x1b[0m", f"\u001b[33m{kwargs[0]}\x1b[0m", "\033[1;31;40m", kwargs[1], "\x1b[0m"))

def info(*kwargs): 
    t = time.strftime("%H:%M:%S")
    if len(kwargs) == 1: sys.stdout.write("[{}] {}{}{}\n".format(f"\033[1;34;40m{t}\x1b[0m", "\033[1;33;40m", kwargs[0], "\x1b[0m"))
    else: sys.stdout.write("[{}] - ({}) {}{}{}\n".format(f"\033[1;34;40m{t}\x1b[0m", f"\u001b[33m{kwargs[0]}\x1b[0m", "\033[1;33;40m", kwargs[1], "\x1b[0m"))

def success(*kwargs):
    t = time.strftime("%H:%M:%S")
    if len(kwargs) == 1: sys.stdout.write("[{}] {}{}{}\n".format(f"\033[1;34;40m{t}\x1b[0m", "\033[1;32;40m", kwargs[0], "\x1b[0m"))
    else: sys.stdout.write("[{}] - ({}) {}{}{}\n".format(f"\033[1;34;40m{t}\x1b[0m", f"\u001b[33m{kwargs[0]}\x1b[0m", "\033[1;32;40m", kwargs[1], "\x1b[0m"))

def update_console():
    while True:
        ctypes.windll.kernel32.SetConsoleTitleW(f"Tokens: {len(tokens)} | Codes Claimed: {data.success} | Locked Tokens: {data.locked} | Email Locked Tokens: {data.em_locked} | No Nitro Tokens: {data.no_nitro}")
       
def getDict():
    proxy = random.choice(open("input/proxies.txt", "r").read().splitlines())
    return {'http://': f'http://{proxy}', 'https://': f'http://{proxy}'}

def remove_item(file: str, item: str):
    lock.acquire()
    all = open(f'{file}.txt', "r").read().split("\n")
    for thing in all:
        if item == thing: all.remove(item)
    else: open(f'{file}.txt', "w").write("\n".join(all))
    lock.release()
            
def get_code(token):
    proxi = getDict()
    url = f'https://discord.com/api/v9/outbound-promotions/{promotion_id}/claim'
    headers={
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": token,
    "cookie": "__dcfduid=41071d405c1411edaff649bf5fbbcd1b; __sdcfduid=41071d415c1411edaff649bf5fbbcd1bc63a78024c99e8490f1e30d13dc6d4916a43101ed32071f43e9dd618fb83cdbf",
    "referer": "https://discord.com/channels/967617613960187974/981260247807168532",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
    "x-discord-locale": "en-US",
    "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMi4wLjUwMDUuNjEgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwMi4wLjUwMDUuNjEiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTMwNDEwLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
    }
    try:
        r = requests.post(url, headers=headers, proxies=None if proxyless else proxi)
        print(r.text)
        if r.status_code == 200:
            code = r.json()['code']
            success(f"Got code ({code}) ({promotion_id})")
            codes.write(code + '\n')
            data.success += 1

        elif r.status_code == 403:
            if "This action requires a premium subscription" in r.text:
                data.no_nitro += 1
                info(f"Token doesnt have nitro ({token})")

            elif "You need to verify your account in order to perform this action." in r.text:
                data.locked += 1
                error(f"Token is locked ({token})")

            elif "You need to verify your e-mail in order to perform this action." in r.text:
                data.em_locked += 1
                error(f"Token is email locked ({token})")

            elif 'Unauthorized' in r.text:
                error("Token is invalid ({})".format(token))

            else:
                e = r.json()["message"]
                error(f"Other error ({e}) + ({token})")

        remove_item("input/tokens", token)
    except Exception as err:
        error(err)
            
def check(token):
    try:
        proxi = getDict()
        headers={
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "cookie": "__dcfduid=41071d405c1411edaff649bf5fbbcd1b; __sdcfduid=41071d415c1411edaff649bf5fbbcd1bc63a78024c99e8490f1e30d13dc6d4916a43101ed32071f43e9dd618fb83cdbf",
        "referer": "https://discord.com/channels/967617613960187974/981260247807168532",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": config["user_agent"],
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMi4wLjUwMDUuNjEgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwMi4wLjUwMDUuNjEiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTMwNDEwLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
        }
        r = requests.get("https://discord.com/api/v9/users/@me/outbound-promotions/codes", headers=headers, proxies=None if proxyless else proxi)  
        if r.status_code == 200:
            if r.text == []:
                data.no_nitro += 1
                info(f"Token doesnt have nitro ({token})")
            else:
                for promo in r.json():
                    promotion = promo["promotion"]["outbound_title"]
                    id = promo["promotion"]["id"]
                    code = promo["code"]
                    if not os.path.exists(f'output/{promotion}'): 
                        os.makedirs(f'output/{promotion}')
                        open(f'output/{promotion}/{id}.txt', 'w')
                    open(f'output/{promotion}/{id}.txt', 'a').write(code + '\n')
                    success(f"Got code ({code}) ({promotion}) ({promotion_id})")
                    data.success += 1
                    if 'PC Game Pass (3 Months)' in promotion:
                        while True:
                            print(proxi)
                    elif id == 1013912809710559232:
                        while True:
                            print(proxi)

        elif r.status_code == 403:
            if "You need to verify your account in order to perform this action." in r.text:
                data.locked += 1
                error(f"Token is locked ({token})")
                
            elif "You need to verify your e-mail in order to perform this action." in r.text:
                data.em_locked += 1
                error(f"Token is email locked ({token})")

            elif 'Unauthorized' in r.text:
                error("Token is invalid ({})".format(token))

            else:
                e = r.json()
                error(f"Other error ({e}) + ({token})")

        remove_item("input/tokens", token)
    except Exception as err:
        error(err)
    


def start(threads):
    threading.Thread(target=update_console).start()
    while True:
        try:
            local_threads=[]
            for _ in range(threads):
                tk = tokens[0]
                if config["use_id"]: start_thread = threading.Thread(target=get_code, args=[tk])
                else: start_thread = threading.Thread(target=check, args=[tk])
                local_threads.append(start_thread)
                start_thread.start()
                tokens.pop(0)
            for thread in local_threads:
                thread.join()
        except IndexError:
            break

if __name__ == "__main__":
    start(threads)

