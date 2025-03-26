import os
import asyncio
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
import logging
from pathlib import Path

from oauth_handler import OAuthHandler
from content_generator import ContentGenerator
from linkedin_manager import LinkedInManager

# Configure logging with more verbose output
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more verbose output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('linkedin_poster.log', mode='w')  # 'w' mode to start fresh
    ]
)
logger = logging.getLogger(__name__)
logger.debug("Logging initialized")  # Verify logging is working

class LinkedInPostAutomation:
    def __init__(self):
        # Load environment variables
        env_path = Path('.env')
        load_dotenv(dotenv_path=env_path)
        
        # Debug environment loading
        logger.info("Environment variables loaded")
        logger.info(f"GEMINI_API_KEY present: {bool(os.getenv('GEMINI_API_KEY'))}")
        
        # Initialize components
        self.oauth_handler = OAuthHandler()
        self.content_generator = ContentGenerator()
        self.linkedin_manager = LinkedInManager(self.oauth_handler)
        
    async def initialize(self) -> bool:
        """Initialize the automation system"""
        try:
            # Verify OAuth token
            token = await self.oauth_handler.get_valid_token()
            if not token:
                logger.error("Failed to obtain valid OAuth token")
                return False
                
            # Verify LinkedIn connection
            profile = await self.linkedin_manager.get_user_profile()
            logger.info(f"Connected as: {profile.get('localizedFirstName')} {profile.get('localizedLastName')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False

    async def create_and_post_content(self, topics: List[str], schedule_time: Optional[datetime] = None) -> None:
        """Generate and post content for given topics"""
        try:
            # Generate content for all topics
            posts = await self.content_generator.create_content_batch(topics)

            for post in posts:
                try:
                    logger.info(f"Processing post for topic: {post['topic']}")

                    if schedule_time:
                        result = await self.linkedin_manager.schedule_post(
                            content=post['content'],
                            schedule_time=schedule_time,
                            hashtags=post['hashtags']
                        )
                        logger.info(f"Post scheduled for {schedule_time}")
                    else:
                        result = await self.linkedin_manager.create_post(
                            content=post['content'],
                            hashtags=post['hashtags']
                        )
                        logger.info("Post published successfully")
                        
                    # Wait briefly between posts to avoid rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error posting content for topic '{post['topic']}': {e}")
                    
        except Exception as e:
            logger.error(f"Error in content creation and posting: {e}")

# CLI Interface
def cli():
    """Command line interface for the automation tool"""
    import argparse
    from datetime import datetime, timedelta
    import random
    import os
    
    parser = argparse.ArgumentParser(description='LinkedIn Post Automation Tool')
    parser.add_argument('--schedule', type=str, help='Schedule time (YYYY-MM-DD HH:MM)')
    
    args = parser.parse_args()
    
    # Always read from topics.txt in the current directory
    all_topics = []
    try:
        with open('topics.txt', 'r') as f:
            all_topics = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: topics.txt not found in current directory")
        return
    except Exception as e:
        print(f"Error reading topics.txt: {e}")
        return
        
    # Select one random topic
    if all_topics:
        topics = [random.choice(all_topics)]
        print(f"Selected topic: {topics[0]}")
    else:
        print("Error: No topics found")
        return
    
    # Parse schedule time if provided
    schedule_time = None
    if args.schedule:
        try:
            schedule_time = datetime.strptime(args.schedule, '%Y-%m-%d %H:%M')
        except ValueError as e:
            print(f"Error parsing schedule time: {e}")
            return
    
    # Run the automation
    asyncio.run(LinkedInPostAutomation().create_and_post_content(topics, schedule_time))

if __name__ == "__main__":
    cli()