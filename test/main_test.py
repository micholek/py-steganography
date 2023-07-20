import logging
import unittest
import msg_img

class TestLogging(unittest.TestCase):
  def test_configure_logging(self):
    for level in [logging.DEBUG, logging.INFO, logging.WARNING]:
      with self.subTest(level=level):
        msg_img.configure_logging(level)
        self.assertEqual(msg_img._logger.level, level)


if __name__ == '__main__':
  unittest.main()
