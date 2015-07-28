import re

infile = open('sequences/running.txt', 'r')


def pgen(s):
    for i in range(0,len(s),3):
        pname = s[i]
        ptype = s[i+1]
        pval  = s[i+2]

        if ptype == 'i':
            pval = int(pval)
        elif ptype == 'f':
            pval = float(pval)

        yield {pname: pval}

def parammatch(s, channel):
    pdict = {}
    if 'GPIB' not in channel:
        entries = s.split(' ')
        for p in pgen(entries):
            pdict.update(p)
    else:
        pdict.update({'gpibcommand': s})

    return pdict    



linepattern = r"""
(?P<name>\w+)
\s+ \{ \s+
(?P<channel>[\w:]+)
\s+
@
(?P<time> [-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)
\s+
(?P<params>.*?)
\s+
\}
\s+
"""

def linematch(line):
    m = re.match(linepattern, line, re.X)
    if m is not None:
        gd = m.groupdict()

        gd['time'] = float(gd['time'])
        
        d = dict()
        d['time'] = gd['time']
        d['name'] = gd['name']

        u = parammatch(m.group('params'),
                       m.group('channel'))
        d.update(u)

        return d
                
               

        
if __name__ == '__main__':
    for line in infile:
        linematch(line)
    
