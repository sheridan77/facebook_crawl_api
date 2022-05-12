# facebook_crawl_api
Crawl facebook profile, all facebook articles of someone, or do a keyword search to get the latest articles under a keyword cookies required

#### how to use it 
```python
from facebook_crawl_api.function import FaceBook, KeywordSearch
from facebook_crawl_api.model import UserInfo, Article, SearchResult

proxies = {
    "http": "http://127.0.0.1:7892",
    "https": "http://127.0.0.1:7892"
}

cookies = {
    "datr": "vsR0YmLF9RcXrA8aH-9BT8tz",
    "sb": "0cR0YkI11RH6uUmSPiYYXuVH",
    "locale": "en_US",
    "wd": "1904x952",
    "c_user": "1000*********94",
    "xs": "2%3AxHJAAmqr8orCKA%3A2%3A1651819763%3A-1%3A-1",
    "fr": "0ml3marxJWAXpQQHs.AWXAGFWOB_KyU-5SkpxOt0x_jfs.BidMT0.BG.AAA.0.0.BidMUN.AWVUMap844Q",
    "presence": "C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1651820294258%2C%22v%22%3A1%7D"
}
user_id = "100011836534739"
# 设置代理和cookies
# Setting up proxies and cookies
facebook = FaceBook(user_id=user_id, proxies=proxies, cookies=cookies)
# 通过用户id获取用户信息对象
# Get user information object by user id
user_info = facebook.find_user_info()
user: UserInfo = user_info.get("data")
print(user.to_json())
# 通过用户id获取所发表的帖子
# Get posted posts by user id
user_article = facebook.find_user_article()
next_url = user_article.get("next_url")
articles: [Article] = user_article.get("data")
print(next_url)
print([i.to_json() for i in user_article.get("data")])
# 通过下一页的链接进行翻页操作
# Flip through the links on the next page
next_url = user_article.get("next_url")
# next_url = "https://m.facebook.com/profile/timeline/stream/?cursor=AQHR01DS-HcnGj3Gs1b-cVLP1timggTyDvxRhddtsbx8rmoPtehqdiuawOFpAJPoKu8Ue0woGhCOksmGtqp2zRqnMOmSzlYCmrFm3UhJ8RsR1iJW9UjXGNKRRHzphwJroZr6&start_time=-9223372036854775808&profile_id=100011836534739&replace_id=u_0_1y_2y"
next_page_article = facebook.find_user_article(next_url=next_url)
print(next_page_article.get("next_url"))
print([i.to_json() for i in next_page_article.get("data")])
# 关键词搜索
# key word search
search = KeywordSearch(proxies=proxies, cookies=cookies)
res = search.search("mustang")
print(res)
print([i.to_dict() for i in res.get("data")])
next_url = res.get("next_url")
print(next_url)
fb_dtsg = res.get("fb_dtsg")
res2 = search.search("mustang", next_url=next_url, fb_dtsg=fb_dtsg)
# print([i.to_dict() for i in res2.get("data")])
print(res2)
```
