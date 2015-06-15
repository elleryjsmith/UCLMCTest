import glob
import json

def loadcategories(dataset):

    cats = glob.glob("categories/" + dataset + "/*.txt")

    cts = dict()
    
    for cat in cats:
        with open(cat,"r") as fl:
            nm = cat.split("/")[2].split(".")[0].replace("|","/")
            cts[nm] = []
            for ln in fl:
                ps = ln.replace("\n","").split(".")[2].split(",")
                cts[nm].append((int(ps[0]) * 4) + int(ps[1]))

    return cts

def loadstories(dataset):

    with open("datasets/" + dataset + ".json","r") as fl:
        return json.load(fl)

    
if __name__ == "__main__":

    datasets = ["mc" + d + "." + t
                for d in ["160","500"]
                for t in ["dev","train","test"]]

    for dataset in datasets:

        stories = loadstories(dataset)
        categories = loadcategories(dataset)

        for story in stories:
            story["categories"] = [[],[],[],[]]

        for category in categories:
            for i in categories[category]:
                stories[i / 4]["categories"][i % 4].append(category)

        with open("datasets/" + dataset + ".json","w") as fl:
            json.dump(stories,fl)
