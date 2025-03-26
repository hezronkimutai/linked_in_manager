import os
import json
from typing import Dict, Optional, List
import aiohttp
from datetime import datetime
from oauth_handler import OAuthHandler

class LinkedInManager:
    def __init__(self, oauth_handler: OAuthHandler):
        self.oauth_handler = oauth_handler
        self.base_url = "https://api.linkedin.com/v2"
        self.user_info = None
        
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers with valid access token"""
        token = await self.oauth_handler.get_valid_token()
        if not token:
            raise Exception("No valid access token available")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          params: Optional[Dict] = None, retries: int = 3) -> Dict:
        """Make HTTP request to LinkedIn API with retry logic"""
        async with aiohttp.ClientSession() as session:
            while retries > 0:
                try:
                    headers = await self._get_headers()
                    url = f"{self.base_url}/{endpoint}"
                    
                    async with session.request(method, url, headers=headers,
                                            json=data, params=params) as response:
                        if response.status == 401:
                            # Token might be expired, try to refresh
                            await self.oauth_handler.get_valid_token()
                            retries -= 1
                            continue
                            
                        response_text = await response.text()
                        
                        if response.status not in [200, 201]:
                            raise Exception(f"LinkedIn API error: {response.status} - {response_text}")
                            
                        return json.loads(response_text) if response_text else {}
                        
                except Exception as e:
                    if retries <= 1:
                        raise Exception(f"Failed after {3-retries} retries: {str(e)}")
                    retries -= 1
                    
            raise Exception("Maximum retries exceeded")

    async def get_user_profile(self) -> Dict:
        """Get current user's profile information"""
        if not self.user_info:
            self.user_info = await self._make_request(
                "GET",
                "userinfo"
            )
        return self.user_info

    async def create_post(self, content: str, hashtags: Optional[List[str]] = None) -> Dict:
        """Create a new post on LinkedIn"""
        try:
            # Get user profile
            try:
                user_info = await self.get_user_profile()
                print(f"Generated post for user: {user_info}")
            except Exception as e:
                raise Exception(f"Failed to fetch user profile: {str(e)}")

            # Validate user ID
            user_id = user_info.get("sub")
            if not user_id:
                raise Exception("Could not determine user ID from profile")
            
            # Validate content
            if not content or not content.strip():
                raise ValueError("Post content cannot be empty")

            # Combine content with hashtags
            full_content = content
            if hashtags:
                try:
                    full_content += "\n\n" + " ".join(hashtags)
                except Exception as e:
                    raise Exception(f"Error formatting hashtags: {str(e)}")

            # Prepare post data
            post_data = {
                "author": f"urn:li:person:{user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": full_content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            # Make the API request to create the post
            return await self._make_request("POST", "ugcPosts", data=post_data)

        except ValueError as ve:
            # Handle validation errors
            raise ValueError(f"Validation error: {str(ve)}")
        except Exception as e:
            # Handle all other errors
            raise Exception(f"Failed to create LinkedIn post: {str(e)}")

    async def schedule_post(self, content: str, schedule_time: datetime,
                          hashtags: Optional[List[str]] = None) -> Dict:
        """Schedule a post for future publication"""
        user_info = await self.get_user_profile()
        user_id = user_info.get("id")
        
        if not user_id:
            raise Exception("Could not determine user ID")
            
        # Combine content with hashtags
        full_content = content
        if hashtags:
            full_content += "\n\n" + " ".join(hashtags)

        post_data = {
            "author": f"urn:li:person:{user_id}",
            "lifecycleState": "SCHEDULED",
            "scheduledTime": int(schedule_time.timestamp() * 1000),  # Convert to milliseconds
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": full_content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        return await self._make_request("POST", "ugcPosts", data=post_data)

    async def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a specific post"""
        try:
            analytics = await self._make_request(
                "GET",
                f"socialMetrics/{post_id}",
                params={"fields": "totalShareStatistics"}
            )
            return analytics.get("totalShareStatistics", {})
        except Exception as e:
            print(f"Error fetching analytics for post {post_id}: {e}")
            return {}

    async def delete_post(self, post_id: str) -> bool:
        """Delete a LinkedIn post"""
        try:
            await self._make_request("DELETE", f"ugcPosts/{post_id}")
            return True
        except Exception as e:
            print(f"Error deleting post {post_id}: {e}")
            return False

# Example usage
async def main():
    oauth_handler = OAuthHandler()
    linkedin = LinkedInManager(oauth_handler)
    
    try:
        profile = await linkedin.get_user_profile()
        print(f"Connected as: {profile.get('localizedFirstName')} {profile.get('localizedLastName')}")
        
        # Example post
        post = await linkedin.create_post(
            "Testing the LinkedIn API integration! #LinkedInAPI #Testing",
            hashtags=["#Python", "#Development"]
        )
        print(f"Post created successfully: {post}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())