import json
import sys
import os
import glob

Games = {}
def splitTeamScore(ts):
    k = ts.rfind(" ")
    t = ts[:k]
    s = ts[k+1:]
    return t, s

def run(filename):
    file = open(filename, 'r')
    outfile = open(filename+".json", 'w')
    content = file.readlines()
    index = 0;
    while index < len(content):
        game = {}
        gid = content[index].strip()
        gdate = content[index + 1].strip()
        gtime = content[index + 2].strip()
        vt = content[index + 3].strip()
        ht = content[index + 4].strip()
        vs = -1
        hs = -1
        # game finished
        if (gtime == "FINAL"):
            vt, vs = splitTeamScore(vt)
            ht, hs = splitTeamScore(ht)
            #print vt
            #print vs
        game["id"] = gid
        game["date"] = gdate
        game["time"] = gtime
        game["ht"] = ht
        game["vt"] = vt
        game["hs"] = hs
        game["vs"] = vs

        key = ht + vt + gdate
        if key in Games:
            print key
            print "Error, dup key should not happen"
        else:
            Games[key] = game

        
        index += 8
    for gk in Games.keys():    
        js = json.dumps(Games[gk], ensure_ascii=False, indent=4, sort_keys=True)
        outfile.write(js)
        outfile.write('\n')
    

if __name__ == "__main__":
    path = "/Users/yuanzhedong/Documents/mobvoi/nba-crawler/nbademo/data/"
    # for fname in glob.glob(os.path.join(path,"*.txt")):
    #     print fname
    #     run(fname)
    run("./data/JAN.txt")
