my_dict = {'ne': 4, 'ns': 3, 'nw': 2, 'en': 4, 'es': 8, 'ew': 1, 'se': 3, 'sn': 9, 'sw': 5, 'wn': 4, 'we': 4, 'ws': 6}

# should get 52

total = 0
for key, value in my_dict.items():
    total += value

print(total)