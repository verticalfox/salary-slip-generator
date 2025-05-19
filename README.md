# Salary Slip Generator

Generate beautiful, professional salary slip PDFs for employees from an Excel file using a customizable HTML template.

## Features
- **Batch PDF Generation:** Create salary slips for all employees in your Excel sheet in one go.
- **Customizable Template:** Uses an HTML template for modern, branded salary slips (with your company logo).
- **Flexible Data Mapping:** Handles various Excel column names and formats.
- **Automatic Amount in Words:** Converts net pay to words (Indian Rupees format).
- **Portable:** Works on macOS, Linux, and Windows (with Python 3.7+).

## Requirements
- Python 3.7+
- [WeasyPrint](https://weasyprint.org/) (for HTML to PDF conversion)
- pandas, num2words, openpyxl

## Setup
1. **Clone the repository:**
   ```sh
   git clone https://github.com/verticalfox/salary-slip-generator.git
   cd salary-slip-generator
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## Usage
1. **Prepare your Excel file:**
   - Each row = one employee
   - Must include columns like `Name`, `Month`, `Salary to be paid`, etc.
2. **Customize the HTML template:**
   - Edit `Sample Salary Slip  copy.html` to match your branding and fields.
   - Place your logo in the `assets/` folder and reference it in the template.
3. **Run the generator:**
   ```sh
   python Salary-slip/salary_slip_generator.py <path_to_excel_file>
   ```
   Example:
   ```sh
   python Salary-slip/salary_slip_generator.py /path/to/your/salary_data.xlsx
   ```
4. **Find your PDFs:**
   - Generated files will be named like `Salary_Slip_<EmployeeName>_<Month>.pdf` in the project directory.

## Example Output
![Sample Salary Slip](assets/sample_salary_slip_screenshot.png)

## Customization
- **Template:** Edit the HTML file for layout, colors, and fields.
- **Logo:** Place your logo in `assets/` and update the `<img src="...">` in the template.
- **Fields:** The script is flexible with column names, but you can adjust mappings in `salary_slip_generator.py` if needed.

## License
MIT License

---
Made with ❤️ by Vertical Fox 