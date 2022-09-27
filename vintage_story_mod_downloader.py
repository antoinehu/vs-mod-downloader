import requests
import re
import string
import os, sys
import wget_ as wget
from bs4 import BeautifulSoup as bs

home_url = "https://mods.vintagestory.at"
modlist_url = "https://mods.vintagestory.at/list/mod"

req_modname=requests.get(modlist_url,'html.parser')
search_active = False
curr_path=os.path.dirname(os.path.abspath(__file__))

if not os.path.isfile(".\\modsdir.txt"):
    f=open(".\\modsdir.txt", "w+")    
    mods_dir=input('What is your mod directory?')
    f.write(mods_dir)
    f.close

f=open(".\\modsdir.txt", "r")

if f.read()=='':
    f.close()
    f=open(".\\modsdir.txt", "w")
    mods_dir=input('What is your mod directory?')
    f.write(mods_dir)
    f.close()

f.close()
    
f=open(".\\modsdir.txt", "r")
modpath=f.read()
f.close()

path_out='.\\output'
if not os.path.isdir(path_out):
    os.mkdir(path_out)
    print("Creating output directory")


modlist = os.listdir(modpath)
mods=[]

search=input("\nDo you wanna search mods by hand? (y or n): ")

if search.lower() not in ['y','yes']:
    for mod in modlist:
        if mod[-4:-1]+mod[-1] == '.zip':
            upper=[]
            for j,mm in enumerate(mod):
                if mm.isupper():
                    upper.append(j)
            modx=mod.split(' ')[0]
            if 5 in upper or 6 in upper:
                m=mod[0:-4]
                m=m[0:9]
                mods.append([m,mod[0:-4]])
                modx=''
                mody=''
            else:
                m=mod[0:-4]
                m=m[0:6]
                if 'xlib' in m:
                    m='xlib'  
                mods.append([m,mod[0:-4]])
else:
    search_active = True

if search_active:
    for i in range(0,1000):
        mods.append(['',''])

for m,full_mod in mods:
    break_ = False
    mod_name=m
    if search_active:
        mod_name=input('\n\nSearch for mod name (0 for quit): ')
        full_mod=''
        if mod_name=='0':
            print("Exiting...")
            sys.exit(0)
    
    mod_name=mod_name.strip(" _-.'!0")
    regex=r'' 
    for m in mod_name:
        regex=regex+'[\_\-\.\'\!\s]*'+m
    regex=regex+'[\_\-\.\'\!\s]*'
    #print(regex)
    
    html_modname=req_modname.text
    html_modname=html_modname.strip(" _-.'!")
    p_htmlmodname=bs(html_modname)
    #print(p_htmlmodname)

    mod_urls=p_htmlmodname.find_all('strong',text=re.compile(".*({}).*".format(regex),re.IGNORECASE))
    if len(mod_urls) == 0:
        break_ = True
        print("\n\nNo results for {0}\n".format(mod_name))
    elif len(mod_urls)==1:
        mod_urls.append('x')

    #os.system('cls')
        
    if not break_:

        if mod_urls[-1]!='x':
            print("\n\nFound more than one mod for search {0}".format(mod_name))
            if full_mod:
                print("Full mod name: {0}\n".format(full_mod))
            for i,n in enumerate(mod_urls):
                print(str(i+1)+'. '+str(n)[8:-9])
            x=int(input("\nWhich do you want to download? (0 for pass): "))-1
            full_mod=str(mod_urls[x])[8:-9]
            if x==-1:
               continue
            mod_url=mod_urls[x].parent['href']
        else:
            mod_url=mod_urls[0].parent['href']

        url=home_url+mod_url

        req_filelist = requests.get(url, 'html.parser')
        html_filelist=req_filelist.text
        
        p_htmlfilelist= bs(html_filelist)
        trs = p_htmlfilelist.body.find_all('tr', attrs={"data-assetid":True})
        latest = max(trs, key = lambda tr: int(tr.attrs["data-assetid"]))
        fileid = latest.find('a', {'href':re.compile(r'/download\?fileid.')})['href']
        downlink=home_url+fileid

        #os.system('cls')
        print('\n\n'+full_mod)
        print(url)
        print(downlink)
        response=wget.download(downlink, out=path_out)
    else:
        break_=False

c=input("\n\nDownload complete press any key to exit\n")

