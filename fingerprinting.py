import sys
import time
import logging
import threading

USAGE = "<host> <port> <count> <interval>"

try:
    # prevent scapy warning messages
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    import scapy.all as scapy
except:
    print "Scapy is a requirement (http://www.secdev.org/projects/scapy/)."
    sys.exit()

def timestr(t):
    return "{0:.25f}".format(t)

def send_packet(packet, index, answers):
    time_b = time.time()
    p = scapy.sr1(packet, verbose=False)
    time_a = time.time()
    answer = []
    for option in p['TCP'].options:
        if option[0] == 'Timestamp':
            answer.append(index)
            answer.append(option[1][0])
            answer.append(time_a)
            answer.append(time_b)
            answers.append(answer)
            return

if __name__ == "__main__":

    # process arguments
    try:
        host = sys.argv[1]
        port = sys.argv[2]
        count = int(sys.argv[3])
        interval = int(sys.argv[4]) / 1000.0
    except:
        print "USAGE:", sys.argv[0], USAGE
        sys.exit()

    # create packet
    ip = scapy.IP(dst=host)
    tcp = scapy.TCP(port, flags="S", options=[("Timestamp", (0, 0))])
    packet = ip / tcp

    #print "# args:", sys.argv[1:]
    #print "# addr:", [p.dst for p in ip]
    #print "# time:", timestr(time.time())

    # send packets
    answers = []
    threads = []
    for i in range(count):
        params = (packet, i, answers)
        thread = threading.Thread(target=send_packet, args=params)
        threads.append(thread)
        thread.start()
        time.sleep(interval)

    for i in range(count):
        threads[i].join()

    sorted_answers = {}
    for a in answers:
        sorted_answers[a[0]] = a[1:]

    for i in xrange(len(sorted_answers) - 1, -1, -1):
        sorted_answers[i] = [sorted_answers[i][0] - sorted_answers[0][0],
                             sorted_answers[i][1] - sorted_answers[0][1],
                             sorted_answers[i][2] - sorted_answers[0][2]]

    for i in xrange(len(sorted_answers)):
        print i, sorted_answers[i][0] - ((sorted_answers[i][1] + sorted_answers[i][2]) / 2)
