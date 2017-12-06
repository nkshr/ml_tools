from eval_info import eval_info

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--left',
        type = str,
        default = './result'
    )
    parser.add_argument(
        '--right',
        type = str,
        default = './result'
    )

    flags, unparsed = parser.parse_known_args() 

    left_einfo = eval_info.eval_info()
    left_einfo.read(flags.left)

    right_einfo = eval_info.eval_info()
    right_einfo.read(flags.right)

    
