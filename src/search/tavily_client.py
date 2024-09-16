from tavily import TavilyClient as TavilyAPI
from src.utils.logger import logger
import json
import re
from functools import lru_cache
from datetime import datetime

class TavilyClient:
    def __init__(self, config):
        self.client = TavilyAPI(api_key=config.TAVILY_API_KEY)

    @lru_cache(maxsize=100)
    def search(self, query):
        current_date = datetime.now().strftime("%Y-%m-%d")
        query_with_date = f"{query} (as of {current_date})"
        logger.info(f"Performing Tavily search for query: {query_with_date}")
        try:
            search_result = self.client.get_search_context(query_with_date, search_depth="advanced", max_tokens=8000)
            logger.info(f"Tavily search result type: {type(search_result)}")
            logger.info(f"Tavily search result: {search_result[:500]}...")  # Print first 500 characters of the result
            
            if isinstance(search_result, str):
                search_result = json.loads(search_result)
            
            summary = self.summarize_search_results(search_result, query, current_date)
            return json.dumps({"summary": summary, "full_results": search_result, "search_date": current_date})
        except Exception as e:
            logger.error(f"Error in Tavily search: {e}")
            return json.dumps({"error": str(e), "search_date": current_date})

    def summarize_search_results(self, search_results, query, current_date):
        if not isinstance(search_results, list) or len(search_results) == 0:
            return f"As of {current_date}, I couldn't find any solid information about that. Want to try rephrasing your question?"

        summary = f"Here's what I found as of {current_date}:\n\n"
        for result in search_results[:3]:  # Limit to top 3 results for brevity
            content = result.get('content', '')
            
            # Extract key information
            sentences = re.split(r'(?<=[.!?])\s+', content)
            relevant_text = ' '.join(sentences[:2])  # Take first two sentences
            
            # Remove URLs and other technical details
            relevant_text = re.sub(r'http\S+', '', relevant_text)
            relevant_text = re.sub(r'\S+@\S+', '', relevant_text)
            
            summary += f"- {relevant_text.strip()}\n"

        summary += f"\nThis information is current as of {current_date}. Is there anything specific you'd like to know more about?"
        return summary