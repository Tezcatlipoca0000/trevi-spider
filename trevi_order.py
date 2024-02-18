"""
Download the order placed to comercial treviño 
"""
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
	"https://www.googleapis.com/auth/gmail.readonly"
]

def get_order():
	# Get gmail authorization
	creds = None
	if os.path.exists("token.json"):
		creds = Credentials.from_authorized_user_file("token.json", SCOPES)
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
			creds = flow.run_local_server(port=0)
		with open("token.json", "w") as token:
			token.write(creds.to_json()) 
	try:
		# Build
		service = build("gmail", "v1", credentials=creds)
		# Get correct message id
		result = service.users().messages().list(
			userId="me",
			labelIds=["INBOX"],
			q="filename:pedido.xlsx",
			maxResults=1
		).execute()
		messages = result.get("messages", [])
		msg_id = messages[0]["id"]
		# Get correct message
		message = service.users().messages().get(
			userId="me",
			id=msg_id
		).execute()
		# Export attachment
		for part in message["payload"]["parts"]:
			if part["filename"]:
				if "data" in part["body"]:
					data = part["body"]["data"]
				else:
					att_id = part["body"]["attachmentId"]
					att = service.users().messages().attachments().get(
						userId="me",
						messageId=msg_id,
						id=att_id
					).execute()
					data = att["data"]
					file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
					path = part["filename"]
				with open(path, "wb") as f:
					f.write(file_data)
		print("pedido.xlsx fue descargado correctamente")
	# Error catching
	except HttpError as error:
		print(f"An error occured: {error}")

if __name__ == "__main__":
	get_order()