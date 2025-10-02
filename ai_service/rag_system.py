# ai_service/rag_system.py

import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PartyPlanningRAG:
    """파티 플래닝을 위한 RAG 시스템"""
    
    def __init__(self):
        # ChromaDB 설정
        self.chroma_client = chromadb.PersistentClient(
            path=os.path.join(settings.BASE_DIR, "vector_db"),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # OpenAI 임베딩 모델
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        
        # 컬렉션 이름들
        self.collections = {
            'party_ideas': 'party_planning_ideas',
            'venues': 'party_venues',
            'catering': 'catering_options',
            'decorations': 'decoration_ideas',
            'activities': 'party_activities'
        }
        
        # 텍스트 분할기
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # 벡터 스토어 초기화
        self._initialize_vector_stores()
    
    def _initialize_vector_stores(self):
        """벡터 스토어 초기화 및 기본 데이터 로드"""
        try:
            # 기본 파티 플래닝 데이터 추가
            self._add_default_party_data()
            logger.info("RAG 시스템이 성공적으로 초기화되었습니다.")
        except Exception as e:
            logger.error(f"RAG 시스템 초기화 오류: {e}")
    
    def _add_default_party_data(self):
        """기본 파티 플래닝 데이터 추가"""
        # 파티 아이디어 데이터
        party_ideas = [
            {
                "type": "생일파티",
                "content": "생일파티 기획: 케이크, 촛불, 생일축하 노래, 선물 교환, 게임 활동. 예산: 10-50만원",
                "category": "birthday",
                "budget_range": "100000-500000"
            },
            {
                "type": "결혼기념일",
                "content": "결혼기념일 파티: 로맨틱한 분위기, 꽃 장식, 기념품, 사진 촬영, 특별 메뉴. 예산: 20-100만원",
                "category": "anniversary",
                "budget_range": "200000-1000000"
            },
            {
                "type": "회사 파티",
                "content": "회사 파티: 팀빌딩 활동, 네트워킹, 프레젠테이션, 뷔페식 식사, 시상식. 예산: 인당 3-10만원",
                "category": "corporate",
                "budget_range": "30000-100000"
            },
            {
                "type": "졸업파티",
                "content": "졸업파티: 기념품 제작, 사진 부스, 축하 메시지, 동창회 연락처 교환. 예산: 5-30만원",
                "category": "graduation",
                "budget_range": "50000-300000"
            }
        ]
        
        # 장소 데이터
        venue_data = [
            {
                "name": "실내 카페/레스토랑",
                "content": "아늑한 분위기, 음식 서비스 가능, 소규모 모임에 적합, 날씨 걱정 없음. 비용: 시간당 10-30만원",
                "capacity": "10-50명",
                "cost_range": "100000-300000"
            },
            {
                "name": "호텔 연회장",
                "content": "격식 있는 분위기, 풀 서비스, 대규모 행사 가능, 주차 편리. 비용: 100-500만원",
                "capacity": "50-200명",
                "cost_range": "1000000-5000000"
            },
            {
                "name": "야외 공원",
                "content": "자연스러운 분위기, 넓은 공간, 저렴한 비용, 날씨 의존적. 비용: 무료-10만원",
                "capacity": "제한없음",
                "cost_range": "0-100000"
            }
        ]
        
        # 케이터링 데이터  
        catering_data = [
            {
                "type": "뷔페",
                "content": "다양한 음식 선택, 셀프 서비스, 비교적 저렴, 대규모 행사에 적합. 비용: 인당 15-40천원",
                "cost_per_person": "15000-40000"
            },
            {
                "type": "코스 요리",
                "content": "격식 있는 서빙, 정해진 메뉴, 개인별 서빙, 고급스러운 분위기. 비용: 인당 50-150천원",
                "cost_per_person": "50000-150000"
            },
            {
                "type": "간식/디저트",
                "content": "간단한 파티에 적합, 케이크, 쿠키, 음료수, 부담없는 분위기. 비용: 인당 5-20천원",
                "cost_per_person": "5000-20000"
            }
        ]
        
        # 각 컬렉션에 데이터 추가
        self._add_documents_to_collection('party_ideas', party_ideas)
        self._add_documents_to_collection('venues', venue_data)
        self._add_documents_to_collection('catering', catering_data)
    
    def _add_documents_to_collection(self, collection_type: str, documents: List[Dict]):
        """특정 컬렉션에 문서 추가"""
        try:
            collection_name = self.collections[collection_type]
            
            # ChromaDB 컬렉션 생성 또는 가져오기
            try:
                collection = self.chroma_client.get_collection(collection_name)
            except:
                collection = self.chroma_client.create_collection(collection_name)
            
            # 문서들을 벡터화하여 저장
            for doc in documents:
                doc_id = str(uuid.uuid4())
                content = doc.get('content', '')
                
                # 메타데이터 준비
                metadata = {k: v for k, v in doc.items() if k != 'content'}
                
                # 임베딩 생성
                embedding = self.embeddings.embed_query(content)
                
                # 컬렉션에 추가
                collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[metadata]
                )
                
        except Exception as e:
            logger.error(f"문서 추가 오류 ({collection_type}): {e}")
    
    def search_relevant_info(self, query: str, collection_types: List[str] = None, top_k: int = 5) -> List[Dict]:
        """관련 정보 검색"""
        if collection_types is None:
            collection_types = list(self.collections.keys())
        
        all_results = []
        
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.embeddings.embed_query(query)
            
            for collection_type in collection_types:
                collection_name = self.collections[collection_type]
                
                try:
                    collection = self.chroma_client.get_collection(collection_name)
                    
                    # 유사도 검색
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=top_k
                    )
                    
                    # 결과 포맷팅
                    for i, doc in enumerate(results['documents'][0]):
                        result = {
                            'content': doc,
                            'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                            'score': 1 - results['distances'][0][i] if results['distances'][0] else 0,
                            'collection': collection_type
                        }
                        all_results.append(result)
                        
                except Exception as e:
                    logger.error(f"컬렉션 검색 오류 ({collection_type}): {e}")
                    continue
            
            # 점수 기준으로 정렬
            all_results.sort(key=lambda x: x['score'], reverse=True)
            
            return all_results[:top_k]
            
        except Exception as e:
            logger.error(f"검색 오류: {e}")
            return []
    
    def add_custom_knowledge(self, content: str, metadata: Dict, collection_type: str = 'party_ideas'):
        """사용자 정의 지식 추가"""
        try:
            self._add_documents_to_collection(collection_type, [{'content': content, **metadata}])
            logger.info(f"사용자 정의 지식이 {collection_type}에 추가되었습니다.")
        except Exception as e:
            logger.error(f"사용자 정의 지식 추가 오류: {e}")
    
    def get_contextual_information(self, party_request: Dict) -> str:
        """파티 요청에 기반한 맥락적 정보 검색"""
        # 검색 쿼리 구성
        query_parts = []
        
        if party_request.get('party_type'):
            query_parts.append(f"파티 종류: {party_request['party_type']}")
        
        if party_request.get('budget'):
            query_parts.append(f"예산: {party_request['budget']}원")
            
        if party_request.get('guest_count'):
            query_parts.append(f"참석자: {party_request['guest_count']}명")
            
        if party_request.get('special_requirements'):
            query_parts.append(party_request['special_requirements'])
        
        search_query = " ".join(query_parts)
        
        # 관련 정보 검색
        results = self.search_relevant_info(search_query, top_k=10)
        
        # 검색 결과를 문맥 정보로 변환
        context_info = []
        for result in results:
            context_info.append(f"[{result['collection']}] {result['content']}")
        
        return "\n\n".join(context_info)