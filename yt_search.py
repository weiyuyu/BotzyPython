from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser


# Set DEVELOPER_KEY to the API key value 
DEVELOPER_KEY = "AIzaSyDp29Ou9donbgn_N0hnzeELpuP641qAKLc"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(title):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=title,
    maxResults=5
  ).execute()

  videos_id = []
  videos_title = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videos_id.append(search_result["id"]["videoId"])
      videos_title.append(search_result["snippet"]["title"])
  
  return videos_id[], videos_title