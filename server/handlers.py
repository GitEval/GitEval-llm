import grpc
from api import llm_pb2, llm_pb2_grpc
from . import models, service


class LLMServiceServicer(llm_pb2_grpc.LLMServiceServicer):
    def __init__(self):
        self._service = service.Service()  # 使用现有的 Service 实现

    async def GetDomain(self, request, context):
        try:
            # 从 gRPC 请求中解析并构造内部的 DomainRequest 模型
            req = models.DomainRequest(
                repos=[models.Repo(name=repo.name, readme=repo.readme, language=repo.language, commit=repo.commit) for
                       repo in
                       request.repos],  # 解析 repos
                bio=request.bio
            )
            # 异步调用服务层的 get_domain 方法，并使用 await 等待其完成
            response = await self._service.get_domain(req)
            # 返回响应
            return llm_pb2.GetDomainResponse(
                domains=[llm_pb2.Domain(domain=d.domain, confidence=d.confidence) for d in response.domains])
        except Exception as e:
            context.set_details(f"Error in GetDomain: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return llm_pb2.GetDomainResponse()  # 返回空响应，或根据需要设置错误字段

    async def GetEvaluation(self, request, context):
        try:
            # 验证 user_events 的格式
            user_events = []
            for event in request.user_events:
                # 确保每个事件的 repo 字段存在并符合 RepoInfo 模型
                repo_info = {
                    "name": event.repo.name,
                    "description": event.repo.description,
                    "stargazers_count": event.repo.stargazers_count,
                    "forks_count": event.repo.forks_count,
                    "created_at": event.repo.created_at,
                    "subscribers_count": event.repo.subscribers_count,
                }

                # 构建 UserEvent 对象
                user_event = models.UserEvent(
                    repo=models.RepoInfo(**repo_info),
                    commit_count=event.commit_count,
                    issues_count=event.issues_count,
                    pull_request_count=event.pull_request_count,
                )

                user_events.append(user_event)

            # 构造 GetEvaluationRequest
            req = models.GetEvaluationRequest(
                bio=request.bio,
                followers=request.followers,
                following=request.following,
                total_private_repos=request.total_private_repos,
                total_public_repos=request.total_public_repos,
                user_events=user_events,  # 使用处理后的 user_events 数据
                domains=request.domains
            )

            # 异步调用服务层的 get_evaluation 方法，并使用 await 等待其完成
            response = await self._service.get_evaluation(req)

            # 返回响应
            return llm_pb2.GetEvaluationResponse(evaluation=response.evaluation)

        except ValueError as ve:
            # 针对数据格式错误的处理
            print(f"ValueError in GetEvaluation: {str(ve)}")
            context.set_details(f"ValueError: {str(ve)}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return llm_pb2.GetEvaluationResponse()  # 返回空响应，或者设置具体错误字段

        except Exception as e:
            # 捕获其他类型的错误
            print(f"Error in GetEvaluation: {str(e)}")
            context.set_details(f"Error in GetEvaluation: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return llm_pb2.GetEvaluationResponse()  # 返回空响应，或者设置具体错误字段

    async def GetArea(self, request, context):
        try:
            # 解析请求并构造内部的 AreaRequest
            req = models.AreaRequest(
                bio=request.bio,
                company=request.company,
                location=request.location,
                follower_areas=request.follower_areas,
                following_areas=request.following_areas
            )
            # 异步调用服务层的 get_area 方法，并使用 await 等待其完成
            response = await self._service.get_area(req)
            # 返回响应
            return llm_pb2.GetAreaResponse(area=response.area, confidence=response.confidence)
        except Exception as e:
            context.set_details(f"Error in GetArea: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return llm_pb2.GetAreaResponse()  # 返回空响应，或根据需要设置错误字段
