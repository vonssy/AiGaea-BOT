# AI Gaea Network BOT
AI Gaea Network BOT

Register Here : [AI Gaea Network](https://app.aigaea.net/register?ref=gaj5yIoPw8Osap) | Use Code: gaj5yIoPw8Osap

## Fitur

  - Auto Get Account Information
  - Auto Run With Auto Proxy if u Choose 1 [Use [Monosans Proxy](https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt)]
  - Auto Run With Manual Proxy if u Choose 2 [Paste Ur personal proxy in manual_proxy.txt]
  - Auto Run Without Proxy if u Choose 3
  - Auto Complete Available Mission
  - Auto Connect Dashboard and Extenesion Network
  - Multi Accounts With Threads

## Prasyarat

Pastikan Anda telah menginstal Python3.9 dan PIP.

## Instalasi

1. **Kloning repositori:**
   ```bash
   git clone https://github.com/vonssy/AiGaea-BOT.git
   ```
   ```bash
   cd AiGaea-BOT
   ```

2. **Instal Requirements:**
   ```bash
   pip install -r requirements.txt #or pip3 install -r requirements.txt
   ```

## Konfigurasi

### Screenshots

<div style="text-align: center;">
  <h4><strong>The First 8 Digits of Ur Browser ID</strong></h4>
  <img src="image.png" alt="Image" width="500"/>
</div>

- **accounts.json:** Anda akan menemukan file `accounts.json` di dalam direktori proyek. Pastikan `accounts.json` berisi data yang sesuai dengan format yang diharapkan oleh skrip. Berikut adalah contoh format file:

  ```bash
    [
        {
            "Browser_ID": "The first 8 digits of your browser_id 1",
            "Token": "Your aigaea_bearer_token 1"
        },
        {
            "Browser_ID": "The first 8 digits of your browser_id 2",
            "Token": "Your aigaea_bearer_token 2"
        }
    ]
  ```
- **manual_proxy.txt:** Anda akan menemukan file `manual_proxy.txt` di dalam direktori proyek. Pastikan `manual_proxy.txt` berisi data yang sesuai dengan format yang diharapkan oleh skrip. Berikut adalah contoh format file:
  ```bash
    ip:port # Default Protcol HTTP.
    protocol://ip:port
    protocol://user:pass@ip:port
  ```

## Jalankan

```bash
python bot.py #or python3 bot.py
```

## Penutup

Terima kasih telah mengunjungi repository ini, jangan lupa untuk memberikan kontribusi berupa follow dan stars.
Jika Anda memiliki pertanyaan, menemukan masalah, atau memiliki saran untuk perbaikan, jangan ragu untuk menghubungi saya atau membuka *issue* di repositori GitHub ini.

**vonssy**