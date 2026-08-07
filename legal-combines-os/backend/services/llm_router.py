"""
LLM Router — Multi-LLM Provider Routing
"""
import json
import logging
from typing import Dict, Any, Optional, List
import requests

from ..config import Config

logger = logging.getLogger(__name__)


class LLMRouter:
    """Route requests to appropriate LLM providers"""

    def __init__(self):
        self.providers = {
            'deepseek': {
                'api_key': Config.DEEPSEEK_API_KEY,
                'api_url': 'https://api.deepseek.com/v1/chat/completions',
                'model': 'deepseek-chat',
                'available': bool(Config.DEEPSEEK_API_KEY)
            },
            'openrouter': {
                'api_key': Config.OPENROUTER_API_KEY,
                'api_url': 'https://openrouter.ai/api/v1/chat/completions',
                'models': ['openai/gpt-4', 'anthropic/claude-3-sonnet'],
                'available': bool(Config.OPENROUTER_API_KEY)
            }
        }
        self.default_provider = 'deepseek'

    def chat_completion(self, messages: List[Dict[str, str]], provider: str = None, **kwargs) -> Dict[str, Any]:
        """Generate chat completion from selected provider"""
        provider = provider or self.default_provider
        provider_config = self.providers.get(provider)
        
        if not provider_config or not provider_config['available']:
            return self._fallback_completion(messages)
        
        try:
            if provider == 'deepseek':
                return self._deepseek_completion(messages, **kwargs)
            elif provider == 'openrouter':
                return self._openrouter_completion(messages, **kwargs)
            else:
                return self._fallback_completion(messages)
        except Exception as e:
            logger.error(f"Error with provider {provider}: {str(e)}")
            return self._fallback_completion(messages)

    def _deepseek_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate completion using DeepSeek API"""
        provider_config = self.providers['deepseek']
        
        payload = {
            'model': kwargs.get('model', provider_config['model']),
            'messages': messages,
            'temperature': kwargs.get('temperature', 0.7),
            'max_tokens': kwargs.get('max_tokens', 1000),
        }
        
        headers = {
            'Authorization': f'Bearer {provider_config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(provider_config['api_url'], json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        return {
            'provider': 'deepseek',
            'content': data['choices'][0]['message']['content'],
            'model': data.get('model', 'unknown'),
            'usage': data.get('usage', {})
        }

    def _openrouter_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate completion using OpenRouter API"""
        provider_config = self.providers['openrouter']
        model = kwargs.get('model', provider_config['models'][0])
        
        payload = {
            'model': model,
            'messages': messages,
            'temperature': kwargs.get('temperature', 0.7),
            'max_tokens': kwargs.get('max_tokens', 1000),
        }
        
        headers = {
            'Authorization': f'Bearer {provider_config["api_key"]}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://legal-combines.com',
            'X-Title': 'Legal Combines OS'
        }
        
        response = requests.post(provider_config['api_url'], json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        return {
            'provider': 'openrouter',
            'content': data['choices'][0]['message']['content'],
            'model': data.get('model', 'unknown'),
            'usage': data.get('usage', {})
        }

    def _fallback_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Fallback completion (simulated)"""
        last_message = messages[-1]['content'] if messages else "No message"
        return {
            'provider': 'fallback',
            'content': f"Received: {last_message[:50]}... Set up API keys for full LLM functionality.",
            'model': 'fallback',
            'usage': {'prompt_tokens': 0, 'completion_tokens': 0}
        }

    def analyze_document(self, text: str, provider: str = None) -> Dict[str, Any]:
        """Analyze document using LLM"""
        messages = [
            {"role": "system", "content": "You are a legal document analysis expert."},
            {"role": "user", "content": f"Analyze this document: {text[:3000]}"}
        ]
        return self.chat_completion(messages, provider)

    def compliance_check(self, company_data: Dict[str, Any], provider: str = None) -> Dict[str, Any]:
        """Check compliance for a company"""
        company_str = json.dumps(company_data, indent=2)
        messages = [
            {"role": "system", "content": "You are a compliance expert."},
            {"role": "user", "content": f"Check compliance for: {company_str}"}
        ]
        return self.chat_completion(messages, provider)
