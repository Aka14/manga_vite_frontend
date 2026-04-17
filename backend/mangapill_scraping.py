import re
from urllib import request
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
import webbrowser
from dotenv import load_dotenv
import os
from jose import jwt
import supabase
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from pydantic import BaseModel
from uuid import UUID

load_dotenv()
app = FastAPI()
mangadex_key = os.getenv("MANGADEX_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
service_role_key = os.getenv("SUPABASE_ROLE_KEY")

base_url = "https://www.mangapill.com"

#returns the id (ex. returns 5256) in https://www.mangapill.com/chapters/5256-10074000/shakunetsu-kabaddi-chapter-74
def get_manga_id(manga_url):
     id = manga_url.split("/chapters/")[1].split("-")[0]
     return id

#returns the number after the id (ex. returns 1074000) in https://www.mangapill.com/chapters/5256-10074000/shakunetsu-kabaddi-chapter-74
def get_manga_postID(manga_url):
    post_id = manga_url.split("-")[1].split("/")[0]
    return post_id

#returns the latest chapter in link form
#(ex. returns "https://www.mangapill.com/chapters/5256-10074000" 
#for "https://www.mangapill.com/chapters/5256-10044500/shakunetsu-kabaddi-chapter-44.5")
def find_latest_chapter(manga_url):
    id = get_manga_id(manga_url)
    page = requests.get(base_url + "/manga/" + id, allow_redirects=True)
    soup = BeautifulSoup(page.text, features="html.parser")
    chapters = soup.find(id="chapters")
    if chapters is None:
        print(f"Warning: Could not find chapters div for {id}")
        return None
    latest = chapters.find_all("a", href=True)[0]['href']
    chapter_number = latest.split("chapter-")[-1]
    post_id = get_manga_postID(latest)
    return int(chapter_number), base_url + "/chapters/" + id + "-" + post_id

print(find_latest_chapter("https://www.mangapill.com/chapters/5256-10044500/shakunetsu-kabaddi-chapter-44.5"))



