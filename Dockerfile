FROM python:3.11-slim

# Install system libraries required by WeasyPrint (HTML to PDF)
# Reference: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       libcairo2 \
       libpango-1.0-0 \
       libpangoft2-1.0-0 \
       libgdk-pixbuf-2.0-0 \
       libffi8 \
       shared-mime-info \
       fonts-dejavu \
       curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for better build cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -U pip wheel setuptools \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Default command prints help; users pass the Excel path at runtime
CMD ["python", "Salary-slip/salary_slip_generator.py", "--help"]


