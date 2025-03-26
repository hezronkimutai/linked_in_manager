import webbrowser

CLIENT_ID = "774q1m523tz2oi"
REDIRECT_URI = "http://localhost:8000/callback"  # Your redirect URI
SCOPE = "openid profile r_events w_member_social email rw_events"  # All necessary scopes

# Construct the authorization URL
auth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}"

# Open the URL in the default web browser for the user to authorize
webbrowser.open(auth_url)
