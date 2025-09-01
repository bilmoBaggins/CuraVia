# Use official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y mariadb-client

# Copy the rest of your application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Add a non-root user to run the application
RUN useradd --create-home celeryuser
USER celeryuser

RUN chmod +x /app/wait-for-mysql.sh

# Command to run FastAPI app (adjust main:app if your entrypoint is different)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]