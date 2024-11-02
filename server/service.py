from collections import Counter
from typing import List

from langchain_openai import ChatOpenAI

import config.config as config
from . import models
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate

# 定义技术领域列表
tech_areas = [
    "前端开发", "后端开发", "数据科学", "人工智能", "移动开发",
    "区块链", "网络安全", "游戏开发", "数据库开发", "云计算",
]

areas = ','.join(tech_areas)

# 定义 Prompt 模板
domain_template = """
基于用户提供的仓库和 README 内容，以及不同编程语言的使用比重，请分析该用户可能的技术领域。
以下是预定义的技术领域：{tech_areas}
参与的项目仓库名称：{repo_name}
参与的项目的简介:{readme}
参与项目的使用编程语言比重:{repo_language}
请返回用户可能的技术领域，可以返回多个。
返回格式: ["领域1", "领域2", ...]
"""

evaluation_template = """
请根据以下 GitHub 用户的信息进行综合评价：

用户的各个仓库事件及其相关活动：
{user_events}

个人简介：{bio}
技术领域：{domains}
粉丝数量：{followers}
关注数量：{following}
私人仓库数量：{total_private_repos}
公开仓库数量：{total_public_repos}
GitHub 账号创建时间：{created_at}
所属组织：{organizations}
硬盘使用量：{disk_usage} KB

根据以上信息，请给出该用户的综合评价，涵盖技术能力、活跃度、影响力以及对开源社区的贡献。请使用 0 到 5 星的星级评分。
"""


area_template = """
请根据以下用户的 GitHub 信息对其可能的地区进行推测。

个人简介: {bio}
公司信息: {company}
自述地区: {location}
粉丝的自述地区分布: {followers}
关注的用户的自述地区分布: {following}

请根据以上信息推测该用户最可能所在的国家或地区(使用中文表示)，并提供一个置信度分数（0到1，1表示非常确定，0表示无法确定）。如果信息不足以做出明确推测，请将地区置为"N/A"

返回格式如下：
{"country": "<推测的国家或地区>", "confidence": <置信度>}
"""


# 创建 PromptTemplate 和 LLMChain
domain_prompt = PromptTemplate(
    input_variables=["bio", "organizations", "repos_summary", "tech_areas"],
    template=domain_template
)

evaluation_prompt = PromptTemplate(
    input_variables=[
        "user_events",
        "bio",
        "domain",
        "follower",
        "following",
        "total_private_repos",
        "total_public_repos",
        "created_at",
        "organizations",
        "disk_usage"
    ],
    template=evaluation_template
)



area_prompt = PromptTemplate(
    input_variables=["bio","location","company","follower","following"],
    template=area_template
)

class Service:
    def __init__(self):
        # 创建 ChatOpenAI 模型
        llm = ChatOpenAI(model=config.model, openai_api_key=config.api_key)
        self.domainChain = LLMChain(prompt=domain_prompt, llm=llm)
        self.evaluationChain = LLMChain(prompt=evaluation_prompt, llm=llm)
        self.areaChain = LLMChain(prompt=area_prompt, llm=llm)

    def _evaluate_repos(self, repos: List[models.Repo]) -> str:
        evaluations = []
        for repo in repos:
            # 为每个仓库生成评价
            result = self.evaluationChain.run({
                "repo_name": repo.name,
                "repo_language": repo.language,
                "repo_commit": repo.commit,
                "repo_star": repo.star,
                "repo_readme": repo.readme
            })
            evaluations.append(f"{repo.name} 的评价：{result}")
        return "\n".join(evaluations)

    def get_domain(self, req: models.DomainRequest) -> models.DomainResponse:
        tech_areas = []

        # 生成仓库汇总信息
        for repo in req.repos:
            # 调用 LLMChain 进行领域推理
            result = self.domainChain.run({
                "repo_name": repo.name,
                "repo_language": repo.language,
                "readme": repo.readme,
                "tech_areas": areas
            })

            # 确保返回的格式是 ["领域1", "领域2", ...]
            tech_areas.extend(eval(result))  # 使用 extend 直接加入列表

        # 统计每个领域的出现次数
        area_counts = Counter(tech_areas)

        # 获取出现次数最多的三个领域
        most_common_areas = area_counts.most_common(3)

        # 只提取领域名
        top_areas = [area for area, count in most_common_areas]

        return models.DomainResponse(domain=top_areas)

    def get_evaluation(self, req: models.EvaluationRequest) -> models.EvaluationResponse:
        user_events = []
        for event in req.user_events:
            if len(user_events) == 100:#限制长度为100
                break
            else:
                user_events.append(f'仓库描述:{event.repo.description},仓库star数{event.repo.stargazers_count},仓库fork数{event.repo.forks_count},仓库创建时间:{event.repo.created_at},仓库贡献者数量:{event.repo.subscribers_count},用户对仓库commit数量:{event.commit_count},用户对仓库提issue数量:{event.issues_count},用户对仓库提pr次数:{event.pull_request_count}')
        # 调用 LLMChain 进行综合评价
        final_evaluation = self.evaluationChain.run({
            "user_events": user_events,
            "bio": req.bio,
            "organizations": req.organizations,
            "total_private_repos": req.total_private_repos,
            "req.total_public_repos": req.total_public_repos,
            "created_at": req.created_at,
        })

        return models.EvaluationResponse(evaluation=final_evaluation)

    def get_area(self, req: models.AreaRequest) -> models.AreaResponse:
        # 运行 areaChain 并获取返回结果
        result = self.areaChain.run({
            "bio": req.bio,
            "company": req.company,
            "location": req.location,
            "follower": req.follower,
            "following": req.following,
        })

        # 解析返回的 JSON 格式结果
        area_result = eval(result)  # 将字符串格式转换为字典

        # 返回 AreaResponse 包含国家和置信度
        return models.AreaResponse(
            country=area_result["country"],
            confidence=area_result["confidence"]
        )
