


#!/bin/bash




# Identifier les PID des processus gunicorn sur le port 8000
pids=$(lsof -ti tcp:8000)

# Tuer ces processus
for pid in $pids; do
    echo "Killing process $pid"
    kill -9 $pid
done



# Identifier les PID des processus gunicorn sur le port 8000
pids=$(lsof -ti tcp:8001)

# Tuer ces processus
for pid in $pids; do
    echo "Killing process $pid"
    kill -9 $pid
done



# Identifier les PID des processus gunicorn sur le port 8000
pids=$(lsof -ti tcp:8002)

# Tuer ces processus
for pid in $pids; do
    echo "Killing process $pid"
    kill -9 $pid
done


