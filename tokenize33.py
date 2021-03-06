
from codecs import BOM_UTF8
from token import *

from collections import namedtuple
import re
import itertools as _itertools
import token

__all__ = token.__all__ +['detect_encoding', 'tokenize','open']

NL = N_TOKENS + 1
tok_name[NL] = 'NL'
ENCODING = N_TOKENS + 2
tok_name[ENCODING] = 'ENCODING'
# tok_name[NEWLINE] ='NEWLINE'


cookie_re = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)',re.ASCII)
blank_re = re.compile(br'^[ \t\f]*(?:[#\r\n]|$)',re.ASCII)

def group(*choices): return '(' + '|'.join(choices) + ')'
def any(*choices): return group(*choices) + '*'
def maybe(*choices): return group(*choices) + '?'



# Number
Decnumber = r'(?:0(?:_?0)*|[1-9](?:_?[0-9])*)'
#whitespace
Whitespace = r'[ \f\t]*'
Ignore =  any(r'\\\r?\n') 

#comment
Comment = r'#[^\r\n]*'

# # allToken =Whitespace+'|'+Decnumber+'|'+Newline
allToken = group(Decnumber,Comment,Ignore)



def _compile(expr):
    return re.compile(expr,re.UNICODE)



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


class TokenInfo(namedtuple('TokenInfo','type string start end line')):
    def __repr__(self):
        annotated_type = '%d (%s)' % (self.type, tok_name[self.type])
        return ('TokenInfo(type=%s, string=%r, start=%r, end=%r, line=%r)' %
                self._replace(type=annotated_type))

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




def tokenize(readline):
    from itertools import chain
    encdoing,fline = detect_encoding(readline)
    gen=iter(readline,b'')
    return _tokenize(chain(fline,gen).__next__, encdoing)
    # return chain(fline).__next__()

# token种类NEWLINE,INDENT,DEDENT,identifier,keywords
def test_tokenize(readline,encoding):
    if encoding is not None:
        if encoding == 'utf-8-sig':
            encoding = 'utf-8'
        yield TokenInfo(ENCODING,encoding,(0,0),(0,0),'')
    
    while True:
        line = readline()
        line=line.decode(encoding)
        print(line)
        # print('s')


def _tokenize(readline, encoding):
    lnum = 0
    numberchars = '0123456789'

    if encoding is not None:
        if encoding == 'utf-8-sig':
            encoding = 'utf-8'
        yield TokenInfo(ENCODING,encoding,(0,0),(0,0),'')

    while True:
        try:
            line = readline()
        except StopIteration:
            line = b''
      
        if encoding is not None:
            line = line.decode(encoding)
     
        lnum += 1    
        pos,length = 0,len(line)
       
        if line and line[pos] in '#\r\n':
            if line[pos] == '#':
                comment_token = line[pos:].rstrip('\r\n')
                yield TokenInfo(COMMENT,comment_token,(lnum,pos),(lnum,pos+len(comment_token)),line)     
            pos += len(comment_token)
            yield TokenInfo(NL,line[pos:],(lnum,pos),(lnum,len(line)),line)
            continue

        if not line:
            break

        while pos < length:
            # 解析有用的tokens组，过滤无用的
            # 支持NUmber
            # 使用正则表达式过滤
            Prematch = _compile(allToken).match(line,pos)
         
            if Prematch:
                start,end =Prematch.span(1)
                startpos,endpos,pos =(lnum,start),(lnum,end),end
                    
                token ,initial= line[start:end],line[start]
                if initial in numberchars:
                   
                    yield TokenInfo(NUMBER,token, startpos,endpos,line)
                elif initial in '\r\n':
                    yield TokenInfo(NEWLINE,token,startpos,endpos,line)

                elif initial.isidentifier():               # ordinary name
                    yield TokenInfo(NAME, token, startpos,endpos, line)

            else:
                pos += 1
           


# 1.NEWLINE和NL都是 \r\n或者\n,如何判断
#comment正则，才能获取comment Token
# 关键字都是NAME，符号就是OP


def main():
    with open('some.py','rb') as f:
        tokens = list(tokenize(f.readline))
    for t in tokens:
        print(t)

if __name__ == "__main__":
    main()