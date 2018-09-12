# -*- coding: utf-8 -*-

# @Author: Balis0ng 2018-09-03 14:08:35

# 修改自他人脚本，修正了如下几个Bug：
# [1] 文件重名bug
# [2] 中文文件名Bug
# [3] 修改文件move Bug
# [4] 误删正常文件Bug
# 增加了如下功能:
# [1] 被删除的文件自动还原
# [2] 支持监控与脚本不同目录
# [3] 目录名随机化。

#use: 直接运行该脚本，然后输入待监控目录的绝对路径即可



import os
import hashlib
import shutil
import ntpath
import time
import sys
import random
import string
reload(sys) #解决中文问题
sys.setdefaultencoding('utf-8') 
CWD = raw_input('please input check dir:') #检测目录输入
FILE_MD5_DICT = {}      # 文件MD5字典
ORIGIN_FILE_LIST = []  #最开始的目录结构
# 特殊文件路径字符串
Special_path_str = 'drops_'+''.join(random.sample(string.ascii_letters + string.digits, 16))
bakstring = 'bak_'+''.join(random.sample(string.ascii_letters + string.digits, 16))
logstring = 'log_'+''.join(random.sample(string.ascii_letters + string.digits, 16))
webshellstring = 'webshell_'+''.join(random.sample(string.ascii_letters + string.digits, 16))
difffile = 'diff_'+''.join(random.sample(string.ascii_letters + string.digits, 16))
Special_string = 'drops_log'  # 免死金牌
UNICODE_ENCODING = "utf-8"
INVALID_UNICODE_CHAR_FORMAT = r"\?%02x"
# 文件路径字典
spec_base_path = os.path.realpath(os.path.join(os.getcwd(), Special_path_str))
Special_path = {
    'bak' : os.path.realpath(os.path.join(spec_base_path, bakstring)),
    'log' : os.path.realpath(os.path.join(spec_base_path, logstring)),
    'webshell' : os.path.realpath(os.path.join(spec_base_path, webshellstring)),
    'difffile' : os.path.realpath(os.path.join(spec_base_path, difffile)),
}
def isListLike(value):
    return isinstance(value, (list, tuple, set))

# 获取Unicode编码
def getUnicode(value, encoding=None, noneToNull=False):
    if noneToNull and value is None:
        return NULL
    if isListLike(value):
        value = list(getUnicode(_, encoding, noneToNull) for _ in value)
        return value
    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        while True:
            try:
                return unicode(value, encoding or UNICODE_ENCODING)
            except UnicodeDecodeError, ex:
                try:
                    return unicode(value, UNICODE_ENCODING)
                except:
                    value = value[:ex.start] + "".join(INVALID_UNICODE_CHAR_FORMAT % ord(_) for _ in value[ex.start:ex.end]) + value[ex.end:]
    else:
        try:
            return unicode(value)
        except UnicodeDecodeError:
            return unicode(str(value), errors="ignore")
            
# 目录创建
def mkdir_p(path):
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

# 获取当前所有文件路径
def getfilelist(cwd):
    filelist = []
    for root,subdirs, files in os.walk(cwd):
        for filepath in files:
            originalfile = os.path.join(root, filepath)
            if Special_path_str not in originalfile:
                filelist.append(originalfile)
    return filelist

