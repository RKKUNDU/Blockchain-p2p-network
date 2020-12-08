NUM_OF_PEERS=10
NUM_OF_ADVERSARY=1
SEED_IP='127.0.0.1'
SEED_PORT='12345'
NODE_HASH_POWER=6.7
ADVERSARY_HASH_POWER=33
EXPERIMENT_TIME=10 #600 sec or 10 min
FLOOD_PERCENTAGE=10

python3 seed.py $SEED_IP $SEED_PORT &

iat=
iit=

i=1
# run $NUM_OF_PEERS peers
while [[ $i -le $NUM_OF_PEERS ]]
do
    # echo "python3 dummy.py ${NODE_HASH_POWER}"
    python3 peer.py ${NODE_HASH_POWER} &
    sleep 4

    ((i++))
done

i=1
# run $NUM_OF_PEERS adversaries
while [[ $i -le $NUM_OF_ADVERSARY ]]
do
    # echo "python3 dummy.py ${ADVERSARY_HASH_POWER} ${iit}"
    python3 adversary.py ${ADVERSARY_HASH_POWER} ${iit} ${FLOOD_PERCENTAGE} &
    # sleep 2

    ((i++))
done


# wait for $EXPERIMENT_TIME for the seed, peer programs to run
sleep $EXPERIMENT_TIME

# send signal to the seed, peer, adversary 
killall -15 python3
sleep 5
killall -9 python3
sleep 10

python3 write_graph_data $iit $iat

echo "Experiment complete"