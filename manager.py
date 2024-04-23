import csv


def csv_to_dict(file_path, key_name, value_name):
    d = {}
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        next(reader)
        for row in reader:
            key = row[key_name].strip()
            value = row[value_name].strip()
            d[key] = value
    return d


def append_dict_list(d:dict, key:str, value:int):
    if (key not in d):
        d[key] = []
    d[key].append(value)


def dict_list_to_csv(d: dict, path:str):
     with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key, value in d.items():
                writer.writerow([key.upper(), str(value)])


def csv_to_dict_list(filename):
    data_dict = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            key = row[0]
            values = row[1].strip('[]').split(',')
            values = list(map(str, values))
            data_dict[key] = values
    return data_dict


def dict_dict_to_csv(data, file_path, headers):
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(headers)
        
        for outer_key, inner_dict in data.items():
            for inner_key, value in inner_dict.items():
                inner_key = inner_key.strip(" '")
                writer.writerow([outer_key, inner_key, value])


def add_dict(d:dict, key:str, value:int):
    if (key not in d):
        d[key] = 0
    d[key] += value


def add_dict_dict(d:dict, key:str):
    if (key not in d):
        d[key] = {}


def max_dict(dmax:dict, d:dict, key:str):    
    if (key not in dmax):
        dmax[key] = 0
    dmax[key] = max(dmax[key], d[key])

