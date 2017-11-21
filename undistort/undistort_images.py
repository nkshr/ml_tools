import argparse
import subprocess
import os

program = "/home/ubuntu/ml/ml_tools/undistort/undistort"
action_camera_photo_air_intrinsic = "/home/ubuntu/Action_Camera/calib_result/air/photo/intrinsic_matrix.txt"
action_camera_photo_air_distortion = '/home/ubuntu/Action_Camera/calib_result/air/photo/distortion_matrix.txt'
action_camera_movie_water_intrinsic = "/home/ubuntu/Action_Camera/calib_result/water/movie/intrinsic_matrix.txt"
action_camera_movie_water_distortion = "/home/ubuntu/Action_Camera/calib_result/water/movie/distortion_matrix.txt"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_dir',
                        type = str,
                        default = './',
                        help = ''
    )
    parser.add_argument('--mode',
                        type = str,
                        default = 'photo',
                        help = '',
    )
    parser.add_argument('--env',
                        type = str,
                        default = 'air',
                        help =''
    )
    parser.add_argument('--debug',
                        action = "store_true",
                        help = ''
    )
    parser.add_argument('--prefix',
                        type = str,
                        default = 'cropped_',
                        help=''
    )

    flags, unparsed = parser.parse_known_args()

    if flags.debug == 'y':
        print(flags)

    intrinsic = ''
    distortion = ''
    if flags.mode == 'photo':
        print('photo')
        if flags.env  == 'air':
            intrinsic = action_camera_photo_air_intrinsic
            distortion = action_camera_photo_air_distortion
        elif flags.env == 'water':
            intrinsic = action_camera_photo_water_intrinsic
            distortion = action_camera_photo_water_distortion
    elif flags.mode == "movie":
        if flags.env == 'air':
            intrinsic = action_camera_movie_air_intrinsic
            distortion = action_camera_movie_air_distortion
        elif flags.env == 'water':
            intrinsic = action_camera_movie_water_intrinsic
            distortion = action_camera_movie_water_distortion
            
    imgs = [file for file in os.listdir(flags.image_dir) if file.endswith(('png', 'jpg', 'JPG'))]
    for img in imgs:
        img = os.path.join(flags.image_dir, img)
        uimg = img
        #cmd = [program, intrinsic, distortion, img, uimg]
        cmd = program + ' ' + intrinsic + ' ' + distortion + ' ' + img + ' ' + uimg
        if flags.debug:
            print(cmd)
        else:
            subprocess.call(cmd, shell = True)
