import ccxt
import  pygsheets


gc = pygsheets.authorize(service_account_file='sheets_key.json')
ws = gc.open('Крипта стата').worksheet()

bitget = ccxt.binance()

BYBIT_API_KEY = "8foHKmewIagRdKwrFu"
BYBIT_API_SECRET = "jlamiX5GJEzcLjm58Mu6jCp7Tzi1czcmo4yO"
BYBIT_API_NAME = "crypto_tg"


BITGET_API_KEY = 'bg_2bbcb275f312f0e3e9a0c4450f666680'
BIGET_SECRET = '5c59843c8472f218acb7ec5143d8e88afc88214bc39094e9334e0e166622f114'
BITGET_PASS = 'qwerty02artemka3'

BINANCE_API_KEY = "lFIdAfhiCObuEWZ0KLA1uM86GlM04rgtXXUuV8Gne0TRCSr6UiE3mmM3L6fKRoHq"
BINANCE_API_SECRET = "CuewEHNL93tsrDsPgfZ1dAPvFEVV5kGiEVJ1OhRrf4CSXIpXPQ0eWyBR7BKROjZW"
BINANCE_API_NAME = "crypto_bot"

# 6322204624:AAGshhRKPYSDOTIgtjjlc80HWlFRItpKzxI - test
# 6474806621:AAHXLwsFGKofMMZEIzY8d4jEtrnyBcgS-Xs - base
# 1h 6502861726:AAEzqW6si7CWVacsq8gtlsNutkydVrnYKZM
BOT_API_TOKEN = "6502861726:AAEzqW6si7CWVacsq8gtlsNutkydVrnYKZM"