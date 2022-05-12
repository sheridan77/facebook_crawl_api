# -*- coding: utf-8 -*-
"""
@File    :  function.py
@Time    :  2022/2/15 17:09:24
@Author  :  Zrq
@Contact :  ceshi17777813307@163.com
@Version :  V1.1
@Desc    :  主函数文件
"""
import datetime
import json
import logging
import re

from lxml import etree
from facebook_crawl_api.core import BaseClient
from facebook_crawl_api.model import UserInfo, Article, SearchResult

logger = logging.getLogger(__name__)


class FaceBook(BaseClient):
    def __init__(
            self,
            user_id,
            proxies: dict = None,
            timeout: int = None,
            cookies: dict = None
    ):
        super().__init__(proxies=proxies, timeout=timeout, cookies=cookies)
        self.user_id = user_id

    def find_user_info(self, **kwargs) -> dict:
        """
        通过user id 或者个性域名获取facebook的用户信息
        :param kwargs: 可选参数
        :return: {状态 消息 数据}
        """
        link = self.get_user_info_link()
        if isinstance(link, dict):
            # 如果返回类型是dict cookies失效
            return link
        else:
            self.requests_args.update(
                {
                    'headers': {
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,en-US;q=0.9",
                        "Connection": "close",
                        "Host": "m.facebook.com",
                        "Referer": link,
                        "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; PCRT00 Build/N2G48H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36",
                        "X-Requested-With": "XMLHttpRequest",
                        "X-Response-Format": "JSONStream"
                    }
                }
            )
            response = self.get(link, **kwargs)
            # print(response.text)
            html = etree.HTML(response.text)
            # 用户个性域名
            try:
                user_domain_id = re.findall(r'https://m\.facebook\.com/(.*?)/about', response.text)[0]
            except IndexError:
                user_domain_id = None
            # 用户主页名字
            nickname = html.xpath('/html/head/title/text()')[0]
            # 工作信息
            work_tree = html.xpath('//div[@id="work"]')
            # 教育信息
            education_tree = html.xpath('//div[@id="education"]')
            # 生活信息
            living_tree = html.xpath('//div[@id="living"]')
            # 联系方式信息
            contact_info = html.xpath('//div[@id="contact-info"]')
            # 基本信息
            basic_info = html.xpath('//div[@id="basic-info"]')
            # 人际关系
            relationship = html.xpath('//div[@id="relationship"]')
            # 家庭信息
            family = html.xpath('//div[@id="family"]')
            # 个人简介
            bio = html.xpath('//div[@id="bio"]')
            # 生活纪实
            year_overviews = html.xpath('//div[@id="year-overviews"]')
            # 座右铭
            quote = html.xpath('//div[@id="quote"]')

            user_info = UserInfo()

            if work_tree:
                self.parse_info(work_tree, 'work', user_info)

            if education_tree:
                self.parse_info(education_tree, 'education', user_info)

            if living_tree:
                self.parse_info(living_tree, 'living', user_info)

            if contact_info:
                self.parse_info(contact_info, 'contact', user_info)

            if basic_info:
                self.parse_info(basic_info, 'basic', user_info)

            if relationship:
                self.parse_info(relationship, 'relationship', user_info)

            if family:
                self.parse_info(family, 'family', user_info)

            if bio:
                self.parse_info(bio, 'bio', user_info)

            if year_overviews:
                self.parse_info(year_overviews, 'year', user_info)

            if quote:
                self.parse_info(quote, 'quote', user_info)

            user_id = re.findall(r'entity_id:(\d+)', response.text)[0]
            user_info.user_num_id = user_id
            user_info.user_domain_id = user_domain_id
            user_info.nickname = nickname

            return {
                'status': 'success',
                'msg': '获取成功',
                'data': user_info
            }

    def find_user_article(self, next_url: str = None, **kwargs) -> dict:
        """
        通过user id或者个性域名或者下一页的链接获取facebook用户的帖子
        :param next_url: 下一页的链接，可在返回信息中查找
        :param kwargs: 可选参数
        :return: {状态 消息 下一页的链接 数据列表}
        """
        if next_url:
            # 如果有下一页的链接 直接使用该链接进行抓取
            if not next_url.startswith("http"):
                next_url = 'https://m.facebook.com' + next_url
            self.requests_args.update({
                'headers': {
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,en-US;q=0.9",
                    "Connection": "close",
                    "Host": "m.facebook.com",
                    "Referer": f"https://m.facebook.com",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; PCRT00 Build/N2G48H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-Response-Format": "JSONStream"
                }})
            response = self.get(next_url, **kwargs).text
            # with open('a.html', 'w', encoding='utf-8') as fp:
            #     fp.write(response)
            # 将数据转换成json格式的
            json_data = json.loads(response.replace('for (;;);', ''))
            actions = json_data.get('payload').get('actions')
            article_object_list = list()
            # 置空next_url 便于之后的判断
            next_url = None
            for action in actions:
                cmd = action.get("cmd")
                if cmd == 'replace':
                    # 存储文章信息的HTML在cmd==replace的对象中
                    html = action.get('html')
                    html = etree.HTML(html)
                    article_list = html.xpath('//article')
                    article_object_list = self.parse_article(article_list)
            for action in actions:
                cmd = action.get("cmd")
                if cmd == 'script':
                    # 存储有下一页链接的JavaScript在cmd==code的对象中
                    code: str = action.get('code')
                    code = code.replace('\\', '')
                    pattern = re.compile(r'"href":"(.*?)"')
                    next_url = pattern.findall(code)
            if next_url:
                return {
                    'status': 'success',
                    'mag': '获取成功',
                    'data': article_object_list,
                    'next_url': 'https://m.facebook.com' + next_url[0]
                }
            else:
                return {
                    'status': 'success',
                    'msg': '获取成功',
                    'data': article_object_list
                }

        else:
            word_pattern = re.compile(r'[A-Za-z]')
            res = word_pattern.findall(str(self.user_id))
            if res:
                self.requests_args.update({
                    'headers': {
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,en-US;q=0.9",
                        "Connection": "close",
                        "Host": "m.facebook.com",
                        "Referer": f"https://m.facebook.com/{self.user_id}",
                        "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; PCRT00 Build/N2G48H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36",
                        "X-Requested-With": "XMLHttpRequest",
                        "X-Response-Format": "JSONStream"
                    }})
                url = f'https://m.facebook.com/{self.user_id}'
                response = self.get(url, **kwargs)
            else:
                self.requests_args.update({
                    'headers': {
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,en-US;q=0.9",
                        "Connection": "close",
                        "Host": "m.facebook.com",
                        "Referer": f"https://m.facebook.com/profile.php?id={self.user_id}",
                        "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; PCRT00 Build/N2G48H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36",
                        "X-Requested-With": "XMLHttpRequest",
                        "X-Response-Format": "JSONStream"
                    }})
                url = f"https://m.facebook.com/profile.php?id={self.user_id}"
                response = self.get(url, **kwargs)

            if '你必须先登录' in response.text:
                logger.error("cookies失效")
                return {
                    'status': 'error',
                    'msg': 'cookies失效'
                }
            href_pattern = re.compile(r'href:"(/profile/timeline/stream/.*?)"', re.S)
            next_url = href_pattern.findall(response.text)
            # 此次请求中也有一部分文章信息，匹配出来后进行解析入库
            article_pattern = re.compile(r'<div class="hidden_elem"><code.*?>(.*?)</code>', re.S)
            article_res = article_pattern.findall(response.text)
            article_object_list = list()
            for article in article_res:
                # 只有一个匹配中有文章链接
                # import time
                # with open(f'{time.time()}.html', 'w', encoding='utf-8') as fp:
                #     fp.write(article)
                html = etree.HTML(article.replace('<!--', '').replace('-->', ''))
                article_list = html.xpath('//article')
                save_list = self.parse_article(article_list)
                if save_list:
                    article_object_list: [Article] = save_list

            if next_url:
                return {
                    'status': 'success',
                    'mag': '获取成功',
                    'data': article_object_list,
                    'next_url': 'https://m.facebook.com' + next_url[0]
                }
            else:
                return {
                    'status': 'success',
                    'msg': '获取成功',
                    'data': article_object_list
                }

    @staticmethod
    def parse_article(article_list) -> [Article]:
        article_object_list = list()
        for article in article_list:
            # 用户信息 尝试第一种方式，在链接中直接匹配出数字id和个性域名
            user_info = article.xpath('./div/header/div[2]/div/div/div/div/a/@href')[0]
            # print(user_info)
            try:
                story_fbid = re.findall(r'story_fbid=(.*?)&', user_info)[0]
            except IndexError:
                try:
                    story_fbid = re.findall(r'fbid=(\d+)&', user_info)[0]
                except IndexError:
                    continue
            profile_id = re.findall(r'&id=(\d+)&', user_info)[0]
            # print(profile_id)
            user_id_info = article.xpath('./div/header/div[1]/div/div/a/@href')[0]
            user_id = re.findall(r'/(.*?)\?', user_id_info)[0]

            # 用户名
            user_name = article.xpath('.//header/div/div/div/a/i/@aria-label')[0].split(',')[0]
            # 时间信息
            date_and_time = article.xpath('.//header/div[2]/div/div/div/div//text()')
            date = date_and_time[0]
            # 有些帖子只有年月日信息
            try:
                date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
            except ValueError:
                try:
                    date = datetime.datetime.strptime(date, '%Y年%m月%d日')
                except ValueError:
                    try:
                        if '小时' in date:
                            date_and_time = date_and_time[0].replace('小时', '').strip()
                            timedelta = datetime.timedelta(hours=int(date_and_time))
                        elif '分钟' in date:
                            date_and_time = date_and_time[0].replace('分钟', '').strip()
                            timedelta = datetime.timedelta(minutes=int(date_and_time))
                        elif '昨天' in date:
                            timedelta = datetime.timedelta(days=1)
                        else:
                            raise ValueError
                        now = datetime.datetime.now()
                        date = now - timedelta
                    except ValueError:
                        date = datetime.datetime.strptime(date, '%m月%d日 %H:%M').replace(year=datetime.datetime.now().year)

            article_detail = ''.join(date_and_time).replace('更多选项', '')
            one_article = Article(
                story_fbid=story_fbid,
                username=user_name,
                profile_id=profile_id,
                user_id=user_id,
                article_create_time=date,
                article_detail=article_detail
            )
            # 提取帖子内容
            content = article.xpath('./div/div[1]/div[1]/span//text()')
            content = '\n'.join(content)
            one_article.content = content
            # 提取图片和视频列表
            picture_list = article.xpath('./div/div[2]//a')
            video = article.xpath('./div/div[2]/section/div/div/@data-store')
            media_list = list()
            if picture_list:
                for picture in picture_list:
                    try:
                        # 匹配图片链接
                        style = picture.xpath('.//i/@style')[0]
                        url_pattern = re.compile(r"url\('(.*?)'\)")
                        res = url_pattern.findall(style)[0]
                        # 将链接格式化
                        media_url = res.replace('\\\\3a ', ':').replace('\\\\3d ', '=').replace('\\\\26 ', '&')
                        media_url = media_url.replace('\\3a ', ':').replace('\\3d ', '=').replace('\\26 ', '&')
                        media_list.append(media_url)
                    except IndexError:
                        pass

            elif video:
                try:
                    # 匹配视频链接
                    # print(video[0].replace('\\', ''))
                    pattern = re.compile(r'"videoURL":"(https://www\.facebook\.com/.*?/videos/\d+/)"')
                    video_url = pattern.findall(video[0].replace('\\', ''))[0]
                    media_list.append(video_url)
                except IndexError:
                    pass

            one_article.media = media_list
            article_object_list.append(one_article)
        return article_object_list

    @staticmethod
    def parse_info(info_tree: etree.HTML, type_: str, user_info: UserInfo):
        detail_list = list()
        # 查找该信息树的标头
        info = info_tree[0].xpath('./header//text()')
        info = ''.join([i.strip() for i in info])
        div_list = info_tree[0].xpath('./div/div')
        # 所有的信息都存放在该div列表中
        for div in div_list:
            if type_ in ('work', 'education'):
                detail = ','.join([i.strip() for i in div.xpath('.//span//text()')])
            elif type_ in ('living', 'relationship', 'family'):
                detail = '--'.join([i.strip() for i in div.xpath('.//header//text()')])
            elif type_ in ('contact', 'basic', 'bio', 'quote', 'year'):
                detail = '--'.join([i.strip() for i in div.xpath('.//text()')])
            else:
                raise
            detail_list.append(detail)
            if type_ == 'work':
                user_info.work = detail_list
            elif type_ == 'education':
                user_info.education = detail_list
            elif type_ == 'living':
                user_info.living = detail_list
            elif type_ == 'relationship':
                user_info.relationship = detail_list
            elif type_ == 'family':
                user_info.family = detail_list
            elif type_ == 'contact':
                user_info.contact = detail_list
            elif type_ == 'basic':
                user_info.basic = detail_list
            elif type_ == 'bio':
                user_info.bio = detail_list
            elif type_ == 'quote':
                user_info.quote = detail_list
            elif type_ == 'year':
                user_info.year_overviews = detail_list
        return user_info

    def get_user_info_link(self, **kwargs):
        word_pattern = re.compile(r'[A-Za-z]')
        res = word_pattern.findall(str(self.user_id))
        if not res:
            url = f'https://m.facebook.com/profile.php?id={self.user_id}'
            self.requests_args.update({
                'headers': {
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,en-US;q=0.9",
                    "Connection": "close",
                    "Host": "m.facebook.com",
                    "Referer": f"https://m.facebook.com/profile.php?id={self.user_id}",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; PCRT00 Build/N2G48H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-Response-Format": "JSONStream"
                }})
            response = self.get(url, **kwargs)
            if '你必须先登录' in response.text:
                logger.error("cookies失效")
                return {
                    'status': 'error',
                    'message': 'cookies失效',
                    'data': None
                }
            else:

                pattern = re.compile(r'(https://m\.facebook\.com/.*?/about)')
                detail_link = pattern.findall(response.text)
                if detail_link:
                    logger.info("详情页链接" + detail_link[0])
                    return detail_link[0]
                else:
                    return f'https://m.facebook.com/profile.php?id={self.user_id}&v=info'
        else:
            return f'https://m.facebook.com/{self.user_id}/about'


