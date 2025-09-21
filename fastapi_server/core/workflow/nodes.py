"""
LangGraph 워크플로우 노드 구현
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from fastapi_server.core.workflow.state import (
    AgentStateDict, WorkflowNodes, WorkflowRouter, 
    StateManager, StateTransitionRules, WorkflowConfig
)
from fastapi_server.core.agents.interfaces import (
    ICitizenQueryAnalyzer, IPolicyDocumentRetriever,
    ICitizenFriendlyProcessor, IInteractiveResponseGenerator,
    QueryAnalysisInput, DocumentRetrievalInput,
    ContentProcessingInput, ResponseGenerationInput
)
from fastapi_server.core.logging_config import get_logger

logger = get_logger(__name__)


class WorkflowNodeImplementation:
    """워크플로우 노드 구현"""
    
    def __init__(
        self,
        query_analyzer: ICitizenQueryAnalyzer,
        document_retriever: IPolicyDocumentRetriever,
        content_processor: ICitizenFriendlyProcessor,
        response_generator: IInteractiveResponseGenerator,
        config: Optional[Dict[str, Any]] = None
    ):
        self.query_analyzer = query_analyzer
        self.document_retriever = document_retriever
        self.content_processor = content_processor
        self.response_generator = response_generator
        self.config = WorkflowConfig.get_config(config)
        
        logger.info("WorkflowNodeImplementation initialized with config", extra={
            "config": self.config
        })
    
    async def query_analysis_node(self, state: AgentStateDict) -> AgentStateDict:
        """질의 분석 노드"""
        logger.info("Starting query analysis", extra={
            "session_id": state.get("session_id"),
            "query": state.get("user_query")
        })
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 입력 데이터 준비
            analysis_input = QueryAnalysisInput(
                query=state["user_query"],
                session_id=state["session_id"],
                context=state.get("context", {})
            )
            
            # Agent 실행
            result = await self.query_analyzer.process(analysis_input)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            if result.is_success():
                analysis_output = result.get_data()
                
                # 상태 업데이트
                updated_state = StateManager.update_state(state, {
                    "processed_query": analysis_output.processed_query,
                    "query_intent": analysis_output.intent,
                    "query_category": analysis_output.category,
                    "query_keywords": analysis_output.keywords,
                    "query_entities": analysis_output.entities,
                    "query_confidence": analysis_output.confidence,
                    "current_step": "query_analysis"
                })
                
                # 처리 시간 추가
                updated_state = StateManager.add_processing_time(
                    updated_state, "query_analysis", processing_time
                )
                
                logger.info("Query analysis completed successfully", extra={
                    "session_id": state.get("session_id"),
                    "confidence": analysis_output.confidence,
                    "intent": analysis_output.intent,
                    "processing_time": processing_time
                })
                
                return updated_state
            else:
                error_msg = f"Query analysis failed: {result.get_error()}"
                logger.error(error_msg, extra={
                    "session_id": state.get("session_id"),
                    "processing_time": processing_time
                })
                
                return StateManager.set_error(state, error_msg)
                
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Query analysis node error: {str(e)}"
            
            logger.error(error_msg, exc_info=e, extra={
                "session_id": state.get("session_id"),
                "processing_time": processing_time
            })
            
            return StateManager.set_error(state, error_msg)
    
    async def document_retrieval_node(self, state: AgentStateDict) -> AgentStateDict:
        """문서 검색 노드"""
        logger.info("Starting document retrieval", extra={
            "session_id": state.get("session_id"),
            "processed_query": state.get("processed_query")
        })
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 입력 데이터 준비
            retrieval_input = DocumentRetrievalInput(
                processed_query=state.get("processed_query", state["user_query"]),
                keywords=state.get("query_keywords", []),
                category=state.get("query_category"),
                max_results=self.config.get("max_results", 5)
            )
            
            # Agent 실행
            result = await self.document_retriever.process(retrieval_input)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            if result.is_success():
                retrieval_output = result.get_data()
                
                # 문서를 딕셔너리 형태로 변환 (JSON 직렬화 가능하도록)
                search_results = []
                for doc in retrieval_output.documents:
                    search_results.append({
                        "id": doc.id,
                        "title": doc.title,
                        "content": doc.content,
                        "category": doc.category,
                        "published_date": doc.published_date,
                        "difficulty": doc.difficulty.value,
                        "score": doc.score,
                        "highlights": doc.highlights,
                        "metadata": doc.metadata
                    })
                
                # 상태 업데이트
                updated_state = StateManager.update_state(state, {
                    "search_results": search_results,
                    "total_results_count": retrieval_output.total_count,
                    "search_strategy": retrieval_output.search_strategy,
                    "current_step": "document_retrieval"
                })
                
                # 처리 시간 추가
                updated_state = StateManager.add_processing_time(
                    updated_state, "document_retrieval", processing_time
                )
                
                logger.info("Document retrieval completed successfully", extra={
                    "session_id": state.get("session_id"),
                    "results_count": retrieval_output.total_count,
                    "search_strategy": retrieval_output.search_strategy,
                    "processing_time": processing_time
                })
                
                return updated_state
            else:
                error_msg = f"Document retrieval failed: {result.get_error()}"
                logger.error(error_msg, extra={
                    "session_id": state.get("session_id"),
                    "processing_time": processing_time
                })
                
                return StateManager.set_error(state, error_msg)
                
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Document retrieval node error: {str(e)}"
            
            logger.error(error_msg, exc_info=e, extra={
                "session_id": state.get("session_id"),
                "processing_time": processing_time
            })
            
            return StateManager.set_error(state, error_msg)
    
    async def content_processing_node(self, state: AgentStateDict) -> AgentStateDict:
        """내용 처리 노드"""
        logger.info("Starting content processing", extra={
            "session_id": state.get("session_id"),
            "results_count": state.get("total_results_count", 0)
        })
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 검색 결과를 DocumentResult 객체로 변환
            from fastapi_server.models.schemas import DocumentResult, DifficultyLevel
            
            documents = []
            for doc_data in state.get("search_results", []):
                doc = DocumentResult(
                    id=doc_data["id"],
                    title=doc_data["title"],
                    content=doc_data["content"],
                    category=doc_data["category"],
                    published_date=doc_data["published_date"],
                    difficulty=DifficultyLevel(doc_data["difficulty"]),
                    score=doc_data["score"],
                    highlights=doc_data.get("highlights", []),
                    metadata=doc_data.get("metadata", {})
                )
                documents.append(doc)
            
            # 입력 데이터 준비
            processing_input = ContentProcessingInput(
                documents=documents,
                user_query=state["user_query"],
                target_difficulty=DifficultyLevel.BEGINNER  # 기본값
            )
            
            # Agent 실행
            result = await self.content_processor.process(processing_input)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            if result.is_success():
                processing_output = result.get_data()
                
                # 상태 업데이트
                updated_state = StateManager.update_state(state, {
                    "simplified_content": processing_output.simplified_content,
                    "key_points": processing_output.key_points,
                    "step_by_step_guide": processing_output.step_by_step_guide,
                    "terminology_explanations": processing_output.terminology_explanations,
                    "readability_score": processing_output.readability_score,
                    "current_step": "content_processing"
                })
                
                # 처리 시간 추가
                updated_state = StateManager.add_processing_time(
                    updated_state, "content_processing", processing_time
                )
                
                logger.info("Content processing completed successfully", extra={
                    "session_id": state.get("session_id"),
                    "readability_score": processing_output.readability_score,
                    "key_points_count": len(processing_output.key_points),
                    "processing_time": processing_time
                })
                
                return updated_state
            else:
                error_msg = f"Content processing failed: {result.get_error()}"
                logger.error(error_msg, extra={
                    "session_id": state.get("session_id"),
                    "processing_time": processing_time
                })
                
                return StateManager.set_error(state, error_msg)
                
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Content processing node error: {str(e)}"
            
            logger.error(error_msg, exc_info=e, extra={
                "session_id": state.get("session_id"),
                "processing_time": processing_time
            })
            
            return StateManager.set_error(state, error_msg)
    
    async def response_generation_node(self, state: AgentStateDict) -> AgentStateDict:
        """응답 생성 노드"""
        logger.info("Starting response generation", extra={
            "session_id": state.get("session_id"),
            "simplified_content_length": len(state.get("simplified_content", ""))
        })
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 처리된 내용 객체 생성
            from fastapi_server.core.agents.interfaces import ContentProcessingOutput
            
            processed_content = ContentProcessingOutput(
                simplified_content=state.get("simplified_content", ""),
                key_points=state.get("key_points", []),
                step_by_step_guide=state.get("step_by_step_guide", []),
                terminology_explanations=state.get("terminology_explanations", {}),
                readability_score=state.get("readability_score", 0.0)
            )
            
            # 입력 데이터 준비
            generation_input = ResponseGenerationInput(
                user_query=state["user_query"],
                processed_content=processed_content,
                chat_history=[],  # 추후 구현
                include_suggestions=True
            )
            
            # Agent 실행
            result = await self.response_generator.process(generation_input)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            if result.is_success():
                generation_output = result.get_data()
                
                # 상태 업데이트
                updated_state = StateManager.update_state(state, {
                    "final_response": generation_output.main_response,
                    "follow_up_questions": generation_output.follow_up_questions,
                    "related_links": generation_output.related_links,
                    "confidence_score": generation_output.confidence_score,
                    "current_step": "response_generation"
                })
                
                # 처리 시간 추가
                updated_state = StateManager.add_processing_time(
                    updated_state, "response_generation", processing_time
                )
                
                logger.info("Response generation completed successfully", extra={
                    "session_id": state.get("session_id"),
                    "confidence_score": generation_output.confidence_score,
                    "response_length": len(generation_output.main_response),
                    "follow_ups_count": len(generation_output.follow_up_questions),
                    "processing_time": processing_time
                })
                
                return updated_state
            else:
                error_msg = f"Response generation failed: {result.get_error()}"
                logger.error(error_msg, extra={
                    "session_id": state.get("session_id"),
                    "processing_time": processing_time
                })
                
                return StateManager.set_error(state, error_msg)
                
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Response generation node error: {str(e)}"
            
            logger.error(error_msg, exc_info=e, extra={
                "session_id": state.get("session_id"),
                "processing_time": processing_time
            })
            
            return StateManager.set_error(state, error_msg)


class ConditionalEdgeImplementation:
    """조건부 엣지 구현"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = WorkflowConfig.get_config(config)
    
    def route_after_analysis(self, state: AgentStateDict) -> str:
        """질의 분석 후 라우팅"""
        decision = WorkflowRouter.route_after_analysis(state)
        
        logger.info("Routing after analysis", extra={
            "session_id": state.get("session_id"),
            "next_step": decision["next_step"],
            "reason": decision["reason"],
            "confidence": decision["confidence"]
        })
        
        return decision["next_step"]
    
    def route_after_retrieval(self, state: AgentStateDict) -> str:
        """문서 검색 후 라우팅"""
        decision = WorkflowRouter.route_after_retrieval(state)
        
        logger.info("Routing after retrieval", extra={
            "session_id": state.get("session_id"),
            "next_step": decision["next_step"],
            "reason": decision["reason"],
            "confidence": decision["confidence"],
            "results_count": state.get("total_results_count", 0)
        })
        
        return decision["next_step"]
    
    def route_after_processing(self, state: AgentStateDict) -> str:
        """내용 처리 후 라우팅"""
        decision = WorkflowRouter.route_after_processing(state)
        
        logger.info("Routing after processing", extra={
            "session_id": state.get("session_id"),
            "next_step": decision["next_step"],
            "reason": decision["reason"],
            "confidence": decision["confidence"],
            "readability_score": state.get("readability_score", 0.0)
        })
        
        return decision["next_step"]
    
    def route_after_response(self, state: AgentStateDict) -> str:
        """응답 생성 후 라우팅"""
        decision = WorkflowRouter.route_after_response(state)
        
        logger.info("Routing after response", extra={
            "session_id": state.get("session_id"),
            "next_step": decision["next_step"],
            "reason": decision["reason"],
            "confidence": decision["confidence"],
            "confidence_score": state.get("confidence_score", 0.0)
        })
        
        return decision["next_step"]


