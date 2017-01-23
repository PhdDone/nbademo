import json

Games = {}

def splitTeamScore(ts):
    k = ts.rfind(" ")
    t = ts[:k]
    s = ts[k+1:]
    return t, s

def run(filename):
    file = open(filename, 'r')
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
            print "Error, dup key should not happen"
        else:
            Games[key] = game

        
        index += 8
    for gk in Games.keys():    
        js = json.dumps(Games[gk], ensure_ascii=False, indent=4, sort_keys=True)
        print(js)
    

if __name__ == "__main__":
    run("DEC.txt")
