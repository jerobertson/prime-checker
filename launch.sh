sudo docker swarm leave --force
sudo docker swarm init
sudo docker stack deploy -c docker-compose.yml primecheck
