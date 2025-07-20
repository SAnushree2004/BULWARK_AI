import requests
from eval3 import EnhancedCyberbullyingDetector as CyberbullyingDetector, get_content_scores


# access_token= "EAAToZCefBbW4BO0BLLgEQBA7pOJGrtKlvyZAYeU2Xirv0EsQLHjOMILMHkOZC1o3oDgRjYvFPgwgoss7Ib2AYf1QpjQBOUobAHYAZA1Bs5TlWnGGIYeLgVIXoJGKv53XZAPFjn6sjzbOX7xAYZCLUsXhUcSL70oXZCMiFGv4CbsAAZAhRoMrwnpjm3rXE6HdV5jy"
model_path = "cyberbullying_model.h5"
tokenizer_path = "cyberbullying_tokenizer.pickle"
model_info_path = "cyberbullying_model_info.pickle"

def wholefunction(access_token):
  cyberbullying_detector = CyberbullyingDetector(model_path, tokenizer_path, model_info_path)

    # access_token= "EAAToZCefBbW4BO0BLLgEQBA7pOJGrtKlvyZAYeU2Xirv0EsQLHjOMILMHkOZC1o3oDgRjYvFPgwgoss7Ib2AYf1QpjQBOUobAHYAZA1Bs5TlWnGGIYeLgVIXoJGKv53XZAPFjn6sjzbOX7xAYZCLUsXhUcSL70oXZCMiFGv4CbsAAZAhRoMrwnpjm3rXE6HdV5jy"

  # Function to get Facebook Page ID
  def get_facebook_page_id(access_token):
      url = f"https://graph.facebook.com/v16.0/me/accounts?access_token={access_token}"
      response = requests.get(url)

      if response.status_code == 200:
          data = response.json()
          pages = data.get("data", [])
          if pages:
              for page in pages:
                  return page.get("id")  # Return the first page ID found
          else:
              return None
      else:
          print("Error:", response.status_code, response.json())
          return None

  # Function to get Instagram Business Account ID
  def get_instagram_business_account(page_id, access_token):
      url = f"https://graph.facebook.com/v16.0/{page_id}"
      params = {
          "fields": "instagram_business_account",
          "access_token": access_token
      }
      response = requests.get(url, params=params)

      if response.status_code == 200:
          data = response.json()
          if 'instagram_business_account' in data:
              instagram_account_id = data['instagram_business_account']['id']
              return instagram_account_id
          else:
              return None
      else:
          return None

  # Function to get Instagram username by Instagram Business Account ID
  def get_instagram_username(instagram_business_id, access_token):
      url = f"https://graph.facebook.com/v16.0/{instagram_business_id}"
      params = {
          "fields": "username",
          "access_token": access_token
      }
      response = requests.get(url, params=params)

      if response.status_code == 200:
          data = response.json()
          return data.get("username")
      else:
          print("Error fetching Instagram username:", response.status_code, response.json())
          return None

  # Function to get the latest media from the Instagram Business Account
  def get_latest_media(instagram_business_id, access_token):
      url = f"https://graph.facebook.com/v16.0/{instagram_business_id}/media"
      params = {
          "fields": "id,caption,timestamp",
          "access_token": access_token,
          "limit": 1  # Restrict the response to only the latest post
      }
      response = requests.get(url, params=params)
      # return response.json().get("data", [])
      data = response.json().get("data", [])
      return data[0]['id'] if data else None  # Extract the ID of the latest post or return None

  # Function to fetch comments with pagination from Instagram
  def get_comments_with_pagination(media_id, access_token):
      comments = []
      url = f"https://graph.facebook.com/v16.0/{media_id}/comments"
      params = {
          "fields": "id,text,timestamp,username",
          "access_token": access_token
      }

      while url:
          response = requests.get(url, params=params)

          if response.status_code != 200:
              print(f"Error: {response.status_code}, Response: {response.text}")
              break

          data = response.json()
          # print(data)

          if 'data' not in data or len(data['data']) == 0:
              print(f"No comments for Post ID: {media_id}")

          comments.extend(data.get("data", []))

          url = data.get("paging", {}).get("next", None)

          # print(comments)

          extracted_comments = [{'message': comment['text'], 'commenter': comment['username']} for comment in comments]

      return extracted_comments

