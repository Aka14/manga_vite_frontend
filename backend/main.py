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
from mangapill_scraping import find_latest_chapter
from API_functions import get_manga_cover

load_dotenv()
app = FastAPI()
mangadex_key = os.getenv("MANGADEX_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
service_role_key = os.getenv("SUPABASE_ROLE_KEY")



app.add_middleware(
    CORSMiddleware,
#     allow_origins= [
#     "http://localhost",
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
#     "https://www.mangapill.com",
#     "http://www.mangapill.com"
# ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)

base_url = "https://www.mangapill.com"

class ChapterData(BaseModel):
    chapter_link: str
    userId: str

class DeleteData(BaseModel):
    manga_name: str
    db_name: str
    userId: str

@app.post('/api/get-data')
async def get_token(token: Request):
    data = await token.json()
    token = data.get("token")
    try: 
        response = supabase.auth.get_user(token)
    except Exception as e:
        print(f"Error: {e}")
        print("Invalid or expired token")
    return {"recieved": token}

supabase = create_client(supabase_url, service_role_key)

def save_manga_to_db(userId, manga_data, manga_url, db_name="saved_manga"):
    manga_name = manga_data[0]
    current_chapter = manga_data[1]
    manga_cover = get_manga_cover(manga_name)
    print("DEBUG userId:", userId, type(userId))
    print(db_name)
    print(find_chapter(manga_name, manga_url, current_chapter))
    supabase.table(db_name).insert(
        {
        "user_id": str(userId),
        "name": manga_name,
        "chapter_link": find_chapter(manga_name, manga_url, current_chapter),
        "current_chapter": current_chapter,
        "cover_link": manga_cover
    }
    ).execute()

def duplicate_check(collection, manga_name):
    for manga in collection:
        if manga_name == manga['name']:
            return True
    return False

def save_manga(manga_list, manga_name, chapter_link,current_chapter=1):
    manga_cover = get_manga_cover(manga_name)
    manga = {
        "name": manga_name,
        "current_chapter": current_chapter,
        "chapter_url": chapter_link,
        "latest_chapter": None,
        "latest_chapter_url":None,
        "cover_link": manga_cover
    }
    if duplicate_check(manga_list, manga_name) == False:
        manga_list.append(manga)
    return manga

def get_manga_from_js(chapter_link):
    page = requests.get(chapter_link)
    soup = BeautifulSoup(page.text, features="html.parser")
    result = soup.find(id="top").get_text()
    print(result)
    name = result.split(" Chapter ")
    print(name[0])
    return [name[0], float(name[1])]

@app.post('/api/get-current-link')
async def get_link(data: ChapterData):
    link = data.chapter_link
    userId = data.userId
    print("link", link)
    manga_data = get_manga_from_js(link)
    print(manga_data)
    save_manga_to_db(userId, manga_data, link, "saved_manga")
    return {"recieved": link}

@app.post('/api/get-re-read-link')
async def get_link(data: ChapterData):
    link = data.chapter_link
    userId = data.userId
    print(userId)
    manga_data = get_manga_from_js(link)
    print(manga_data)
    save_manga_to_db(userId, manga_data, "reReads")
    return {"recieved": link}

@app.post("/api/remove-manga")
def remove_manga(data: DeleteData):
    userId = data.userId
    manga_name = data.manga_name
    print("removing", manga_name)
    db_name = data.db_name
    print("removing from db", db_name)
    supabase.table(db_name).delete().eq("user_id", userId).eq("name", manga_name).execute()
    return {"status": "success"}

@app.get("/api/get-saved-manga")
def get_saved_manga(request: Request):
    auth = request.headers.get("authorization")
    token = auth.split(" ")[1]
    userId = supabase.auth.get_user(token).user.id
    saved_manga = []
    table = supabase.table("saved_manga").select("*").eq("user_id", userId).execute()
    for manga in table.data:
        save_manga(saved_manga, manga['name'], manga["chapter_link"], manga['current_chapter'])   
    # print(saved_manga
    return {"saved_manga": saved_manga}

@app.get("/api/get-re-reads")
def get_re_reads(request: Request):
    auth = request.headers.get("authorization")
    token = auth.split(" ")[1]
    userId = supabase.auth.get_user(token).user.id
    re_reads = []
    table = supabase.table("reReads").select("*").eq("user_id", userId).execute()
    for manga in table.data:
        save_manga(re_reads, manga['name'], manga["chapter_link"], manga['current_chapter'])
    return {"re_reads": re_reads}

@app.get("/api/get-new-chapters")
def get_new_chapters(request: Request):
    print("newchaps")
    new_chapters = []
    auth = request.headers.get("authorization")
    token = auth.split(" ")[1]
    userId = supabase.auth.get_user(token).user.id
    saved_manga = supabase.table("saved_manga").select("*").eq("user_id", userId).execute()
    for manga in saved_manga.data:
        latest = find_latest_chapter(manga['chapter_link'])
        manga['latest_chapter'] = latest[0]
        manga['latest_chapter_url'] = latest[1]
        if latest[0] != manga['chapter_link'].split("/")[-1].split("-")[-1]:
            new_chapters.append(manga)
    print(new_chapters)
    return {"new_chapters": new_chapters}

@app.get("/")
def read_root():
    return {"Hello": "Manga App!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

