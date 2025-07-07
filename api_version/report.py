from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
import base64
from io import BytesIO
from PIL import Image
import os
from datetime import datetime
from fpdf import FPDF
import re 


def create_platform_report(platform_name, comments_data, dataurl):

    def dataurl_to_image(dataurl, output_image_path):
        # Remove the prefix "data:image/png;base64," or similar
        header, encoded = dataurl.split(",", 1)

        # Decode the base64 string
        image_data = base64.b64decode(encoded)

        # Convert binary data to an image
        image = Image.open(BytesIO(image_data))

        # Save the image to the specified output path
        image.save(output_image_path)
        return output_image_path

    def get_severity_level(decimal_score):
        # Convert decimal score to percentage first
        percentage = round(decimal_score * 100)
        
        if percentage <= 33:
            return "Low", percentage
        elif percentage <= 67:
            return "Medium", percentage
        else:
            return "High", percentage

    def get_severity_description(severity, username):
        descriptions = {
            "Low": f"""
            Analysis of the {platform_name} account '{username}' shows a low level of concerning activity.
            While some comments have been flagged, the overall toxicity level is minimal.
            Continued monitoring is recommended, but immediate action may not be necessary.
            Regular community guideline reminders could help maintain this positive environment.
            """,
            
            "Medium": f"""
            The {platform_name} account '{username}' shows a moderate level of concerning activity.
            A significant number of comments have been flagged for potentially harmful content.
            Increased monitoring and targeted moderation is recommended.
            Implementation of additional comment filtering and user guidelines should be considered.
            """,
            
            "High": f"""
            Urgent attention is required for the {platform_name} account '{username}'.
            Analysis reveals a high concentration of toxic and harmful comments.
            Immediate intervention and strict moderation measures are strongly recommended.
            Consider temporary comment restrictions and reviewing current moderation policies.
            """
        }
        return descriptions[severity]

    def create_report(platform_name, comments_data, dataURL):
        username = comments_data['username']
        decimal_score = comments_data['average_score']
        severity_level, score_percentage = get_severity_level(decimal_score)
        filtered_comments = comments_data['filtered_comments']

        # Generate PDF filename
        pdf_filename = f"{platform_name}_cyberbullying_complaint_report.pdf"
        output_dir = "reports"
        os.makedirs(output_dir, exist_ok=True)
        pdf_path = os.path.join(output_dir, pdf_filename)

        # Create PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)

        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(235, 770, f"Platform Based Report ({platform_name.capitalize()})")

        # Insert gauge image
        output_image_path = os.path.join(output_dir, "output_image.png")
        image_path = dataurl_to_image(dataurl, output_image_path)
        c.drawImage(image_path, 30, 520, width=400, height=200)

        # Severity Level
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, 500, f"Severity Level: {severity_level} ({score_percentage}%)")

        # Suspected Comments Section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, 450, "Suspected Comments and Users:")

        y_position = 420

        # Display comments
        for comment_data in filtered_comments:
            if y_position < 100:  # If we're running out of space
                c.showPage()  # Start a new page
                y_position = 750  # Reset position for new page
            c.setFont("Helvetica", 10)
            c.drawString(30, y_position, f"Comment: {comment_data['text']}")
            c.drawString(30, y_position - 15, f"User: {comment_data['user']}")
            y_position -= 40

        # Now add Incident Description above Summary
        c.setFont("Helvetica-Bold", 12)
        y_position -= 20  # Add some space before incident description
        c.drawString(30, y_position, "Incident Description:")

        # Get and format the severity-based description
        incident_text = get_severity_description(severity_level, username)

        # Create paragraph with the description
        styles = getSampleStyleSheet()
        paragraph = Paragraph(incident_text, styles["Normal"])
        paragraph.wrapOn(c, 500, 100)  # Adjust wrap height
        paragraph.drawOn(c, 30, y_position - 80)  # Position description below its heading

        # Summary at the bottom
        y_position -= 100  # Adjust position after incident description
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Summary:")

        c.setFont("Helvetica", 10)
        c.drawString(30, y_position - 20, f"Total Suspected Users: {len(filtered_comments)}")
        c.drawString(30, y_position - 40, f"Overall Toxicity Level: {score_percentage}%")

        c.save()
        return pdf_path

    return create_report(platform_name, comments_data, dataurl)

