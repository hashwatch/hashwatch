docker build -t hashwatch .
docker run -p 8000:8000 -d --restart unless-stopped hashwatch