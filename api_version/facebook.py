import requests
import emoji

# Replace with your User Access Token
# user_access_token = 'EAAHsz7eRJyIBOwbpzj1AFcnepX3E41jS5IuqS62oRNKTSBiyj47jLdjDv3S8ZAZBwfNOYcdIn4hjZBHHqRuYfmhRWZBG7TYCjiISoYsifj9V1Efbn9ZCtDsCBrVrM6ZCcohr5r5lc44Qt4CQk48ZA42DsGpBDwOTJiJ5d80AfxB9ZCxZAaBRZCbki7ddSP'
perspective_api_key = 'AIzaSyB_t-5i3lsDNlY6W93SADVddDClTEeizB0'  # Replace with your Perspective API key

def wholefunction(user_access_token):

  # Function to extract page_id and page_access_token from user_access_token
  def extract_page_info(user_access_token):
      url = f'https://graph.facebook.com/v17.0/me/accounts?access_token={user_access_token}'
      response = requests.get(url)
      if response.status_code == 200:
          data = response.json()
          pages = data.get('data', [])
          if pages:
              page_access_token = pages[0].get('access_token')  # Use this token
              page_id = pages[0].get('id')
              page_name = pages[0].get('name')
              return page_access_token, page_id, page_name
          else:
              # print("No pages found.")
              return None, None
      else:
          # print(f"Error: {response.status_code} - {response.text}")
          return None, None

  # Function to extract latest post_id
  def extract_latest_post_id(access_token, page_id):
      url = f"https://graph.facebook.com/v16.0/{page_id}/posts?access_token={access_token}"
      response = requests.get(url)
      if response.status_code == 200:
          data = response.json()
          posts = data.get("data", [])
          if posts:
              latest_post_id = posts[0].get("id")
              return latest_post_id
          else:
              print("No posts found for this page.")
              return None
      else:
          # print(f"Error: {response.status_code} - {response.text}")
          return None

  # Function to fetch comments for a given post
  def fetch_comments(post_id, access_token):
      url = f"https://graph.facebook.com/v16.0/{post_id}/comments?fields=from,message,created_time&access_token={access_token}"
      response = requests.get(url)
      if response.status_code == 200:
          data = response.json()
          comments = data.get("data", [])
          # print(comments)
          if comments:

            extracted_comments = [
                {
                  'message': comment.get('message', ''),
                  'commenter': comment.get('from', {}).get('name', 'Anonymous')
                }
                for comment in comments if 'message' in comment
            ]
            # print(extracted_comments)
            return extracted_comments
              # return [comment.get('message', '') for comment in comments if 'message' in comment]
          else:
              # print("No comments found.")
              return []
      else:
          # print(f"Error: {response.status_code} - {response.text}")
          return []


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
            'average_score': 0,
            'error_message': f"Processing error: {str(e)}"
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
          text = comment['message']
          user = comment['commenter']

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
              # print(raw_text)
              converted_text = emoji.demojize(raw_text)
              # print(converted_text)
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
  def filter_cyberbullying_comments(comments_data, average_score_threshold=0.1):
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

      # Return the top 5 comments
      return filtered_comments[:5]

  page_access_token, page_id, page_name = extract_page_info(user_access_token)
  post_id = extract_latest_post_id(page_access_token, page_id)
  comments = fetch_comments(post_id, page_access_token)
  result = analyze_comment_section_with_perspective(comments, perspective_api_key)
  average_score = result['overall_average_score']
  username = page_name
  filtered_comments = filter_cyberbullying_comments(result)
  final_dict = {
      'username': username,
      'average_score': average_score,
      'filtered_comments': filtered_comments
  }

  return final_dict

#   25/3/25
# user_access_token = "EAAHsz7eRJyIBO25VRyvuMZA6bWIOf2cTg4DzGIJ1MDUEiEdoZB7BJZAUXUe8grcZAZAEZBoH9WmrC6TsiZBWT1ZBCfjw6aIkxlGx0dsMBg0NhdpriPbdLiCLOrl9yvVKuG24rdvLJS7k0AxIuHZCOCEKTAqZAPN9hSEVmY4UH33bFYj3euZCRNs3lATy3U5"
# x = wholefunction(user_access_token)
# print(x)