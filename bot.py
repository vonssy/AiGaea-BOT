from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, base64, time, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class AiGaea:
    def __init__(self) -> None:
        self.UA = FakeUserAgent().random
        self.DASHBOARD_HEADERS = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://app.aigaea.net",
            "Priority": "u=1, i",
            "Referer": "https://app.aigaea.net/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": self.UA
        }
        self.EXTENSION_HEADERS = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "chrome-extension://cpjicfogbgognnifjgmenmaldnmeeeib",
            "Priority": "u=1, i",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Storage-Access": "active",
            "User-Agent": self.UA
        }
        self.BASE_API = "https://api.aigaea.net/api"
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
    
    def decode_token(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            username = parsed_payload["username"]
            user_id = parsed_payload["userid"]
            
            return username, user_id
        except Exception as e:
            return None, None
    
    def mask_account(self, account):
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account

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
    
    async def user_earning(self, token: str, username: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/earn/info"
        headers = {
            **self.DASHBOARD_HEADERS,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(username, proxy, Fore.RED, f"GET Earning Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def complete_training(self, token: str, username: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/ai/complete"
        data = json.dumps({"detail":"2_0_0"})
        headers = {
            **self.DASHBOARD_HEADERS,
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
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
                return self.print_message(username, proxy, Fore.RED, f"Complete Today Training Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def user_ip(self, gaea_token: str, username: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/network/ip"
        headers = {
            **self.EXTENSION_HEADERS,
            "Authorization": f"Bearer {gaea_token}",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(username, proxy, Fore.RED, f"GET IP Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def send_ping(self, gaea_token: str, browser_id: str, username: str, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/network/ping"
        data = json.dumps({"uid":user_id, "browser_id":browser_id, "timestamp":int(time.time()), "version":"3.0.19"})
        headers = {
            **self.EXTENSION_HEADERS,
            "Authorization": f"Bearer {gaea_token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
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
                return self.print_message(username, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def process_user_earning(self, gaea_token: str, username: str, user_id: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None

            earning = await self.user_earning(gaea_token, username, proxy)
            if earning and earning.get("msg") == "Success":
                today = earning.get("data", {}).get("today_total", "N/A")
                total = earning.get("data", {}).get("total_total", "N/A")
                soul = earning.get("data", {}).get("total_soul", "N/A")
                uptime = earning.get("data", {}).get("today_uptime", "N/A")

                self.print_message(username, proxy, Fore.GREEN, "GET Earning Data Success"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Today Gaea:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {today} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Total Gaea: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{total} PTS{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Soul:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {soul} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Today Uptime: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{uptime} Minutes{Style.RESET_ALL}"
                )

            await asyncio.sleep(30 * 60)
            
    async def process_complete_training(self, gaea_token: str, username: str, user_id: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None

            train = await self.complete_training(gaea_token, username, proxy)
            if train and train.get("code") == 200:
                burned_points = train.get("burned_points", 0)
                soul = train.get("soul", 0)
                blindbox = train.get("blindbox", 0)

                self.print_message(username, proxy, Fore.GREEN, "Today Training Completed "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Burned {burned_points} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{soul} Soul PTS{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{blindbox} Blindbox{Style.RESET_ALL}"
                )
            elif train and train.get("code") == 400:
                self.print_message(username, proxy, Fore.YELLOW, "Today Training Already Completed")

            await asyncio.sleep(12 * 60 * 60)

    async def process_get_ip_address(self, gaea_token: str, username: str, user_id: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None

        ip_data = None
        while ip_data is None:
            ip_data = await self.user_ip(gaea_token, username, proxy)
            if not ip_data:
                proxy = self.rotate_proxy_for_account(user_id) if use_proxy else None
                await asyncio.sleep(5)
                continue

            country = ip_data.get("data", {}).get("country", "N/A")
            host = ip_data.get("data", {}).get("host", "N/A")

            self.print_message(username, proxy, Fore.GREEN, "GET IP Data Success"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}Country:{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {country} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Connected Host: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{host}{Style.RESET_ALL}"
            )

            return True

    async def process_send_ping(self, gaea_token: str, browser_id: str, username: str, user_id: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )

            ping = await self.send_ping(gaea_token, browser_id, username, user_id, proxy)
            if ping and ping.get("msg") == "Success":
                score = ping.get("data", {}).get("score", "N/A")

                self.print_message(username, proxy, Fore.GREEN,"PING Success "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Network Score: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{score}{Style.RESET_ALL}"
                )

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 10 Minutes For Next Ping...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(10 * 60)
        
    async def process_accounts(self, gaea_token: str, browser_id: str, username: str, user_id: str, use_proxy: bool, trained: str):
        is_ready = await self.process_get_ip_address(gaea_token, username, user_id, use_proxy)
        if is_ready:

            tasks = []
            if trained:
                tasks.append(self.process_complete_training(gaea_token, username, user_id, use_proxy))

            tasks.append(self.process_user_earning(gaea_token, username, user_id, use_proxy))
            tasks.append(self.process_send_ping(gaea_token, browser_id, username, user_id, use_proxy))
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
                    if account:
                        gaea_token = account["gaeaToken"]
                        browser_id = account["browserId"]

                        if gaea_token and browser_id:
                            username, user_id = self.decode_token(gaea_token)

                            if username and user_id:
                                tasks.append(asyncio.create_task(self.process_accounts(gaea_token, browser_id, username, user_id, use_proxy, trained)))

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