#   # Function to analyze the overall comment section with Perspective API
#   def process_response(user, text, response_json, error_message, total_score, comments_data):
#     """
#     Process the response to extract attribute scores, calculate average, and update results.
#     """
#     try:
#         attribute_scores = {
#             attribute: attribute_data['summaryScore']['value']
#             for attribute, attribute_data in response_json.get('attributeScores', {}).items()
#         }

#         # Calculate average score for this comment
#         average_score = sum(attribute_scores.values()) / len(attribute_scores) if attribute_scores else 0
#         total_score += average_score  # Add to total for overall average

#         # Find the highest scoring attribute
#         highest_attr = max(attribute_scores, key=attribute_scores.get) if attribute_scores else None


#         # Append analyzed data to the results
#         comments_data.append({
#             'user': user,
#             'text': text,
#             'highest_attribute': highest_attr,
#             # 'attribute_scores': attribute_scores,  # Uncomment if needed
#             'average_score': average_score,
#             # 'error_message': error_message  # Include error info if any
#         })
#     except Exception as e:
#         # Handle unexpected issues during processing
#         comments_data.append({
#             'user': user,
#             'text': text,
#             'average_score': 0,
#             'error_message': f"Processing error: {str(e)}"
#         })

#     return total_score

  def analyze_comment(comments, cyberbullying_detector):

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

        username = instagram_username
        result = {
        #   'comments_analysis': comments_data,
            'username' : 'username',
          'average_score': overall_average_score,
          'filtered_comments' : top_toxic_comments
        }
        
        print(result)
        return result

#   # Function to filter comments based on average score threshold
#   def filter_cyberbullying_comments(comments_data, average_score_threshold=0.1):
#       filtered_comments = []
#       # Process only "comments_analysis" part
#       for comment_data in comments_data['comments_analysis']:
#           text = comment_data['text']
#           user = comment_data['user']
#           average_score = comment_data['average_score']
#           highest_attribute = comment_data['highest_attribute']

#           # Check against average_score threshold
#           if average_score > average_score_threshold:
#               filtered_comments.append({
#                   'text': text,
#                   'user': user,
#                   'highest_attribute': highest_attribute,
#                   'average_score': average_score,
#                   # 'attribute_scores': comment_data['attribute_scores']
#               })
#       # Sort the filtered comments by average_score in descending order
#       filtered_comments.sort(key=lambda x: x['average_score'], reverse=True)

#       # Return the top 5 comments
#       return filtered_comments[:5]

  page_id = get_facebook_page_id(access_token)
  # print(page_id)
  instagram_business_id = get_instagram_business_account(page_id, access_token)
  # print(instagram_business_id)
  instagram_username = get_instagram_username(instagram_business_id, access_token)
  # print(instagram_username)
  media_id = get_latest_media(instagram_business_id, access_token)
  # print(media_id)
  comments = get_comments_with_pagination(media_id, access_token)
  print(comments)
  result = analyze_comment(comments,cyberbullying_detector)
#   average_score = result['overall_average_score']
#   username = instagram_username
#   filtered_comments = filter_cyberbullying_comments(result)
#   final_dict = {
#       'username': username,
#       'average_score': average_score,
#       'filtered_comments': filtered_comments
#   }

  return result

# # EXAMPLE USAGE
#   25/3/25
# access_token = "EAAToZCefBbW4BO1G0zsUBZCNi6GGNzfOCYJC0ki5FjttKgCX7LZA4O0GSDaMF0AmGZB1dVthDgrcQmhZC7qlLOXYEl5ZCVKu3eZAHDNC87K91cKZCZCTia8lhpK1u2yBAlR4m7CZBPfZCIIoZAqrY79U2BRKoNgerEZA9GktXQ6121VCzgG9UHXSNTt0DNAbY353bJAnZC"
# x = wholefunction(access_token)
# print(x)