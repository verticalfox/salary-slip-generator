import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import sys
import pdfkit
from num2words import num2words
from datetime import datetime
import calendar
import os
import argparse

try:
    # Optional dependency at runtime; container has it, local may not
    from weasyprint import HTML  # type: ignore
    _WEASYPRINT_AVAILABLE = True
except Exception:
    HTML = None  # type: ignore
    _WEASYPRINT_AVAILABLE = False

# Function to generate PDF
def generate_pdf(employee_data, filename, month):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    # Employee Summary Table
    data = [
        ["Employee Name", employee_data['Name']],
        ["No of Leaves", employee_data['No of leaves']],
        ["No of Total Days", employee_data['No of total days']],
        ["No of Days Worked", employee_data['No of days worked']],
        ["Yearly Salary", employee_data['Yearly salary']],
        [f"Monthly Salary {month}", employee_data[f'Monthly salary {month}']],
        ["Salary to be Paid", employee_data['Salary to be paid']],
        ["Total Final Amount to be Paid", employee_data['Total final amount to be paid to EE']],
        ["Invoice Number", employee_data['Invoice Number']],
        ["Month", employee_data['Month']],
        ["Invoice Date", employee_data['Invoice Date']],
        ["Due Date", employee_data['Due Date']]
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

# Function to generate PDF from HTML template
def generate_pdf_from_html(employee_data, template_path, output_path):
    with open(template_path, 'r') as file:
        html_content = file.read()

    # Replace placeholders with actual data, handling missing values
    html_content = html_content.replace('{{employee_name}}', str(employee_data.get('Name', 'N/A')))
    # Remove this line to avoid overwriting the formatted employee_id
    # html_content = html_content.replace('{{employee_id}}', str(employee_data.get('Employee ID', '')))
    html_content = html_content.replace('{{pay_period}}', str(employee_data.get('Month', 'N/A')))

    # Calculate pay date as the last day of the month if not present
    pay_date = employee_data.get('Pay Date', '')
    if not pay_date:
        month_column = next(col for col in employee_data.index if 'Monthly salary' in col)
        month = month_column.split()[-1]
        year = '2025'
        month_number = datetime.strptime(month, '%B').month
        last_day = calendar.monthrange(int(year), month_number)[1]
        pay_date = f"{last_day}/{month_number}/{year}"
    html_content = html_content.replace('{{pay_date}}', pay_date)

    # Salary and related fields
    salary_to_be_paid = employee_data.get('Salary to be paid', 0)
    if pd.isna(salary_to_be_paid):
        salary_to_be_paid = 0
    salary_to_be_paid_fmt = f"Rs.{float(salary_to_be_paid):,.2f}"
    html_content = html_content.replace('{{total_net_pay}}', salary_to_be_paid_fmt)
    
    # Use 'Basic' column for {{basic}}
    basic_val = employee_data.get('Basic', 0)
    if pd.isna(basic_val):
        basic_val = 0
    basic_fmt = f"Rs.{float(basic_val):,.2f}"
    html_content = html_content.replace('{{basic}}', basic_fmt)
    
    html_content = html_content.replace('{{gross_earnings}}', salary_to_be_paid_fmt)
    html_content = html_content.replace('{{total_net_payable}}', salary_to_be_paid_fmt)
    html_content = html_content.replace('{{amount_in_words}}', num2words(int(round(salary_to_be_paid)), lang='en_IN').replace('euro', 'rupees').replace('Rupees', 'rupees').title() + ' Only')

    # Paid days and LOP days
    paid_days_val = employee_data.get('No of days worked', '')
    if pd.isna(paid_days_val) or paid_days_val == '':
        paid_days_str = ''
    else:
        try:
            paid_days_str = str(int(float(paid_days_val)))
        except Exception:
            paid_days_str = str(paid_days_val)
    html_content = html_content.replace('{{paid_days}}', paid_days_str)
    html_content = html_content.replace('{{lop_days}}', '0')

    # Details section (flexible matching)
    # Format join date to only show date part
    join_date_val = get_flexible_column(employee_data, ['Join Date'])
    if pd.isna(join_date_val) or join_date_val in [None, '', 'nan', 'NaT']:
        join_date_str = 'N/A'
    elif hasattr(join_date_val, 'strftime'):
        join_date_str = join_date_val.strftime('%Y-%m-%d')
    elif isinstance(join_date_val, str) and ' ' in join_date_val:
        join_date_str = join_date_val.split(' ')[0]
    else:
        join_date_str = str(join_date_val)
    html_content = html_content.replace('{{designation}}', str(get_flexible_column(employee_data, ['Designation'])))
    html_content = html_content.replace('{{bank_account_number}}', str(get_flexible_column(employee_data, ['Bank Account Number', 'Bank Account No.'])))
    html_content = html_content.replace('{{join_date}}', join_date_str)
    html_content = html_content.replace('{{bank_name}}', str(get_flexible_column(employee_data, ['Bank Name'])))
    # Employee ID as integer if possible
    emp_id_val = get_flexible_column(employee_data, ['Employee ID', 'Emp ID', 'ID'])
    if pd.isna(emp_id_val) or emp_id_val == '':
        emp_id_str = ''
    else:
        try:
            emp_id_str = str(int(float(emp_id_val)))
        except Exception:
            emp_id_str = str(emp_id_val)
    html_content = html_content.replace('{{employee_id}}', emp_id_str)

    # Earnings (other than basic)
    def format_rs(val):
        try:
            return f"Rs.{float(val):,.2f}"
        except Exception:
            return "Rs.0.00"
    html_content = html_content.replace('{{house_rent_allowance}}', format_rs(employee_data.get('House Rent Allowance', 0)))
    html_content = html_content.replace('{{conveyance_allowance}}', format_rs(employee_data.get('Conveyance Allowance', 0)))
    html_content = html_content.replace('{{special_allowance}}', format_rs(employee_data.get('Special Allowance', 0)))

    # Deductions
    html_content = html_content.replace('{{income_tax}}', format_rs(employee_data.get('Income Tax', 0)))
    html_content = html_content.replace('{{provident_fund}}', format_rs(employee_data.get('Provident Fund', 0)))
    html_content = html_content.replace('{{total_deductions}}', format_rs(employee_data.get('Total Deductions', 0)))

    # Convert HTML to PDF using WeasyPrint
    if not _WEASYPRINT_AVAILABLE:
        raise RuntimeError("WeasyPrint not available in this environment")
    HTML(string=html_content, base_url=os.getcwd()).write_pdf(output_path)

def get_flexible_column(employee_data, possible_names):
    # Normalize column names: lowercase, remove spaces
    normalized_cols = {col.lower().replace(' ', '').replace('_', ''): col for col in employee_data.index}
    for name in possible_names:
        norm_name = name.lower().replace(' ', '').replace('_', '')
        if norm_name in normalized_cols:
            return employee_data[normalized_cols[norm_name]]
    return ''

# Read Excel file
def read_excel(file_path):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.replace('\xa0', ' ').str.strip()  # Replace non-breaking spaces and trim
    return df

# Main function
def main():
    parser = argparse.ArgumentParser(description="Generate Salary Slip PDFs from an Excel file")
    parser.add_argument("excel_file", help="Path to the Excel file containing employee data")
    parser.add_argument("--engine", choices=["auto", "weasyprint", "reportlab"], default="auto",
                        help="PDF rendering engine. 'auto' tries WeasyPrint then falls back to ReportLab")
    parser.add_argument("--template", default='Sample Salary Slip  copy.html',
                        help="Path to HTML template (used with WeasyPrint)")
    parser.add_argument("--out-dir", default='.', help="Directory to write PDFs to")
    args = parser.parse_args()

    df = read_excel(args.excel_file)
    print("Column names:", df.columns)

    # Resolve engine choice
    preferred_engine = args.engine
    use_weasy = False
    if preferred_engine == "weasyprint":
        use_weasy = True
        if not _WEASYPRINT_AVAILABLE:
            print("WeasyPrint not available; please install it or use --engine reportlab", file=sys.stderr)
            sys.exit(2)
    elif preferred_engine == "reportlab":
        use_weasy = False
    else:
        use_weasy = _WEASYPRINT_AVAILABLE

    # Ensure output directory exists
    os.makedirs(args.out_dir, exist_ok=True)

    # Try to generate using chosen engine; in 'auto' we silently fall back to reportlab on error
    for _, row in df.iterrows():
        month_value = str(row.get('Month', '')).strip().replace(' ', '_')
        name_value = str(row.get('Name', '')).strip().replace(' ', '_')
        filename = os.path.join(args.out_dir, f"Salary_Slip_{name_value}_{month_value}.pdf")

        if use_weasy:
            try:
                generate_pdf_from_html(row, args.template, filename)
                continue
            except Exception as exc:
                if preferred_engine == "weasyprint":
                    raise
                print(f"WeasyPrint failed ({exc}). Falling back to ReportLab table PDF...", file=sys.stderr)

        # Fallback to basic ReportLab PDF summary
        # Try to infer month name for the summary row
        try:
            month_column = next(col for col in row.index if 'Monthly salary' in col)
            month_for_summary = month_column.split()[-1]
        except StopIteration:
            month_for_summary = str(row.get('Month', ''))
        generate_pdf(row, filename, month_for_summary)

if __name__ == "__main__":
    main() 