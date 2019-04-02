
from codecs import BOM_UTF8
from token import *

import re
import token

__all__ = token.__all__ +['detect_encoding', 'tokenize','open']

cookie_re = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)',re.ASCII)
blank_re = re.compile(br'^[ \t\f]*(?:[#\r\n]|$)',re.ASCII)


def _get_normal_name(orig_enc):
    """Imitates get_normal_name in tokenizer.c."""
    # Only care about the first 12 characters.
    enc = orig_enc[:12].lower().replace("_", "-")
    if enc == "utf-8" or enc.startswith("utf-8-"):
        return "utf-8"
    if enc in ("latin-1", "iso-8859-1", "iso-latin-1") or \
       enc.startswith(("latin-1-", "iso-8859-1-", "iso-latin-1-")):
        return "iso-8859-1"
    return orig_enc


class TokenInfo(object):
    pass


def detect_encoding(readline):
    """
    1.如果没有规定encoding,就使用`utf-8`
    2. `.py`文件首行有类似于# coding=<encoding name>
    那么detect_encoding就需要用正则抓取规定的encoding
    3.如果首行有`0xEF,0xBB,0xBF`bom，则使用`utf-8-sig`
    """
    bom_found = False
    encoding= None
    default = 'utf-8'
    def readLine():
        try:
            return readline()
        except StopIteration:
            return b''

    # 首先获取fristline先检测是否和cookie_re一致,如果合适则抓取合适的encoding
    def _find_cookie(line):
        try:
            line_str = line.decode('utf-8')
        except UnicodeDecodeError:
            msg = "invalid or missing encoding declaration"
            raise SyntaxError(msg)        
        
        match = cookie_re.match(line_str)
        if not match:
            return None
        encoding = _get_normal_name(match.group(1))

        if bom_found:
            if encoding != 'utf-8':
                msg = 'encoding problem: utf-8'
                raise SyntaxError(msg)
            
            encoding = 'utf-8-sig'

        return encoding

    firstline = readLine()    
    if firstline.startswith(BOM_UTF8):
        bom_found = True
        firstline = firstline[3:]
        default = 'utf-8-sig'
    if not firstline:
        return default,[]
    
    encoding = _find_cookie(firstline)
    if encoding:
        return encoding,[firstline]
    if not blank_re.match(firstline):

        return default,[firstline]

    secondline = readLine()
    if not secondline:
        return default,[firstline]

    encoding = _find_cookie(secondline)
    if encoding:
        return encoding,[firstline,secondline]

    return default,[firstline,secondline]




def tokenize(file):
    encdoing,exline = detect_encoding(readline)



def _tokenize(parameter_list):
    pass
    



def main():
    pass

