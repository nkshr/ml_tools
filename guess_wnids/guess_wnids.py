import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--imagenet_config',
        type = str,
        default = './structure_released.xml',
        help = ''
    )
    parser.add_argument(
        '--labels',
        type = str,
        default = './imagenet_slim_labels.txt',
        help = ''
    )
    parser.add_argument(
        '--wnid_map',
        type = str,
        default = './wnid_map.txt',
        help = '',
    )
    parser.add_argument(
        '--guessed',
        type = str,
        default = './guessed_wnid_map.txt',
        help = ''
    )

    flags, unparsed = parser.parse_known_args()

    with open(flags.labels, 'r') as f:
        labels = []
        for line in f.readlines():
            labels.append(line.replace('\n',''))
    
    with open(flags.wnid_map, 'r') as f:
        wnid_map = []
        for line in f.readlines():
            if line is not None:
                toks = line.split(maxsplit=1)
                wnid = toks[0]
                label = toks[1].replace('\n', '')
                wnid_map.append((wnid, label))

    print(len(labels))
    print(len(wnid_map))

    with open(flags.guessed, 'w') as f:
        for label in labels:
            matched_labels = []
            for elem in wnid_map:
                if label in elem[1]:
                    matched_labels.append(elem)

            if len(matched_labels) == 1:
                f.write(matched_labels[0][0]+'\n')
            elif len(matched_labels) == 0:
                print(label, 'was not found.')
            else:
                f.write("---------"+str(len(matched_labels))+"""'label matched with """+label+"--------\n")
                for matched_label in matched_labels:
                    f.write(matched_label[0]+' '+matched_label[1]+'\n')
                f.write('--------------\n')