def complaint_report(name, email, facebook_data, instagram_data, youtube_data, twitter_data):

  username = name
  # Generate PDF Report
  pdf = FPDF()
  pdf.set_auto_page_break(auto=True, margin=15)
  pdf.add_page()
  pdf.set_font("Arial", size=12)

  # From Information
  pdf.cell(0, 10, txt=f"From: {username}", ln=True)
  pdf.cell(0, 10, txt=f"{email}", ln=True)
  pdf.cell(0, 10, txt="Subject: Cyberbullying Complaint Report", ln=True)

  pdf.cell(0, 8, txt="", ln=True)
  pdf.cell(0, 6, txt="Respected Sir/Madam,", ln=True)

  incident_description = f"""
  I am {username}, a social media influencer. I am filing a complaint related to the offensive comments I encountered on social media platforms Instagram, YouTube, Facebook, and Twitter. The comments were analyzed and the report was generated using the Bulwark AI website. I kindly request you to consider the complaint and take necessary action.
  """
  pdf.multi_cell(0, 8, txt=incident_description)
  pdf.cell(0, 5, txt="", ln=True)

  # Generate Table Header
  def generate_table_header():
      pdf.set_font("Arial", style="B", size=10)
      headers = ["Platform", "Detected Comment", "Suspected User", "Context"]
      col_widths = [30, 85, 45, 30]
      for i, header in enumerate(headers):
          pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
      pdf.ln()

  # Add table data
  def add_table_data(data, platform_name):
      pdf.set_font("Arial", size=10)
      col_widths = [30, 85, 45, 30]
      print(data)
      for comment in data['filtered_comments']:
          pdf.cell(col_widths[0], 10, platform_name, 1)
          clean_text = re.sub(r'[^\x00-\x7F]+', '', comment['text'])
          pdf.cell(col_widths[1], 10, clean_text[:45] + ("..." if len(clean_text) > 45 else ""), 1)
          pdf.cell(col_widths[2], 10, comment['user'], 1)
          pdf.cell(col_widths[3], 10, comment['highest_attribute'], 1)
          pdf.ln()

  # Generate tables
  pdf.cell(0, 10, txt="Details of Detected Comments:", ln=True)
  generate_table_header()
  add_table_data(facebook_data, "Facebook")
  add_table_data(instagram_data, "Instagram")
  add_table_data(youtube_data, "YouTube")
  add_table_data(twitter_data, "Twitter")

  # Closing Statement
  closing_statement = """
  I kindly request immediate action to investigate and address this issue at the earliest.
  Thank you for your attention and understanding in this matter.
  """
  pdf.multi_cell(0, 5, txt=closing_statement)
  pdf.cell(0, 7, txt="", ln=True)
  pdf.cell(0, 7, txt="Yours sincerely,", ln=True)
  pdf.cell(0, 7, txt=f"{username}", ln=True)
  pdf.cell(0, 7, txt=f"Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)

   # Save the PDF
  pdf_filename = "Cyberbullying_Complaint_Report.pdf"  # Predefined filename
  pdf.output(pdf_filename)

  print(os.path.abspath(pdf_filename))
  return pdf_filename

# EXAMPLE USAGE

# name = "hgh"
# email = "jhjg"
# youtube_data = {'username': 'LokeshBagora', 'average_score': 0.0111912333, 'filtered_comments': [{'text': 'No one slot is there sir', 'user': '@rajapreethirangam783', 'average_score': 0.01723873775, 'highest_attribute': 'TOXICITY'}, {'text': 'showing slot not available', 'user': '@anisingh0884', 'average_score': 0.01471441825, 'highest_attribute': 'TOXICITY'}, {'text': 'Exam center only on hyderabad 😢', 'user': '@yathirajan8088', 'average_score': 0.013101024875000002, 'highest_attribute': 'TOXICITY'}, {'text': 'Can bsc students apply', 'user': '@heysravs6109', 'average_score': 0.011350674299999999, 'highest_attribute': 'TOXICITY'}, {'text': 'Where should we keep resume?', 'user': '@srividyaguttula', 'average_score': 0.010742544625000001, 'highest_attribute': 'TOXICITY'}]}
# instagram_data = {'username': 'xnz004', 'average_score': 0.23541751820312498, 'filtered_comments': [{'text': 'What rubbish are you doing', 'user': 'akshaya_p.u', 'highest_attribute': 'TOXICITY', 'average_score': 0.44853682725}, {'text': 'Its very rubbish', 'user': '_zain_u93', 'highest_attribute': 'TOXICITY', 'average_score': 0.3690182545}, {'text': 'Negatively rubbish', 'user': '_zain_u93', 'highest_attribute': 'TOXICITY', 'average_score': 0.361712646}, {'text': 'You are wrong. It is foolishness', 'user': 'moose.3018942', 'highest_attribute': 'INSULT', 'average_score': 0.306176924875}, {'text': 'What an ugly flower, very irritating 😠', 'user': 'goat.3251806', 'highest_attribute': 'TOXICITY', 'average_score': 0.28241263125}]}
# facebook_data = {'username': 'Theertha Fans Kothakurissi', 'average_score': 0.3098054562, 'filtered_comments': [{'text': 'I will kill you', 'user': 'Anonymous', 'average_score': 0.63346093, 'highest_attribute': 'TOXICITY'}, {'text': 'Go away idiot, stupid, nonsense', 'user': 'Anonymous', 'average_score': 0.609404315, 'highest_attribute': 'TOXICITY'}, {'text': 'You are an idiot', 'user': 'Anonymous', 'average_score': 0.598019061, 'highest_attribute': 'TOXICITY'}, {'text': 'go away stupid', 'user': 'Anonymous', 'average_score': 0.56362652275, 'highest_attribute': 'TOXICITY'}, {'text': 'Ugly', 'user': 'Anonymous', 'average_score': 0.324963938, 'highest_attribute': 'TOXICITY'}]}
# twitter_data = {'username': 'Theertha Fans Kothakurissi', 'average_score': 0.3098054562, 'filtered_comments': [{'text': 'I will kill you', 'user': 'Anonymous', 'average_score': 0.63346093, 'highest_attribute': 'TOXICITY'}, {'text': 'Go away idiot, stupid, nonsense', 'user': 'Anonymous', 'average_score': 0.609404315, 'highest_attribute': 'TOXICITY'}, {'text': 'You are an idiot', 'user': 'Anonymous', 'average_score': 0.598019061, 'highest_attribute': 'TOXICITY'}, {'text': 'go away stupid', 'user': 'Anonymous', 'average_score': 0.56362652275, 'highest_attribute': 'TOXICITY'}, {'text': 'Ugly', 'user': 'Anonymous', 'average_score': 0.324963938, 'highest_attribute': 'TOXICITY'}]}

# x = complaint_report(name, email, facebook_data, instagram_data, youtube_data, twitter_data)
# print(x)