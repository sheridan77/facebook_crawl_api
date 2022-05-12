# -*- coding: utf-8 -*-
"""
@File    :  model.py
@Time    :  2022/2/15 17:07:10
@Author  :  Zrq
@Version :  V1.0
@Contact :  ceshi17777813307@163.com
@Desc    :  模型文件
"""
import datetime
import json
import logging

logger = logging.getLogger(__name__)


class BaseModel:
    def to_dict(self) -> dict:
        raise NotImplementedError

    def to_json(self) -> str:
        raise json.dumps(self.to_dict(), ensure_ascii=False)


class UserInfo(BaseModel):
    def __init__(
            self,
            user_num_id: "str|int" = None,  # 用户纯数字id
            user_domain_id: str = None,  # 用户个性域名
            nickname: str = None,  # 用户主页名字
            work: list = None,  # 工作信息
            education: list = None,  # 教育信息
            living: list = None,  # 居住信息
            contact: list = None,  # 联系方式
            basic: list = None,  # 基础信息
            relationship: list = None,  # 人际关系
            family: list = None,  # 家庭信息
            bio: list = None,  # 个人简介
            year_overviews: list = None,  # 生活纪实
            quote: list = None  # 座右铭
    ):
        self.user_num_id = user_num_id
        self.user_domain_id = user_domain_id
        self.nickname = nickname
        self.work = work
        self.education = education
        self.living = living
        self.contact = contact
        self.basic = basic
        self.relationship = relationship
        self.family = family
        self.bio = bio
        self.year_overviews = year_overviews
        self.quote = quote

    def to_dict(self) -> dict:
        return {
            'user_num_id': self.user_num_id,
            'user_domain_id': self.user_domain_id,
            'nickname': self.nickname,
            'work': self.work,
            'education': self.education,
            'living': self.living,
            'contact': self.contact,
            'basic': self.basic,
            'relationship': self.relationship,
            'family': self.family,
            'bio': self.bio,
            'year_overviews': self.year_overviews,
            'quote': self.quote
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class Article(BaseModel):
    def __init__(
            self,
            story_fbid: int,
            username: str,
            profile_id: "str|int",
            user_id: str,
            article_create_time: datetime,
            article_detail: str,
            content: str = None,
            media: list = None,
    ):
        self.story_fbid = story_fbid
        self.username = username
        self.profile_id = profile_id
        self.user_id = user_id
        self.article_create_time = article_create_time
        self.article_detail = article_detail
        self.content = content
        self.media = media

    def to_dict(self) -> dict:
        return {
            'story_fbid': self.story_fbid,
            'username': self.username,
            'profile_id': self.profile_id,
            'user_id': self.user_id,
            'article_create_time': self.article_create_time,
            'article_detail': self.article_detail,
            'content': self.content,
            'media': self.media,
        }

    def to_json(self) -> str:
        data = self.to_dict()
        if data.get('article_create_time'):
            data['article_create_time'] = data['article_create_time'].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        return json.dumps(data, ensure_ascii=False)


class SearchResult(BaseModel):
    def __init__(
            self,
            story_fbid: 'str|int',
            profile_id: 'str|int',
            keyword: str,
            article_create_time: datetime,
            user_id: 'str|int',
            content: str,
            media: list
    ):
        self.story_fbid = story_fbid
        self.profile_id = profile_id
        self.keyword = keyword
        self.article_create_time = article_create_time
        self.user_id = user_id
        self.content = content
        self.media = media

    def to_dict(self) -> dict:
        return {
            'story_fbid': self.story_fbid,
            'profile_id': self.profile_id,
            'keyword': self.keyword,
            'user_id': self.user_id,
            'content': self.content,
            'media': self.media,
            'article_create_time': self.article_create_time
        }

    def to_json(self) -> str:
        data = self.to_dict()
        return json.dumps(data, ensure_ascii=False)
