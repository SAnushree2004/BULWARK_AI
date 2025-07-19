# Bulwark AI 🚨🧠  
A Final Year Project to Fight Cyberbullying Across Social Media Platforms

## 🔍 Overview
**Bulwark AI** is a web application designed to detect and analyze toxic and offensive comments across social media platforms like Facebook, Instagram, YouTube, and X (formerly Twitter). It uses machine learning and natural language processing (NLP) to identify cyberbullying and generates comprehensive reports, including complaint-ready summaries for authorities.

## 🌐 Live Demo
👉 [https://bulwark-ai.onrender.com](https://bulwark-ai.onrender.com)

### 🔑 Sample Login

Use the following credentials to explore the app:

- **Email**: anjanam@gmail.com  
- **Password**: Anjana@1234

> Note: This is a sample test account for demo purposes only.

## 📌 Features
- 🔐 User-friendly interface with Sign Up/Login
- 🌐 Platform support: Facebook, Instagram, YouTube, and X
- 🧠 Toxicity detection using **Google Perspective API**
- 📊 Live toxicity score with a speedometer UI
- 📝 Platform-wise reports and consolidated complaint reports
- ☁️ Hosted on Render

## 🧠 Two Versions of Bulwark AI

We have developed **two versions** of Bulwark AI to explore both third-party tools and custom machine learning models:

1. **Perspective API Version** (Live on Render)  
   - Uses **Google’s Perspective API** to analyze the toxicity of comments.
   - Offers high accuracy, fast response time, and reliable results using Google’s pre-trained models.
   - Currently deployed at 👉 [https://bulwark-ai.onrender.com](https://bulwark-ai.onrender.com)

2. **Custom ML Model Version** (Offline/Experimental)  
   - Uses a machine learning model **trained by us** on a labeled dataset of social media comments.
   - Integrates preprocessing, vectorization (e.g., TF-IDF), and a classifier (like Logistic Regression or Random Forest).
   - Allows for offline processing and better control over model tuning and training.

> This dual approach helped us compare real-world APIs with custom-built solutions, giving us deeper insight into NLP and toxicity detection challenges.

## 🛠️ Tech Stack

| Frontend       | Backend         | APIs & Tools            | Deployment |
|----------------|------------------|--------------------------|------------|
| HTML, CSS, JS  | Python + Flask   | Google Perspective API   | Render     |
| Bootstrap      | Flask-Restful    | Facebook Graph API       |            |
| Chart.js       |                  | YouTube Data v3 API      |            |
|                |                  | (Twitter via scraping)   |            |

## 👩‍💻 Our Contributions

This project was built with strong teamwork and sleepless nights:

- **Frontend**: UI Design, Navigation, Speedometer display
- **Backend**:
  - YouTube & Facebook comment extraction
  - Flask integration & routing
  - Perspective API analysis logic
- **Deployment**: Flask app deployed using **Render**

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/bulwark-ai.git
   cd bulwark-ai

2. **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    
4. **Configure environment variables:**

    ## Get API keys for:
    - Google Perspective API
    - Facebook Graph API
    - YouTube Data API v3

    ## Create a .env file in the root directory and add your credentials:

    ```env
      PERSPECTIVE_API_KEY= "your_key_here"
      FACEBOOK_ACCESS_TOKEN= "your_key_here"
      YOUTUBE_API_KEY= "your_key_here"
   
5. **Run the Flask app:**
    
    ```bash
    python app.py
    
6. **🌐 Open in browser:**

      Once the server is running, open your browser and visit:
      
      👉 [http://localhost:5000](http://localhost:5000)
      

## 📄 Report Generation

- Generate a **platform-wise analysis report**
- Option to generate a **combined complaint report** for authorities

## 🎓 Academic Note

This project was developed as the **main project** for the final year B.Tech (Information Technology) program.  
It was driven by the desire to address the growing issue of cyberbullying through the power of AI.

## 📢 License

This project is for academic and demonstration purposes.  
Please contact the authors for permission before reusing or extending this code for commercial use.

---

**Let’s fight cyberbullying — one toxic comment at a time.** 🚫💬
