import argparse
import csv
from datetime import timedelta
import datetime
import os
from PIL import Image
import pytesseract
import re
import pandas as pd

def extract_qr_payment_info(html):
    # Date: any "DD Month 20YY" pattern
    date_match = re.search(r'\d{2} \w+ 20\d{2}', html)
    date = date_match.group(0) if date_match else None

    # Amount: e.g. SGD 8.00
    amount_match = re.search(r'SGD ([\d\.,]+)', html)
    amount = amount_match.group(1) if amount_match else None

    # Extract Merchant (try PayNow first, fallback to NETS)
    merchant_match = re.search(
        r'has been made to ([^<]+?) using', html) or \
        re.search(r'To</td><td> :</td><td>(.*?)</td>', html)

    merchant = merchant_match.group(1).strip() if merchant_match else None
    
    return {
        "date": datetime.datetime.strptime(date, "%d %B %Y").strftime("%Y-%m-%d") if date else None,
        "merchant": merchant,
        "amount": amount
    }

def extract_transactions(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    transactions = []

    i = 0
    while i < len(lines):
        merchant_match = re.match(r"(.+?)\s+\$([\d.,]+)", lines[i])
        if merchant_match:
            merchant = merchant_match.group(1).strip()
            amount = "$" + merchant_match.group(2).strip()
            # Look ahead for relative date (within next 2 lines)
            date = "Unknown"
            for j in range(1, 3):
                if i + j < len(lines):
                    if re.search(r"\b(yesterday|today|[a-z]+day|hours? ago|minutes? ago)\b", lines[i + j], re.I):
                        date = lines[i + j].strip()
                        break
            transactions.append({
                "date": date,
                "merchant": merchant,
                "amount": amount
                })
            i += 3  # Skip the block
        else:
            i += 1

    return transactions

def extract_text(image):
    grayscale = image.convert("L")
    binarized = grayscale.point(lambda x: 0 if x < 140 else 255, mode='1')
    config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(binarized, config=config)

def compute_absolute_date(date_str, screenshot_date):
    screenshot_date = datetime.datetime.strptime(screenshot_date[:10], "%Y-%m-%d")
    
    if date_str.lower() == "yesterday":
        return screenshot_date - timedelta(days=1)
    elif date_str.lower() in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        # Get the day of week for the current date
        target_day = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(date_str.lower())
        current_day = screenshot_date.weekday()
        # Calculate the difference in days to the previous occurrence of the specified day
        days_difference = (current_day - target_day) % 7
        return screenshot_date - timedelta(days=days_difference)
    else:
        return screenshot_date

def process_downloaded_images(screenshots_dir):
    all_transactions = []
    for filename in sorted(os.listdir(screenshots_dir)):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            filepath = os.path.join(screenshots_dir, filename)
            image = Image.open(filepath)

            text = extract_text(image)
            transactions = extract_transactions(text)
            for transaction in transactions:
                transaction["date"] = compute_absolute_date(transaction["date"], filename).strftime("%Y-%m-%d")
            all_transactions += transactions
        elif filename.lower().endswith(".html"):
            with open(os.path.join(screenshots_dir, filename), 'r', encoding='utf-8') as f:
                html = f.read()
                transaction = extract_qr_payment_info(html)
                all_transactions += [transaction]
    
    return all_transactions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract transactions from images in a directory.")
    parser.add_argument("--screenshots_dir", required=True, help="Directory to import downloaded images.")
    parser.add_argument("--csv_output_path", required=True, help="Path to write resulting csv file.")

    args = parser.parse_args()

    screenshots_dir = args.screenshots_dir
    csv_output_path = args.csv_output_path

    transactions = process_downloaded_images(screenshots_dir)
    transactions_df = pd.DataFrame(transactions)
    transactions_df = transactions_df.drop_duplicates(subset=["date", "amount", "merchant"], keep="first")
    transactions_df.to_csv(csv_output_path, index=False)
