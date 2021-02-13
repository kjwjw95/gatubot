from bs4 import BeautifulSoup
import requests
import json


def news_kor():
    url = "https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=101"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.3"}
    html = requests.get(url, headers=headers,)
    soup = BeautifulSoup(html.text, "html.parser")
    metadata = soup.find_all("div", class_="cluster_text", limit=30)
    news = []
    key = 0
    for i in metadata:
        new = {"title": i.a.get_text().rstrip(
            '\n'), "href": i.a.get("href"), "key": key}
        key += 1
        news.append(new)
    return news


def news_usa():
    url = "https://www.cnbc.com/world/"
    trans_url = "https://dapi.kakao.com/v2/translation/translate"
    KEY = "KakaoAK 49ba514a295f31e38cc9ceee74c0a862"
    header_trans = {"Authorization": KEY}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.3"}
    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.text, "html.parser")
    metadata = soup.find_all("div", class_="LatestNews-headline", limit=10)
    news = []
    key = 0
    for i in metadata:
        title = i.a.get_text()
        title = title.replace("\n", "")
        tr = {"query": title, "src_lang": "en", "target_lang": "kr"}
        translate = requests.get(
            url=trans_url, headers=header_trans, params=tr)
        new = {"title": json.loads(translate.text)[
            "translated_text"][0][0], "href": i.a.get("href"), "eng_title": title, "key": key}
        key += 1
        news.append(new)
    return news


def getnews(lng):
    print(lng)
    if lng == "kor":
        return news_kor()
    else:
        return news_usa()
