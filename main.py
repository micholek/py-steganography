#!/usr/bin/env python3

import argparse
import functools
import logging
import re
from PIL import Image

BISTREAM_TERMINATOR = '0' * 8

logger = logging.getLogger(__name__)


def split_message_into_bitstream(message):
    return ''.join(f'{ord(byte):08b}' for byte in message)


def is_bitstream_finished(terminated_bitstream):
    return (len(terminated_bitstream) % 8 == 0) and (
        terminated_bitstream[-8:] == BISTREAM_TERMINATOR
    )


def encode(image, offset, message):
    message_bitstream = split_message_into_bitstream(message)
    data_bitstream = message_bitstream + BISTREAM_TERMINATOR
    data_bitstream_length = len(data_bitstream)
    logger.debug(f'Data bitstream: {data_bitstream}, '
                 f'length: {data_bitstream_length}')
    width, height = image.size
    logger.debug(f'Image dimensions: {image.size}')
    image_length = width * height // 8
    if image_length < data_bitstream_length:
        raise Exception('The message will never fit in the image')
    elif offset > image_length:
        raise Exception(f'The offset {offset} exceeds image length '
                        f'{image_length}')
    elif image_length - offset < data_bitstream_length:
        raise Exception(f'The message will not fit in the image '
                        f'at offset {offset}')
    pixels = image.load()
    changed_bits_count = 0
    for bit_index, bit in enumerate(data_bitstream):
        x = (bit_index + offset) % width
        y = (bit_index + offset) // width
        r, g, b = pixels[x, y]
        modified_b = b // 2 * 2 + int(bit)
        pixels[x, y] = (r, g, modified_b)
        if b != modified_b:
            logger.debug(f'{bit_index}/{data_bitstream_length}: '
                         f'rgb{(r, g, b)} -> rgb{(r, g, modified_b)}')
            changed_bits_count += 1
    changed_bits_ratio = round(changed_bits_count / data_bitstream_length * 100,
                               2)
    logger.debug(f'{changed_bits_count}/{data_bitstream_length} bits changed '
                 f'({changed_bits_ratio} %)')
    return data_bitstream


def encode_message_in_image(image_path, offset, message, output_image_path):
    logger.info(f'Encoding message `{message}` at offset '
                f'{hex(offset)} in {image_path}')
    with Image.open(image_path) as image:
        encode(image, offset, message)
        image.save(output_image_path)


def decode(image, offset):
    width, height = image.size
    logger.debug(f'Image dimensions: {image.size}')
    image_length = width * height // 8
    if offset > image_length:
        raise Exception(f'The offset {offset} exceeds '
                        f'image length {image_length}')
    pixels = image.load()
    data_bitstream = ''
    bit_index = 0
    while True:
        if is_bitstream_finished(data_bitstream):
            logger.debug(f'Message terminated')
            break
        x = (bit_index + offset) % width
        y = (bit_index + offset) // width
        b = pixels[x, y][2]
        bit = b & 1
        data_bitstream += str(bit)
        logger.debug(f'msg[{bit_index}] = {bit}')
        bit_index += 1
    logger.debug(f'Message bitstream: {data_bitstream}, length: {bit_index}')
    message_bitstream = data_bitstream[:-8]
    message_bitstream_length = len(message_bitstream)
    return ''.join(chr(int(byte, 2)) for byte in re.findall('.{8}', message_bitstream))


def decode_message_from_image(image_path, offset):
    logger.info(f'Decoding message at offset {hex(offset)} from {image_path}')
    with Image.open(image_path) as image:
        message = decode(image, offset)
        logger.info(f'Decoded message: {message}')


def configure_logging():
    # suppress PIL DEBUG logs by globally setting WARNING logging level
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.WARNING)
    logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()
    main_parser.add_argument(
        'image_path',
        help='Path to image used to encode/decode message'
    )
    main_parser.add_argument(
        'offset',
        type=functools.partial(int, base=0),
        help='Message position in image file'
    )
    subparsers = main_parser.add_subparsers(
        title='Actions',
        description='Available actions to perform',
        required=True
    )
    encode_parser = subparsers.add_parser('encode')
    encode_parser.add_argument(
        'message',
        help='Message to encode in image file'
    )
    encode_parser.add_argument(
        'output_image_path',
        help='Path to resulting image with encoded message'
    )
    encode_parser.set_defaults(func=encode_message_in_image)
    decode_parser = subparsers.add_parser('decode')
    decode_parser.set_defaults(func=decode_message_from_image)
    args = main_parser.parse_args()

    configure_logging()
    func = args.func
    del args.func
    func(**vars(args))
