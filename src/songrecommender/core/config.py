import os
from dotenv import load_dotenv
import tekore as tk

load_dotenv() 

client_id = "35d1b955706e49e1840dc314a179780a"
client_secret = "ad3d52b0129443ce98cbfcd294288874"

print("✅ client_id:", client_id)
print("✅ client_secret:", "OK" if client_secret else "❌ NO SETEADO")

cred = tk.Credentials(client_id, client_secret)
token = cred.request_client_token()
spotify = tk.Spotify(token)