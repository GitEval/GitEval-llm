from pydantic import BaseModel
from typing import Dict, List, Optional


class Repo(BaseModel):
    name: Optional[str]
    readme: Optional[str]
    language: Optional[str]


class DomainRequest(BaseModel):
    repos: List[Repo]  # 仓库列表
    bio: str  # 个人简介


class Domain(BaseModel):
    domain: str
    confidence: float


class DomainResponse(BaseModel):
    domains: List[Domain]  # 响应消息内容


class RepoInfo(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None  # 仓库描述
    stargazers_count: Optional[int] = None  # Star 数量
    forks_count: Optional[int] = None  # Fork 数量
    created_at: Optional[str] = None  # 创建时间
    subscribers_count: Optional[int] = None  # 订阅者数量


class UserEvent(BaseModel):
    repo: RepoInfo  # 仓库信息
    commit_count: int  # 提交计数
    issues_count: int  # Issue 计数
    pull_request_count: int  # Pull Request 计数


class GetEvaluationRequest(BaseModel):
    bio: Optional[str]  # 个人简介
    followers: int  # 粉丝
    following: int  # 关注
    total_private_repos: int  # 私人仓库数量
    total_public_repos: int  # 公开仓库数量
    user_events: List[UserEvent]  # 用户事件
    domains: Optional[List[str]]  # 技术领域


class EvaluationResponse(BaseModel):
    evaluation: str


class AreaRequest(BaseModel):
    bio: Optional[str]  # 个人简介
    company: Optional[str]
    location: Optional[str]
    follower_areas: Optional[List[str]]  # 粉丝的地区
    following_areas: Optional[List[str]]  # 追随者的地区


class AreaResponse(BaseModel):
    area: str
    confidence: float
