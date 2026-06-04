# Use a lightweight Python runtime
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install build dependencies and Python requirements
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . ./

# Expose port and default environment
ENV PORT=8080
EXPOSE 8080

# Run with Gunicorn for production-style container execution
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
