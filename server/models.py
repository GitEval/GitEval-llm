from pydantic import BaseModel
from typing import Dict, List, Optional


class Repo(BaseModel):
    name: str
    readme: str
    language: Dict[str, float]
    commit: int  # 该用户commit次数
    add: int  # 增加的commit数量
    delete: int  # 减少的数量
    star: int  # 该项目被star数量
    fork: int  # 该项目被fork数量


class DomainRequest(BaseModel):
    repos: List[Repo]  # 仓库列表
    bio: str  # 个人简介
    organizations: List[str]  # 所属组织


class DomainResponse(BaseModel):
    domain: List[str]  # 响应消息内容

class RepoInfo(BaseModel):
    description: Optional[str]
    stargazers_count: Optional[int]
    forks_count: Optional[int]
    created_at: Optional[str]
    subscribers_count: Optional[int]

class UserEvent(BaseModel):
    repo: Optional[RepoInfo]  # 仓库信息
    commit_count: int  # 提交计数
    issues_count: int  # Issue 计数
    pull_request_count: int  # Pull Request 计数


class EvaluationRequest(BaseModel):
    bio: str  # 个人简介
    followers: int  # 粉丝
    following: int  # 关注
    total_private_repos: int  # 私人仓库数量
    total_public_repos: int  # 公开仓库数量
    user_events: List[UserEvent]
    domains: List[str]  # 技术领域
    created_at: str  # 建号时间
    organizations: List[str]  # 所属组织
    disk_usage: float  # 硬盘使用量单位是kb


class EvaluationResponse(BaseModel):
    evaluation: str

class AreaRequest(BaseModel):
    bio: str  # 个人简介
    company:str
    location:str
    follower_areas: List[str] # 粉丝的地区
    following_areas: List[str] # 追随者的地区


class AreaResponse(BaseModel):
    area: str
    Confidence:float
