from colorama import Fore, Style, init

init(autoreset=True)

def heading(msg):
    print(Fore.MAGENTA + Style.BRIGHT + "=" * 60)
    print(Fore.MAGENTA + Style.BRIGHT + msg)
    print(Fore.MAGENTA + Style.BRIGHT + "=" * 60)

def subheading(msg):
    print(Fore.BLUE + Style.BRIGHT + msg)

def info(msg):
    print(Fore.CYAN + msg)

def success(msg):
    print(Fore.GREEN + "✔ " + msg)

def warning(msg):
    print(Fore.YELLOW + "⚠ " + msg)

def error(msg):
    print(Fore.RED + "✖ " + msg)

def normal(msg):
    print(msg)
