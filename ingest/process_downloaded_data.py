import argparse
import datetime
import os
import re

import pandas as pd

from Extractor.AppleWalletExtractor import AppleWalletExtractor
from Extractor.QRPaymentExtractor import QRPaymentExtractor

def process_downloaded_files(screenshots_dir):
    all_transactions = []

    for filename in sorted(os.listdir(screenshots_dir)):
        print(f"Processing file: {filename}")
        with open(os.path.join(screenshots_dir, filename), "rb") as f:
            file_bytes = f.read()

        # If filename starts with a date like "2025-05-25_184131", parse it as a datetime object
        capture_date = None
        date_match = re.match(r"(\d{4}-\d{2}-\d{2}_\d{6})", filename)
        if date_match: 
            capture_date = datetime.datetime.strptime(filename[:15], "%Y-%m-%d_%H%M%S")

        extractors = [AppleWalletExtractor(), QRPaymentExtractor()]

        for extractor in extractors:
            if extractor.detect_file_type(file_bytes):
                transactions = extractor.extract_transactions(file_bytes, capture_date)
                all_transactions += transactions
                break

        all_transactions += transactions
    
    return all_transactions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract transactions from images in a directory.")
    parser.add_argument("--screenshots_dir", required=True, help="Directory to import downloaded images.")
    parser.add_argument("--csv_output_path", required=True, help="Path to write resulting csv file.")

    args = parser.parse_args()

    screenshots_dir = args.screenshots_dir
    csv_output_path = args.csv_output_path

    print(f"Processing screenshots from: {screenshots_dir}")
    transactions = process_downloaded_files(screenshots_dir)

    print(f"Extracted {len(transactions)} transactions.")
    transactions_df = pd.DataFrame(transactions)
    transactions_df = transactions_df.drop_duplicates(subset=["date", "amount", "merchant"], keep="first")
    transactions_df = transactions_df.sort_values(by=["date", "merchant"])   

    print(f"Writing transactions to: {csv_output_path}") 
    transactions_df.to_csv(csv_output_path, index=False)

    print("Processing complete.")
