import httpx
import os
from bs4 import BeautifulSoup
import argparse
import shutil

class Scraping34:
    def __init__(self,character,output):
        self.character = character
        self.output = output 

        ffmpeg_path = shutil.which("ffmpeg")      
        wget_path = shutil.which("wget")


        if not ffmpeg_path:
            if os.name == "nt":
                print("[scraping34] Do you want to download ffmpeg? (Essential dependency)")
                want = input("> ")

                if want == "y":
                    if os.name == "nt":
                        os.system("winget install ffmpeg")
                    else:
                        os.system("apt install ffmpeg -y ")
                else:
                    print("[scraping 34]ok...")
                    quit()
        if not wget_path:
            print("[scraping34] do you want to dowload wget? ((Essential dependency)")
            want = input("> ")
            if want == "nt":
                if os.name == "nt":
                    os.system("winget install wget")
                else:
                    os.system("apt install wget")
            else:
              print("[scraping 34]ok...")
              quit()


    def run(self):
        resp = httpx.get(f"https://rule34.gg/?tags={self.character}&sort=date_no&exclude=&page=1")
        if resp.status_code == 200:
          soup = BeautifulSoup(resp.text,"html.parser")
          conteiner = soup.find("div",class_="media")
          if conteiner:
              img = conteiner.find("img")
              if img:
                  link = img.get("src") 
                  os.system(f"wget -O ./hentai.webp {link} ")
                  os.system(f"ffmpeg -i ./hentai.webp {self.output} ")
                  os.system("rm hentai.webp")
                  return "download completed"
                  
          else:
             return "Error processing HTML"
             quit()
        else:

            print(f"Error status:{resp.status_code}  Try updating the repository; the API may be experiencing instability or may have changed its policies.")
            quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--character")
    parser.add_argument("-o","--outputfile")
    args = parser.parse_args()

    if not args.character or not args.outputfile:
        print("use \n python main.py --character='target' --outpufile='hentai_filename.jpg'")
        quit()
    scraping = Scraping34(args.character,args.outputfile)
    scraping.run()

