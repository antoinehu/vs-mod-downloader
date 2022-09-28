import requests
import re
import os, sys
from bs4 import BeautifulSoup as bs
from pathlib import Path
import logging
try:
    import wget
except ImportError:
    import wget_ as wget

home_url = "https://mods.vintagestory.at"
modlist_url = "https://mods.vintagestory.at/list/mod"
OUTPUT_DIR = "output"

def get_mod_download_url(mod_page_url):
    req_filelist = requests.get(mod_page_url, 'html.parser')
    html_filelist = req_filelist.text

    p_htmlfilelist = bs(html_filelist, features="lxml")
    trs = p_htmlfilelist.body.find_all('tr', attrs={"data-assetid": True})
    latest = max(trs, key=lambda tr: int(tr.attrs["data-assetid"]))
    fileid = latest.find('a', {'href': re.compile(r'/download\?fileid.')})['href']
    downlink = home_url + fileid
    logging.debug("Mod download link:", downlink)
    return downlink


def get_mods_from_moddir(modpath):
    modlist = os.listdir(modpath)
    for mod in modlist:
        if mod[-4:-1] + mod[-1] == '.zip':
            upper = []
            for j, mm in enumerate(mod):
                if mm.isupper():
                    upper.append(j)
            modx = mod.split(' ')[0]
            if 5 in upper or 6 in upper:
                m = mod[0:-4]
                m = m[0:9]
                mods.append([m, mod[0:-4]])
                modx = ''
                mody = ''
            else:
                m = mod[0:-4]
                m = m[0:6]
                if 'xlib' in m:
                    m = 'xlib'
                mods.append([m, mod[0:-4]])
    return mods

def get_mod_page_urls(modname):
    modname = modname.strip(" _-.'!0")
    regex = r''
    for m in modname:
        regex = regex + '[\_\-\.\'\!\s]*' + m
    regex = regex + '[\_\-\.\'\!\s]*'
    logging.debug("regex: ", regex)

    html_modname = req_modname.text
    html_modname = html_modname.strip(" _-.'!")
    p_htmlmodname = bs(html_modname, features="lxml")
    # print(p_htmlmodname)
    urls = p_htmlmodname.find_all('strong', text=re.compile(".*({}).*".format(regex), re.IGNORECASE))
    return urls

if __name__ == "__main__":
    mods = []
    # Ask user how to download mods
    while True:
        answer = int(input("\nSearch mods by hand (1), read mods automatically from a directory (2) , or exit (0)?"))
        if answer == 1:
            search_active = True
            break
        elif answer == 2:
            search_active = False
            config_file = Path("modsdir.txt")
            try:
                with open(config_file, "r") as f:
                    mods_dir = f.read()
            except FileNotFoundError:
                mods_dir = input('What is your mod directory?')
                print(f"Writing {mods_dir} to " + str(config_file.absolute()))
                with open(config_file, "w") as f:
                    f.write(mods_dir)
            modpath = Path(mods_dir)
            mods = get_mods_from_moddir(modpath)
            break
        elif answer == 0:
            search_active = False
            break
        else:
            print("Input not recognized. ")

    # Get page with all the mods
    req_modname = requests.get(modlist_url, 'html.parser')

    # Create output directory
    path_out = Path(OUTPUT_DIR)
    if not path_out.is_dir():
        print("Creating output directory at " + str(path_out.absolute()))
        path_out.mkdir()

    while len(mods) > 0 or search_active:
        if search_active:
            mod_name = input('\n\nSearch for mod name (0 for quit): ')
            full_mod = mod_name
            if mod_name == '0':
                break
        else:
            mod_name, full_mod = mods.pop()

        mod_urls = get_mod_page_urls(mod_name)
        if len(mod_urls) == 1:
            mod_url = mod_urls[0].parent['href']
        elif len(mod_urls) > 1:
            print(f"\n\nFound more than one mod for search {mod_name}")
            if full_mod:
                print(f"Full mod name: {full_mod}\n")
            for i, n in enumerate(mod_urls):
                print(str(i + 1) + '. ' + str(n)[8:-9])
            x = int(input("\nWhich do you want to download? (0 for pass): ")) - 1
            full_mod = str(mod_urls[x])[8:-9]
            if x == -1:
                continue
            mod_url = mod_urls[x].parent['href']
        else:
            print(f"No results for {mod_name}.")
            continue

        url=home_url+mod_url
        print(f"Downloading {full_mod}.")
        download_url = get_mod_download_url(url)
        response = wget.download(download_url, out=str(path_out))
        print(f"{full_mod} downloaded successfully.")

    print("Done. Exiting...")


