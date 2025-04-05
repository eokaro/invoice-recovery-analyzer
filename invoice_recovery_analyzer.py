import csv
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("invoice_recovery_analyzer.log"),
        logging.StreamHandler()
    ]
)

def load_invoice_data(file_path: str) -> List[Dict]:
    """
    Loads invoice data from a CSV file.

    The CSV file should have the following columns:
    - client_id: Identifier for the client
    - invoice_id: Invoice identifier
    - invoiced_amount: Amount invoiced
    - paid_amount: Amount paid

    Args:
        file_path (str): Path to the CSV file containing invoice data.

    Returns:
        List[Dict]: A list of dictionaries with invoice data.
    """
    invoices = []
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    row['invoiced_amount'] = float(row['invoiced_amount'])
                    row['paid_amount'] = float(row['paid_amount'])
                    invoices.append(row)
                except ValueError as ve:
                    logging.error(f"Error parsing amounts in row {row}: {ve}")
        logging.info(f"Loaded {len(invoices)} invoice records from {file_path}")
    except FileNotFoundError as fnf_error:
        logging.error(f"File not found: {fnf_error}")
    return invoices

def analyze_recoveries(invoices: List[Dict]) -> Dict[str, float]:
    """
    Analyzes the invoice data to calculate recovery amounts for each client.

    Args:
        invoices (List[Dict]): A list of invoice data dictionaries.

    Returns:
        Dict[str, float]: A dictionary mapping client IDs to their total recovery amount.
    """
    recovery_totals = {}
    for invoice in invoices:
        client_id = invoice.get("client_id", "Unknown")
        invoiced = invoice.get("invoiced_amount", 0)
        paid = invoice.get("paid_amount", 0)
        if paid < invoiced:
            recovery = invoiced - paid
            recovery_totals[client_id] = recovery_totals.get(client_id, 0) + recovery
            logging.debug(f"Client {client_id} - Invoice {invoice.get('invoice_id')}: Recovery ${recovery:.2f}")
    return recovery_totals

def generate_report(recovery_totals: Dict[str, float]) -> str:
    """
    Generates a client-ready report summarizing the recovery amounts.

    Args:
        recovery_totals (Dict[str, float]): A dictionary mapping client IDs to recovery amounts.

    Returns:
        str: A formatted string report.
    """
    report_lines = ["Invoice Recovery Report", "========================", ""]
    if not recovery_totals:
        report_lines.append("No recoveries needed. All invoices are fully paid.")
    else:
        for client, total in recovery_totals.items():
            report_lines.append(f"Client {client}: Recoverable Amount: ${total:,.2f}")
    report = "\n".join(report_lines)
    logging.info("Report generated successfully")
    return report

def main():
    """
    Main function to run the Invoice Recovery Analyzer.
    """
    # For demonstration, we'll use a sample CSV file "invoices.csv".
    # In a production environment, this file would be provided or pulled from a secure source.
    file_path = "invoices.csv"
    
    invoices = load_invoice_data(file_path)
    if not invoices:
        print("No invoice data available. Please check the CSV file.")
        return

    recovery_totals = analyze_recoveries(invoices)
    report = generate_report(recovery_totals)
    print(report)

if __name__ == "__main__":
    main()
