import asyncio
import json
from collections import Counter, defaultdict
from typing import List
import re
from .search import country_search
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import config.config as config
from . import models
from langchain.prompts import PromptTemplate
from .models import Domain, DomainResponse

# 定义技术领域列表
define_tech_areas = [
    "前端开发", "后端开发", "数据科学", "人工智能", "移动开发",
    "区块链", "网络安全", "游戏开发", "数据库开发", "云计算",
]

areas = ','.join(define_tech_areas)

# 定义 Prompt 模板
domain_template = """
基于用户提供的仓库信息，请分析该用户可能的技术领域。
以下是预定义的技术领域，推测的领域只能从这里选取：{tech_areas}
参与的项目仓库名称：{repo_name}
参与的项目的简介：{readme}
参与项目的使用最多的编程语言：{repo_language}

请返回用户可能的技术领域及其置信度，格式如下：
[
    {{"domain": "领域1", "confidence": <置信度1>}},
    {{"domain": "领域2", "confidence": <置信度2>}},
    ...
]
每次至多返回两个领域,确保输出为有效的 JSON 格式，不要包含其他文本说明。
"""

evaluation_template = """
请根据以下 GitHub 用户的信息为我提供综合评价：

我的各个仓库事件及其相关活动：
{user_events}

我的个人简介：
{bio}
我的技术领域：
{domains}
我的粉丝数量：
{followers}
我的关注数量：
{following}
我的私人仓库数量：
{total_private_repos}
我的公开仓库数量：
{total_public_repos}

根据以上信息，请给出对我的评价，包括以下部分：涵盖技术能力、活跃度、影响力、开源社区的贡献、综合评价。请使用 0 到 5 星的星级评分,并简单论述。
请直接说评价，不需要讲述目的。
"""

area_template = """
请根据以下用户的 GitHub 信息对其可能的地区进行推测。
向量搜索获取到的地区{areas}
个人简介: {bio}
公司信息: {company}
自述地区: {location}
粉丝的自述地区分布: {follower}
关注的用户的自述地区分布: {following}

请根据以上信息推测该用户最可能所在的国家或地区(使用中文名称)，只返回到国家这个层级，省，市等不返回。
并提供一个置信度分数（0到1，1表示非常确定，0表示无法确定）。如果信息不足以做出明确推测，请将地区置为"N/A"

返回格式如下：
{{"country": "<推测的国家或地区>", "confidence": <置信度>}}
确保返回的国家或地区是中文,且输出为有效的 JSON 格式，不要包含其他文本说明。
"""

# 创建 PromptTemplate 和 LLMChain
domain_prompt = PromptTemplate(
    input_variables=[
        "repo_name",
        "repo_language",
        "readme",
        "tech_areas"
    ],
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
    ],
    template=evaluation_template
)

area_prompt = PromptTemplate(
    input_variables=["areas","bio", "company", "location", "follower", "following"],
    template=area_template
)


