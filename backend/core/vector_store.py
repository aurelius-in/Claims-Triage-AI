"""
ChromaDB vector store integration for RAG implementation and knowledge base indexing.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import hashlib
from datetime import datetime

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import numpy as np

from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Global ChromaDB client
chroma_client: Optional[chromadb.Client] = None
embedding_model: Optional[SentenceTransformer] = None

# Collection names
KNOWLEDGE_BASE_COLLECTION = "knowledge_base"
DOCUMENT_EMBEDDINGS_COLLECTION = "document_embeddings"
POLICY_COLLECTION = "policies"
SOP_COLLECTION = "sops"

class ChromaDBManager:
    """Manages ChromaDB operations for RAG and knowledge base."""
    
    def __init__(self):
        self.client = None
        self.embedding_model = None
        self.collections = {}
        
    async def initialize(self) -> bool:
        """Initialize ChromaDB client and embedding model."""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize collections
            await self._initialize_collections()
            
            logger.info("✅ ChromaDB initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {str(e)}")
            return False
    
    async def _initialize_collections(self):
        """Initialize all required collections."""
        try:
            # Knowledge base collection
            self.collections[KNOWLEDGE_BASE_COLLECTION] = self.client.get_or_create_collection(
                name=KNOWLEDGE_BASE_COLLECTION,
                metadata={"description": "Knowledge base for decision support"}
            )
            
            # Document embeddings collection
            self.collections[DOCUMENT_EMBEDDINGS_COLLECTION] = self.client.get_or_create_collection(
                name=DOCUMENT_EMBEDDINGS_COLLECTION,
                metadata={"description": "Document embeddings for similarity search"}
            )
            
            # Policies collection
            self.collections[POLICY_COLLECTION] = self.client.get_or_create_collection(
                name=POLICY_COLLECTION,
                metadata={"description": "Policy documents for compliance"}
            )
            
            # SOPs collection
            self.collections[SOP_COLLECTION] = self.client.get_or_create_collection(
                name=SOP_COLLECTION,
                metadata={"description": "Standard Operating Procedures"}
            )
            
            logger.info("✅ ChromaDB collections initialized")
            
        except Exception as e:
            logger.error(f"❌ Collection initialization failed: {str(e)}")
            raise
    
    async def close(self):
        """Close ChromaDB connections."""
        try:
            if self.client:
                self.client.reset()
            logger.info("✅ ChromaDB connections closed")
        except Exception as e:
            logger.error(f"❌ ChromaDB close failed: {str(e)}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return []
    
    def _generate_id(self, content: str, prefix: str = "") -> str:
        """Generate unique ID for content."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{prefix}{content_hash}"
    
    async def add_knowledge_base_entry(
        self,
        content: str,
        metadata: Dict[str, Any],
        category: str = "general"
    ) -> str:
        """Add entry to knowledge base."""
        try:
            collection = self.collections[KNOWLEDGE_BASE_COLLECTION]
            
            # Generate embedding
            embedding = self._generate_embedding(content)
            if not embedding:
                raise ValueError("Failed to generate embedding")
            
            # Generate ID
            entry_id = self._generate_id(content, "kb_")
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[{
                    **metadata,
                    "category": category,
                    "timestamp": datetime.utcnow().isoformat(),
                    "content_length": len(content)
                }],
                ids=[entry_id]
            )
            
            logger.info(f"✅ Knowledge base entry added: {entry_id}")
            return entry_id
            
        except Exception as e:
            logger.error(f"❌ Failed to add knowledge base entry: {str(e)}")
            raise
    
    async def search_knowledge_base(
        self,
        query: str,
        n_results: int = 5,
        category: Optional[str] = None,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant information."""
        try:
            collection = self.collections[KNOWLEDGE_BASE_COLLECTION]
            
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                raise ValueError("Failed to generate query embedding")
            
            # Build where clause for category filter
            where_clause = {}
            if category:
                where_clause["category"] = category
            
            # Search collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Filter by similarity threshold
            filtered_results = []
            for i, distance in enumerate(results["distances"][0]):
                similarity = 1 - distance  # Convert distance to similarity
                if similarity >= threshold:
                    filtered_results.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": similarity
                    })
            
            logger.info(f"✅ Knowledge base search returned {len(filtered_results)} results")
            return filtered_results
            
        except Exception as e:
            logger.error(f"❌ Knowledge base search failed: {str(e)}")
            return []
    
    async def add_document_embedding(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Add document embedding for similarity search."""
        try:
            collection = self.collections[DOCUMENT_EMBEDDINGS_COLLECTION]
            
            # Generate embedding
            embedding = self._generate_embedding(content)
            if not embedding:
                raise ValueError("Failed to generate embedding")
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[{
                    **metadata,
                    "document_id": document_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "content_length": len(content)
                }],
                ids=[document_id]
            )
            
            logger.info(f"✅ Document embedding added: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"❌ Failed to add document embedding: {str(e)}")
            raise
    
    async def find_similar_documents(
        self,
        content: str,
        n_results: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find similar documents based on content."""
        try:
            collection = self.collections[DOCUMENT_EMBEDDINGS_COLLECTION]
            
            # Generate embedding
            embedding = self._generate_embedding(content)
            if not embedding:
                raise ValueError("Failed to generate embedding")
            
            # Search collection
            results = collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Filter by similarity threshold
            similar_documents = []
            for i, distance in enumerate(results["distances"][0]):
                similarity = 1 - distance
                if similarity >= threshold:
                    similar_documents.append({
                        "document_id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": similarity
                    })
            
            logger.info(f"✅ Found {len(similar_documents)} similar documents")
            return similar_documents
            
        except Exception as e:
            logger.error(f"❌ Similar document search failed: {str(e)}")
            return []
    
    async def add_policy(
        self,
        policy_name: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Add policy document."""
        try:
            collection = self.collections[POLICY_COLLECTION]
            
            # Generate embedding
            embedding = self._generate_embedding(content)
            if not embedding:
                raise ValueError("Failed to generate embedding")
            
            # Generate ID
            policy_id = self._generate_id(content, "policy_")
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[{
                    **metadata,
                    "policy_name": policy_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "content_length": len(content)
                }],
                ids=[policy_id]
            )
            
            logger.info(f"✅ Policy added: {policy_name}")
            return policy_id
            
        except Exception as e:
            logger.error(f"❌ Failed to add policy: {str(e)}")
            raise
    
    async def search_policies(
        self,
        query: str,
        n_results: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search policies for relevant information."""
        try:
            collection = self.collections[POLICY_COLLECTION]
            
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                raise ValueError("Failed to generate query embedding")
            
            # Search collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Filter by similarity threshold
            relevant_policies = []
            for i, distance in enumerate(results["distances"][0]):
                similarity = 1 - distance
                if similarity >= threshold:
                    relevant_policies.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": similarity
                    })
            
            logger.info(f"✅ Policy search returned {len(relevant_policies)} results")
            return relevant_policies
            
        except Exception as e:
            logger.error(f"❌ Policy search failed: {str(e)}")
            return []
    
    async def add_sop(
        self,
        sop_name: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Add Standard Operating Procedure."""
        try:
            collection = self.collections[SOP_COLLECTION]
            
            # Generate embedding
            embedding = self._generate_embedding(content)
            if not embedding:
                raise ValueError("Failed to generate embedding")
            
            # Generate ID
            sop_id = self._generate_id(content, "sop_")
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[{
                    **metadata,
                    "sop_name": sop_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "content_length": len(content)
                }],
                ids=[sop_id]
            )
            
            logger.info(f"✅ SOP added: {sop_name}")
            return sop_id
            
        except Exception as e:
            logger.error(f"❌ Failed to add SOP: {str(e)}")
            raise
    
    async def search_sops(
        self,
        query: str,
        n_results: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search SOPs for relevant procedures."""
        try:
            collection = self.collections[SOP_COLLECTION]
            
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                raise ValueError("Failed to generate query embedding")
            
            # Search collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Filter by similarity threshold
            relevant_sops = []
            for i, distance in enumerate(results["distances"][0]):
                similarity = 1 - distance
                if similarity >= threshold:
                    relevant_sops.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": similarity
                    })
            
            logger.info(f"✅ SOP search returned {len(relevant_sops)} results")
            return relevant_sops
            
        except Exception as e:
            logger.error(f"❌ SOP search failed: {str(e)}")
            return []
    
    async def get_decision_support(
        self,
        case_context: str,
        decision_type: str = "general",
        n_results: int = 3
    ) -> Dict[str, Any]:
        """Get decision support information from knowledge base."""
        try:
            # Search knowledge base
            kb_results = await self.search_knowledge_base(
                case_context,
                n_results=n_results,
                category=decision_type
            )
            
            # Search policies
            policy_results = await self.search_policies(
                case_context,
                n_results=n_results
            )
            
            # Search SOPs
            sop_results = await self.search_sops(
                case_context,
                n_results=n_results
            )
            
            return {
                "knowledge_base": kb_results,
                "policies": policy_results,
                "sops": sop_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Decision support failed: {str(e)}")
            return {
                "knowledge_base": [],
                "policies": [],
                "sops": [],
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check ChromaDB health status."""
        try:
            # Check if client is initialized
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized"
                }
            
            # Check collections
            collection_status = {}
            for name, collection in self.collections.items():
                try:
                    count = collection.count()
                    collection_status[name] = {
                        "status": "healthy",
                        "document_count": count
                    }
                except Exception as e:
                    collection_status[name] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
            
            return {
                "status": "healthy",
                "collections": collection_status,
                "embedding_model": "all-MiniLM-L6-v2"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global ChromaDB manager instance
chroma_manager = ChromaDBManager()

# Convenience functions
async def init_vector_store() -> bool:
    """Initialize vector store."""
    return await chroma_manager.initialize()

async def close_vector_store():
    """Close vector store connections."""
    await chroma_manager.close()

async def add_knowledge_base_entry(content: str, metadata: Dict[str, Any], category: str = "general") -> str:
    """Add entry to knowledge base."""
    return await chroma_manager.add_knowledge_base_entry(content, metadata, category)

async def search_knowledge_base(query: str, n_results: int = 5, category: Optional[str] = None, threshold: float = 0.7) -> List[Dict[str, Any]]:
    """Search knowledge base."""
    return await chroma_manager.search_knowledge_base(query, n_results, category, threshold)

async def add_document_embedding(document_id: str, content: str, metadata: Dict[str, Any]) -> str:
    """Add document embedding."""
    return await chroma_manager.add_document_embedding(document_id, content, metadata)

async def find_similar_documents(content: str, n_results: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
    """Find similar documents."""
    return await chroma_manager.find_similar_documents(content, n_results, threshold)

async def get_decision_support(case_context: str, decision_type: str = "general", n_results: int = 3) -> Dict[str, Any]:
    """Get decision support information."""
    return await chroma_manager.get_decision_support(case_context, decision_type, n_results)

async def vector_store_health_check() -> Dict[str, Any]:
    """Check vector store health."""
    return await chroma_manager.health_check()
