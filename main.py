import argparse
import functools
import logging
import msg_img


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
    encode_parser.set_defaults(func=msg_img.encode_message_in_image)
    decode_parser = subparsers.add_parser('decode')
    decode_parser.set_defaults(func=msg_img.decode_message_from_image)
    args = main_parser.parse_args()

    # suppress PIL DEBUG logs by globally setting WARNING logging level
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.WARNING)
    msg_img.configure_logging(logging.DEBUG)

    func = args.func
    del args.func
    func(**vars(args))
