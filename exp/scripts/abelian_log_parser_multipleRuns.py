##########################################
# To parse log files generated by abelian.
# Author: Gurbinder Gill
# Email: gurbinder533@gmail.com
#########################################

import re
import os
import sys, getopt
import csv
import numpy
import subprocess

######## NOTES:
# All time values are in sec by default.


def match_timers(fileName, benchmark, forHost, numRuns, numThreads, time_unit, total_hosts, partition, run_identifier):

  mean_time = 0.0;
  recvNum_total = 0
  recvBytes_total = 0
  sendNum_total = 0
  sendBytes_total = 0
  sync_pull_avg_time_total = 0.0;
  extract_avg_time_total = 0.0;
  set_avg_time_total = 0.0;
  sync_push_avg_time_total = 0.0;
  graph_init_time = 0
  hg_init_time = 0
  total_time = 0

  if(benchmark == "cc"):
    benchmark = "ConnectedComp"

  if(benchmark == "pagerank"):
    benchmark = "PageRank"

  if (time_unit == 'seconds'):
    divisor = 1000
  else:
    divisor = 1

  log_data = open(fileName).read()


  timer_regex = re.compile(re.escape(run_identifier) + r',\(NULL\),0\s,\sTIMER_0,\d*,0,(\d*)')
  timers = re.findall(timer_regex, log_data)
  #print timers

  time = []
  total_mean_time=0.0

  print timers
  for i in range(int(total_hosts)):
    time.append(0)

  for timer in timers:
    total_mean_time += float(timer)
    print "TIMER : ", timer

  print "TOTAL MEAN TIME " , total_mean_time
  total_mean_time = total_mean_time/int(total_hosts)
  total_mean_time /= divisor
  mean_time = total_mean_time = round(total_mean_time, 3)
  print "Total Mean time: ", total_mean_time

  rep_regex = re.compile((run_identifier) + r',\(NULL\),0\s,\sREPLICATION_FACTOR_0_0,(\d*),\d*,(.*)')

  rep_search = rep_regex.search(log_data)
  rep_factor = 0;
  if rep_search is not None:
    rep_factor = rep_search.group(2)
    rep_factor = round(float(rep_factor), 3)
  print ("Replication factor  : ", rep_factor)


  #Finding mean compute time over all hosts
  do_all_regex = re.compile((run_identifier) + r',\(NULL\),0\s,\s.*DO_ALL_IMPL_(?i)' + re.escape(benchmark) + r'_0_\d*'  +r',.*' + r',\d*,(\d*)')
  do_all_all_hosts = re.findall(do_all_regex, log_data)
  num_arr = numpy.array(map(int,do_all_all_hosts))

  print ("NUM_ARR", num_arr)
  sum_do_all = numpy.sum(num_arr, axis=0)
  print "XXXX " , sum_do_all
  mean_do_all = float(sum_do_all)/float(total_hosts)


  print "mean_do_all", mean_do_all


  #Finding mean serialization time
  sync_extract_regex = re.compile((run_identifier) + r',\(NULL\),0\s,\sSYNC_PU.._EXTRACT_(?i)' + re.escape(benchmark) + r'_0_\d*'  +r',.*' + r',\d*,(\d*)')
  sync_extract_all_hosts = re.findall(sync_extract_regex, log_data)
  num_arr = numpy.array(map(int,sync_extract_all_hosts))

  sum_extract = numpy.sum(num_arr, axis=0)

  sync_extract_firstItr_regex = re.compile((run_identifier) +r',\(NULL\),0\s,\sSYNC_PU.._EXTRACT_FirstItr_(?i)' + re.escape(benchmark) + r'_0_\d*'  +r',.*' + r',\d*,(\d*)')
  sync_extract_firstItr_all_hosts = re.findall(sync_extract_firstItr_regex, log_data)
  num_arr_firstItr = numpy.array(map(int,sync_extract_firstItr_all_hosts))

  # TOTAL EXTRACT
  sum_extract += numpy.sum(num_arr_firstItr, axis=0)
  mean_exract_time = round(sum_extract/float(total_hosts),3)


  #Finding mean deserialization time
  sync_set_regex = re.compile((run_identifier) + r',\(NULL\),0\s,\sSYNC_PU.._SET_(?i)' + re.escape(benchmark) + r'_0_\d*'  +r',.*' + r',\d*,(\d*)')
  sync_set_all_hosts = re.findall(sync_set_regex, log_data)
  num_arr = numpy.array(map(int,sync_set_all_hosts))

  sum_set = numpy.sum(num_arr, axis=0)

  sync_set_firstItr_regex = re.compile((run_identifier) +r',\(NULL\),0\s,\sSYNC_PU.._SET_FirstItr_(?i)' + re.escape(benchmark) + r'_0_\d*'  +r',.*' + r',\d*,(\d*)')
  sync_set_firstItr_all_hosts = re.findall(sync_set_firstItr_regex, log_data)
  num_arr_firstItr = numpy.array(map(int,sync_set_firstItr_all_hosts))

  # TOTAL EXTRACT
  sum_set += numpy.sum(num_arr_firstItr, axis=0)
  mean_set_time = round(sum_set/float(total_hosts),3)


  #Finding total mean communication time 
  sync_regex = re.compile((run_identifier) + r',\(NULL\),0\s,\sSYNC_.*WARD_(?i)' + re.escape(benchmark) + r'_0_\d*'  +r',.*' + r',\d*,(\d*)')
  sync_all_hosts = re.findall(sync_regex, log_data)
  if sync_all_hosts is None:
    sync_regex = re.compile((run_identifier) + r',\(NULL\),0\s,\sSYNC_PU.._(?i)' + re.escape(benchmark) + r'_0_\d*'  +r',.*' + r',\d*,(\d*)')
    sync_all_hosts = re.findall(sync_regex, log_data)
  num_arr = numpy.array(map(int,sync_all_hosts))

  sum_sync = numpy.sum(num_arr, axis=0)

  sync_firstItr_regex = re.compile((run_identifier) +r',\(NULL\),0\s,\sSYNC_.*WARD_FirstItr_(?i)' + re.escape(benchmark) + r'_0_\d*'  +r',.*' + r',\d*,(\d*)')
  sync_firstItr_all_hosts = re.findall(sync_firstItr_regex, log_data)
  if sync_firstItr_all_hosts is None:
    sync_firstItr_regex = re.compile((run_identifier) +r',\(NULL\),0\s,\sSYNC_PU.._FirstItr_(?i)' + re.escape(benchmark) + r'_0_\d*'  +r',.*' + r',\d*,(\d*)')
    sync_firstItr_all_hosts = re.findall(sync_firstItr_regex, log_data)
  num_arr_firstItr = numpy.array(map(int,sync_firstItr_all_hosts))

  # TOTAL SYNC TIME
  sum_sync += numpy.sum(num_arr_firstItr, axis=0)
  mean_sync_time = sum_sync/float(total_hosts)
  mean_sync_time = round(mean_sync_time/divisor,3)

  #Finding total communication volume in bytes 
  sync_bytes_regex = re.compile((run_identifier) + r',\(NULL\),0\s,\sSYNC_PU.._SEND_BYTES_(?i)' + re.escape(benchmark) + r'_0_\d*'  +r',.*' + r',\d*,(\d*)')
  sync_bytes_all_hosts = re.findall(sync_bytes_regex, log_data)
  num_arr = numpy.array(map(int,sync_bytes_all_hosts))

  sum_sync_bytes = numpy.sum(num_arr, axis=0)
  print "BYTES : ", sum_sync_bytes

  sync_bytes_firstItr_regex = re.compile((run_identifier) +r',\(NULL\),0\s,\sSYNC_PU.._SEND_BYTES_FirstItr_(?i)' + re.escape(benchmark) + r'_0_\d*'  +r',.*' + r',\d*,(\d*)')
  sync_bytes_firstItr_all_hosts = re.findall(sync_bytes_firstItr_regex, log_data)
  num_arr_firstItr = numpy.array(map(int,sync_bytes_firstItr_all_hosts))

  # TOTAL BYTES EXCHANGED
  sum_sync_bytes += numpy.sum(num_arr_firstItr, axis=0)
  print "BYTES : ", sum_sync_bytes
  total_sync_bytes = sum_sync_bytes


  #75ae6860-be9f-4498-9315-1478c78551f6,(NULL),0 , NUM_WORK_ITEMS_0_0,0,0,262144
  #Total work items, averaged across hosts
  work_items_regex = re.compile((run_identifier) + r',\(NULL\),0\s,\sNUM_WORK_ITEMS_0_\d*,\d*,\d*,(\d*)')
  work_items = re.findall(work_items_regex, log_data)
  print work_items
  num_arr = numpy.array(map(int,work_items))
  total_work_item = numpy.sum(num_arr, axis=0)
  print total_work_item



  ## Get Graph_init, HG_init, total
  #81a5b117-8054-46af-9a23-1f28e5ed1bba,(NULL),0 , TIMER_GRAPH_INIT,0,0,306
  #timer_graph_init_regex = re.compile((run_identifier) +r',\(NULL\),0\s,\sTIMER_GRAPH_INIT,\d*,\d*,(\d*)')
  timer_hg_init_regex = re.compile((run_identifier) +r',\(NULL\),0\s,\sTIMER_HG_INIT' + r',\d*,\d*,(\d*)')
  timer_hg_init_all_hosts = re.findall(timer_hg_init_regex, log_data)

  num_arr = numpy.array(map(int,timer_hg_init_all_hosts))
  avg_hg_init_time = float(numpy.sum(num_arr, axis=0))/float(total_hosts)
  avg_hg_init_time = round((avg_hg_init_time / divisor),3)
  load_time = avg_hg_init_time

  print "avg_hg_init time : ", avg_hg_init_time

  timer_total_regex = re.compile((run_identifier) +r',\(NULL\),0\s,\sTIMER_TOTAL' + r',\d*,\d*,(\d*)')


  #timer_graph_init = timer_graph_init_regex.search(log_data)
  #timer_hg_init = timer_hg_init_regex.search(log_data)
  timer_total = timer_total_regex.search(log_data)
  if timer_total is not None:
    total_time = float(timer_total.group(1))
    total_time /= divisor
    total_time = round(total_time, 3)


  num_iter_regex = re.compile((run_identifier) +r',\(NULL\),0\s,\sNUM_ITERATIONS_0' + r',\d*,\d*,(\d*)')
  num_iter_search = num_iter_regex.search(log_data)
  if num_iter_regex is not None:
    if num_iter_search is None:
      num_iter = -1
    else:
      num_iter = num_iter_search.group(1)
    print "NUM_ITER : ", num_iter

  return mean_time,rep_factor,mean_do_all,mean_exract_time,mean_set_time,mean_sync_time,total_sync_bytes,num_iter,total_work_item,load_time,total_time

