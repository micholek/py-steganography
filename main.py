#!/usr/bin/env python3

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


def encode_message_in_image(image, message, offset):
    message_bitstream = split_message_into_bitstream(message)
    data_bitstream = message_bitstream + BISTREAM_TERMINATOR
    data_bitstream_length = len(data_bitstream)
    logger.debug(f'Data bitstream length: {data_bitstream_length}')
    width, height = image.size
    logger.debug(f'Image dimensions: {image.size}')
    image_length = width * height // 8
    if image_length < data_bitstream_length:
        raise Exception('The message will never fit in the image')
    elif offset > image_length:
        raise Exception(f'The offset {offset} exceeds image length {image_length}')
    elif image_length - offset < data_bitstream_length:
        raise Exception(f'The message will not fit in the image at offset {offset}')
    pixels = image.load()
    changed_bits_count = 0
    for bit_index, bit in enumerate(data_bitstream):
        x = (bit_index + offset) % width
        y = (bit_index + offset) // width
        r, g, b = pixels[x, y]
        modified_b = b // 2 * 2 + int(bit)
        pixels[x, y] = (r, g, modified_b)
        if b != modified_b:
            logger.debug((f'{bit_index}/{data_bitstream_length}: '
                          f'rgb{(r, g, b)} -> rgb{(r, g, modified_b)}'));
            changed_bits_count += 1;
    logger.debug(f'{changed_bits_count} bits changed ({round(changed_bits_count / data_bitstream_length * 100, 2)} %)')
    return data_bitstream


def decode_message_from_image(image, offset):
    width, height = image.size
    image_length = width * height // 8
    if offset > image_length:
        raise Exception(f'The offset {offset} exceeds image length {image_length}')
    pixels = image.load()
    data_bitstream = ''
    bit_index = 0
    while not is_bitstream_finished(data_bitstream):
        x = (bit_index + offset) % width
        y = (bit_index + offset) // width
        b = pixels[x, y][2]
        bit = b & 1
        data_bitstream += str(bit)
        bit_index += 1
    message_bitstream = data_bitstream[:-8]
    return ''.join(chr(int(byte, 2)) for byte in re.findall('.{8}', message_bitstream))


def configure_logging():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING) # supress PIL debug logging
    logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    configure_logging()
    test_message = 'test message'

    logger.info(f'Message to encode: {test_message}')

    with Image.open('ee.png') as image:
        bitstream = encode_message_in_image(image, test_message, 0x100)
        image.save('ee2.png')

    with Image.open('ee2.png') as image:
        message = decode_message_from_image(image, 0x100)

    logger.info(f'Encoded message as bitstream: {bitstream}')
    logger.info(f'Decoded message: {message}')
