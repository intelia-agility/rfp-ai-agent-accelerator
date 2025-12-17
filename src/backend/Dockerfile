
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Set default PORT if not provided
ENV PORT=8080

# Run the web service on container startup.
# Use uvicorn with proper timeout and worker configuration for Cloud Run
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --timeout-keep-alive 0

