import requests
import json

# Replace with your Gemini API key
GEMINI_API_KEY = "AIzaSyDA6DBtNg33vlq74Nu1US77bnND-EuenOw"

# Replace with your LinkedIn Access Token
ACCESS_TOKEN ="AQXrmIhJsV8oLtbdwnKZw-j68ighV9XSU9soZMZk-QqVLO9GaDhZewI_E5c-G72BBOFNbMc9o_kYEPISP7mAx5r_3Z-xm5AoxGrLJNIdRvDQa7w_ejDL6z4AmU-eSPwomZrOE8HfC-P671lpm6jGhrvMvtLwFpMTioHwZmdHsqAE-QsKY3cdwr9gQ7YcPwX6r6lfIti7Cx3KoAFtpnthEQvldZZFxx89zvXTIY1vq_kZW-y-LZBgjhmCNPv-VOyOWckbuBA-mQlJQL8aTrGILLXOZzF6eFAqOxK8Eu7gQ7nYssC7T1WTZOHtWHEg3k5psMp2BFfySku3G_-mQzusNOQiRxk8kw"
share_url = "https://api.linkedin.com/v2/ugcPosts"


# Function to share content on LinkedIn
def share_on_linkedin(post_content):
    """Posts the generated content to LinkedIn."""
    # Get LinkedIn User ID dynamically using the /me endpoint
    profile_url = "https://api.linkedin.com/v2/me"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Send GET request to fetch LinkedIn profile data
    # profile_response = requests.get(profile_url, headers=headers)

    # if true:
    # Extract the user ID from the response
    # user_data = profile_response.json()
    user_id = "QH4JwS_aly"
    if user_id:
        post_data = {
            "author": f"urn:li:person:{user_id}",  # Use the dynamic LinkedIn user ID
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # Send POST request to LinkedIn API to share content
        response = requests.post(share_url, headers=headers, data=json.dumps(post_data))

        if response.status_code == 201:
            print("Post successfully shared on LinkedIn!")
        else:
            print(f"Error posting to LinkedIn: {response.status_code}")
            print(response.json())
    else:
        print("Error: User ID not found in profile response.")


# Main logic
if __name__ == "__main__":
    topic_list = ["AI in Healthcare", "Future of Remote Work", "Sustainability in Tech"]
    
    for topic in topic_list:
        print(f"Generating post for topic: {topic}")
        
        # Manually defining LinkedIn post content for each topic
        if topic == "AI in Healthcare":
            post_content = "AI in Healthcare is revolutionizing the way we approach patient care. With advancements in machine learning and data analytics, healthcare providers can now make more accurate diagnoses, personalize treatment plans, and predict health outcomes with greater precision. It's an exciting time for the healthcare industry, and the potential for positive change is immense. #AI #Healthcare #Innovation"
        elif topic == "Future of Remote Work":
            post_content = "The future of remote work is bright! As companies embrace flexible work environments, employees enjoy better work-life balance, and businesses access a global talent pool. With the right technology and policies, remote work can lead to more productive and innovative teams. #RemoteWork #FutureOfWork #Technology"
        elif topic == "Sustainability in Tech":
            post_content = "Sustainability in technology is not just a buzzword—it's a necessity. With the tech industry's growing environmental impact, companies must prioritize green practices, energy efficiency, and responsible resource management. The future of tech must be built on sustainable foundations. #Sustainability #TechForGood #GreenTech"

        if post_content:
            print(f"Generated Post: \n{post_content}")
            print("Posting to LinkedIn...")
            share_on_linkedin(post_content)
        print("\n---\n")