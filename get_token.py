import dropbox

APP_KEY = "czyil21143kucio"
APP_SECRET = "wheywf9lrzujo6f"

# This forces Dropbox to give us a permanent offline token
auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET, token_access_type='offline')
authorize_url = auth_flow.start()

print("\n--- STOP AND DO THIS ---")
print("1. Click this link (or copy/paste it into your browser):")
print(authorize_url)
print("2. Click 'Allow' on the Dropbox page.")
print("3. Copy the authorization code it gives you.")
print("------------------------\n")

auth_code = input("Paste the authorization code here and hit Enter: ").strip()

try:
    oauth_result = auth_flow.finish(auth_code)
    print("\n SUCCESS! Here is your permanent Refresh Token:")
    print("--------------------------------------------------")
    print(oauth_result.refresh_token)
    print("--------------------------------------------------")
    print("Copy that exact string and put it in your dropbox_secrets.json file!")
except Exception as e:
    print('\n Error:', e)
