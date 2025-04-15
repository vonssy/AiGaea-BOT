from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, uuid, time, json, os, pytz

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
        self.account_proxies = {}

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
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}AI Gaea - BOT
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
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account
        
    def generate_random_browser_id(self, browser_id: str):
        random_browser_id = str(uuid.uuid4())[8:]
        if len(browser_id) == 32:
            return browser_id

        return browser_id[:8] + random_browser_id

    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {account} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        while True:
            try:
                trained = input("Auto Complete Training? Will Burned 0-2500 PTS (y/n) ->").strip().lower()
                if trained in ["y", "n"]:
                    trained = trained == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Enter 'y' to Yes or 'n' to Skip.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' to Yes or 'n' to Skip.{Style.RESET_ALL}")

        return choose, trained

    async def user_data(self, token: str, proxy=None):
        url = "https://api.aigaea.net/api/auth/session"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "0",
            "Content-Type": "application/json"

        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                async with session.post(url=url, headers=headers) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['data']
        except (Exception, ClientResponseError) as e:
            return self.print_message(self.mask_account(token), proxy, Fore.RED, f"GET User ID Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
        
    async def user_ip(self, token: str, username: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/network/ip"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(username, proxy, Fore.RED, f"GET IP Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
        
    async def user_earning(self, token: str, username: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/earn/info"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(username, proxy, Fore.RED, f"GET Earning Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def complete_training(self, token: str, username: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/ai/complete"
        data = json.dumps({"detail":"1_0_0"})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(username, proxy, Fore.RED, f"Complete Training Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def mission_lists(self, token: str, username: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/mission/list"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(username, proxy, Fore.RED, f"GET Available Mission Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def complete_mission(self, token: str, username: str, mission_id: int, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/mission/complete-mission"
        data = json.dumps({"mission_id":mission_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                    continue
                
                return self.print_message(username, proxy, Fore.RED, f"Complete Available Mission Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def send_ping(self, token: str, radnom_browser_id: str, username: str, user_id: str, use_proxy: bool, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/network/ping"
        data = json.dumps({"browser_id":radnom_browser_id, "timestamp":int(time.time()), "uid":user_id, "version":"2.0.2"})
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
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                self.print_message(username, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                proxy = self.rotate_proxy_for_account(token) if use_proxy else None
                return None
            
    async def process_user_earning(self, token: str, username: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(token) if use_proxy else None
            earning = await self.user_earning(token, username, proxy)
            if earning:
                today = earning['today_total']
                total = earning['total_total']
                uptime = earning['today_uptime']

                self.print_message(username, proxy, Fore.WHITE,
                    f"Earning Today {today} PTS "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Earning Total {total} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Uptime: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Today {uptime} Minutes{Style.RESET_ALL}"
                )

            await asyncio.sleep(15 * 60)
            
    async def process_complete_training(self, token: str, username: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(token) if use_proxy else None
            train = await self.complete_training(token, username, proxy)
            if train and train.get("code") == 200:
                burned_points = train.get('burned_points', 0)
                soul = train.get('soul', 0)
                blindbox = train.get('blindbox', 0)

                self.print_message(username, proxy, Fore.GREEN, "Training Completed "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Burned {burned_points} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{soul} Soul PTS{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{blindbox} Blindbox{Style.RESET_ALL}"
                )
            elif train and train.get("code") == 400:
                self.print_message(username, proxy, Fore.YELLOW, "Training Already Completed")

            await asyncio.sleep(24 * 60 * 60)

    async def process_user_missions(self, token: str, username: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(token) if use_proxy else None
            missions = await self.mission_lists(token, username, proxy)
            if missions:
                completed = False
                for mission in missions:
                    mission_id = str(mission['id'])
                    title = mission['title']
                    reward = mission['points']
                    status = mission['status']

                    if mission and status == "AVAILABLE":
                        complete = await self.complete_mission(token, username, mission_id, proxy)
                        if complete:
                            self.print_message(username, proxy, Fore.WHITE,
                                f"Mission {title}"
                                f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{reward} PTS{Style.RESET_ALL}"
                            )
                        else:
                            self.print_message(username, proxy, Fore.WHITE,
                                f"Mission {title} "
                                f"{Fore.RED + Style.BRIGHT}Isn't Completed{Style.RESET_ALL}"
                            )
                        
                    else:
                        completed = True

                if completed:
                    self.print_message(username, proxy, Fore.GREEN,
                        "All Available Mission Is Completed"
                    )
                
            await asyncio.sleep(12 * 60 * 60)

    async def process_send_ping(self, token: str, browser_id: str, username: str, user_id: str, server_host: str, use_proxy: bool):
        radnom_browser_id = self.generate_random_browser_id(browser_id)
        while True:
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )

            proxy = self.get_next_proxy_for_account(token) if use_proxy else None
            ping = await self.send_ping(token, radnom_browser_id, username, user_id, use_proxy, proxy)
            if ping:
                score = ping['score']

                self.print_message(username, proxy, Fore.GREEN,
                    "PING Success"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Network Score:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {score} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Server Host: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{server_host}{Style.RESET_ALL}"
                )

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 10 Minutes For Next Ping...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(10 * 60)

    async def get_user_data(self, token: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(token) if use_proxy else None
        user = None
        while user is None:
            user = await self.user_data(token, proxy)
            if not user:
                proxy = self.rotate_proxy_for_account(token) if use_proxy else None
                continue

            self.print_message(self.mask_account(token), proxy, Fore.GREEN, "GET User ID Success")

            server_host = "Unknown"
            ip_data = await self.user_ip(token, user['name'], proxy)
            if ip_data:
                server_host = ip_data['host']

            return user, server_host
        
    async def process_accounts(self, token: str, browser_id: str, use_proxy: bool, trained: str):
        user, server_host = await self.get_user_data(token, use_proxy)
        if user and server_host:
            username = user['name']
            user_id = user['uid']

            tasks = []
            if trained:
                tasks.append(self.process_complete_training(token, username, use_proxy))
            tasks.append(self.process_user_earning(token, username, use_proxy))
            tasks.append(self.process_user_missions(token, username, use_proxy))
            tasks.append(self.process_send_ping(token, browser_id, username, user_id, server_host, use_proxy))
            await asyncio.gather(*tasks)

    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED+Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            use_proxy_choice, trained = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for account in accounts:
                    browser_id = account.get('Browser_ID')
                    token = account.get('Token')

                    if token and browser_id:
                        tasks.append(self.process_accounts(token, browser_id, use_proxy, trained))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = AiGaea()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] AI Gaea - BOT{Style.RESET_ALL}                                       "                              
        )