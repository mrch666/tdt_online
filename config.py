import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    MEDIA_FOLDER = "C:/Program Files (x86)/tdt3/bases/img/"
    MODELGOODS_PER_PAGE = 10
    serverdb=os.environ.get('SERVER_TDT')  #localchost or 127.0.0.1
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_ECHO= True
    DEBUG=True
    CACHE_TYPE="SimpleCache"
    CACHE_DEFAULT_TIMEOUT=300
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or f'''firebird://SYSDBA:masterkey@{serverdb}:3055/C:\\Program Files (x86)\\tdt3\\bases\\TDTBASE.FDB?charset=win1251'''
    # SQLALCHEMY_DATABASE_URI = os.environ.get(
    #     'DATABASE_URL') or f'''firebird://SYSDBA:masterkey@{serverdb}:3055/C:\\Program Files (x86)\\tdt3\\bases\\TDTBASE.FDB?charset
    #     =win1251&fb_library_name={os.path.join(basedir, 'libudfdll.so')}'''
