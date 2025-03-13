FROM python:3.12-slim

# Set working directory
WORKDIR /app 
#ENV  ALGORITHM="HS256"

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY .   /app/

# Expose the FastAPI port
EXPOSE 8000

# Start the FastAPI app
CMD ["fastapi", "run", "app.py"]
