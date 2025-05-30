import datetime
import re

from Extractor.TransactionFileExtractor import TransactionFileExtractor

class QRPaymentExtractor(TransactionFileExtractor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def detect_file_type(self, data) -> bool:
        """
        Detects if the given file is an HTML or text file containing NETS or PayNow payment information.
        Returns True if it is, False otherwise.
        """
        html_decoded = data.decode('utf-8', errors='ignore').lower()
        return ('nets' in html_decoded or 'paynow' in html_decoded)
    
    def extract_transactions(self, data, capture_date):
        """
        Extracts transactions from the given HTML data.
        Returns a list of transactions.
        """
        html_decoded = data.decode('utf-8')
        transaction = self.extract_qr_payment_info(html_decoded)
        return [transaction]
    
    def extract_qr_payment_info(self, html_decoded):
        # Date: any "DD Month 20YY" pattern
        date_match = re.search(r'\d{2} \w+ 20\d{2}', html_decoded)
        date = date_match.group(0) if date_match else None

        # Amount: e.g. SGD 8.00
        amount_match = re.search(r'SGD ([\d\.,]+)', html_decoded)
        amount = amount_match.group(1) if amount_match else None

        # Extract Merchant (try PayNow first, fallback to NETS)
        merchant_match = re.search(
            r'has been made to ([^<]+?) using', html_decoded) or \
            re.search(r'To</td><td> :</td><td>(.*?)</td>', html_decoded)

        merchant = merchant_match.group(1).strip() if merchant_match else None
        
        return {
            "date": datetime.datetime.strptime(date, "%d %B %Y").strftime("%Y-%m-%d") if date else None,
            "merchant": merchant,
            "amount": amount
        }
