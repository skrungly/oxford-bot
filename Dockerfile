FROM python:3.9-slim

# Install pipenv
RUN pip install -U pipenv

# Create the working directory
WORKDIR /bot

# Install project dependencies
COPY Pipfile* ./
RUN pipenv install --system --deploy

# Copy the source code in last to optimize rebuilding the image
COPY . .

CMD python3 bot.py
