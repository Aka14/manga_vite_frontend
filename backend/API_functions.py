import re
import requests


def normalize_title(title):
    title = re.sub(r"\s*\(.*?\)", "", title)
    return title.strip()

def get_manga_cover(manga_name):
    base_mangadex_url = 'https://api.mangadex.org'
    id_params = {'title': normalize_title(manga_name), 'limit': 1}
    id_response = requests.get(base_mangadex_url + '/manga', params=id_params)
    id_data = id_response.json()
    if not id_data["data"]:
        return None
    else:
        id = id_data["data"][0]["id"]
        cover_params = {'manga[]': id, 'limit': 1}
        cover_response = requests.get(base_mangadex_url + '/cover', params=cover_params)
        cover_data = cover_response.json()
    if cover_data["data"]:
        file_name = cover_data["data"][0]["attributes"]["fileName"]
        cover_url ='https://uploads.mangadex.org/covers/' + id + '/' + file_name + '.256.jpg'
        return cover_url
    return None
