import sys
import csv
from collections import OrderedDict
import matplotlib
import matplotlib.pyplot as plt

if __name__ == '__main__':

    """
    Generates the csv file containing the statistics (perf measurements). It checks for '####' at the beginning of every line, if it finds it, the second word will be the key and the third word will be the measured performance in cycles.
    Input: filename of the file containing the redirected output from console (.txt file)
    Output: .csv file containig the statistics
    """

start_token1 = 'starting'
start_token2 = 'nettype:'
stop_token1 = 'ending'
stop_token2 = 'copying'
start_found = 0

log_file = open(sys.argv[1])

perf_dict = OrderedDict()

count = 0

head_list=[]

while True:

    line = log_file.readline()
    line_split=line.split()
    #    if len(line_split) == 0 and start_found == 1:
    #        break;
    if len(line_split) == 0:# and start_found == 0:
        continue
        # line = log_file.readline()
        # line_split=line.split()
        # if len(line_split) == 0:
        #     break
    if line_split[0]=="END":
        break

    if line_split[0]!='####':
        head = line_split[0]
        head_list.append(head)
        continue

    if line_split[0]=='####':
        line_split[1] = head+"-"+line_split[1]
        if line_split[1] in perf_dict:
            #           print("key exists\n")
            perf_dict[line_split[1]].append(int(line_split[2]))
           #           print(perf_dict)
        else:
            #           print("key doesn't exists\n")
            perf_dict[line_split[1]] = [int(line_split[2])]


keys = perf_dict.keys()
#print(keys)
with open(sys.argv[1][:-4]+".csv", "w") as outfile:
    writer = csv.writer(outfile, delimiter = ",")
    writer.writerow(list(keys))#(list(perf_dict.keys()))
    writer.writerows(zip(*[perf_dict[key] for key in keys]))#perf_dict.values()))

############## PLOT ###############

print(perf_dict)


for head in head_list:

    subdict = OrderedDict()

    for k,v in perf_dict.items():
        if head in k and 'mean_cycles' in k:
            tmp_k = k.replace(head+'-mean_cycles_', '')
            subdict[tmp_k] = v

    print(subdict)
    fig, ax = plt.subplots()

    lists = sorted(subdict.items()) # sorted by key, return a list of tuples

    x, y = zip(*lists) # unpack a list of pairs into two tuples

    print("x {}, y {}".format(x,y))

    plt.plot(x, y, 'o')
    plt.title(head)
    plt.show()

