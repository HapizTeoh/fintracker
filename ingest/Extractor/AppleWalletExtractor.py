import datetime
from io import BytesIO
import re

import pytesseract
from PIL import Image

from Extractor.TransactionFileExtractor import TransactionFileExtractor

class AppleWalletExtractor(TransactionFileExtractor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def detect_file_type(self, data) -> bool:
        """
        Detects if the given file is an Apple Wallet screenshot.
        Returns True if it is, False otherwise.
        """
        # Check PNG signature
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return True
        # Check JPEG signature
        if data[:2] == b'\xff\xd8':
            return True
        return False
    
    def extract_transactions(self, data, capture_date):
        file_bytes = BytesIO(data)  # Convert to BytesIO for PIL compatibility
        image = Image.open(file_bytes)

        text = self.extract_text_from_apple_wallet(image)
        transactions = self.extract_transactions_from_text(text)
        for transaction in transactions:
            transaction["date"] = self.compute_absolute_date(transaction["date"], capture_date).strftime("%Y-%m-%d")
            
        return transactions
    
    def extract_transactions_from_text(self, text):
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        transactions = []

        i = 0
        while i < len(lines):
            merchant_match = re.match(r"(.+?)\s+\$([\d.,]+)", lines[i])
            if merchant_match:
                merchant = merchant_match.group(1).strip()
                amount = merchant_match.group(2).strip()
                # Look ahead for relative date (within next 2 lines)
                date = "Unknown"
                for j in range(1, 3):
                    if i + j < len(lines):
                        if re.search(r"\b(yesterday|today|[a-z]+day|hours? ago|minutes? ago|\d{1,2}/\d{1,2}/\d{2})\b", lines[i + j], re.I):
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

    def extract_text_from_apple_wallet(self, image):
        grayscale = image.convert("L")
        binarized = grayscale.point(lambda x: 0 if x < 140 else 255, mode='1')
        config = r'--oem 3 --psm 6'
        return pytesseract.image_to_string(binarized, config=config)

    def compute_absolute_date(self, date_str, screenshot_date):
        # screenshot_date = datetime.datetime.strptime(screenshot_date[:10], "%Y-%m-%d")
        names_of_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        if date_str.lower() == "yesterday":
            return screenshot_date - datetime.timedelta(days=1)
        elif date_str.lower() in names_of_days:
            # Get the day of week for the current date
            target_day = names_of_days.index(date_str.lower())
            current_day = screenshot_date.weekday()
            # Calculate the difference in days to the previous occurrence of the specified day
            days_difference = (current_day - target_day) % 7
            return screenshot_date - datetime.timedelta(days=days_difference)
        elif re.search(r"\d{1,2}/\d{1,2}/\d{2}", date_str):
            return datetime.datetime.strptime(date_str, "%d/%m/%y").replace(year=screenshot_date.year)
        else:
            return screenshot_date
