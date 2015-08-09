import cPickle as pickle
import json
import csv
import functools as ft
import operator as op

def loadstories(dataset):

    with open("datasets/" + dataset + ".json","r") as fl:
        return json.load(fl)

def loadrte(dataset):    

    with open("datasets/" + dataset + ".rte","r") as fl:
        return pickle.load(fl)

def ans(dataset):

    def corr(x):
        return map(ft.partial(op.eq,ord(x) - 0x41),range(4))

    with open("datasets/" + dataset + ".ans","r") as fl:     
        return map(corr,reduce(list.__add__,csv.reader(fl,delimiter='\t')))

    
datasets = {"dev":{"160":{"stories":loadstories("mc160.dev"),
                               "answers":ans("mc160.dev"),
                               "rtescores":loadrte("mc160.dev"),
                               "settype":"mc160",
                               },
                        "500":{"stories":loadstories("mc500.dev"),
                               "answers":ans("mc500.dev"),
                               "rtescores":loadrte("mc500.dev"),
                               "settype":"mc500",
                               },
                   },
            "train":{"160":{"stories":loadstories("mc160.train"),
                               "answers":ans("mc160.train"),
                               "rtescores":loadrte("mc160.train"),
                               "settype":"mc160",
                               },
                        "500":{"stories":loadstories("mc500.train"),
                               "answers":ans("mc500.train"),
                               "rtescores":loadrte("mc500.train"),
                               "settype":"mc500",
                               },
                    },
            "devtrain":{"160":{"stories":(loadstories("mc160.dev") +
                                          loadstories("mc160.train")),
                               "answers":(ans("mc160.dev") +
                                         ans("mc160.train")),
                               "rtescores":(loadrte("mc160.dev") +
                                            loadrte("mc160.train")),
                               "settype":"mc160",
                               },
                        "500":{"stories":(loadstories("mc500.dev") +
                                          loadstories("mc500.train")),
                               "answers":(ans("mc500.dev") +
                                          ans("mc500.train")),
                               "rtescores":(loadrte("mc500.dev") +
                                            loadrte("mc500.train")),
                               "settype":"mc500",
                               },
                        },
            "test":{"160":{"stories":loadstories("mc160.test"),
                           "answers":ans("mc160.test"),
                           "rtescores":loadrte("mc160.test"),
                           "settype":"mc160",
                           },
                    "500":{"stories":loadstories("mc500.test"),
                           "answers":ans("mc500.test"),
                           "rtescores":loadrte("mc500.test"),
                           "settype":"mc500",
                           },
                    },
            }


