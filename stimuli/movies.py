import os
import shlex
import argparse
import subprocess
import numpy as np


def ffmpeg(source, vframes, out, extend = 0, image = None):
    cmd = ("ffmpeg -r 60 -i {0!s} -pix_fmt yuv420p -vcodec libx264 -vframes " +
           "{1:d} {2!s}").format(source, vframes, out)
    subprocess.run(shlex.split(cmd), check=True)
    if extend > 0:
        cmd = ('ffmpeg -i {0!s} -filter_complex ' +\
               '\"[0]trim=0:2[a];[0]setpts=PTS-2/TB[b];[0][b]overlay[c];[a][c]concat\"' + \
               ' {0!s} -y').format(out)
        subprocess.run(shlex.split(cmd), check=True)

    if not image is None:
        t = vframes * (1.0/60.0)
        cmd = ('ffmpeg -i {0!s} -i {1!s} -filter_complex '+ \
               '\"[0:v] [1:v] concat=n=2:v=1 [v] \" -c:v libx264 -strict -2 -map \"[v]\" ' +\
               '{0!s} -y').format(out, image)
        subprocess.run(shlex.split(cmd), check=True)
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

    parser.add_argument("source", type = str,
        help = "Path to scene")

    parser.add_argument("out", type = str,
        help = "Path to save movie")

    parser.add_argument("--file", '-f', type = str, default = "galileo_renders_*.png",
        help = "Name of image file")

    args = parser.parse_args()
    ff.ensureDir(args.out)

    if not ff.isDir(args.source):
        raise ValueError("Path {} not found".format(args.source))

    path_str = ff.join(args.source, args.file.replace("*", "%d"))
    files = ff.find(args.source, args.file)

    if len(files) == 0:
        print("No matches for {}".format(path_str))
        return
    elif len(files) < 13:
        print("Impossibly low number of renders present")
        return

    print("Found {0:d} image frames".format(len(files)))

    collision_file = ff.join(args.source, "galileo_collisions.npy")
    if not ff.isFile(collision_file):
        raise ValueError("Could not find {0!s}".format(collision_file))

