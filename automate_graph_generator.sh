NUM_OF_PEERS=4
NUM_OF_ADVERSARY=1
START=1
SEED_IP='127.0.0.1'
SEED_PORT='12345'
NODE_HASH_POWER=6.7
ADVERSARY_HASH_POWER=33
EXPERIMENT_TIME=6 #600 sec or 10 min
# python3 seed.py & $SEED_IP $SEED_PORT

# inter-invalid block generation time
iit_list=(0.5 1.0 1.5 2.0)

for iit in ${iit_list[@]}
do
    echo -e "Running for iit=${iit}"
    i=1
    # run $NUM_OF_PEERS peers
    while [[ $i -le $NUM_OF_PEERS ]]
    do
        # echo "python3 dummy.py ${NODE_HASH_POWER}"
        python3 peer.py ${NODE_HASH_POWER} &
        ((i++))
    done

    i=1
    # run $NUM_OF_PEERS adversaries
    while [[ $i -le $NUM_OF_ADVERSARY ]]
    do
        # echo "python3 dummy.py ${ADVERSARY_HASH_POWER} ${iit}"
        python3 dummy.py ${ADVERSARY_HASH_POWER} ${iit} &
        # python3 adversary.py ${ADVERSARY_HASH_POWER}        
        ((i++))
    done

    # wait for $EXPERIMENT_TIME for the seed, peer programs to run
    sleep $EXPERIMENT_TIME

    # send signal to the seed, peer, adversary 
    killall -2 python3
    killall -15 python3
    echo 
done

python3 graph_generation.py