class KeywordSearch(BaseClient):
    """
    关键词检索帖子的类
    """

    def __init__(
            self,
            proxies: dict = None,
            timeout: int = None,
            cookies: dict = None
    ):
        super().__init__(proxies=proxies, timeout=timeout, cookies=cookies)

    def search(self, keyword: str, next_url: str = None, fb_dtsg: str = None, **kwargs):
        """
        检索
        :param keyword: 关键词
        :param next_url: 下一页的链接
        :param fb_dtsg: 必要的请求参数，可从首页获取
        :param kwargs: 其他参数
        :return: 数据和状态
        """
        # cookies的user id
        cookies_user_id = self.cookies.get('c_user')
        if not next_url and not fb_dtsg:
            # 没有下一页的链接和必要的请求参数，从头开始请求
            url = "https://m.facebook.com/"
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,en-US;q=0.9",
                "Connection": "close",
                "Host": "m.facebook.com",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; PCRT00 Build/N2G48H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36",
                "X-Requested-With": "com.android.browser"
            }
            self.requests_args.update(
                {
                    'headers': headers
                }
            )
            response = self.get(url, **kwargs)
            html = etree.HTML(response.text)
            # 获取必要的下一次要请求时携带的参数
            fb_dtsg = html.xpath('//input[@name="fb_dtsg"]/@value')[0]
            # 获取帖子
            url = "https://m.facebook.com/search/posts/"
            params = {
                "__user": cookies_user_id,
                "q": keyword
            }
            self.requests_args.update(
                {
                    'params': params
                }
            )
            response = self.get(url, **kwargs)
            # with open('a.html', 'w', encoding='utf-8') as fp:
            #     fp.write(response.text)
            pattern = re.compile(r'href:"(https://m\.facebook\.com/search/posts/\?q=.*?&cursor=.*?)"', re.S)
            # 获取下一页的链接
            next_url = pattern.findall(response.text)
            # 获取存储帖子的HTML列表
            content_html_list = etree.HTML(response.text).xpath('//div[@class="story_body_container"]')
            # 解析帖子
            content_list = self.parse_article(content_html_list, keyword)
            # 如果有下一页的链接返回的数据
            if next_url:
                return {
                    'status': 'success',
                    'msg': '获取成功',
                    'fb_dtsg': fb_dtsg,
                    'next_url': next_url[0],
                    'data': content_list
                }
            # 没有下一页链接返回的数据
            else:
                return {
                    'status': 'success',
                    'msg': '获取成功',
                    'data': content_list
                }
        # 如果有下一页的链接和请求的必要参数，直接进行请求
        elif next_url and fb_dtsg:
            params = {
                "q": keyword
            }
            data = {
                "__user": cookies_user_id,
                "fb_dtsg": fb_dtsg
            }
            self.requests_args.update(
                {
                    'params': params,
                    'data': data
                }
            )
            response = self.post(next_url, **kwargs)
            content_html_list = etree.HTML(response.text).xpath('//div[@class="story_body_container"]')
            content_list = self.parse_article(content_html_list, keyword)

            pattern = re.compile(r'href:"(https://m\.facebook\.com/search/posts/\?q=.*?&cursor=.*?)"', re.S)
            next_url = pattern.findall(response.text)
            if next_url:
                return {
                    'status': 'success',
                    'msg': '获取成功',
                    'fb_dtsg': fb_dtsg,
                    'next_url': next_url[0],
                    'data': content_list
                }
            else:
                return {
                    'status': 'success',
                    'msg': '获取成功',
                    'data': content_list
                }
        # 下一页参数和必要参数必须同时出现或同时不出现
        else:
            return {
                'status': 'error',
                'msg': '没有的获取类型'
            }

    @staticmethod
    def parse_article(content_html_list: list, keyword) -> list:
        """
        解析获取到的搜索结果
        :param content_html_list: 内容HTML列表
        :param keyword: 关键词
        :return: 解析好的内容列表
        """
        content_list = list()
        for content_html in content_html_list:
            # 获取存放user_id的a标签href属性值
            try:
                user_id_href = content_html.xpath('./header//a/@href')[0]
            except IndexError:
                continue
            # print(user_id_href)
            user_id_pattern = re.compile(r'id=(\d+)')
            user_id = user_id_pattern.findall(user_id_href)
            if user_id:
                user_id = user_id[0]
            else:
                user_id_pattern = re.compile(r'/(.*?)\?')
                user_id = user_id_pattern.findall(user_id_href)[0]

            profile_and_story_id = content_html.xpath('./header/div[2]/div/div/div/div/a/@href')[0]
            # print(profile_and_story_id)
            try:
                story_id = re.findall(r'story_fbid=(.*?)&', profile_and_story_id)[0]
                profile_id = re.findall(r'&id=(\d+)&', profile_and_story_id)[0]
            except IndexError:
                continue
            date_and_time = content_html.xpath('./header/div[2]/div/div/div/div/a/abbr/text()')
            date = date_and_time[0]
            try:
                date = datetime.datetime.strptime(date, "%Y年%m月%d日 %H:%M")
            except ValueError:
                try:
                    date = datetime.datetime.strptime(date, '%Y年%m月%d日')
                except ValueError:
                    try:
                        if '小时' in date:
                            date_and_time = date_and_time[0].replace('小时', '').strip()
                            timedelta = datetime.timedelta(hours=int(date_and_time))
                        elif '分钟' in date:
                            date_and_time = date_and_time[0].replace('分钟', '').strip()
                            timedelta = datetime.timedelta(minutes=int(date_and_time))
                        elif '昨天' in date:
                            timedelta = datetime.timedelta(days=1)
                        else:
                            raise ValueError
                        now = datetime.datetime.now()
                        date = now - timedelta
                    except ValueError:
                        date = datetime.datetime.strptime(date, '%m月%d日 %H:%M').replace(year=datetime.datetime.now().year)

            text_list = content_html.xpath('./div[1]/div/span//text()')
            text = ''.join([t.strip() for t in text_list])

            media_list = content_html.xpath('./div[2]//i/@style')
            save_list = list()
            for media in media_list:
                # print(media)
                pattern = re.compile(r'url\((.*?)\)', re.S)
                url = pattern.findall(media)[0].replace('\\3a ', ':').replace('\\3d ', '=').replace('\\26 ',
                                                                                                    '&').replace("'",
                                                                                                                 "")
                save_list.append(url)

            search_result = SearchResult(
                story_fbid=story_id,
                profile_id=profile_id,
                keyword=keyword,
                user_id=user_id,
                content=text,
                media=save_list,
                article_create_time=date
            )
            content_list.append(search_result)

        return content_list
