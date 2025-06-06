docker rm -f agent-bubble
echo y | docker image prune -a 
docker build -t agent-image -f app/Dockerfile .
docker run -it --name agent-bubble agent-image:latest