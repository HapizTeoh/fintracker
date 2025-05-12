import argparse
import email
import imaplib
import os
from email.header import decode_header
from email.utils import parsedate_to_datetime

IMAP_SERVER = "imap.gmail.com"

def download_email_data_from_gmail(email_account, email_password, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(email_account, email_password)
    mail.select("inbox")

    _, data = mail.search(None, "ALL")
    email_ids = data[0].split()

    print(f"Found {len(email_ids)} email(s)")

    for num in email_ids:
        print(f"Processing email ID: {num.decode('utf-8')} out of {len(email_ids)}")
        result, data = mail.fetch(num, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Parse the email date
        email_date_raw = msg["Date"]
        email_date = parsedate_to_datetime(email_date_raw)
        
        process_email(msg, email_date)

    mail.logout()

def process_email(msg, date):
    # Format date for filename: YYYY-MM-DD_HHMMSS
    date_str = date.strftime("%Y-%m-%d_%H%M%S")

    for part in msg.walk():
        # PayNow QR payments: If part is HTML and contains "payment" in the content, save it.
        if part.get_content_type() == "text/html":
            content = part.get_payload(decode=True)
            if "payment" not in content.decode("utf-8", errors="ignore").lower():
                continue
            filepath = os.path.join(output_dir, f"{date_str}.html")
            with open(filepath, 'wb') as f:
                f.write(content)
        # Apple Wallet screenshots: If part is an image, save it.
        elif part.get_content_maintype() == "image":
            filename = part.get_filename()
            decoded_name, encoding = decode_header(filename)[0]
            if isinstance(decoded_name, bytes):
                filename = decoded_name.decode(encoding or "utf-8")
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                ext = os.path.splitext(filename)[1]
                dated_filename = f"{date_str}{ext}"
                filepath = os.path.join(output_dir, dated_filename)
                content = part.get_payload(decode=True)
                with open(filepath, 'wb') as f:
                    f.write(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images and extract payment info from Gmail.")
    parser.add_argument("--email_address", required=True, help="Email account to log in to Gmail.")
    parser.add_argument("--email_password", required=True, help="Password for the email account.")
    parser.add_argument("--output_directory", required=True, help="Directory to save downloaded images or emails.")

    args = parser.parse_args()

    email_address = args.email_address
    email_password = args.email_password
    output_dir = args.output_directory

    download_email_data_from_gmail(email_address, email_password, output_dir)
