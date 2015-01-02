
raw_instances = []

with open('HIGGS.csv', 'r') as f:
	# use iterator to skip the first label row
	lineIter = iter(f)
	max = 0
	for line in lineIter:
		entry = line.strip().split(',')
		entry[0] = int(float(entry[0]))
		raw_instances.append(entry)
		max = max + 1
		if max == 10000:
			break


print raw_instances[2]

