from tokenize33 import detect_encoding
from unittest import TestCase


class TestDetectEncoding(TestCase):
    
    def get_readline(self,lines):
        index = 0
        def readline():
            nonlocal index
            line = lines[index]
            index += 1
            return line
        return readline

    def test_no_bom_no_cookie(self):
        lines = (b'#something\n',
                 b'#hello\n'
                )
        encoding,expectedlines = detect_encoding(self.get_readline(lines))                 
        self.assertEqual(encoding,'utf-8')
        self.assertEqual(expectedlines,list(lines[:]))

    def test_bom_no_cookie(self):
        lines =(b'\xef\xbb\xbf# something\n',
                b'print(something)\n')
        encoding,expectedlines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding,'utf-8-sig')
        self.assertEqual(expectedlines, [b'# something\n', b'print(something)\n'])

    def test_no_bom_cookie(self):
        lines = (b'# -*- coding: latin-1 -*-\n',
                b'print(something)\n')
        encoding,expectedlines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding, 'iso-8859-1')
        self.assertEqual(expectedlines, [b'# -*- coding: latin-1 -*-\n'])

    def test_bom_and_cookie_first_line(self):
        lines =(b'\xef\xbb\xbf#coding=utf-8\n',
                b'print(something)\n')
        encoding,expectedlines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding, 'utf-8-sig')
        self.assertEqual(expectedlines, [b'#coding=utf-8\n'])
      
    def test_mismatch_bom_and_cookie_first_line(self):
        lines =(b'\xef\xbb\xbf# -*- coding: latin-1 -*-\n',
                b'print(something)\n')
        readline = self.get_readline(lines)
        self.assertRaises(SyntaxError, detect_encoding, readline)


if __name__ == "__main__":
    unittest.main()
