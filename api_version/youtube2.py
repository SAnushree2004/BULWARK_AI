from googleapiclient.discovery import build
from urllib.parse import urlparse
import requests
import emoji
import re

youtube_api_key = 'AIzaSyBvEMeD7kwabK033VS3zT8ahEEY_JKjoBA'  # Replace with your YouTube API key
perspective_api_key = 'AIzaSyB_t-5i3lsDNlY6W93SADVddDClTEeizB0'  # Replace with your Perspective API key
# YouTube_link = 'https://www.youtube.com/@LokeshBagora'  # Replace with your desired channel URL



def wholefunction(YouTube_link):
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
          # if 'items' in response:
          #     for item in response['items']:
          #         comment = item['snippet']['topLevelComment']['snippet']['textDisplay']['authorDisplayName']
          #         comments.append(comment)
          #         print(comments)

          if 'items' in response:
            for item in response['items']:
                snippet = item['snippet']['topLevelComment']['snippet']
                comment = snippet['textDisplay']
                author_name = snippet['authorDisplayName']  # Extract the display name of the commenter
                comments.append({ 'Message': comment,'Commenter': author_name})
                # print(comments)

                # for comment_info in comments:
                #   print(f"Author: {comment_info['author']}, Comment: {comment_info['comment']}")

          else:
              print("No comments found for the video.")
              return

          return comments

      except Exception as e:
          print("An error occurred:", e)


  def process_response(user, text, response_json, error_message, total_score, comments_data):
      """
      Process the response to extract attribute scores, calculate average, and update results.
      """
      try:
          attribute_scores = {
              attribute: attribute_data['summaryScore']['value']
              for attribute, attribute_data in response_json.get('attributeScores', {}).items()
          }

          # Calculate average score for this comment
          average_score = sum(attribute_scores.values()) / len(attribute_scores) if attribute_scores else 0
          total_score += average_score  # Add to total for overall average

          # Find the highest scoring attribute
          highest_attr = max(attribute_scores, key=attribute_scores.get) if attribute_scores else None

          # Append analyzed data to the results
          comments_data.append({
              'user': user,
              'text': text,
              'highest_attribute': highest_attr,
              # 'attribute_scores': attribute_scores,  # Uncomment if needed
              'average_score': average_score,
              # 'error_message': error_message  # Include error info if any
          })
      except Exception as e:
          # Handle unexpected issues during processing
          comments_data.append({
              'user': user,
              'text': text,
              'average_score': 0
            #   'error_message': f"Processing error: {str(e)}"
          })

      return total_score


  def analyze_comment_section_with_perspective(comments, perspective_api_key):
      """
      Analyze comments using Perspective API and calculate toxicity scores.
      """
      comments_data = []
      total_score = 0  # To calculate overall average score
      total_comments = len(comments)

      for comment in comments:
          text = comment['Message']
          user = comment['Commenter']

          url = f"https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={perspective_api_key}"
          analyze_request = {
              'comment': {'text': text},
              'requestedAttributes': {
                  'TOXICITY': {},
                  'INSULT': {},
                  'PROFANITY': {},
                  'THREAT': {}
              }
          }

          response = requests.post(url, json=analyze_request)
          # print(response)

          if response.status_code == 200:
              # Successful response
              data = response.json()
              total_score = process_response(user, text, data, None, total_score, comments_data)

          elif response.status_code == 400:
              # Handle client error (e.g., bad request)
              # print(f"Error analyzing comment from {user}: {response.status_code}")

              # Convert emojis in the response text to descriptive text
              raw_text = response.text
            #   print(raw_text)
              converted_text = emoji.demojize(raw_text)
            #   print(converted_text)
              try:
                  data = response.json()
              except ValueError:
                  data = {}

              # Process with available data and error message
              total_score = process_response(user, text, data, converted_text, total_score, comments_data)

          else:
              # Handle other unexpected errors
              # print(f"Unexpected error analyzing comment from {user}: {response.status_code}")
              # print(response.text)
              comments_data.append({
                  'user': user,
                  'text': text,
                  'average_score': 0,
                  # 'error_message': f"Unexpected error: {response.status_code} - {response.text}"
              })

      # Calculate overall average score
      overall_average_score = total_score / total_comments if total_comments > 0 else 0

      return {
          'comments_analysis': comments_data,
          'overall_average_score': overall_average_score
      }

  # Function to filter comments based on average score threshold
  def filter_cyberbullying_comments(comments_data, average_score_threshold=0.01):
      filtered_comments = []
      # Process only "comments_analysis" part
      for comment_data in comments_data['comments_analysis']:
          text = comment_data['text']
          user = comment_data['user']
          average_score = comment_data['average_score']
          highest_attribute = comment_data['highest_attribute']

          # Check against average_score threshold
          if average_score > average_score_threshold:
              filtered_comments.append({
                  'text': text,
                  'user': user,
                  'average_score': average_score,
                  'highest_attribute': highest_attribute
                  # 'attribute_scores': comment_data['attribute_scores']
              })
      # Sort the filtered comments by average_score in descending order
      filtered_comments.sort(key=lambda x: x['average_score'], reverse=True)

      filtered_comments = filtered_comments[:5]

      if len(filtered_comments) == 0:
        filtered_comments = [{'text': 'No comments', 'user': 'No one', 'average_score':0}]

      # Return the top 5 comments
      return filtered_comments

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
  result = analyze_comment_section_with_perspective(comments, perspective_api_key)
  # print(result)
  average_score = result['overall_average_score']
  username = extract_youtube_username(YouTube_link)
  filtered_comments = filter_cyberbullying_comments(result)
  final_dict = {
      'username': username,
      'average_score': average_score,
      'filtered_comments': filtered_comments
  }
#   print(final_dict)
  return final_dict

# # EXAMPLE USAGE
# x = wholefunction(YouTube_link)
# print(x)