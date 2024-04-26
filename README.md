## Message encoder/decoder

The script allows for embedding a message inside an image and extracting a message from an image. Uses [Pillow library](https://pillow.readthedocs.io/en/latest/index.html) to manipulate image data.

Pure steganography approach is used:
  - message is encoded by writing the LSB of blue component of a pixel RGB value
  - message is decoded by reading the LSB of blue component of a pixel RGB value

### Usage

```
usage: main.py [-h] image_path offset {encode,decode} ...     

positional arguments:
  image_path       Path to image used to encode/decode message
  offset           Message position in image file

options:
  -h, --help       show this help message and exit

Actions:
  Available actions to perform

  {encode,decode}
```

### Example

Encoding a message `msg` at offset `0x10` of `normal.png` file and exporting the resulting image to `encoded.png` file.

```
>py main.py normal.png 0x10 encode msg encoded.png      
INFO: Encoding message `msg` at offset 0x10 in normal.png
DEBUG: Data bitstream: 01101101011100110110011100000000, length: 32
DEBUG: Image dimensions: (1920, 1080)
DEBUG: 1/32: rgb(135, 182, 226) -> rgb(135, 182, 227)
DEBUG: 2/32: rgb(135, 182, 226) -> rgb(135, 182, 227)
DEBUG: 4/32: rgb(135, 182, 226) -> rgb(135, 182, 227)
DEBUG: 5/32: rgb(135, 182, 226) -> rgb(135, 182, 227)
DEBUG: 7/32: rgb(135, 182, 226) -> rgb(135, 182, 227)
DEBUG: 9/32: rgb(135, 182, 226) -> rgb(135, 182, 227)
DEBUG: 10/32: rgb(135, 182, 226) -> rgb(135, 182, 227)
DEBUG: 11/32: rgb(135, 182, 226) -> rgb(135, 182, 227)
DEBUG: 14/32: rgb(135, 182, 226) -> rgb(135, 182, 227)
DEBUG: 15/32: rgb(135, 182, 226) -> rgb(135, 182, 227)
DEBUG: 16/32: rgb(134, 181, 225) -> rgb(134, 181, 224)
DEBUG: 19/32: rgb(134, 181, 225) -> rgb(134, 181, 224)
DEBUG: 20/32: rgb(134, 181, 225) -> rgb(134, 181, 224)
DEBUG: 13/32 bits changed (40.62 %)
```

Decoding the message:

```
>py main.py encoded.png 0x10 decode 
INFO: Decoding message at offset 0x10 from encoded.png
DEBUG: Image dimensions: (1920, 1080)
DEBUG: msg[0] = 0
DEBUG: msg[1] = 1
DEBUG: msg[2] = 1
DEBUG: msg[3] = 0
DEBUG: msg[4] = 1
DEBUG: msg[5] = 1
DEBUG: msg[6] = 0
DEBUG: msg[7] = 1
DEBUG: msg[8] = 0
DEBUG: msg[9] = 1
DEBUG: msg[10] = 1
DEBUG: msg[11] = 1
DEBUG: msg[12] = 0
DEBUG: msg[13] = 0
DEBUG: msg[14] = 1
DEBUG: msg[15] = 1
DEBUG: msg[16] = 0
DEBUG: msg[17] = 1
DEBUG: msg[18] = 1
DEBUG: msg[19] = 0
DEBUG: msg[20] = 0
DEBUG: msg[21] = 1
DEBUG: msg[22] = 1
DEBUG: msg[23] = 1
DEBUG: msg[24] = 0
DEBUG: msg[25] = 0
DEBUG: msg[26] = 0
DEBUG: msg[27] = 0
DEBUG: msg[28] = 0
DEBUG: msg[29] = 0
DEBUG: msg[30] = 0
DEBUG: msg[31] = 0
DEBUG: Message terminated
DEBUG: Message bitstream: 01101101011100110110011100000000, length: 32
INFO: Decoded message: msg
```
