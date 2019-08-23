import sys
import csv
from collections import OrderedDict

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
    if (line_split[0]==start_token1 and start_found == 0):
        start_found=1
        print("start found\n")
    if (line_split[0]==start_token2 and start_found == 0):
        count += 1
        if count == 1:
            start_found=1
            print("start found True or False\n")
        elif count == 3:
            count = 0
    if start_found == 0:
        continue
    if ((line_split[0]==stop_token1 or line_split[0]==stop_token2) and start_found == 1):
        start_found=0
        if line_split[0] == stop_token1:
            print("end found\n")
        else:
            print("end found True or False\n")
    if start_found == 1 and line_split[0]=='####':
        if (line_split[2] == "True" or line_split[2] == "False"):
            #print("hello?")
            #count += 1
            
            #if count > 6 and count <= 9:
            #print("line_split[0] {}, line_split[1] {}, line_split[2] {}".format(line_split[0], line_split[1], line_split[2]))
            line_split[2] = int(line_split[2] == 'True')
            #print("line_split[2] {}".format(line_split[2]))
            #elif count > 9:
            #    count = 0
            #    continue
            #else:
            #    print(count)
            #    continue

            # if line_split[2] == "True":
        #     print("line_split[0] {}, line_split[1] {}, line_split[2] {}".format(line_split[0], line_split[1], line_split[2]))
        #     line_split[2] = 1
        # elif line_split[2] == "False":

        #     line_split[2] = 0

        if line_split[1] in perf_dict:
            #           print("key exists\n")
            perf_dict[line_split[1]].append(int(line_split[2]))
           #           print(perf_dict)
        else:
            #           print("key doesn't exists\n")
            perf_dict[line_split[1]] = [int(line_split[2])]

# print(perf_dict)

keys = perf_dict.keys()
#print(keys)
with open(sys.argv[1][:-4]+".csv", "w") as outfile:
    writer = csv.writer(outfile, delimiter = ",")
    writer.writerow(list(keys))#(list(perf_dict.keys()))
    writer.writerows(zip(*[perf_dict[key] for key in keys]))#perf_dict.values()))