class Service:
    def __init__(self):
        # 创建 ChatOpenAI 模型
        llm = ChatOpenAI(model=config.model, openai_api_key=config.api_key, base_url=config.base_url)
        self.domainChain = domain_prompt | llm | StrOutputParser()  # 组合成一个chain,langChain新版的抽象写法,我觉得很emmmm
        self.evaluationChain = evaluation_prompt | llm | StrOutputParser()
        self.areaChain = area_prompt | llm | StrOutputParser()

    async def fetch_domain_for_repo(self, repo: models.Repo) -> List[Domain]:
        # 截断 readme 内容，确保其长度在合理范围内
        truncated_readme = self.truncate_readme(repo.readme)

        # 调用 LLMChain 进行领域推理
        result = self.domainChain.invoke({
            "repo_name": repo.name,
            "repo_language": repo.language,
            "readme": truncated_readme,
            "tech_areas": areas,
        })

        cleaned_result = result.replace('```json', '').replace('```', '').strip()
        # 尝试使用正则匹配返回的数组格式
        pattern = r'\[(.*?)\]'
        match = re.search(pattern, cleaned_result, re.DOTALL)
        if match:
            # 提取匹配的部分并转换为列表
            area_list_str = match.group(0)  # 获取完整的数组字符串
            try:
                domains = json.loads(area_list_str)
                return [Domain(domain=d['domain'], confidence=d['confidence']) for d in domains]
            except (json.JSONDecodeError, KeyError) as e:
                # 将字符串解析为对象列表
                print(f"解析失败，跳过该仓库: {repo.name} 的结果: {result}，错误: {e}")
                return []  # 返回空列表，表示解析失败
        else:
            print(f"未匹配到有效数组格式，跳过该仓库: {repo.name} 的结果: {result}")
            return []  # 返回空列表，表示没有匹配到结果

    async def get_domain(self, req: models.DomainRequest) -> DomainResponse:
        tech_areas = []
        tasks = []

        for repo in req.repos:
            tasks.append(asyncio.create_task(self.fetch_domain_for_repo(repo)))

        for i in range(0, len(tasks), 5):
            results = await asyncio.gather(*tasks[i:i + 5])
            for result in results:
                tech_areas.extend(result)

        area_counts = Counter(d.domain for d in tech_areas)
        threshold = len(req.repos) / 5 * 2
        filtered_areas = [d for d in tech_areas if area_counts[d.domain] >= threshold]

        # 计算 filtered_areas 中的 commit 总和
        total_commits = sum(repo.commit for repo in req.repos if repo.name in filtered_areas)

        domain_confidence = defaultdict(list)
        for area in filtered_areas:
            if area.confidence >= 0.3:
                # 计算 commit 占比并调整置信度
                commit_ratio = area.commit / total_commits if total_commits > 0 else 0
                adjusted_confidence = min(area.confidence * (1 + commit_ratio), 1)  # 限制置信度不超过1
                domain_confidence[area.domain].append(adjusted_confidence)

        # 计算每个领域的平均调整置信度
        averaged_domains = [
            Domain(domain=domain, confidence=sum(confidences) / len(confidences))
            for domain, confidences in domain_confidence.items()
        ]

        # 筛选和排序
        top_areas = sorted(
            (d for d in averaged_domains if d.confidence >= 0.6),
            key=lambda x: x.confidence,
            reverse=True
        )[:3]

        return DomainResponse(domains=top_areas)

    def truncate_readme(self, readme: str, max_length: int = 5000) -> str:
        """截断 readme 内容，确保其不超过指定的最大长度"""
        if len(readme) > max_length:
            return readme[:max_length] + '...'  # 截断并添加省略号
        return readme

    async def get_evaluation(self, req: models.GetEvaluationRequest) -> models.EvaluationResponse:
        user_events = []
        try:
            # 尝试拼接用户事件信息
            for event in req.user_events:
                if len(user_events) == 100:  # 限制长度为100
                    break
                else:
                    user_events.append(
                        f'仓库名称:{event.repo.name},仓库描述:{event.repo.description},仓库star数{event.repo.stargazers_count},'
                        f'仓库fork数{event.repo.forks_count},仓库创建时间:{event.repo.created_at},'
                        f'仓库贡献者数量:{event.repo.subscribers_count},用户对仓库commit数量:{event.commit_count},'
                        f'用户对仓库提issue数量:{event.issues_count},用户对仓库提pr次数:{event.pull_request_count}')
        except Exception as e:
            # 如果拼接用户事件信息出错，则记录错误并返回默认值
            print(f"拼接用户事件信息出错: {e}")
            user_events = []  # 设置为默认空列表

        try:
            # 调用 LLMChain 进行综合评价
            final_evaluation = self.evaluationChain.invoke({
                "user_events": user_events,
                "bio": req.bio,
                "following": req.following,
                "domains": req.domains,
                "followers": req.followers,
                "total_private_repos": req.total_private_repos,
                "total_public_repos": req.total_public_repos,
            })
        except Exception as e:
            # 如果调用 LLMChain 出错，则记录错误并返回默认值
            print(f"调用 LLMChain 出错: {e}")
            final_evaluation = "评价失败"  # 返回默认的错误信息

        return models.EvaluationResponse(evaluation=final_evaluation)

    async def get_area(self, req: models.AreaRequest) -> models.AreaResponse:
        # 向量搜索获取可能的国家
        query_text = f"个人简介: {req.bio}\n公司信息: {req.company}\n自述地区: {req.location}\n粉丝的自述地区分布: {req.follower_areas}\n关注的用户的自述地区分布: {req.following_areas}"
        #
        search_areas = country_search.search(query_text)
        try:
            # 运行 areaChain 并获取返回结果
            result = self.areaChain.invoke({
                "areas": search_areas,
                "bio": req.bio,
                "company": req.company,
                "location": req.location,
                "follower": req.follower_areas,
                "following": req.following_areas,
            })

            # 使用正则表达式匹配 country 和 confidence
            pattern = r'"country":\s*"([^"]+)",\s*"confidence":\s*([0-1](?:\.\d+)?)'
            match = re.search(pattern, result)

            if match:
                country = match.group(1)  # 提取国家
                confidence = float(match.group(2))  # 提取置信度并转换为 float
            else:
                # 如果没有匹配结果，返回默认值
                country = "N/A"
                confidence = 0.0

        except Exception as e:
            # 错误处理：可以根据需要记录错误日志
            print(f"Error occurred: {e}")
            country = "N/A"
            confidence = 0.0

        # 返回 AreaResponse 包含国家和置信度
        return models.AreaResponse(
            area=country,
            confidence=confidence
        )
