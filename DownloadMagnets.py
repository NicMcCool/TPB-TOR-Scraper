import bs4, requests, re, os
import subprocess, psutil
from selenium import webdriver

magnetDatabase = <update here>

# TOR SETTINGS
torport = 9150
proxies = {
    "http": "socks5h://localhost:{}".format(torport),
    "https": "socks5h://localhost:{}".format(torport),
}

# check that tor is up and running - must be up to request tor links
def checkIfProcessRunning(processName):
    """
    Check if there is any running process that contains the given name processName.
    """
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if proc.name().lower() == processName.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


# output of tor check
if checkIfProcessRunning("tor.exe"):
    print("Tor is running.")
else:
    print("Starting up Tor.")
    os.startfile("<tor app location>")
    input("When Tor is running press Enter to continue...")

# Grab the magnet links, save to db, remove ones with banned words, and open in Deluge
def grabber(webLink, bannedWords):
    tpb = requests.get(webLink, proxies=proxies)
    tpbC = tpb.content
    soup = bs4.BeautifulSoup(tpbC, "html.parser")
    # check if site is up or down
    upOrDown = len(tpbC)
    if upOrDown < 100:
        print("The site may be down...")
    else:
        print("The site looks to be live.")
    # reset links list
    Links = []

    # get magnets
    for magnets in soup.findAll("a", attrs={"href": re.compile("^magnet:\?xt")}):
        link = magnets.get("href")
        Links.append(link)

    # sanitze inputs as all lowercase
    bannedWordsLower = [x.lower() for x in bannedWords]
    linksLower = [x.lower() for x in Links]
    magnetDBFile = open(magnetDatabase, "r")
    magnetCheck = magnetDBFile.read()

    # remove any link with banned words
    list = [
        x
        for x in linksLower
        if not any(word in x.split(".") for word in bannedWordsLower)
    ]

    # remove any link that has already been added to the database
    list2 = [x for x in list if not any(word in x.split(".") for word in magnetCheck)]

    # print magnet link to screen, write to databse, then open link
    magnetDB = open(magnetDatabase, "a")
    for magnet in list2:
        magnetReadable = "_".join(
            (magnet.replace("=", ".").replace("+", ".")).split(".")[2:7]
        )
        print(magnetReadable)
        magnetDB.write(magnet + "\n")
        os.startfile(magnet)


bannedWordsTPB4k = ["1080p", "cam", "kor", "french", "spanish"]             #example banmned words list for 4k movies
tpb4kTor = "http://<update>.onion/search/4k%20atmos/0/99/207"               #example link with search. provide your own tor TPB link

grabber(tpb4kTor, bannedWordsTPB4k)


# TODO : Cycle through links and banned words