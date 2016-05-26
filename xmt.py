# -*- coding: utf-8 -*-
import os
import subprocess
import click
import codecs

try:
    import simplejson as json
except ImportError:
    import json

__author__ = 'banxi'


def _json_from_path(path):
    with codecs.open(path, mode='r', encoding='utf-8') as f:
        return json.loads(f.read())


def _json_to_path(jsonobj, path):
    json_str = json.dumps(jsonobj, indent='  ')
    with codecs.open(path, mode='w', encoding='utf-8') as f:
        f.write(json_str)


class ContentsJson(object):
    def __init__(self, path):
        with codecs.open(path, mode='r', encoding='utf-8') as f:
            self.contents = json.loads(f.read())
        self.path = path

    def for_json(self):
        return self.contents

    @property
    def images(self):
        return self.contents['images']

    @property
    def has_2x_image(self):
        for img in self.images:
            if img['scale'] == '2x' and img.get('filename'):
                return True
        return False

    def save(self):
        json_str = json.dumps(self.contents, indent='  ')
        with codecs.open(self.path, mode='w', encoding='utf-8') as f:
            f.write(json_str)

    def update_2x_image(self, image_name):
        for img in self.images:
            if img['scale'] == '2x':
                img['filename'] = image_name
        self.save()


def _g2x(path, imageset_name=None):
    image_3x_basename = os.path.basename(path)
    image_2x_basename = image_3x_basename
    if imageset_name:
        image_2x_basename = imageset_name + '@2x.png'
        fullpath = os.path.join(os.path.dirname(path), image_2x_basename)
        if os.path.exists(fullpath):
            image_2x_basename = imageset_name + "@2x-1.png"
    else:
        image_2x_basename = path + '.@2x'
        if '@3x' in image_3x_basename:
            image_2x = image_3x_basename.replace("@3x", "@2x")
        else:
            base_name, ext = image_3x_basename.rsplit('.')
            # jpeg file automatically convert to png
            image_2x_basename = base_name + '@2x.png'
            fullpath = os.path.join(os.path.dirname(path), image_2x_basename)
            if os.path.exists(fullpath):
                image_2x_basename = imageset_name + "@2x-1.png"
    image_3x = path
    image_2x = os.path.join(os.path.dirname(path), image_2x_basename)
    print("convert 3x file %s to 2x file %s" % (image_3x, image_2x))
    # convert $img -resize  66.66%x66.66% $newImg
    convert_args = [
        'convert',
        image_3x,
        '-resize',
        '66.66%x66.66%',
        image_2x,
    ]
    status_code = subprocess.call(convert_args)
    if status_code != 0:
        print("Failed to g2x for file %s" % image_3x)
    return status_code == 0, image_2x_basename


def _walk_g2x_root(root_path):
    for root, dirs, files in os.walk(root_path):
        if root.endswith(".appiconset"):
            print("ignore appiconset dir")
            continue
        for name in files:
            if not ('png' in name or 'jpg' in name or 'jpeg' in name):
                continue
            imageset_name = None
            imageset_dir = None
            if root.endswith('.imageset'):
                imageset_dir = os.path.split(root)[-1]
                imageset_name = imageset_dir.split('.')[0]
            path = os.path.join(root, name)
            print("Current Path %s" % path)
            if imageset_dir and imageset_name:
                json_path = os.path.join(root, 'Contents.json')
                contents = ContentsJson(json_path)
                if contents.has_2x_image:
                    print("%s has 2x image" % name)
                    continue
                else:
                    print("Try g2x for %s" % name)
                    ok, image_2x_basename = _g2x(path, imageset_name)
                    if ok:
                        contents.update_2x_image(image_2x_basename)

            else:
                _g2x(path, imageset_name)


@click.group()
def xmt():
    pass


@xmt.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=True))
def g2x(path):
    if os.path.isfile(path):
        _g2x(path)
    elif os.path.isdir(path):
        print("is path")
        _walk_g2x_root(path)


@xmt.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=True))
def mkappicon(path):
    contents_path = os.path.join(os.path.dirname(__file__), "AppIconContents.json")
    contents = _json_from_path(contents_path)

    def make_pixel_size(point_size,  scale):
        w, h = point_size.split('x')
        scale_value = float(scale[0])
        return "%dx%d" % (float(w) * scale_value, float(h) * scale_value)

    folder = "AppIcon.appiconset"
    if not os.path.exists(folder):
        os.mkdir(folder)

    for image in contents["images"]:
        point_size = image["size"]
        scale = image["scale"]
        pixel_size = make_pixel_size(point_size, scale)
        convert_args = [
            'convert',
            path,
            '-resize',
            pixel_size,
            os.path.join(folder, image["filename"]),
        ]
        subprocess.check_call(convert_args)

    contents_json_path = os.path.join(folder, 'Contents.json')
    _json_to_path(contents, contents_json_path)


def main():
    xmt()


if __name__ == '__main__':
    main()
