# 1. Use an official Python base image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy your dependencies file first
COPY requirements.txt .

# 4. Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application files
COPY . .

# 6. Expose the port Hugging Face expects
EXPOSE 7860

# 7. Run Uvicorn binding to your app on port 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]