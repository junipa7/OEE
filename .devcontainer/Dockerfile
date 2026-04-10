FROM python:3.9-slim

# Set the working directory
WORKDIR /workspace

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the application
CMD ["python", "src/auto_st/main.py"]