# Use official Python 3.9 image
FROM python:3.9

# Standard user setup for HuggingFace Spaces
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy and install dependencies
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy everything else
COPY --chown=user . /app

# Collect Static Files for Django
RUN python manage.py collectstatic --noinput

# Ensure SQLite database is writable
RUN touch db.sqlite3 && chmod 777 db.sqlite3 || true

# HuggingFace uses Port 7860
EXPOSE 7860

# CMD to start both the Web process and the Bot
CMD ["sh", "-c", "gunicorn resume_optimizer.wsgi --bind 0.0.0.0:7860 & python bot/bot.py"]
