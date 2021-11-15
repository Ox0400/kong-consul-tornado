FROM python:alpine
RUN pip install --no-cache tornado python-consul
COPY start.py /start.py
ENTRYPOINT python /start.py
expose 8080
