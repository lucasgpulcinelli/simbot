
import consts


quotes = []

fp = open(consts.quotes_file, "r")

for line in fp:
    if line[0] == '*':
        quotes.append(line[2:-1])
    
fp.close()
