from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from colorama import *
from datetime import datetime
from fake_useragent import FakeUserAgent
import asyncio, time, base64, json, uuid, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class AiGaea:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://app.aigaea.net",
            "Referer": "https://app.aigaea.net/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}AiGaea - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        try:
            if not os.path.exists('accounts.json'):
                self.log(f"{Fore.RED}File 'accounts.json' tidak ditemukan.{Style.RESET_ALL}")
                return

            with open('accounts.json', 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_auto_proxies(self):
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url) as response:
                    response.raise_for_status()
                    content = await response.text()
                    with open('proxy.txt', 'w') as f:
                        f.write(content)

                    self.proxies = content.splitlines()
                    if not self.proxies:
                        self.log(f"{Fore.RED + Style.BRIGHT}No proxies found in the downloaded list!{Style.RESET_ALL}")
                        return
                    
                    self.log(f"{Fore.GREEN + Style.BRIGHT}Proxies successfully downloaded.{Style.RESET_ALL}")
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
                    self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                    await asyncio.sleep(3)
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed to load proxies: {e}{Style.RESET_ALL}")
            return []
        
    async def load_manual_proxy(self):
        try:
            if not os.path.exists('manual_proxy.txt'):
                print(f"{Fore.RED + Style.BRIGHT}Proxy file 'manual_proxy.txt' not found!{Style.RESET_ALL}")
                return

            with open('manual_proxy.txt', "r") as f:
                proxies = f.read().splitlines()

            self.proxies = proxies
            self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed to load manual proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        
        return f"http://{proxies}" # Change with yours proxy schemes if your proxy not have schemes [http:// or socks5://]

    def get_next_proxy(self):
        if not self.proxies:
            self.log(f"{Fore.RED + Style.BRIGHT}No proxies available!{Style.RESET_ALL}")
            return None

        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.check_proxy_schemes(proxy)
    
    def generate_browser_id(self, browser_id: str):
        random_browser_id = str(uuid.uuid4())[8:]
        if len(browser_id) > 8:
            browser_id = browser_id[:8]

        return browser_id + random_browser_id
    
    def hide_token(self, token):
        hide_token = token[:3] + '*' * 3 + token[-3:]
        return hide_token
    
    def decode_token(self, token: str):
        header, payload, signature = token.split(".")
        decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
        parsed_payload = json.loads(decoded_payload)
        if parsed_payload and "expire" in parsed_payload:
            exp_time = parsed_payload['expire']
            exp_time_wib = datetime.fromtimestamp(exp_time, pytz.utc).astimezone(wib).strftime('%x %X %Z')
            return exp_time_wib

    def print_token_exp(self, name):
        return self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT} Access Token Expired {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )
        
    async def user_data(self, token: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/auth/session"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "0",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        if response.status == 401:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {self.hide_token(token)} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Access Token Expired {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                            return

                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def user_earning(self, token: str, name: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/earn/info"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            self.print_token_exp(name)
                            return

                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def user_ip(self, token: str, name: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/network/ip"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            self.print_token_exp(name)
                            return
                            
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def mission_lists(self, token: str, name: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/mission/list"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            self.print_token_exp(name)
                            return
                        
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def complete_mission(self, token: str, name: str, mission_id: int, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/mission/complete-mission"
        data = json.dumps({"mission_id":mission_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        if response.status == 401:
                            self.print_token_exp(name)
                            return
                        
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def earning_log(self, token: str, name: str, proxy=None):
        while True:
            earning_total = 0
            earning_today = 0
            today_uptime = 0
            time = "N/A"

            exp_token_time = self.decode_token(token)
            if exp_token_time:
                time = exp_token_time

            earning = await self.user_earning(token, name, proxy)
            if earning:
                earning_total = earning['total_total']
                earning_today = earning['today_total']
                today_uptime = earning['today_uptime']

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Earning {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}Total {earning_total} PTS{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}Today {earning_today} PTS{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}Uptime{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {today_uptime} Minutes {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Token Expired at {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{time}{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
            )
            await asyncio.sleep(900)
                
    async def send_ping(self, token: str, name: str, browser_id: str, uid: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/network/ping"
        data = json.dumps({"browser_id":browser_id, "timestamp":int(time.time()), "uid":uid, "version":"2.0.2"})
        headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "chrome-extension://cpjicfogbgognnifjgmenmaldnmeeeib",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "User-Agent": FakeUserAgent().random
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        if response.status == 401:
                            self.print_token_exp(name)
                            return
                        
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
        
    async def question(self):
        while True:
            try:
                print("1. Run With Auto Proxy")
                print("2. Run With Manual Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Auto" if choose == 1 else 
                        "With Manual" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    await asyncio.sleep(1)
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
        
    async def process_accounts(self, token: str, browser_id: str, use_proxy: bool):
        hide_token = self.hide_token(token)
        ping_count = 1
        proxy = None

        if use_proxy:
            proxy = self.get_next_proxy()

        user = None
        while user is None:
            user = await self.user_data(token, proxy)
            if not user:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {hide_token} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Proxy {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}GET User Data Failed{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                )
                await asyncio.sleep(1)

                if not use_proxy:
                    return

                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Try With Next Proxy...{Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )

                proxy = self.get_next_proxy()
                continue
            
            name = user['name']
            uid = user['uid']

            asyncio.create_task(self.earning_log(token, name, proxy))

            missions = await self.mission_lists(token, name, proxy)
            if missions:
                completed = False
                for mission in missions:
                    mission_id = str(mission['id'])
                    status = mission['status']

                    if mission and status == "AVAILABLE":
                        complete = await self.complete_mission(token, name, mission_id, proxy)
                        if complete:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Mission {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{mission['title']}{Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Reward {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{mission['points']} PTS{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Mission {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{mission['title']}{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Isn't Completed {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        
                    else:
                        completed = True

                if completed:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} All Available Mission Is Completed {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} GET Mission Data Failed {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                )

            host = "Unknown"
            ip = await self.user_ip(token, name, proxy)
            if ip:
                host = ip['host']

            while True:
                ping = await self.send_ping(token, name, browser_id, uid, proxy)
                if ping:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Proxy {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}PING {ping_count} Success{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}Network Score {ping['score']}{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Host{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {host} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                else:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Proxy {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}PING {ping_count} Failed{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Host{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {host} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                    )

                    if use_proxy:
                        proxy = self.get_next_proxy()

                ping_count += 1

                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Wait For 10 Minutes For Next Ping...{Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )
                await asyncio.sleep(600)
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED}No accounts loaded from 'accounts.json'.{Style.RESET_ALL}")
                return

            use_proxy_choice = await self.question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            if use_proxy and use_proxy_choice == 1:
                await self.load_auto_proxies()
            elif use_proxy and use_proxy_choice == 2:
                await self.load_manual_proxy()
            
            while True:
                tasks = []
                for account in accounts:
                    token = account["Token"]
                    browser_id = account["Browser_ID"]
                    if token and browser_id:
                        browser_id = self.generate_browser_id(browser_id)
                        tasks.append(self.process_accounts(token, browser_id, use_proxy))

                await asyncio.gather(*tasks)
                await asyncio.sleep(3)

        except (Exception, FileNotFoundError) as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            return

if __name__ == "__main__":
    try:
        bot = AiGaea()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] AiGaea - BOT{Style.RESET_ALL}                                       "                              
        )