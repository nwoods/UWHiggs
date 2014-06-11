infile = "HZZ_events.txt"
outfile = "HZZ_skim.txt"
m4lMin = 100
m4lMax = 1000
mz1Min = 60
mz1Max = 120
mz2Min = 60
mz2Max = 120

with open(infile, 'r') as fin:
    with open(outfile, 'w') as fout:

        cands = fin.readlines()
        
        passed = []# {'run': [], 'lumi': [], 'event': [], 'm4l': [], 'mz1': [], 'mz2': [], 'pt4l': []}

        for cand in cands:
            data = cand.split(":")
            evNum = data[2]
            passDict = {}
#             passDict['run'] = float(data[0])
#             passDict['lumi'] = float(data[1])
            passDict['event'] = int(data[2])
            passDict['m4l'] =   float(data[3])
            passDict['mz1'] =   float(data[4])
            passDict['mz2'] =   float(data[5])
            passDict['pt4l'] =  float(data[9])

            if passDict['m4l'] > m4lMin and passDict['m4l'] < m4lMax \
                    and passDict['mz1'] > mz1Min and passDict['mz1'] < mz1Max \
                    and passDict['mz2'] > mz2Min and passDict['mz2'] < mz2Max:
                # put items in list as (key,val) tuples because dictionaries aren't ordered
                passed.append(sorted(passDict.items()))

        # sort by event number
        passed.sort(key=lambda d: d[0][1])

        for ev in passed:
            line = ''
            for (key,val) in ev:
                line = line + key + " : " + str(val) + "   |   "

            line = line + "\n"
            fout.write(line)


#             [run, lumi, event, m4l, mz1, mz2, massErrRaw
