# Use an official Python runtime as a parent image
FROM python


# Set environment variables
ENV FLASK_APP=start.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5050

# Create and set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app


# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose the port Gunicorn will listen on
EXPOSE 5050

# Start Gunicorn when the container launches
CMD ["gunicorn", "-b", "0.0.0.0:5050", "start:app"]