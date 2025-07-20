from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import urlparse
# from integration_code import CyberbullyingDetector, get_content_scores
from eval3 import EnhancedCyberbullyingDetector as CyberbullyingDetector, get_content_scores

def wholefunction(url):
    def username_extraction(url):
        # Parse the URL
        parsed_url = urlparse(url)
        # Extract the username (last part of the path)
        username = parsed_url.path.strip("/")
        return username

    def setup_driver():
        """Initialize Chrome driver with headless configuration"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enable headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def wait_and_find_element(driver, by, value, timeout=20):
        """Wait for and find an element with better error handling"""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            print(f"Failed to find element: {value}")
            return None

    def get_unique_identifier(comment):
        """Generate a unique identifier for a comment based on text and username"""
        try:
            text = comment.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']").text
            username_element = comment.find_element(By.CSS_SELECTOR, "[data-testid='User-Name']")
            username = username_element.text.split('\n')[1] if len(username_element.text.split('\n')) > 1 else "Unknown"
            return f"{username}_{text}"
        except Exception:
            return None

    def get_comment_data(comment):
        """Extract data from a comment"""
        try:
            text_element = comment.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']")
            username_element = comment.find_element(By.CSS_SELECTOR, "[data-testid='User-Name']")
            
            # Get username (handle) from the username element
            name_parts = username_element.text.split('\n')
            username = name_parts[1] if len(name_parts) > 1 else "Unknown"
            
            return {
                'text': text_element.text if text_element else "",
                'user': username.replace("@", "")  # Remove @ symbol from username
            }
        except Exception:
            return None

    def collect_comments_from_post(driver, processed_comments):
        """Collect up to 5 unique comments from a single post"""
        post_comments = []
        attempts = 0
        max_attempts = 3
        
        while len(post_comments) < 5 and attempts < max_attempts:
            comments = driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")[1:7]  # Skip the main post, get up to 6 comments
            
            for comment in comments:
                identifier = get_unique_identifier(comment)
                if identifier and identifier not in processed_comments:
                    comment_data = get_comment_data(comment)
                    if comment_data and comment_data['text']:
                        post_comments.append(comment_data)
                        processed_comments.add(identifier)
                        if len(post_comments) >= 5:
                            break
            
            if len(post_comments) < 5:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                attempts += 1
        
        return post_comments

    def collect_comments(driver, max_posts=5):
        """Collect up to 5 comments from each of the 5 most recent posts"""
        all_comments = []
        processed_comments = set()  # Track unique comments
        posts_processed = 0
        
        try:
            while posts_processed < max_posts:
                # Find all posts currently visible
                posts = driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
                if posts_processed >= len(posts):
                    print(f"\nNo more posts available. Processed {posts_processed} posts.")
                    break
                    
                try:
                    # Click on the post timestamp to view comments
                    time_element = posts[posts_processed].find_element(By.TAG_NAME, "time")
                    driver.execute_script("arguments[0].click();", time_element)
                    time.sleep(3)
                    
                    # Collect comments from this post
                    post_comments = collect_comments_from_post(driver, processed_comments)
                    all_comments.extend(post_comments)
                    print(f"\rCollected {len(post_comments)} comments from post {posts_processed + 1}", end="")
                    
                    driver.back()
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"\nError processing post {posts_processed + 1}: {str(e)}")
                
                posts_processed += 1
                
            print(f"\nCollected total of {len(all_comments)} unique comments from {posts_processed} posts")
            return all_comments
                    
        except Exception as e:
            print(f"\nError collecting comments: {str(e)}")
            return all_comments

    def main():
        print("Starting analysis...")
        driver = setup_driver()
        wait = WebDriverWait(driver, 20)
        target_username = username_extraction(url)
        twitter_username = "Tabcdhefgh"
        twitter_email = "theerthass67@gmail.com"
        twitter_password = "theertha1234321"
        
        # Initialize the cyberbullying detector
        model_path = "cyberbullying_model.h5"
        tokenizer_path = "cyberbullying_tokenizer.pickle"
        model_info_path = "cyberbullying_model_info.pickle"
            
        cyberbullying_detector = CyberbullyingDetector(model_path, tokenizer_path, model_info_path)

        try:
            print("Logging in to Twitter...")
            
            driver.get("https://twitter.com/i/flow/login")
            time.sleep(5)

            # Handle username field
            username_selectors = [
                "//input[@autocomplete='username']",
                "//input[@name='text']",
                "//input[@type='text']"
            ]

            username_field = None
            for selector in username_selectors:
                try:
                    username_field = wait_and_find_element(driver, By.XPATH, selector)
                    if username_field and username_field.is_displayed():
                        break
                except:
                    continue

            if not username_field:
                raise Exception("Could not find username field")

            # Enter username
            username_field.clear()
            time.sleep(1)
            username_field.send_keys(twitter_username)
            time.sleep(1)
            username_field.send_keys(Keys.RETURN)
            time.sleep(3)

            # Dynamically check for and handle email field if it appears
            try:
                # Check if an input field is visible after entering username
                email_selectors = [
                    "//input[@autocomplete='email']",
                    "//input[@name='text']",
                    "//input[@type='text']"
                ]
                
                email_field = None
                for selector in email_selectors:
                    try:
                        email_field = wait_and_find_element(driver, By.XPATH, selector, timeout=5)  # Shorter timeout for email field check
                        if email_field and email_field.is_displayed():
                            # Check if we're not already at the password screen
                            password_field = driver.find_elements(By.XPATH, "//input[@type='password']")
                            if not password_field or not any(field.is_displayed() for field in password_field):
                                break
                            else:
                                email_field = None  # Already at password screen, email not needed
                    except:
                        continue
                
                if email_field:
                    print("Email verification required. Entering email...")
                    email_field.clear()
                    time.sleep(1)
                    email_field.send_keys(twitter_email)
                    time.sleep(1)
                    email_field.send_keys(Keys.RETURN)
                    time.sleep(3)
                else:
                    print("Email verification not required. Proceeding to password...")
            except Exception as e:
                print(f"Email field handling failed: {str(e)}. Proceeding to password...")
                # Continue to password step regardless of failure here

            # Handle password field
            password_selectors = [
                "//input[@name='password']",
                "//input[@type='password']",
                "//input[@autocomplete='current-password']"
            ]

            password_field = None
            for selector in password_selectors:
                try:
                    password_field = wait_and_find_element(driver, By.XPATH, selector)
                    if password_field and password_field.is_displayed():
                        break
                except:
                    continue

            if not password_field:
                raise Exception("Could not find password field")

            # Enter password
            password_field.clear()
            time.sleep(1)
            password_field.send_keys(twitter_password)
            time.sleep(1)
            password_field.send_keys(Keys.RETURN)
            
            # Wait for login to complete
            time.sleep(5)
            print("Login successful!")

            print(f"Analyzing @{target_username}'s profile...")
            driver.get(f"https://twitter.com/{target_username}")
            time.sleep(3)

            comments = collect_comments(driver)
            if not comments:
                print("No comments were collected. Exiting...")
                return None

            print("Calculating content scores...")
            total_score_sum = 0
            comments_with_scores = []
            
            for comment in comments:
                # Get the single score from our model
                scores = get_content_scores(comment['text'], cyberbullying_detector)
                
                # Create comment with just the bullying score
                comment_with_score = {
                    'text': comment['text'],
                    'user': comment['user'],
                    'bullying_score': scores['average_score']
                }
                
                comments_with_scores.append(comment_with_score)
                total_score_sum += scores['average_score']

            average_total_score = total_score_sum / len(comments) if comments else 0
            
            # Sort by bullying score (high to low)
            comments_with_scores.sort(key=lambda x: x['bullying_score'], reverse=True)
            top_toxic_comments = comments_with_scores[:3]

            result = {
                'username': target_username,
                'average_score': average_total_score,
                'filtered_comments': top_toxic_comments
            }

            return result

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
        finally:
            driver.quit()

    result = main()
    return result

# EXAMPLE USAGE
# if __name__ == "__main__":
#     url = "https://x.com/Tabcdhefgh"
#     x = wholefunction(url)
#     print(x)