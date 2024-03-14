with open('MuCGEC_test.txt') as f_in:
    with open('mucgec.test', 'w') as f_out:
        for line in f_in:
            line = line.strip().split('\t')
            print('S', line[1], sep='\t', file=f_out)
            print('T', end='\n\n', file=f_out)