'''
  if timer_graph_init is not None:
    graph_init_time = float(timer_graph_init.group(1))
    graph_init_time /= divisor
    graph_init_time = round(graph_init_time, 3)

  if timer_hg_init is not None:
    hg_init_time = float(timer_hg_init.group(1))
    hg_init_time /= divisor
    hg_init_time = round(hg_init_time, 3)

  if timer_total is not None:
    total_time = float(timer_total.group(1))
    total_time /= divisor
    total_time = round(total_time, 3)

  print graph_init_time
  print hg_init_time
  print total_time
'''

def get_basicInfo(fileName, run_identifier):

  print ("IDENTIFIER : ", str(run_identifier))
  hostNum_regex = re.compile(re.escape(run_identifier) + r',\(NULL\),0\s,\sHosts,0,0,(\d*)')
  cmdLine_regex = re.compile(re.escape(run_identifier) + r',\(NULL\),0\s,\sCommandLine,0,0,(.*)')
  threads_regex = re.compile(re.escape(run_identifier) + r',\(NULL\),0\s,\sThreads,0,0,(\d*)')
  runs_regex = re.compile(re.escape(run_identifier) + r',\(NULL\),0\s,\sRuns,0,0,(\d*)')

  log_data = open(fileName).read()

  hostNum    = ''
  cmdLine    = ''
  threads    = ''
  runs       = ''
  benchmark  = ''
  algo_type  = ''
  cut_type   = ''
  input_graph = ''

  hostNum_search = hostNum_regex.search(log_data)
  print hostNum_regex.pattern
  print cmdLine_regex.pattern
  if hostNum_search is not None:
    hostNum = hostNum_search.group(1)

  cmdLine_search = cmdLine_regex.search(log_data)
  if cmdLine_search is not None:
    cmdLine = cmdLine_search.group(1)

  threads_search = threads_regex.search(log_data)
  if threads_search is not None:
    threads = threads_search.group(1)

  runs_search    = runs_regex.search(log_data)
  if runs_search is not None:
    runs = runs_search.group(1)
  if runs == "":
    runs = "3"

  print ("CMDLINE : ", cmdLine)
  split_cmdLine_algo = cmdLine.split()[0].split("/")[-1].split("_")
  print split_cmdLine_algo
  benchmark = split_cmdLine_algo[0]
  algo_type = '-'.join(split_cmdLine_algo[1:])

  split_cmdLine_input = cmdLine.split()[1].split("/")
  input_graph_name = split_cmdLine_input[-1]
  input_graph = input_graph_name.split(".")[0]

  print cmdLine
  split_cmdLine = cmdLine.split()
  print split_cmdLine
  cut_type = "edge-cut"
  for index in range(0, len(split_cmdLine)):
    if split_cmdLine[index] == "-enableVertexCut=1":
      cut_type = "vertex-cut"
      break
    elif split_cmdLine[index] == "-enableVertexCut":
         cut_type = "vertex-cut"
         break
    elif split_cmdLine[index] == "-enableVertexCut=0":
         cut_type = "edge-cut"
         break


  devices = str(hostNum) + " CPU"
  deviceKind = "CPU"
  for index in range(2, len(cmdLine.split())):
    split_cmdLine_devices = cmdLine.split()[index].split("=")
    if split_cmdLine_devices[0] == '-pset':
      devices_str = split_cmdLine_devices[-1]
      cpus = devices_str.count('c')
      gpus = devices_str.count('g')
      if str(cpus + gpus) == hostNum and gpus > 0:
        if cpus == 0:
          devices = str(gpus) + " GPU"
          deviceKind = "GPU"
        else:
          devices = str(cpus) + " CPU + " + str(gpus) + " GPU"
          deviceKind = "CPU+GPU"
          hostNum = str(int(hostNum) - cpus)
      break

  return hostNum, cmdLine, threads, runs, benchmark, algo_type, cut_type, input_graph, devices, deviceKind

