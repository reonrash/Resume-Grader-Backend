# Use a lightweight Python base image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY main.py .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application
# Use --host 0.0.0.0 to make the app accessible from outside the container
# The GOOGLE_API_KEY environment variable will be passed at runtime (see docker run command below)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]