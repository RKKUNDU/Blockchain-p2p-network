# python3 graph_generation.py {iit} {percentage_flood} 
import mysql.connector
import hashlib
import sys
import matplotlib.pyplot as plt
import os
import numpy

if len(sys.argv) != 3:
	print("Please enter iit and percentage flood.")



def plot_mining_util_data():
	average_utilization = dict()
	x = list()
	y = list()

	with open(f'graph_data/graph_mining_util_data_iit{iit}_fp{fp}.txt','r') as file:
		lines = file.readlines()
		for line in lines:
			line = line.rstrip('\n')
			arr = line.split(':')
			arr = [float(item) for item in arr]
			key = arr[0]
			avg = arr[2]/arr[1]
			if key in average_utilization.keys():
				average_utilization[key].append(avg)
			else:
				average_utilization[key]=list()
				average_utilization[key].append(avg)

	for key, value in average_utilization.items():
		x.append(key)
		y.append(sum(value)/len(value))

	plt.plot(x, y)
	plt.xlabel('Inter-arrival times')
	plt.ylabel('Avg Utilization')
	plt.title('Inter-arrival times vs Average Utilization')

	plt.savefig(f'./test-output/avg_util_{sys.argv[1]}s_{sys.argv[2]}%.png')

	plt.clf()
	plt.cla()
	plt.close()

def plot_fraction_data():
    x = list()
    y = list()
    fraction_utilization = dict()

    # read from the file
    with open(f'graph_data/graph_fraction_data_iit{iit}_fp{fp}.txt','r') as file:
        lines = file.readlines()    
        for line in lines:
            line = line.rstrip('\n')
            arr = line.split(':')
            arr = [float(item) for item in arr]
            
            iat = arr[0]
            longest_chain_length = arr[1]
            fraction = arr[2]

            if iat in fraction_utilization.keys():
                # update fraction_list since we found a longer chain
                if longest_chain_length > fraction_utilization[iat]['max']:
                    fraction_utilization[iat] = {'max': longest_chain_length, 'fraction_list': [fraction]}
                # append to the fraction_list since there already exists the longest chain with same length
                elif longest_chain_length == fraction_utilization[iat]['max']:
                    fraction_utilization[iat]['fraction_list'].append(fraction)
            else:
                fraction_utilization[iat] = {'max': longest_chain_length, 'fraction_list': [fraction]}

        # store 'fractions' in the dictionary for each inter-arrival time
        for iat in fraction_utilization.keys():
            fraction_list = fraction_utilization[iat]['fraction_list']
            fraction_utilization[iat] = sum(fraction_list) / len(fraction_list)
        
    for key, value in fraction_utilization.items():
        x.append(key)
        y.append(value)

    plt.plot(x, y)
    plt.xlabel('Inter-arrival times')
    plt.ylabel('Fraction of main chain')

    plt.title('Inter-arrival times vs Fraction of main chain')

    # plt.show()
    plt.savefig(f'./test-output/fraction_time_{sys.argv[1]}s_{sys.argv[2]}%.png')

    print(fraction_utilization)
            


if len(sys.argv) != 3:
    print("Enter iit and fp")
    exit(0)

iit = sys.argv[1]
fp = sys.argv[2]

plot_mining_util_data()
plot_fraction_data()



# Clearing the files
# if os.path.exists("graph_data/graph_mining_util_data.txt"):
# 	os.remove("graph_data/graph_mining_util_data.txt")

# if os.path.exists("graph_data/graph_fraction_data.txt"):
# 	os.remove("graph_data/graph_fraction_data.txt")