def format_str(col):
  max_len = 0
  for c in col:
    if max_len < len(str(c)):
      max_len = len(str(c))
  return max_len

def main(argv):
  inputFile = ''
  forHost = ''
  outputFile = 'LOG_output.csv'
  time_unit = 'seconds'
  try:
    opts, args = getopt.getopt(argv,"hi:n:o:md",["ifile=","node=","ofile=","milliseconds"])
  except getopt.GetoptError:
    print 'abelian_log_parser.py -i <inputFile> [-o <outputFile> -n <hostNumber 0 to hosts-1> --milliseconds]'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'abelian_log_parser.py -i <inputFile> [-o <outputFile> -n <hostNumber 0 to hosts-1> --milliseconds]'
      sys.exit()
    elif opt in ("-i", "--ifile"):
      inputFile = arg
    elif opt in ("-n", "--node"):
      forHost = arg
    elif opt in ("-o", "--ofile"):
      outputFile = arg
    elif opt in ("-m", "--milliseconds"):
      time_unit = 'milliseconds'

  if inputFile == '':
    print 'abelian_log_parser.py -i <inputFile> [-o <outputFile> -n <hostNumber 0 to hosts-1> --milliseconds]'
    sys.exit(2)

  print 'Input file is : ', inputFile
  print 'Output file is : ', outputFile
  print 'Data for host : ', forHost

  if forHost == '':
    print 'Find the slowest host and calculating everything for that host'

  #Find the unique identifiers for different runs
  log_data = open(inputFile).read()
  run_identifiers_regex = re.compile(r'(.*),\(NULL\),0\s,\sTIMER_0,0,0,\d*')
  run_identifiers = re.findall(run_identifiers_regex, log_data)
  for run_identifier in run_identifiers:
    print run_identifier

    hostNum, cmdLine, threads, runs, benchmark, algo_type, cut_type, input_graph, devices, deviceKind = get_basicInfo(inputFile, run_identifier)

    #shorten the graph names:
    if input_graph == "twitter-ICWSM10-component_withRandomWeights" or input_graph == "twitter-ICWSM10-component-transpose" or input_graph == "twitter-ICWSM10-component":
      input_graph = "twitter-50"
    elif input_graph == "twitter-WWW10-component_withRandomWeights" or input_graph == "twitter-WWW10-component-transpose" or input_graph == "twitter-WWW10-component":
      input_graph = "twitter-40"

    print 'Hosts : ', hostNum , ' CmdLine : ', cmdLine, ' Threads : ', threads , ' Runs : ', runs, ' benchmark :' , benchmark , ' algo_type :', algo_type, ' cut_type : ', cut_type, ' input_graph : ', input_graph
    print 'Devices : ', devices
    data = match_timers(inputFile, benchmark, forHost, runs, threads, time_unit, hostNum, cut_type, run_identifier)

    print data

    output_str = run_identifier + ',' + benchmark + ',' + 'abelian' + ',' + hostNum  + ',' + threads  + ','
    output_str += deviceKind  + ',' + devices  + ','
    output_str += input_graph  + ',' + algo_type  + ',' + cut_type
    print output_str


    header_csv_str = "run-id,benchmark,platform,host,threads,"
    header_csv_str += "deviceKind,devices,"
    header_csv_str += "input,variant,partition,mean_time,rep_factor,mean_do_all,mean_exract_time,mean_set_time,mean_sync_time,total_sync_bytes,num_iter,num_work_items,load_time,total_time"


    header_csv_list = header_csv_str.split(',')
    try:
      if os.path.isfile(outputFile) is False:
        fd_outputFile = open(outputFile, 'wb')
        wr = csv.writer(fd_outputFile, quoting=csv.QUOTE_NONE, lineterminator='\n')
        wr.writerow(header_csv_list)
        fd_outputFile.close()
        print "Adding header to the empty file."
      else:
        print "outputFile : ", outputFile, " exists, results will be appended to it."
    except OSError:
      print "Error in outfile opening\n"

    data_list = list(data) #[data] #list(data)
    complete_data = output_str.split(",") + data_list
    fd_outputFile = open(outputFile, 'a')
    wr = csv.writer(fd_outputFile, quoting=csv.QUOTE_NONE, lineterminator='\n')
    wr.writerow(complete_data)
    fd_outputFile.close()

'''
  ## Write ghost and slave nodes to a file.
  ghost_array = build_master_ghost_matrix(inputFile, benchmark, cut_type, hostNum, runs, threads)
  ghostNodes_file = outputFile + "_" + cut_type
  fd_ghostNodes_file = open(ghostNodes_file, 'ab')
  fd_ghostNodes_file.write("\n--------------------------------------------------------------\n")
  fd_ghostNodes_file.write("\nHosts : " + hostNum + "\nInputFile : "+ inputFile + "\nBenchmark: " + benchmark + "\nPartition: " + cut_type + "\n\n")
  numpy.savetxt(fd_ghostNodes_file, ghost_array, delimiter=',', fmt='%d')
  fd_ghostNodes_file.write("\n--------------------------------------------------------------\n")
  fd_ghostNodes_file.close()
'''

if __name__ == "__main__":
  main(sys.argv[1:])

