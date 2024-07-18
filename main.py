import base64
import sys
import zlib

from os.path import join as pathjoin
from os.path import isdir, isfile
from os import walk, mkdir, chdir

from colorama import Fore, init

init(autoreset=True)

def log(text, tab='', logtag=True):
    if logtag:
        print('{0}{1} {2}'.format(tab, LOG_TAG, text))
    else:
        print('{0}{1}'.format(tab, text))

def file_is_compressed(path=None, compressed_data=None):
    if compressed_data is not None:
        compressed_data = [compressed_data]
    elif path is not None:
        with open(path, 'rb') as f:
            compressed_data = [line.strip() for line in f.readlines() if line.strip() != b'']
    if len(compressed_data) == 1:
        try:
            header, compressed_src = compressed_data[0].split(b';')
            if header == b'import zlib,base64' and compressed_src[0:40]+compressed_src[-16:] == b"exec(zlib.decompress(base64.b64decode(b''[::-1])[::-1]))":
                return (True, compressed_src[40:-16][::-1])
        except Exception as e:
            pass
    return (False, None)

def pycompressor(path, save_path, decompress=False):
    with open(path, 'rb') as inpf:
        code = ""
        if decompress:
            file_compressed, compressed_src = file_is_compressed(path)
            while file_compressed:
                code = zlib.decompress(base64.b64decode(compressed_src)[::-1])
                file_compressed, compressed_src = file_is_compressed(compressed_data=code)
        else:
            code = "import zlib,base64;exec(zlib.decompress(base64.b64decode({0}[::-1])[::-1]))".format(base64.b64encode(zlib.compress(inpf.read(-1))[::-1])[::-1]).encode('utf-8')
        if code != '':
            for pathp in save_path.split('\\')[:-1]:
                try:
                    chdir(pathp+'\\')
                except:
                    try:
                        mkdir(pathp)
                        chdir(pathp+'\\')
                    except:
                        pass
            with open(save_path, 'wb') as outf:
                outf.write(code)
            return True
    return False

DECOMPRESS_MODE = '--decompress' in sys.argv
LOG_TAG = Fore.LIGHTWHITE_EX+'[PyCompressor]'+Fore.RESET

if DECOMPRESS_MODE:
    print('\n--- '+Fore.LIGHTWHITE_EX+'PyCompressor [DecompressMode]'+Fore.GREEN+' v1.0.0.0'+Fore.LIGHTRED_EX+' by rzc0d3r'+Fore.RESET+ ' ---\n')
else:
    print('\n--- '+Fore.LIGHTWHITE_EX+'PyCompressor [CompressMode]'+Fore.GREEN+' v1.0.0.0'+Fore.LIGHTRED_EX+' by rzc0d3r'+Fore.RESET+ ' ---\n')
    
try:
    INPUT = sys.argv[1]
except:
    log(Fore.RED+'No input!')
    sys.exit(-1)

SAVE_INPUT = INPUT + '_pycompressed'
if DECOMPRESS_MODE:
    if isfile(INPUT): # file
        SAVE_INPUT = INPUT.replace(INPUT.split('\\')[-1], '[PyDecompressed] '+INPUT.split('\\')[-1]).replace('[PyCompressed] ', '')
    else: # folder
        SAVE_INPUT = INPUT.replace('_pycompressed', '') + '_pydecompressed'
else: # compress mode
    if isfile(INPUT): # file
        SAVE_INPUT = INPUT.replace(INPUT.split('\\')[-1], '[PyCompressed] '+INPUT.split('\\')[-1]).replace('[PyDecompressed] ', '')

if isdir(INPUT):
    SAVE_INPUT_RPATH = SAVE_INPUT
    compressed = False
    for rpath, folders, files, in walk(INPUT):
        if files != []:
            SAVE_INPUT_RPATH = rpath.replace(INPUT, SAVE_INPUT)
            for file in files:
                if file.split('.')[-1] == 'py':
                    log('Catalog '+Fore.CYAN+rpath+Fore.RESET+' processing:')
                    break
            for file in files:
                if file.split('.')[-1] == 'py':
                    if DECOMPRESS_MODE:
                        if file_is_compressed(pathjoin(rpath, file))[0]:
                            log('Decompressing a '+Fore.YELLOW+file+Fore.RESET, '    ', False)
                        else:
                            log(Fore.YELLOW+file+Fore.RESET+' was not compressed by PyCompressor!'+Fore.LIGHTBLACK_EX+' [SKIP]'+Fore.RESET, '    ', False)
                    else:
                        log('Compressing a '+Fore.YELLOW+file+Fore.RESET, '    ', False)
                    if pycompressor(pathjoin(rpath, file), pathjoin(SAVE_INPUT_RPATH, file), DECOMPRESS_MODE):
                        compressed = True
    if compressed:
        log('Saved to '+Fore.LIGHTYELLOW_EX+SAVE_INPUT+Fore.RESET)
elif isfile(INPUT):
    if INPUT.split('.')[-1] == 'py':
        if DECOMPRESS_MODE:
            if file_is_compressed(INPUT)[0]:
                log('Decompressing a '+Fore.YELLOW+INPUT+Fore.RESET)
            else:
                log(Fore.YELLOW+INPUT+Fore.RESET+' was not compressed by PyCompressor!'+Fore.LIGHTBLACK_EX+' [SKIP]'+Fore.RESET, '', False)
        else:
            log('Compressing a '+Fore.YELLOW+INPUT+Fore.RESET)
        if pycompressor(INPUT, SAVE_INPUT, DECOMPRESS_MODE):
            log('Saved to '+Fore.LIGHTYELLOW_EX+SAVE_INPUT+Fore.RESET)
    else:
        log(Fore.YELLOW+INPUT+Fore.RESET+' is not a python file! '+Fore.LIGHTBLACK_EX+' [SKIP]'+Fore.RESET, '', False)