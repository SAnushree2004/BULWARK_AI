import requests
from eval3 import EnhancedCyberbullyingDetector as CyberbullyingDetector, get_content_scores

# Replace with your User Access Token
# user_access_token = 'EAAHsz7eRJyIBOwbpzj1AFcnepX3E41jS5IuqS62oRNKTSBiyj47jLdjDv3S8ZAZBwfNOYcdIn4hjZBHHqRuYfmhRWZBG7TYCjiISoYsifj9V1Efbn9ZCtDsCBrVrM6ZCcohr5r5lc44Qt4CQk48ZA42DsGpBDwOTJiJ5d80AfxB9ZCxZAaBRZCbki7ddSP'
model_path = "cyberbullying_model.h5"
tokenizer_path = "cyberbullying_tokenizer.pickle"
model_info_path = "cyberbullying_model_info.pickle"

def wholefunction(user_access_token):

  cyberbullying_detector = CyberbullyingDetector(model_path, tokenizer_path, model_info_path)

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

          username = page_name
          result = {
        #   'comments_analysis': comments_data,
          'username' : username,
          'average_score': overall_average_score,
          'filtered_comments' : top_toxic_comments
          }
        
          print(result)

          return result

  page_access_token, page_id, page_name = extract_page_info(user_access_token)
  post_id = extract_latest_post_id(page_access_token, page_id)
  comments = fetch_comments(post_id, page_access_token)
  result = analyze_comment(comments, cyberbullying_detector)
  return result

#   25/3/25
# user_access_token = "EAAHsz7eRJyIBO25VRyvuMZA6bWIOf2cTg4DzGIJ1MDUEiEdoZB7BJZAUXUe8grcZAZAEZBoH9WmrC6TsiZBWT1ZBCfjw6aIkxlGx0dsMBg0NhdpriPbdLiCLOrl9yvVKuG24rdvLJS7k0AxIuHZCOCEKTAqZAPN9hSEVmY4UH33bFYj3euZCRNs3lATy3U5"
# x = wholefunction(user_access_token)
# print(x)