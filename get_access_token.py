import requests

# Replace with your LinkedIn credentials
CLIENT_ID = "774q1m523tz2oi"
CLIENT_SECRET = "WPL_AP1.rypiS3ucrhEfqqpI.BZVTUg=="
REDIRECT_URI = "http://localhost:8000/callback"  # The same redirect URI you used earlier
AUTHORIZATION_CODE ="AQQaRqYEaLYZnJYVmsuRx7viyLT2CF-1jYxLfR5snXYZE-BCvvIeqdQlR_tfMf9P_iNsK-HtfnH23b_DpgDsrHV8Ydu6scPEihFuC54ZvVNBcf-5RKm7sNpUrXdCnMDgVPbHgL__-ATDtfH27AEtkvEl7aHm-JeiwWwi6UNB2X-No_qwb3xT4fRuAW3RT27uAybrQKg5xXi9LO4WnHA"

token_url = "https://www.linkedin.com/oauth/v2/accessToken"

# Prepare the data for the token exchange request
data = {
    'grant_type': 'authorization_code',
    'code': AUTHORIZATION_CODE,
    'redirect_uri': REDIRECT_URI,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
}

# Make the POST request to exchange the authorization code for an access token
response = requests.post(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})

# Check if the request was successful
if response.status_code == 200:
    access_token = response.json().get('access_token')
    print(f"Access Token: {access_token}")

    # Now use the access token to get the user profile (User ID)
    profile_url = "https://api.linkedin.com/v2/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}

    # Send GET request to LinkedIn API to get user profile information
    profile_response = requests.get(profile_url, headers=headers)

    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        user_id = profile_data.get("sub")
        print(f"Your LinkedIn User ID: {profile_data}")
    else:
        print(f"Error fetching user profile: {profile_response.status_code}")
        print(profile_response.json())

else:
    print(f"Error: {response.status_code}")
    print(response.json())
