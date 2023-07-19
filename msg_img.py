import logging
import re
from PIL import Image

__all__ = [
  'encode_message_in_image',
  'decode_message_from_image',
  'configure_logging'
]

_BISTREAM_TERMINATOR = '0' * 8

_logger = logging.getLogger(__name__)


def _split_message_into_bitstream(message):
    return ''.join(f'{ord(byte):08b}' for byte in message)


def _is_bitstream_finished(terminated_bitstream):
    return (len(terminated_bitstream) % 8 == 0) and (
        terminated_bitstream[-8:] == _BISTREAM_TERMINATOR
    )


def _encode(image, offset, message):
    message_bitstream = _split_message_into_bitstream(message)
    data_bitstream = message_bitstream + _BISTREAM_TERMINATOR
    data_bitstream_length = len(data_bitstream)
    _logger.debug(f'Data bitstream: {data_bitstream}, '
                  f'length: {data_bitstream_length}')
    width, height = image.size
    _logger.debug(f'Image dimensions: {image.size}')
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
            _logger.debug(f'{bit_index}/{data_bitstream_length}: '
                          f'rgb{(r, g, b)} -> rgb{(r, g, modified_b)}')
            changed_bits_count += 1
    changed_bits_ratio = round(changed_bits_count / data_bitstream_length * 100,
                               2)
    _logger.debug(f'{changed_bits_count}/{data_bitstream_length} bits changed '
                  f'({changed_bits_ratio} %)')
    return data_bitstream


def _decode(image, offset):
    width, height = image.size
    _logger.debug(f'Image dimensions: {image.size}')
    image_length = width * height // 8
    if offset > image_length:
        raise Exception(f'The offset {offset} exceeds '
                        f'image length {image_length}')
    pixels = image.load()
    data_bitstream = ''
    bit_index = 0
    while True:
        if _is_bitstream_finished(data_bitstream):
            _logger.debug(f'Message terminated')
            break
        x = (bit_index + offset) % width
        y = (bit_index + offset) // width
        b = pixels[x, y][2]
        bit = b & 1
        data_bitstream += str(bit)
        _logger.debug(f'msg[{bit_index}] = {bit}')
        bit_index += 1
    _logger.debug(f'Message bitstream: {data_bitstream}, length: {bit_index}')
    message_bitstream = data_bitstream[:-8]
    message_bitstream_length = len(message_bitstream)
    return ''.join(chr(int(byte, 2)) for byte in re.findall('.{8}', message_bitstream))


def encode_message_in_image(image_path, offset, message, output_image_path):
    _logger.info(f'Encoding message `{message}` at offset '
                 f'{hex(offset)} in {image_path}')
    with Image.open(image_path) as image:
        _encode(image, offset, message)
        image.save(output_image_path)


def decode_message_from_image(image_path, offset):
    _logger.info(f'Decoding message at offset {hex(offset)} from {image_path}')
    with Image.open(image_path) as image:
        message = _decode(image, offset)
        _logger.info(f'Decoded message: {message}')


def configure_logging(level):
    _logger.setLevel(level)
