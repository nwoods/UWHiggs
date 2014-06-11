''' Stupid little script to parse HZZ event info to try to figure out why many events are failing ID cuts
    Nate Woods, UW Madison'''



evDict = {}
numFailed = {'e': 0, 'm': 0}

with open('HZZ_all_official.txt','r') as f:
    ev = 0
    for line in f.readlines():
        words = line.split()
        if words[0] == 'event':
            ev = int(words[2])
            if ev in evDict:
                ev = 0
                continue
            evDict[ev] = [line]
            continue
            
        if ev != 0:
            evDict[ev].append(line)
            if float(words[-1]) != 1.:
                numFailed[words[0][0]] += 1
            
with open('HZZ_all_skimmed.txt','w') as f2:
    for (event,lines) in sorted(evDict.items(),key=lambda b: b[0]):
        for line in lines:
            f2.write(line)

    for particle, number in numFailed.iteritems():
        f2.write('\n' + particle + ' failed = ' + str(number))