class WorkflowBuilder:
    """워크플로우 빌더"""
    
    def __init__(
        self,
        query_analyzer: ICitizenQueryAnalyzer,
        document_retriever: IPolicyDocumentRetriever,
        content_processor: ICitizenFriendlyProcessor,
        response_generator: IInteractiveResponseGenerator,
        config: Optional[Dict[str, Any]] = None
    ):
        self.nodes = WorkflowNodeImplementation(
            query_analyzer, document_retriever, 
            content_processor, response_generator, config
        )
        self.edges = ConditionalEdgeImplementation(config)
        self.config = WorkflowConfig.get_config(config)
    
    def build_graph(self) -> StateGraph:
        """LangGraph 빌드"""
        logger.info("Building LangGraph workflow")
        
        # StateGraph 생성
        graph = StateGraph(AgentStateDict)
        
        # 노드 추가
        graph.add_node(WorkflowNodes.QUERY_ANALYSIS, self.nodes.query_analysis_node)
        graph.add_node(WorkflowNodes.DOCUMENT_RETRIEVAL, self.nodes.document_retrieval_node)
        graph.add_node(WorkflowNodes.CONTENT_PROCESSING, self.nodes.content_processing_node)
        graph.add_node(WorkflowNodes.RESPONSE_GENERATION, self.nodes.response_generation_node)
        
        # 시작점 설정
        graph.set_entry_point(WorkflowNodes.QUERY_ANALYSIS)
        
        # 조건부 엣지 추가
        graph.add_conditional_edges(
            WorkflowNodes.QUERY_ANALYSIS,
            self.edges.route_after_analysis,
            {
                WorkflowNodes.DOCUMENT_RETRIEVAL: WorkflowNodes.DOCUMENT_RETRIEVAL,
                WorkflowNodes.ERROR: END
            }
        )
        
        graph.add_conditional_edges(
            WorkflowNodes.DOCUMENT_RETRIEVAL,
            self.edges.route_after_retrieval,
            {
                WorkflowNodes.CONTENT_PROCESSING: WorkflowNodes.CONTENT_PROCESSING,
                WorkflowNodes.ERROR: END
            }
        )
        
        graph.add_conditional_edges(
            WorkflowNodes.CONTENT_PROCESSING,
            self.edges.route_after_processing,
            {
                WorkflowNodes.RESPONSE_GENERATION: WorkflowNodes.RESPONSE_GENERATION,
                WorkflowNodes.ERROR: END
            }
        )
        
        graph.add_conditional_edges(
            WorkflowNodes.RESPONSE_GENERATION,
            self.edges.route_after_response,
            {
                WorkflowNodes.COMPLETED: END,
                WorkflowNodes.ERROR: END
            }
        )
        
        logger.info("LangGraph workflow built successfully")
        
        return graph
    
    def create_workflow(self) -> Any:
        """실행 가능한 워크플로우 생성"""
        graph = self.build_graph()
        
        # 메모리 체크포인터 설정 (선택적)
        checkpointer = MemorySaver() if self.config.get("enable_checkpointing", True) else None
        
        # 컴파일된 워크플로우 반환
        workflow = graph.compile(checkpointer=checkpointer)
        
        logger.info("Workflow created successfully", extra={
            "checkpointing_enabled": checkpointer is not None,
            "config": self.config
        })
        
        return workflow