# 计算机文件MD5值
def calcMD5(filepath):
    try:
        with open(filepath,'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            hash = md5obj.hexdigest()
            return hash
    except Exception, e:
        print u'[!] getmd5_error : ' + getUnicode(filepath)
        print getUnicode(e)
        try:
            ORIGIN_FILE_LIST.remove(filepath)
            FILE_MD5_DICT.pop(filepath, None)
        except KeyError, e:
            pass

# 获取所有文件MD5
def getfilemd5dict(filelist = []):
    filemd5dict = {}
    for ori_file in filelist:
        if Special_path_str not in ori_file:
            md5 = calcMD5(os.path.realpath(ori_file))
            if md5:
                filemd5dict[ori_file] = md5
    return filemd5dict

# 备份所有文件
def backup_file(filelist=[]):
    for filepath in filelist:
        if Special_path_str not in filepath:
            shutil.copy2(filepath, os.path.join(Special_path['bak'], ntpath.basename(filepath)+'-'+FILE_MD5_DICT[filepath]))

if __name__ == '__main__':
    print u'---------start------------'
    for value in Special_path:
        mkdir_p(Special_path[value])
    # 获取所有文件路径，并获取所有文件的MD5，同时备份所有文件
    ORIGIN_FILE_LIST = getfilelist(CWD)
    FILE_MD5_DICT = getfilemd5dict(ORIGIN_FILE_LIST)
    backup_file(ORIGIN_FILE_LIST) # 重名BUG修复
    print u'[*] pre work end!'
    while True:
        file_list = getfilelist(CWD)
        # 移除新上传文件
        diff_file_list = list(set(file_list).difference(set(ORIGIN_FILE_LIST)))
        delete_file_list = list(set(ORIGIN_FILE_LIST).difference(set(file_list)))
        # 防止任意文件被修改,还原被修改文件
        if len(diff_file_list) != 0:
            for filepath in diff_file_list:
                try:
                    f = open(filepath, 'r').read()
                except Exception as e:
                    print getUnicode(e)
                    f = ''
                if Special_string not in f:
                    try:
                        print u'[*] webshell find : ' + getUnicode(filepath)
                        shutil.move(filepath, os.path.join(Special_path['webshell'], ntpath.basename(filepath) + '.txt'))
                    except Exception as e:
                        print u'[!] move webshell error, "%s" maybe is webshell.'%getUnicode(filepath)
                        pass
                    try:
                        f = open(os.path.join(Special_path['log'], 'log.txt'), 'a')
                        f.write('newfile: ' + getUnicode(filepath) + ' : ' + str(time.ctime()) + '\n')
                        f.close()
                    except Exception as e:
                        print u'[-] log error : file move error: ' + getUnicode(e)
                        pass
        if len(delete_file_list) !=0:  #被删除的文件自动还原,请注意备份时是否有webshell，否则直接凉凉。
            for deletepath in delete_file_list:
                try:
                    print u'[*] file had be delete: '+getUnicode(deletepath)
                    deletedir = os.path.dirname(deletepath)
                    if os.path.exists(deletedir)==False:
                        os.makedirs(deletedir)
                    shutil.copy2(os.path.join(Special_path['bak'], ntpath.basename(deletepath)+'-'+FILE_MD5_DICT[deletepath]), deletepath)
                except Exception as e:
                    print u'[!] restore delete file error, "%s" can not restore.'%getUnicode(deletepath)
                    pass
                    #ORIGIN_FILE_LIST.remove(deletepath)
                    #FILE_MD5_DICT.pop(deletepath, None)
                try:
                    f = open(os.path.join(Special_path['log'], 'log.txt'), 'a')
                    f.write('delete_file:' + getUnicode(deletepath)+' : '+getUnicode(time.ctime()) + '\n')
                    f.close()
                except Exception as e:
                    print u'[-] log error : done_delete: ' + getUnicode(deletepath) 
                    pass
        md5_dict = getfilemd5dict(ORIGIN_FILE_LIST)
        for filekey in md5_dict:
            if md5_dict[filekey] != FILE_MD5_DICT[filekey]:
                try:
                    f = open(filekey, 'r').read()
                except Exception as e:
                    print getUnicode(e)
                if Special_string not in f:
                    try:
                        print u'[*] file had be change : ' + getUnicode(filekey)
                        shutil.move(filekey, os.path.join(Special_path['difffile'], ntpath.basename(filekey) + '.txt'))
                        shutil.copy2(os.path.join(Special_path['bak'], ntpath.basename(filekey)+'-'+FILE_MD5_DICT[filekey]), filekey)
                    except Exception as e:
                        print u'[!] move webshell error, "%s" maybe is webshell.'%getUnicode(filekey)
                        pass
                    try:
                        f = open(os.path.join(Special_path['log'], 'log.txt'), 'a')
                        f.write('diff_file: ' + getUnicode(filekey) + ' : ' + getUnicode(time.ctime()) + '\n')
                        f.close()
                    except Exception as e:
                        print u'[-] log error : done_diff: ' + getUnicode(filekey)
                        pass
        time.sleep(2)
