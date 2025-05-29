class TransactionFileExtractor:
    def detect_file_type(self, data) -> bool:
        """
        Detects if the given file is of a supported type.
        Returns True if supported, False otherwise.
        """
        return False

    def extract_transactions(self, data, capture_date):
        """
        Extracts transactions from the given file.
        Returns a list of transactions.
        """
        return []
