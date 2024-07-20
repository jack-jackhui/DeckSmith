# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /decksmith

# Install dependencies
COPY requirements.txt /decksmith
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /decksmith/
RUN chown -R www-data:www-data /decksmith

# Expose the port the app runs on
EXPOSE 8502

# Run streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8502"]

