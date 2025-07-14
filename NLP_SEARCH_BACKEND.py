"""
Natural Language Search Backend for Pharmaceutical Intelligence Platform

This module demonstrates how to implement sophisticated natural language search
that understands pharmaceutical domain context and user intent.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import spacy
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import asyncpg
from openai import AsyncOpenAI

class PharmaSearchEngine:
    """Advanced NLP search engine for pharmaceutical news"""
    
    def __init__(self, db_pool: asyncpg.Pool, openai_key: str):
        self.db = db_pool
        self.openai = AsyncOpenAI(api_key=openai_key)
        
        # Load specialized NLP models
        self.nlp = spacy.load("en_core_sci_lg")  # SciSpacy for biomedical text
        self.embedder = SentenceTransformer('pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb')
        
        # Pharmaceutical entity patterns
        self.company_aliases = self._load_company_aliases()
        self.drug_database = self._load_drug_database()
        self.clinical_phases = ['phase 1', 'phase 2', 'phase 3', 'phase i', 'phase ii', 'phase iii']
        
    async def search(self, query: str, limit: int = 20) -> Dict:
        """Process natural language query and return relevant articles"""
        
        # Step 1: Parse and understand the query
        parsed_query = await self._parse_query(query)
        
        # Step 2: Build SQL query based on understanding
        sql_query, params = self._build_smart_query(parsed_query)
        
        # Step 3: Execute search with vector similarity
        results = await self._execute_search(sql_query, params, parsed_query)
        
        # Step 4: Re-rank results using AI
        ranked_results = await self._ai_rerank(results, query)
        
        # Step 5: Generate answer summary
        answer = await self._generate_answer(ranked_results, query)
        
        return {
            "query": query,
            "parsed": parsed_query,
            "results": ranked_results[:limit],
            "answer": answer,
            "total_found": len(results),
            "confidence": self._calculate_confidence(ranked_results, parsed_query)
        }
    
    async def _parse_query(self, query: str) -> Dict:
        """Parse natural language query into structured components"""
        
        # Use GPT-4 for intent understanding
        system_prompt = """You are a pharmaceutical search query parser. 
        Extract the following from user queries:
        - intent: (search, compare, track, analyze, predict)
        - entities: {companies: [], drugs: [], indications: [], topics: []}
        - timeframe: (today, week, month, year, custom date range, all time)
        - filters: {phase: [], approval_status: [], geography: []}
        - sentiment: (positive, negative, neutral, any)
        - relationships: (partnerships, competition, acquisition, etc.)
        
        Return as JSON."""
        
        response = await self.openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        parsed = json.loads(response.choices[0].message.content)
        
        # Enhance with NLP extraction
        doc = self.nlp(query)
        
        # Extract additional entities
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PERSON"]:
                parsed["entities"]["companies"].append(ent.text)
            elif ent.label_ in ["CHEMICAL", "DRUG"]:
                parsed["entities"]["drugs"].append(ent.text)
            elif ent.label_ == "DATE":
                parsed["timeframe"] = self._parse_date(ent.text)
        
        # Normalize company names
        parsed["entities"]["companies"] = [
            self._normalize_company(c) for c in parsed["entities"]["companies"]
        ]
        
        return parsed
    
    def _build_smart_query(self, parsed: Dict) -> Tuple[str, List]:
        """Build optimized SQL query from parsed intent"""
        
        # Base query with full-text search and vector similarity
        query_parts = ["""
            WITH ranked_articles AS (
                SELECT 
                    a.*,
                    ts_rank_cd(search_vector, query) as text_rank,
                    1 - (embeddings <=> $1::vector) as semantic_similarity,
                    CASE 
                        WHEN date_published > NOW() - INTERVAL '7 days' THEN 1.5
                        WHEN date_published > NOW() - INTERVAL '30 days' THEN 1.2
                        ELSE 1.0
                    END as recency_boost
                FROM articles a,
                     plainto_tsquery('english', $2) query
                WHERE 1=1
        """]
        
        params = [
            self.embedder.encode(parsed.get("original_query", "")),
            parsed.get("original_query", "")
        ]
        param_counter = 3
        
        # Add entity filters
        if parsed["entities"]["companies"]:
            query_parts.append(f"AND companies && ${param_counter}::text[]")
            params.append(parsed["entities"]["companies"])
            param_counter += 1
        
        if parsed["entities"]["topics"]:
            query_parts.append(f"AND topics && ${param_counter}::text[]")
            params.append(parsed["entities"]["topics"])
            param_counter += 1
        
        # Add timeframe filter
        if parsed.get("timeframe") and parsed["timeframe"] != "all time":
            query_parts.append(f"AND date_published >= ${param_counter}")
            params.append(self._calculate_date_filter(parsed["timeframe"]))
            param_counter += 1
        
        # Add phase filters
        if parsed["filters"].get("phase"):
            phase_conditions = " OR ".join([
                f"topics @> '[{{"phase": "{phase}"}}]'::jsonb" 
                for phase in parsed["filters"]["phase"]
            ])
            query_parts.append(f"AND ({phase_conditions})")
        
        # Complete the query
        query_parts.append("""
            )
            SELECT *,
                   (text_rank * 0.3 + 
                    semantic_similarity * 0.5 + 
                    confidence_scores * 0.2) * recency_boost as combined_score
            FROM ranked_articles
            WHERE text_rank > 0.01 OR semantic_similarity > 0.7
            ORDER BY combined_score DESC
            LIMIT 100
        """)
        
        return " ".join(query_parts), params
    
    async def _ai_rerank(self, results: List[Dict], query: str) -> List[Dict]:
        """Use AI to re-rank results based on relevance"""
        
        if not results:
            return results
        
        # Prepare context for ranking
        ranking_prompt = f"""Given the search query: "{query}"
        
        Rank these articles by relevance (1-10 scale):
        """
        
        for i, article in enumerate(results[:20]):  # Limit to top 20 for API
            ranking_prompt += f"""
            
            Article {i+1}:
            Title: {article['title']}
            Summary: {article['summary'][:200]}...
            Topics: {', '.join(article['topics'])}
            """
        
        ranking_prompt += """
        
        Return a JSON array of [{id: number, relevance_score: number, reason: string}]
        ordered by relevance_score descending.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a pharmaceutical news relevance expert."},
                {"role": "user", "content": ranking_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        rankings = json.loads(response.choices[0].message.content)
        
        # Apply AI rankings
        ranked_results = []
        ranking_map = {r['id']: r for r in rankings}
        
        for i, article in enumerate(results):
            if i in ranking_map:
                article['ai_relevance'] = ranking_map[i]['relevance_score']
                article['relevance_reason'] = ranking_map[i]['reason']
                article['final_score'] = (
                    article.get('combined_score', 0) * 0.6 + 
                    article['ai_relevance'] * 0.4
                )
            ranked_results.append(article)
        
        return sorted(ranked_results, key=lambda x: x.get('final_score', 0), reverse=True)
    
    async def _generate_answer(self, results: List[Dict], query: str) -> Dict:
        """Generate a natural language answer from search results"""
        
        if not results:
            return {
                "summary": "No relevant articles found for your query.",
                "confidence": 0,
                "sources": []
            }
        
        # Prepare context from top results
        context = "Based on the following pharmaceutical news articles:\n\n"
        sources = []
        
        for i, article in enumerate(results[:5]):
            context += f"""Article {i+1}: {article['title']}
            Published: {article['date_published']}
            Summary: {article['summary']}
            Topics: {', '.join(article['topics'])}
            
            """
            sources.append({
                "title": article['title'],
                "link": article['link'],
                "date": article['date_published']
            })
        
        # Generate comprehensive answer
        answer_prompt = f"""Based on the pharmaceutical news articles provided, 
        answer this query comprehensively: "{query}"
        
        Provide:
        1. A direct answer to the question
        2. Key insights from the articles
        3. Any patterns or trends noticed
        4. Important caveats or limitations
        
        Be specific and cite which articles support each point.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a pharmaceutical intelligence analyst. Provide accurate, insightful answers based solely on the provided articles."},
                {"role": "user", "content": context + "\n\n" + answer_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return {
            "summary": response.choices[0].message.content,
            "confidence": self._calculate_answer_confidence(results),
            "sources": sources,
            "articles_analyzed": len(results[:5])
        }
    
    def _calculate_answer_confidence(self, results: List[Dict]) -> float:
        """Calculate confidence in the answer based on result quality"""
        
        if not results:
            return 0.0
        
        # Factors affecting confidence
        avg_relevance = np.mean([r.get('ai_relevance', 5) for r in results[:5]]) / 10
        result_count = min(len(results), 10) / 10
        score_distribution = np.std([r.get('final_score', 0) for r in results[:10]])
        
        # High standard deviation means clear top results
        distribution_factor = min(score_distribution * 2, 1.0)
        
        confidence = (avg_relevance * 0.5 + result_count * 0.3 + distribution_factor * 0.2)
        
        return round(confidence, 2)
    
    def _normalize_company(self, company_name: str) -> str:
        """Normalize company names to handle variations"""
        
        # Remove common suffixes
        normalized = re.sub(r'\s+(Inc\.?|Corp\.?|Ltd\.?|LLC|plc|AG|SA|NV)$', '', company_name, flags=re.I)
        
        # Check aliases
        return self.company_aliases.get(normalized.lower(), normalized)
    
    def _calculate_date_filter(self, timeframe: str) -> datetime:
        """Convert timeframe string to datetime filter"""
        
        timeframe_map = {
            "today": timedelta(days=1),
            "week": timedelta(days=7),
            "month": timedelta(days=30),
            "quarter": timedelta(days=90),
            "year": timedelta(days=365)
        }
        
        return datetime.now() - timeframe_map.get(timeframe, timedelta(days=30))


# Example usage endpoint
async def natural_language_search_endpoint(request):
    """API endpoint for natural language search"""
    
    query = request.json.get("query")
    limit = request.json.get("limit", 20)
    include_answer = request.json.get("include_answer", True)
    
    # Initialize search engine
    search_engine = PharmaSearchEngine(db_pool, settings.OPENAI_API_KEY)
    
    # Perform search
    results = await search_engine.search(query, limit)
    
    # Track query for analytics
    await track_search_query(query, results["total_found"], request.user_id)
    
    return {
        "success": True,
        "query": query,
        "interpretation": results["parsed"],
        "total_results": results["total_found"],
        "articles": results["results"],
        "answer": results["answer"] if include_answer else None,
        "search_id": generate_search_id()  # For tracking follow-up queries
    }