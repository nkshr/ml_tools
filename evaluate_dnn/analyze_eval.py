from eval_info import eval_info

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--left',
        type = str,
        default = './left'
    )
    parser.add_argument(
        '--right',
        type = str,
        default = './right'
    )
    parser.add_argument(
        '--result',
        type = str,
        default = './result.csv'
    )

    flags, unparsed = parser.parse_known_args() 

    left_einfo = eval_info.eval_info()
    left_einfo.read(flags.left)

    right_einfo = eval_info.eval_info()
    right_einfo.read(flags.right)

    if not left_einfo.get_class_count() != right_einfo.get_class_count():
        print('Error : {} and {} must have same classes.'.format(flags.left, flags.right))
        exit()

    roc_list = []
    for class_id in range(left_einfo.get_class_count()):
        left_class_info = left_einfo.get_class_info(class_id) 
        right_class_info = right_einfo.get_class_info(class_id)
        roc_list.append(right_class_info.top1_rate / left_class_info.top1_rate)

    sorted_indexes = np.argsort(roc_list)[::-1]

    with open(flags.result, 'r') as f:
        for class_id in sorted_indexes:
            left_cinfo = left_einfo.get_class_info(class_id)
            right_cinfo = right_einfo.get_class_info(class_id)
            roc = roc_list(class_id)
            text = '{},{},{},{},{}\n'.format(class_id, left_cinfo.label, left_cinfo.top1_rate, right_cinfo.top1_rate, roc)
            f.write(text)
