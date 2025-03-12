import os
import smtplib
import pandas as pd
from email.message import EmailMessage
import string

# Configuration
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
CSV_FILE = "contacts_test.csv"
TEMPLATE_FILE = "email_template.txt"

def load_template():
    """Loads email template from file."""
    try:
        with open(TEMPLATE_FILE, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Template file {TEMPLATE_FILE} not found!")
        return None

def preview_email(msg, formatted_body):
    """Displays email content and asks for confirmation."""
    print("\n" + "="*50)
    print("EMAIL PREVIEW:")
    print("="*50)
    print(f"To: {msg['To']}")
    print(f"Subject: {msg['Subject']}")
    print("-"*50)
    print(formatted_body)
    print("="*50)
    
    while True:
        response = input("\nSend this email? (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        print("Please enter 'yes' or 'no'")

def send_email(to_email, subject, **template_vars):
    """Sends an email using Gmail SMTP."""
    template = load_template()
    if template:
        try:
            formatted_body = template.format(**template_vars)
        except KeyError as e:
            print(f"Missing template variable: {e}")
            return
    else:
        print("Template file not found or empty")
        return

    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(formatted_body)

    # Add attachment handling
    try:
        with open('sheet_music.pdf', 'rb') as f:
            file_data = f.read()
            file_name = 'sheet_music.pdf'
        msg.add_attachment(file_data, maintype='application', 
                         subtype='octet-stream', 
                         filename=file_name)
    except FileNotFoundError:
        print(f"Warning: Attachment file not found")

    # Preview and confirm before sending
    if preview_email(msg, formatted_body):
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(GMAIL_USER, GMAIL_PASSWORD)
                server.send_message(msg)
            print(f"Email sent successfully to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
    else:
        print("Email sending cancelled")

def main():
    """Reads CSV and sends emails."""
    print("Sending emails...")
    try:
        df = pd.read_csv(CSV_FILE)
        for _, row in df.iterrows():
            template_vars = {
                'first_name': row.get('first_name', ''),
                'last_name': row.get('last_name', ''),
                'company': row.get('company', ''),
                'details': row.get('details', '')
            }
            send_email(row["email"], row["subject"], **template_vars)

    except Exception as e:
        print(f"Error reading CSV: {e}")

if __name__ == "__main__":
    main()
