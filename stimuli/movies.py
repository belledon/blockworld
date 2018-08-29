import os
import shlex
import argparse
import subprocess

import numpy as np

from config import CONFIG

def ffmpeg(source, out, extend = 0, image = None):
    cmd = ("ffmpeg -r 60 -i {0!s} -pix_fmt yuv420p -vcodec libx264 "+\
           "{1!s}").format(source, out)
    subprocess.run(shlex.split(cmd), check=True)
    if extend > 0:
        cmd = ('ffmpeg -i {0!s} -filter_complex ' +\
               '\"[0]trim=0:2[a];[0]setpts=PTS-2/TB[b];[0][b]overlay[c];[a][c]concat\"' + \
               ' {0!s} -y').format(out)
        subprocess.run(shlex.split(cmd), check=True)

    # if not image is None:
    #     t = vframes * (1.0/60.0)
    #     cmd = ('ffmpeg -i {0!s} -i {1!s} -filter_complex '+ \
    #            '\"[0:v] [1:v] concat=n=2:v=1 [v] \" -c:v libx264 -strict -2 -map \"[v]\" ' +\
    #            '{0!s} -y').format(out, image)
    #     subprocess.run(shlex.split(cmd), check=True)
        # cmd = ("ffmpeg -r 60 -i {0!s} -i {3!s} -filter_complex "+\
        # "\"scale=trunc(in_w/2)*2:trunc(in_h/2)*2; " +\
        # "\"[0:v][1:v] overlay=main_w/2-overlay_w/2-90:main_h/2-overlay_h/2-50:enable='between(t,{4!s}, {5!s})'\" "+\
        # "\"[0:v][1:v] overlay=main_w/2-overlay_w/2-90:main_h/2-overlay_h/2-50:enable='between(t,{4!s}, {5!s})'\" "+\
        # " \"geq=random(1)*255:128:128;aevalsrc=-2+random(0)\" " +\
        # "-pix_fmt yuv420p -vcodec libx264 -vframes {1:d} {2!s}").format(
        #     source, vframes, out, image, t - (2./60.), t)



def main():
    parser = argparse.ArgumentParser(
        description = "Generates movie from scene")

    parser.add_argument('--src', type = str, default = 'towers',
                        help = 'Path to rendered frames')

    args = parser.parse_args()
    src = os.path.join(CONFIG['data'], args.src)
    out = os.path.basename(args.src)
    out = os.path.join(CONFIG['data'], '{0!s}_movies'.format(out))
    print(out)

    if not os.path.isdir(out):
        os.mkdir(out)

    towers = next(os.walk(src))[1]
    for tower in towers:
        video_types = next(os.walk(os.path.join(src, tower)))[1]

        for vt in video_types:
            fp = os.path.join(out, '{0!s}_{1!s}.mp4'.format(tower, vt))
            path_str = os.path.join(src, tower, vt, '%d.png')
            ffmpeg(path_str, fp)

if __name__ == '__main__':
    main()
