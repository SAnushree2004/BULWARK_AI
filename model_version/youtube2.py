from googleapiclient.discovery import build
from urllib.parse import urlparse
import requests
import re
from eval3 import EnhancedCyberbullyingDetector as CyberbullyingDetector, get_content_scores

youtube_api_key = 'AIzaSyBvEMeD7kwabK033VS3zT8ahEEY_JKjoBA'  # Replace with your YouTube API key
model_path = "cyberbullying_model.h5"
tokenizer_path = "cyberbullying_tokenizer.pickle"
model_info_path = "cyberbullying_model_info.pickle"



def wholefunction(YouTube_link):
  cyberbullying_detector = CyberbullyingDetector(model_path, tokenizer_path, model_info_path)

  # Function to get channel ID and latest video
  def get_channel_id_and_latest_video(channel_link, api_key):
      try:
          # Parse the provided URL
          parsed_url = urlparse(channel_link)
          path_segments = parsed_url.path.strip('/').split('/')
          youtube = build('youtube', 'v3', developerKey=api_key)

          # Determine if the URL is a standard or custom link
          if 'channel' in path_segments:
              channel_id = path_segments[path_segments.index('channel') + 1]
          else:
              # Extract channel name from custom URL
              if len(path_segments) >= 1:
                  channel_name = path_segments[-1]
              else:
                  raise ValueError("Channel name not found in the provided link.")

              # Use YouTube API to search for the channel by name
              search_request = youtube.search().list(
                  part="id",
                  q=channel_name,
                  type="channel",
                  maxResults=1
              )
              search_response = search_request.execute()

              if 'items' in search_response and len(search_response['items']) > 0:
                  channel_id = search_response['items'][0]['id']['channelId']
              else:
                  raise ValueError("No channel found with the provided name.")

          # Fetch the latest video from the channel
          request = youtube.search().list(
              part="id,snippet",
              channelId=channel_id,
              order="date",
              maxResults=1,
              type="video"
          )
          response = request.execute()

          if 'items' in response and len(response['items']) > 0:
              video_id = response['items'][0]['id']['videoId']
              # video_title = response['items'][0]['snippet']['title']
              return video_id
          else:
              return None

      except Exception as e:
          # print(f"An error occurred: {e}")
          return None

  # Function to fetch comments from YouTube and analyze them
  def get_comments_by_video_id(video_id, youtube_api_key):
      try:
          youtube = build('youtube', 'v3', developerKey=youtube_api_key)

          # Fetch comments for the video
          request = youtube.commentThreads().list(
              part="snippet",
              videoId=video_id,
              maxResults=100
          )
          response = request.execute()
          # print(response)

          # Extract comments
          comments = []
          
          if 'items' in response:
            for item in response['items']:
                snippet = item['snippet']['topLevelComment']['snippet']
                comment = snippet['textDisplay']
                author_name = snippet['authorDisplayName']  # Extract the display name of the commenter
                comments.append({ 'message': comment,'commenter': author_name})
                # print(comments)
          else:
              print("No comments found for the video.")
              return

          return comments

      except Exception as e:
          print("An error occurred:", e)

  def analyze_comment(comments, cyberbullying_detector):
      """
      Analyze comments using Perspective API and calculate toxicity scores.
      """
      comments_data = []
      total_score = 0  # To calculate overall average score
      total_comments = len(comments)
      
      for comment in comments:
        # Get the single score from our model
        scores = get_content_scores(comment['message'], cyberbullying_detector)
                
        # Create comment with just the bullying score
        comments_with_score = {
            'text': comment['message'],
            'user': comment['commenter'],
            'average_score': scores['average_score']
        }
                
        comments_data.append(comments_with_score)
        total_score += scores['average_score']

                    
        # Sort by bullying score (high to low)
        comments_data.sort(key=lambda x: x['average_score'], reverse=True)
        top_toxic_comments = comments_data[:3]


        # Calculate overall average score
        overall_average_score = total_score / total_comments if total_comments > 0 else 0

        username = extract_youtube_username(YouTube_link)
        result = {
        #   'comments_analysis': comments_data,
            'username' : username,
          'average_score': overall_average_score,
          'filtered_comments' : top_toxic_comments
        }
        
        print(result)
        return result

  def extract_youtube_username(url):
    # Regular expression to match YouTube username in the URL
    pattern = r'https?://www\.youtube\.com/@([a-zA-Z0-9_-]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

  latest_video = get_channel_id_and_latest_video(YouTube_link, youtube_api_key)
  print(latest_video)
  comments = get_comments_by_video_id(latest_video, youtube_api_key)
#   print(comments)
  result = analyze_comment(comments, cyberbullying_detector)
  
  return result

# # EXAMPLE USAGE
# YouTube_link = 'https://www.youtube.com/@LokeshBagora'
# x = wholefunction(YouTube_link)
# print(x)