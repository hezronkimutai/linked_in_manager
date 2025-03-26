import os
import logging
import json
import asyncio
from typing import List, Dict, Optional
from time import sleep
import aiohttp
from huggingface_hub import InferenceClient

class ContentGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # Get Hugging Face API token from environment
        self.hf_token = os.getenv('HF_TOKEN')
        if not self.hf_token:
            raise ValueError("HF_TOKEN environment variable is required")
        
        self.logger.info("Initializing ContentGenerator with Hugging Face")
        
        # Initialize the inference client
        self.model = "mistralai/Mixtral-8x7B-Instruct-v0.1"  # Using Mixtral, a powerful open source model
        self.client = InferenceClient(
            model=self.model,
            token=self.hf_token
        )
        self.logger.info(f"Initialized with model: {self.model}")

    async def _generate_text(self, prompt: str, retries: int = 3) -> Optional[str]:
        """Generate text using Hugging Face's API with retry logic"""
        while retries > 0:
            try:
                response = self.client.text_generation(
                    prompt,
                    max_new_tokens=500,
                    temperature=0.7,
                    top_p=0.95,
                    repetition_penalty=1.1
                )
                return response
            except Exception as e:
                self.logger.error(f"Generation error: {str(e)}")
                if retries > 1:
                    retries -= 1
                    await asyncio.sleep(2)
                    continue
                raise
        raise Exception("Failed to generate text after maximum retries")

    async def generate_post(self, topic: str, tone: str = "professional") -> Dict[str, str]:
        """Generate a LinkedIn post with hashtags for a given topic"""
        prompt = f"""
        Task: Create a professional LinkedIn post about {topic}.

        Requirements:
        - Professional and engaging style
        - Include relevant industry insights
        - Between 150-200 words
        - Written in a {tone} tone
        - End with 3-5 relevant hashtags

        Format the response as JSON with 'content' and 'hashtags' keys.
        """
        
        try:
            response_text = await self._generate_text(prompt)
            try:
                # Try to parse as JSON first
                result = json.loads(response_text)
                return {
                    "content": result.get("content", ""),
                    "hashtags": result.get("hashtags", [])
                }
            except json.JSONDecodeError:
                # If not JSON, extract content and hashtags manually
                words = response_text.split()
                hashtags = [word for word in words if word.startswith("#")]
                content = " ".join([word for word in words if not word.startswith("#")])
                return {
                    "content": content.strip(),
                    "hashtags": hashtags
                }
        except Exception as e:
            self.logger.error(f"Error generating post: {str(e)}")
            raise

    async def optimize_content(self, content: str) -> str:
        """Optimize the content for LinkedIn engagement"""
        prompt = f"""
        Task: Optimize this LinkedIn post for maximum engagement while maintaining authenticity:

        Original post:
        {content}

        Requirements:
        1. Use a conversational and engaging tone
        2. Limit technical jargon
        3. Break text into bullet points or shorter sentences
        4. Include a thought-provoking question
        5. Format with clear line breaks
        6. Keep content simple and accessible
        7. Include a clear call to action

        Return only the optimized post content, no additional text.
        """
        
        try:
            return (await self._generate_text(prompt)).strip()
        except Exception as e:
            self.logger.error(f"Error optimizing content: {str(e)}")
            return content

    async def generate_hashtags(self, content: str, count: int = 5) -> List[str]:
        """Generate relevant hashtags based on the content"""
        prompt = f"""
        Task: Generate {count} relevant, professional, and trending LinkedIn hashtags for this content:

        Content:
        {content}

        Return only the hashtags, each starting with #, separated by spaces.
        """
        
        try:
            response_text = await self._generate_text(prompt)
            hashtags = [tag.strip() for tag in response_text.split() if tag.startswith("#")]
            return hashtags[:count]
        except Exception as e:
            self.logger.error(f"Error generating hashtags: {str(e)}")
            return []

    async def create_content_batch(self, topics: List[str], tone: str = "professional") -> List[Dict[str, str]]:
        """Generate a batch of posts for multiple topics"""
        posts = []
        for topic in topics:
            try:
                post = await self.generate_post(topic, tone)
                optimized_content = await self.optimize_content(post["content"])
                hashtags = await self.generate_hashtags(optimized_content)
                posts.append({
                    "topic": topic,
                    "content": optimized_content,
                    "hashtags": hashtags
                })
            except Exception as e:
                self.logger.error(f"Error generating content for topic '{topic}': {e}")
        return posts

if __name__ == "__main__":
    import asyncio
    async def main():
        generator = ContentGenerator()
        topics = ["AI in Healthcare", "Future of Remote Work", "Sustainable Technology"]
        posts = await generator.create_content_batch(topics)
        for post in posts:
            print(f"\nTopic: {post['topic']}")
            print(f"Content: {post['content']}")
            print(f"Hashtags: {' '.join(post['hashtags'])}")

    asyncio.run(main())