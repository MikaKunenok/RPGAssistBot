#class Diseasereader loads Disease instances from json

import json
import os

from disease import Disease

class ReaderError(EnvironmentError):
    pass

def from_dict(disease: dict):
    name = disease.get('name', None)
    period = disease.get('period', None)
    deadly = disease.get('deadly', None)
    treats = disease.get('treats', None)
    stages = disease.get('stages', None)
    if name is None:
        raise ReaderError('no name in ' + str(disease))
    if period is None:
        raise ReaderError('no period in ' + str(disease))
    if deadly is None:
        raise ReaderError('no deadly in ' + str(disease))
    if treats is None:
        raise ReaderError('no treats in ' + str(disease))
    if stages is None:
        raise ReaderError('no stages in ' + str(disease))
    return Disease(name=name,
                  period=period,
                  deadly=deadly,
                  treats=treats,
                  stages=stages
                      )
def from_str(some_input):
    disease = json.loads(some_input)
    return from_dict(disease)

def from_multistr(some_input):
    for disease in json.loads(some_input):
        yield from_dict(disease)

def from_file(filename: str):
    _input = open(filename)
    disease = json.load(_input)
    _input.close()
    return from_dict(disease)

def from_multifile(filename: str):
    _input = open(filename)
    for disease in json.load(_input):
        yield  from_dict(disease)
    _input.close()

def from_dir(dirname: str):
    for filename in os.listdir(dirname):
        _input = open(dirname + filename)
        disease = json.load(_input)
        _input.close()
        yield from_dict(disease)
