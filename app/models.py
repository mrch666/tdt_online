# coding: utf-8
from sqlalchemy import BigInteger, Column, Computed, Date, DateTime, Float, Index, Integer, LargeBinary, SmallInteger, \
    String, Table, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import quoted_name
from sqlalchemy_serializer import SerializerMixin

from app import login
from flask_login import UserMixin

Base = declarative_base()
metadata = Base.metadata


@login.user_loader
def load_user(id):
    return User.query.get(id)


class DImport(Base):
    __tablename__ = quoted_name('_d_import', True)

    id = Column(quoted_name('id', True), Integer, primary_key=True)
    d_id = Column(quoted_name('d_id', True), Text(12), server_default=text("'0'"))
    d_td = Column(quoted_name('d_td', True), Integer)
    d_date = Column(quoted_name('d_date', True), Date)
    d_num = Column(quoted_name('d_num', True), String(200))
    f_id = Column(quoted_name('f_id', True), Text(12), server_default=text("'0'"))
    f_inn = Column(quoted_name('f_inn', True), String(40))
    f_name = Column(quoted_name('f_name', True), String(250))
    f_rs = Column(quoted_name('f_rs', True), String(125))
    f_bank = Column(quoted_name('f_bank', True), String(250))
    f_bic = Column(quoted_name('f_bic', True), String(20))
    f_ks = Column(quoted_name('f_ks', True), String(125))
    f_kpp = Column(quoted_name('f_kpp', True), String(30))
    p_id = Column(quoted_name('p_id', True), Text(12), server_default=text("'0'"))
    p_inn = Column(quoted_name('p_inn', True), String(40))
    p_name = Column(quoted_name('p_name', True), String(250))
    p_rs = Column(quoted_name('p_rs', True), String(125))
    p_bank = Column(quoted_name('p_bank', True), String(250))
    p_bic = Column(quoted_name('p_bic', True), String(20))
    p_ks = Column(quoted_name('p_ks', True), String(125))
    p_kpp = Column(quoted_name('p_kpp', True), String(30))
    d_pt = Column(quoted_name('d_pt', True), String(30))
    d_ot = Column(quoted_name('d_ot', True), String(30))
    d_queue = Column(quoted_name('d_queue', True), String(30))
    d_note = Column(quoted_name('d_note', True), String(250))
    d_term = Column(quoted_name('d_term', True), Date)
    d_sum = Column(quoted_name('d_sum', True), Float)
    ids_opl = Column(quoted_name('ids_opl', True), String(250))
    f_id_state = Column(quoted_name('f_id_state', True), Integer)
    p_id_state = Column(quoted_name('p_id_state', True), Integer)


class AccCash(Base):
    __tablename__ = quoted_name('acc_cash', True)

    rangid = Column(quoted_name('rangid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    cashid = Column(quoted_name('cashid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    access = Column(quoted_name('access', True), Integer)
    accessout = Column(quoted_name('accessout', True), Integer)


class AccFirmagood(Base):
    __tablename__ = quoted_name('acc_firmagoods', True)

    rangid = Column(quoted_name('rangid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    firmaid = Column(quoted_name('firmaid', True), Text(12), primary_key=True, nullable=False,
                     server_default=text("'0'"))


class AccFolder(Base):
    __tablename__ = quoted_name('acc_folders', True)

    rangid = Column(quoted_name('rangid', True), Text(12), primary_key=True, nullable=False)
    folderid = Column(quoted_name('folderid', True), Text(12), primary_key=True, nullable=False)
    access = Column(quoted_name('access', True), Integer)


class AccTid(Base):
    __tablename__ = quoted_name('acc_tid', True)

    rangid = Column(quoted_name('rangid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    t = Column(quoted_name('t', True), Integer, primary_key=True, nullable=False)
    tid = Column(quoted_name('tid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))


class Addon(Base):
    __tablename__ = quoted_name('addons', True)
    __table_args__ = (
        Index('addons_IDX1', 'docid', 'type'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(quoted_name('docid', True), Text(12), server_default=text("'0'"))
    type = Column(quoted_name('type', True), Integer)
    sum = Column(quoted_name('sum', True), Float)
    sum2 = Column(quoted_name('sum2', True), Integer)


t_analog = Table(
    'analog', metadata,
    Column(quoted_name('modelid1', True), Text(12)),
    Column(quoted_name('modelid2', True), Text(12))
)


class Cash(Base):
    __tablename__ = quoted_name('cash', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(100))
    prorder = Column(quoted_name('prorder', True), SmallInteger)
    rashorder = Column(quoted_name('rashorder', True), SmallInteger)
    prplatpor = Column(quoted_name('prplatpor', True), SmallInteger)
    rashplatpor = Column(quoted_name('rashplatpor', True), SmallInteger)
    summa = Column(quoted_name('summa', True), Float, server_default=text("0"))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Cashdevice(Base):
    __tablename__ = quoted_name('cashdevice', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, unique=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(50))
    cashid = Column(quoted_name('cashid', True), Text(12), nullable=False, server_default=text("'0'"))
    params = Column(quoted_name('params', True), String(5000))
    firmid = Column(quoted_name('firmid', True), Text(12), nullable=False, server_default=text("'0'"))
    typecheck = Column(quoted_name('typecheck', True), Integer)
    cash2id = Column(quoted_name('cash2id', True), Text(12), server_default=text("'0'"))


class Changeslist(Base):
    __tablename__ = quoted_name('changeslist', True)

    id = Column(quoted_name('id', True), Integer, primary_key=True)
    tablename = Column(quoted_name('tablename', True), Text(50), nullable=False)
    tid = Column(quoted_name('tid', True), Text(12), nullable=False, server_default=text("'0'"))
    action = Column(quoted_name('action', True), Integer)
    userid = Column(quoted_name('userid', True), Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime, nullable=False, index=True)
    message = Column(quoted_name('message', True), String(30000))


class Changessn(Base):
    __tablename__ = quoted_name('changessn', True)

    id = Column(quoted_name('id', True), Integer, primary_key=True)
    docid = Column(quoted_name('docid', True), Text(12), server_default=text("'0'"))
    inputid = Column(quoted_name('inputid', True), Text(12), server_default=text("'0'"))
    folderid = Column(quoted_name('folderid', True), Text(12), server_default=text("'0'"))
    linkid = Column(quoted_name('linkid', True), Text(12), server_default=text("'0'"))
    act = Column(quoted_name('act', True), Integer)
    snid = Column(quoted_name('snid', True), Text(12), server_default=text("'0'"))


class Compllink(Base):
    __tablename__ = quoted_name('compllink', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), primary_key=True, server_default=text("'0'"))
    count = Column(quoted_name('count', True), BigInteger)


class Country(Base):
    __tablename__ = quoted_name('country', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(30), index=True)
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    code = Column(quoted_name('code', True), String(15))


class Currency(Base):
    __tablename__ = quoted_name('currency', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(50), index=True)
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    s_g_0 = Column(quoted_name('s_g_0', True), String(50))
    s_g_1 = Column(quoted_name('s_g_1', True), String(50))
    s_g_56789 = Column(quoted_name('s_g_56789', True), String(40))
    s_g_234 = Column(quoted_name('s_g_234', True), String(50))
    s_m_0 = Column(quoted_name('s_m_0', True), String(50))
    s_m_1 = Column(quoted_name('s_m_1', True), String(50))
    s_m_56789 = Column(quoted_name('s_m_56789', True), String(50))
    s_m_234 = Column(quoted_name('s_m_234', True), String(50))
    code = Column(quoted_name('code', True), String(15))


class Curslink(Base):
    __tablename__ = quoted_name('curslink', True)

    docid = Column(quoted_name('docid', True), Text(12), primary_key=True, server_default=text("'0'"))
    currid = Column(quoted_name('currid', True), Text(12), primary_key=True, server_default=text("'0'"))
    value = Column(quoted_name('value', True), Float)
    userid = Column(quoted_name('userid', True), Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


t_dbconsts = Table(
    'dbconsts', metadata,
    Column(quoted_name('trgactive', True), Integer),
    Column(quoted_name('version', True), Text(12), server_default=text("'3.0.0.57'")),
    Column(quoted_name('accessbd', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('chlst', True), Integer)
)


class Device(Base):
    __tablename__ = quoted_name('devices', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    typedev = Column(quoted_name('typedev', True), Integer)
    name = Column(quoted_name('name', True), Text(50))
    indexdev = Column(quoted_name('indexdev', True), Integer)
    namedev = Column(quoted_name('namedev', True), String(250))
    params = Column(quoted_name('params', True), String(1000))


class Disccomplink(Base):
    __tablename__ = quoted_name('disccomplink', True)
    __table_args__ = (
        Index('disccomplink_IDX1', 'did', 'cid'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    did = Column(quoted_name('did', True), Text(12), server_default=text("'0'"))
    cid = Column(quoted_name('cid', True), Integer, nullable=False, server_default=text("0"))


class Disclink(Base):
    __tablename__ = quoted_name('disclink', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    did = Column(quoted_name('did', True), Text(12), index=True, server_default=text("'0'"))
    groupid = Column(quoted_name('groupid', True), Text(12), server_default=text("'0'"))
    typeid = Column(quoted_name('typeid', True), Text(12), server_default=text("'0'"))
    firmaid = Column(quoted_name('firmaid', True), Text(12), server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), server_default=text("'0'"))


class Discount(Base):
    __tablename__ = quoted_name('discount', True)
    __table_args__ = (
        Index('discount_IDX1', 'compid', 'fdate', 'ldate'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    compid = Column(quoted_name('compid', True), Integer, nullable=False, server_default=text("0"))
    fdate = Column(quoted_name('fdate', True), Date, nullable=False)
    ldate = Column(quoted_name('ldate', True), Date, nullable=False, index=True)
    state = Column(quoted_name('state', True), Integer, nullable=False, server_default=text("0"))
    name = Column(quoted_name('name', True), String(30))
    value = Column(quoted_name('value', True), Float, server_default=text("0"))


t_discsetup = Table(
    'discsetup', metadata,
    Column(quoted_name('id', True), Integer),
    Column(quoted_name('sum', True), Float, server_default=text("0")),
    Column(quoted_name('value', True), Float, server_default=text("0"))
)


class Doc(Base):
    __tablename__ = quoted_name('docs', True)
    __table_args__ = (
        Index('docs_IDX1', 'docdate', 'number'),
        Index('docs_IDX2', 'partnerid', 'typedoc', 'docdate', 'changedate0'),
        Index('IParent_docs', 'parentdocid', 'typedoc'),
        Index('iCash_docs', 'cashid', 'docdate', 'typedoc', 'number', 'currid'),
        Index('IAlpha_docs', 'typedoc', 'docdate', 'number'),
        Index('I_docs1', 'subtd', 'typedoc', 'docdate', 'number'),
        Index('iPartner_docs', 'partnerid', 'typedoc', 'docdate'),
        Index('I_docs3', 'docdate', 'number'),
        Index('I_docs2', 'subtd', 'typedoc', 'docdate', 'number')
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    subtd = Column(quoted_name('subtd', True), Integer, nullable=False, server_default=text("0"))
    typedoc = Column(quoted_name('typedoc', True), Integer)
    number = Column(quoted_name('number', True), Integer)
    number_str = Column(quoted_name('number_str', True), String(200))
    docdate = Column(quoted_name('docdate', True), Date)
    parentdocid = Column(quoted_name('parentdocid', True), Text(12), server_default=text("'0'"))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    folderid = Column(quoted_name('folderid', True), Text(12), server_default=text("'0'"))
    summa = Column(quoted_name('summa', True), Float, server_default=text("0"))
    dateoplat = Column(quoted_name('dateoplat', True), Date)
    dateprihod = Column(quoted_name('dateprihod', True), Date)
    cashid = Column(quoted_name('cashid', True), Text(12), server_default=text("'0'"))
    currid = Column(quoted_name('currid', True), Text(12), nullable=False, server_default=text("'50'"))
    firmid = Column(quoted_name('firmid', True), Text(12), server_default=text("'0'"))
    partnerid = Column(quoted_name('partnerid', True), Text(12), server_default=text("'0'"))
    peopleid = Column(quoted_name('peopleid', True), Text(12), server_default=text("'0'"))
    nds = Column(quoted_name('nds', True), Float)
    nsp = Column(quoted_name('nsp', True), Float)
    params0 = Column(quoted_name('params0', True), String(1000))
    params1 = Column(quoted_name('params1', True), String(1000))
    note = Column(quoted_name('note', True), String(250))
    userid0 = Column(quoted_name('userid0', True), Text(12), server_default=text("'0'"))
    changedate0 = Column(quoted_name('changedate0', True), DateTime)
    algosum = Column(quoted_name('algosum', True), Integer)


class Docservice(Base):
    __tablename__ = quoted_name('docservices', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    count = Column(quoted_name('count', True), Float)
    nmcount = Column(quoted_name('nmcount', True), Float)
    typedoc = Column(quoted_name('typedoc', True), Integer)
    docid = Column(quoted_name('docid', True), Text(12), index=True, server_default=text("'0'"))
    usedocid = Column(quoted_name('usedocid', True), Text(12), index=True, server_default=text("'0'"))
    price = Column(quoted_name('price', True), Float)
    discount = Column(quoted_name('discount', True), Float, server_default=text("0"))
    servid = Column(quoted_name('servid', True), Text(12), server_default=text("'0'"))
    nds = Column(quoted_name('nds', True), Float)
    nsp = Column(quoted_name('nsp', True), Float)
    priced = Column(quoted_name('priced', True), Float, Computed('("price"*(1-GETDISCOUNT("discount")))'))
    pricez = Column(quoted_name('pricez', True), Float)
    pzcurrid = Column(quoted_name('pzcurrid', True), Text(12), server_default=text("'0'"))


class Docstorage(Base):
    __tablename__ = quoted_name('docstorage', True)
    __table_args__ = (
        Index('docstorage_IDX1', 'modelid', 'typedoc'),
        Index('docstorage_IDX5', 'modelid', 'folderid', 'typedoc', 'nmcount'),
        Index('docstorage_IDX6', 'cognate', 'folderid', 'typedoc', 'nmcount'),
        Index('docstorage_IDX7', 'folderid', 'typedoc', 'nmcount'),
        Index('docstorage_IDX2', 'inputid', 'folderid', 'typedoc', 'nmcount'),
        Index('docstorage_IDX3', 'usedocid', 'inputid'),
        Index('docstorage_IDX8', 'typedoc', 'nmcount')
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    count = Column(quoted_name('count', True), BigInteger)
    nmcount = Column(quoted_name('nmcount', True), BigInteger)
    typedoc = Column(quoted_name('typedoc', True), Integer)
    folderid = Column(quoted_name('folderid', True), Text(12), server_default=text("'0'"))
    inputid = Column(quoted_name('inputid', True), Text(12), index=True, server_default=text("'0'"))
    docid = Column(quoted_name('docid', True), Text(12), index=True, server_default=text("'0'"))
    usedocid = Column(quoted_name('usedocid', True), Text(12), server_default=text("'0'"))
    price = Column(quoted_name('price', True), Float)
    modelid = Column(quoted_name('modelid', True), Text(12), server_default=text("'0'"))
    cognate = Column(quoted_name('cognate', True), Text(12), server_default=text("'0'"))
    nds = Column(quoted_name('nds', True), Float)
    nsp = Column(quoted_name('nsp', True), Float)
    pricer = Column(quoted_name('pricer', True), Float)
    linkid = Column(quoted_name('linkid', True), Text(12), server_default=text("'0'"))
    disc0 = Column(quoted_name('disc0', True), Float, server_default=text("0"))
    disc1 = Column(quoted_name('disc1', True), Float, server_default=text("0"))
    discount = Column(quoted_name('discount', True), Float, Computed('(GETDISCOUNT("disc0")+"disc1")'))
    priced = Column(quoted_name('priced', True), Float, Computed('("price"*(1-GETDISCOUNT("discount")))'))


t_exportid = Table(
    'exportid', metadata,
    Column(quoted_name('partnerid', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('value', True), String(500), nullable=False),
    Column(quoted_name('modelid', True), Text(12), server_default=text("'0'")),
    Index('exportid_IDX1', 'partnerid', 'value')
)


class Firmagood(Base):
    __tablename__ = quoted_name('firmagoods', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(60), index=True)
    printprior = Column(quoted_name('printprior', True), Integer)
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Firmp(Base):
    __tablename__ = quoted_name('firmp', True)
    __table_args__ = (
        Index('firmp_IDX2', 'myfirm', 'inn'),
        Index('IAlpha_firmp', 'myfirm', 'shortname')
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    myfirm = Column(quoted_name('myfirm', True), Text(12), server_default=text("'0'"))
    shortname = Column(quoted_name('shortname', True), String(30))
    name = Column(quoted_name('name', True), String(250))
    inn = Column(quoted_name('inn', True), String(40))
    kpp = Column(quoted_name('kpp', True), String(30))
    address = Column(quoted_name('address', True), String(250))
    gruzaddress = Column(quoted_name('gruzaddress', True), String(300))
    rsno = Column(quoted_name('rsno', True), String(125))
    ksno = Column(quoted_name('ksno', True), String(125))
    bik = Column(quoted_name('bik', True), String(20))
    bank = Column(quoted_name('bank', True), String(250))
    cp = Column(quoted_name('cp', True), SmallInteger)
    svseria = Column(quoted_name('svseria', True), String(15))
    svnumber = Column(quoted_name('svnumber', True), String(15))
    svdate = Column(quoted_name('svdate', True), Date)
    svovd = Column(quoted_name('svovd', True), String(250))
    paspseria = Column(quoted_name('paspseria', True), String(15))
    paspnumber = Column(quoted_name('paspnumber', True), String(15))
    paspdate = Column(quoted_name('paspdate', True), Date)
    paspovd = Column(quoted_name('paspovd', True), String(250))
    okpo = Column(quoted_name('okpo', True), String(150))
    okonh = Column(quoted_name('okonh', True), String(250))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    summa = Column(quoted_name('summa', True), Float, server_default=text("0"))
    secondpodp = Column(quoted_name('secondpodp', True), SmallInteger)
    pechat = Column(quoted_name('pechat', True), SmallInteger)
    discount = Column(quoted_name('discount', True), Float)
    params = Column(quoted_name('params', True), String(5000))
    ogrn = Column(quoted_name('ogrn', True), String(20))
    note1 = Column(quoted_name('note1', True), String(255))
    note2 = Column(quoted_name('note2', True), String(255))
    note3 = Column(quoted_name('note3', True), String(255))
    note4 = Column(quoted_name('note4', True), String(255))
    note5 = Column(quoted_name('note5', True), String(255))
    note6 = Column(quoted_name('note6', True), String(255))
    noted1 = Column(quoted_name('noted1', True), Text(12), nullable=False, server_default=text("'0'"))
    noted2 = Column(quoted_name('noted2', True), Text(12), nullable=False, server_default=text("'0'"))
    noted3 = Column(quoted_name('noted3', True), Text(12), nullable=False, server_default=text("'0'"))
    noted4 = Column(quoted_name('noted4', True), Text(12), nullable=False, server_default=text("'0'"))
    state = Column(quoted_name('state', True), Integer, nullable=False, server_default=text("0"))
    parentid = Column(quoted_name('parentid', True), Text(12), nullable=False, server_default=text("'0'"))
    alerton = Column(quoted_name('alerton', True), Integer)
    alertvalue = Column(quoted_name('alertvalue', True), String(500))
    iscard = Column(quoted_name('iscard', True), Integer, nullable=False, server_default=text("0"))
    cardnumber = Column(quoted_name('cardnumber', True), String(128), index=True)
    ownership = Column(quoted_name('ownership', True), String(255))
    gruz0 = Column(quoted_name('gruz0', True), Integer)
    disccard = Column(quoted_name('disccard', True), Float)
    code = Column(quoted_name('code', True), Text(12))
    note7 = Column(quoted_name('note7', True), String(255))
    note8 = Column(quoted_name('note8', True), String(255))
    note9 = Column(quoted_name('note9', True), String(255))
    note10 = Column(quoted_name('note10', True), String(255))
    note11 = Column(quoted_name('note11', True), String(255))
    note12 = Column(quoted_name('note12', True), String(255))
    note13 = Column(quoted_name('note13', True), String(255))
    note14 = Column(quoted_name('note14', True), String(255))
    note15 = Column(quoted_name('note15', True), String(255))
    note16 = Column(quoted_name('note16', True), String(255))
    note17 = Column(quoted_name('note17', True), String(255))
    note18 = Column(quoted_name('note18', True), String(255))
    noted5 = Column(quoted_name('noted5', True), Text(12), server_default=text("'0'"))
    noted6 = Column(quoted_name('noted6', True), Text(12), server_default=text("'0'"))
    noted7 = Column(quoted_name('noted7', True), Text(12), server_default=text("'0'"))
    noted8 = Column(quoted_name('noted8', True), Text(12), server_default=text("'0'"))
    noted9 = Column(quoted_name('noted9', True), Text(12), server_default=text("'0'"))
    noted10 = Column(quoted_name('noted10', True), Text(12), server_default=text("'0'"))
    noted11 = Column(quoted_name('noted11', True), Text(12), server_default=text("'0'"))
    noted12 = Column(quoted_name('noted12', True), Text(12), server_default=text("'0'"))
    noted13 = Column(quoted_name('noted13', True), Text(12), server_default=text("'0'"))
    noted14 = Column(quoted_name('noted14', True), Text(12), server_default=text("'0'"))
    noted15 = Column(quoted_name('noted15', True), Text(12), server_default=text("'0'"))
    noted16 = Column(quoted_name('noted16', True), Text(12), server_default=text("'0'"))
    noted17 = Column(quoted_name('noted17', True), Text(12), server_default=text("'0'"))
    noted18 = Column(quoted_name('noted18', True), Text(12), server_default=text("'0'"))
    noted19 = Column(quoted_name('noted19', True), Text(12), server_default=text("'0'"))
    noted20 = Column(quoted_name('noted20', True), Text(12), server_default=text("'0'"))
    noted21 = Column(quoted_name('noted21', True), Text(12), server_default=text("'0'"))
    noted22 = Column(quoted_name('noted22', True), Text(12), server_default=text("'0'"))
    email = Column(quoted_name('email', True), String(100))
    priceid = Column(quoted_name('priceid', True), Text(12), server_default=text("'0'"))
    rezerv = Column(quoted_name('rezerv', True), Float)
    slimit = Column(quoted_name('slimit', True), Float)
    discex = Column(quoted_name('discex', True), Float)
    docnote = Column(quoted_name('docnote', True), String(250))


class Firmpgruz(Base):
    __tablename__ = quoted_name('firmpgruz', True)
    __table_args__ = (
        Index('IAlpha_firmpgruz', 'firmpid', 'shortname'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    firmpid = Column(quoted_name('firmpid', True), Text(12), server_default=text("'0'"))
    shortname = Column(quoted_name('shortname', True), String(30))
    name = Column(quoted_name('name', True), String(250))
    inn = Column(quoted_name('inn', True), String(40))
    kpp = Column(quoted_name('kpp', True), String(30))
    address = Column(quoted_name('address', True), String(250))
    rsno = Column(quoted_name('rsno', True), String(125))
    ksno = Column(quoted_name('ksno', True), String(125))
    bik = Column(quoted_name('bik', True), String(20))
    bank = Column(quoted_name('bank', True), String(250))
    okpo = Column(quoted_name('okpo', True), String(150))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


t_flyconst = Table(
    'flyconst', metadata,
    Column(quoted_name('compid', True), Integer),
    Column(quoted_name('flyid', True), Integer),
    Column(quoted_name('flydate', True), DateTime),
    Column(quoted_name('myflyid', True), Integer),
    Column(quoted_name('myflydate', True), DateTime)
)


class Flytable(Base):
    __tablename__ = quoted_name('flytable', True)
    __table_args__ = (
        Index('I_flytable1', 'compid', 'pid', 'id'),
    )

    id = Column(quoted_name('id', True), Integer, primary_key=True)
    pid = Column(quoted_name('pid', True), Integer, nullable=False, server_default=text("0"))
    compid = Column(quoted_name('compid', True), Integer)
    tablename = Column(quoted_name('tablename', True), Text(20))
    uid = Column(quoted_name('uid', True), Text(12), server_default=text("'0'"))
    action = Column(quoted_name('action', True), Integer)
    str = Column(quoted_name('str', True), String(30000))
    memo = Column(quoted_name('memo', True), LargeBinary)
    dtsave = Column(quoted_name('dtsave', True), DateTime)


class Folder(Base):
    __tablename__ = quoted_name('folders', True)
    __table_args__ = (
        Index('ITrailer', 'folder_type', 'istrailer'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    parentid = Column(quoted_name('parentid', True), Text(12), index=True, server_default=text("'0'"))
    folder_type = Column(quoted_name('folder_type', True), Integer)
    name = Column(quoted_name('name', True), String(100), index=True)
    istrailer = Column(quoted_name('istrailer', True), SmallInteger, nullable=False, server_default=text("0"))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    companyid = Column(quoted_name('companyid', True), Text(12), server_default=text("'0'"))
    compid = Column(quoted_name('compid', True), Integer)
    ip = Column(quoted_name('ip', True), String(30))
    pref_num = Column(quoted_name('pref_num', True), Text(10))
    state = Column(quoted_name('state', True), Integer)
    flyid = Column(quoted_name('flyid', True), Integer)
    tcpsrvid = Column(quoted_name('tcpsrvid', True), String(40))


t_formvollink = Table(
    'formvollink', metadata,
    Column(quoted_name('userid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('formname', True), Text(20)),
    Column(quoted_name('modelid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('vollinkid', True), Text(12), server_default=text("'0'")),
    Index('IPrimary_fvl', 'userid', 'formname', 'modelid')
)


class Fpcargo(Base):
    __tablename__ = quoted_name('fpcargo', True)
    __table_args__ = (
        Index('IAlpha_fpcargo', 'firmid', 'shortname'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    firmid = Column(quoted_name('firmid', True), Text(12), server_default=text("'0'"))
    shortname = Column(quoted_name('shortname', True), String(30))
    name = Column(quoted_name('name', True), String(250))
    inn = Column(quoted_name('inn', True), String(40))
    kpp = Column(quoted_name('kpp', True), String(30))
    address = Column(quoted_name('address', True), String(250))
    rsno = Column(quoted_name('rsno', True), String(125))
    ksno = Column(quoted_name('ksno', True), String(125))
    bik = Column(quoted_name('bik', True), String(20))
    bank = Column(quoted_name('bank', True), String(250))
    okpo = Column(quoted_name('okpo', True), String(150))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Fpnote(Base):
    __tablename__ = quoted_name('fpnote', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    ind = Column(quoted_name('ind', True), Integer)
    value = Column(quoted_name('value', True), String(255))


class Groupfirmp(Base):
    __tablename__ = quoted_name('groupfirmp', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(30))
    userid = Column(quoted_name('userid', True), Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    note1 = Column(quoted_name('note1', True), String(255))
    note2 = Column(quoted_name('note2', True), String(255))
    noted1 = Column(quoted_name('noted1', True), Text(12), nullable=False, server_default=text("'0'"))
    noted2 = Column(quoted_name('noted2', True), Text(12), nullable=False, server_default=text("'0'"))
    noted3 = Column(quoted_name('noted3', True), Text(12), nullable=False, server_default=text("'0'"))
    slimit = Column(quoted_name('slimit', True), Float)


class Groupflink(Base):
    __tablename__ = quoted_name('groupflink', True)

    groupid = Column(quoted_name('groupid', True), Text(12), primary_key=True, nullable=False,
                     server_default=text("'0'"))
    firmpid = Column(quoted_name('firmpid', True), Text(12), primary_key=True, nullable=False, index=True,
                     server_default=text("'0'"))


class Groupgood(Base):
    __tablename__ = quoted_name('groupgoods', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(60), index=True)
    printprior = Column(quoted_name('printprior', True), Integer)
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Groupservice(Base):
    __tablename__ = quoted_name('groupservices', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(60))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Groupzatrat(Base):
    __tablename__ = quoted_name('groupzatrat', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(30))
    userid = Column(quoted_name('userid', True), Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Groupzlink(Base):
    __tablename__ = quoted_name('groupzlink', True)

    groupid = Column(quoted_name('groupid', True), Text(12), primary_key=True, nullable=False,
                     server_default=text("'0'"))
    zatratid = Column(quoted_name('zatratid', True), Text(12), primary_key=True, nullable=False,
                      server_default=text("'0'"))


class Gtd(Base):
    __tablename__ = quoted_name('gtd', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    countryid = Column(quoted_name('countryid', True), Text(12), server_default=text("'0'"))
    value = Column(quoted_name('value', True), String(50))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Historydb(Base):
    __tablename__ = quoted_name('historydb', True)

    changedate = Column(quoted_name('changedate', True), DateTime, primary_key=True)
    verdb = Column(quoted_name('verdb', True), String(12))
    action = Column(quoted_name('action', True), Integer)


class Input(Base):
    __tablename__ = quoted_name('input', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, index=True, server_default=text("'0'"))
    docid = Column(quoted_name('docid', True), Text(12), index=True, server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), index=True, server_default=text("'0'"))
    count = Column(quoted_name('count', True), BigInteger)
    pricezakup = Column(quoted_name('pricezakup', True), Float)
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    nds = Column(quoted_name('nds', True), Float)
    nsp = Column(quoted_name('nsp', True), Float)
    gtdid = Column(quoted_name('gtdid', True), Text(12), server_default=text("'0'"))
    countryid = Column(quoted_name('countryid', True), Text(12), server_default=text("'0'"))
    numsert = Column(quoted_name('numsert', True), String(80))
    orgsertid = Column(quoted_name('orgsertid', True), Text(12), nullable=False, server_default=text("'0'"))
    numsertblank = Column(quoted_name('numsertblank', True), String(40))
    datesertout = Column(quoted_name('datesertout', True), Date)
    daterealiz = Column(quoted_name('daterealiz', True), Date)


class Label(Base):
    __tablename__ = quoted_name('label', True)
    __table_args__ = (
        Index('label_IDX1', 'docid', 'modelid'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    value = Column(quoted_name('value', True), String(255), index=True)
    docid = Column(quoted_name('docid', True), Text(12), server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), server_default=text("'0'"))


class Linkedid(Base):
    __tablename__ = quoted_name('linkedid', True)

    id = Column(quoted_name('id', True), Integer, primary_key=True)
    strid = Column(quoted_name('strid', True), String(100), nullable=False, unique=True)


class Modelgood(Base,SerializerMixin):
    __tablename__ = quoted_name('modelgoods', True)
    __table_args__ = (
        Index('IAlpha2_modelgoods', 'typeid', 'firmaid', 'cognate', 'name'),
        Index('ICognate_modelgoods', 'cognate', 'name'),
        Index('IAlpha_modelgoods', 'typeid', 'firmaid', 'name')
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    typeid = Column(quoted_name('typeid', True), Text(12), server_default=text("'0'"))
    firmaid = Column(quoted_name('firmaid', True), Text(12), index=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(250), index=True)
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    imgext = Column(quoted_name('imgext', True), String(7))
    price_card = Column(quoted_name('price_card', True), Text(50))
    cognate = Column(quoted_name('cognate', True), Text(12), server_default=text("'0'"))
    name2 = Column(quoted_name('name2', True), String(200))
    size = Column(quoted_name('size', True), Text(20))
    note1id = Column(quoted_name('note1id', True), Text(12), server_default=text("'0'"))
    note2id = Column(quoted_name('note2id', True), Text(12), server_default=text("'0'"))
    koef = Column(quoted_name('koef', True), Float, server_default=text("0"))
    nds = Column(quoted_name('nds', True), Float)
    nsp = Column(quoted_name('nsp', True), Float)
    russize = Column(quoted_name('russize', True), Text(20))
    issn = Column(quoted_name('issn', True), Integer)
    imgext2 = Column(quoted_name('imgext2', True), String(7))
    discclose = Column(quoted_name('discclose', True), Float)
    comment = Column(quoted_name('comment', True), String(2000))
    wlink = Column(quoted_name('wlink', True), String(200))
    labeled = Column(quoted_name('labeled', True), Integer)

    # def to_dict(self, ):
    #     data = {
    #         'id': self.id,
    #         'name': self.name,
    #         'changedate': self.changedate.isoformat() + 'Z',
    #         'imgext': self.imgext2,
    #
    #
    #     }
    #
    #     return data


t_movings = Table(
    'movings', metadata,
    Column(quoted_name('id', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('foldersid', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('folderdid', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('inputid', True), Text(12), nullable=False, index=True, server_default=text("'0'")),
    Column(quoted_name('count', True), BigInteger),
    Column(quoted_name('datemove', True), Date),
    Column(quoted_name('userid', True), Text(12), nullable=False, server_default=text("'0'")),
    Index('I_movings1', 'foldersid', 'folderdid', 'datemove')
)


class Netevent(Base):
    __tablename__ = quoted_name('netevents', True)

    id = Column(quoted_name('id', True), Integer, primary_key=True, index=True)
    tablename = Column(quoted_name('tablename', True), Text(50))
    params = Column(quoted_name('params', True), String(500))
    action = Column(quoted_name('action', True), Integer)


class Netuser(Base):
    __tablename__ = quoted_name('netusers', True)

    compid = Column(quoted_name('compid', True), Integer, primary_key=True, nullable=False, server_default=text("1"))
    userid = Column(quoted_name('userid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    email = Column(quoted_name('email', True), String(100))
    stop = Column(quoted_name('stop', True), SmallInteger)


class Note(Base):
    __tablename__ = quoted_name('note', True)
    __table_args__ = (
        Index('IAlpha_note', 'groupid', 'name'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    groupid = Column(quoted_name('groupid', True), Text(12), server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(300))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Numdoclink(Base):
    __tablename__ = quoted_name('numdoclink', True)

    parentid = Column(quoted_name('parentid', True), Text(12), primary_key=True, server_default=text("'0'"))
    fpid = Column(quoted_name('fpid', True), Text(12), primary_key=True, server_default=text("'0'"))


class Numdoc(Base):
    __tablename__ = quoted_name('numdocs', True)

    td = Column(quoted_name('td', True), Integer, primary_key=True, nullable=False)
    firmid = Column(quoted_name('firmid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    value = Column(quoted_name('value', True), Integer)


t_opllink = Table(
    'opllink', metadata,
    Column(quoted_name('id', True), Text(12), unique=True, server_default=text("'0'")),
    Column(quoted_name('doc1id', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('doc2id', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('summa', True), Float, server_default=text("0")),
    Index('IDoc1_opllink', 'doc1id', 'doc2id'),
    Index('IDoc2_opllink', 'doc2id', 'doc1id')
)


class Oplplan(Base):
    __tablename__ = quoted_name('oplplan', True)
    __table_args__ = (
        Index('I_oplplan1', 'docid', 'dateopl'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(quoted_name('docid', True), Text(12), server_default=text("'0'"))
    dateopl = Column(quoted_name('dateopl', True), Date)
    sumopl = Column(quoted_name('sumopl', True), Float, server_default=text("0"))


class Orgsert(Base):
    __tablename__ = quoted_name('orgsert', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), Text(100))
    userid = Column(quoted_name('userid', True), Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Paydevice(Base):
    __tablename__ = quoted_name('paydevice', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(50))
    params = Column(quoted_name('params', True), String(5000))


class Person(Base):
    __tablename__ = quoted_name('people', True)
    __table_args__ = (
        Index('people_IDX1', 'firmid', 'secondname', 'firstname', 'lastname'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    firmid = Column(quoted_name('firmid', True), Text(12), server_default=text("'0'"))
    firstname = Column(quoted_name('firstname', True), String(30))
    secondname = Column(quoted_name('secondname', True), String(30))
    lastname = Column(quoted_name('lastname', True), String(30))
    paspseria = Column(quoted_name('paspseria', True), String(15))
    paspnumber = Column(quoted_name('paspnumber', True), String(15))
    paspdate = Column(quoted_name('paspdate', True), Date)
    paspovd = Column(quoted_name('paspovd', True), String(150))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    phone = Column(quoted_name('phone', True), String(30))
    email = Column(quoted_name('email', True), String(30))
    inn = Column(quoted_name('inn', True), String(40))


class Pricedict(Base):
    __tablename__ = quoted_name('pricedict', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), Text(30))


class Pricehistory(Base):
    __tablename__ = quoted_name('pricehistory', True)

    folderid = Column(quoted_name('folderid', True), Text(12), primary_key=True, server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), primary_key=True, index=True, server_default=text("'0'"))
    dt = Column(quoted_name('dt', True), DateTime, primary_key=True, nullable=False)
    userid = Column(quoted_name('userid', True), Text(12))
    p1formula = Column(quoted_name('p1formula', True), String(255))
    p2formula = Column(quoted_name('p2formula', True), String(255))
    p3formula = Column(quoted_name('p3formula', True), String(255))
    p4formula = Column(quoted_name('p4formula', True), String(255))
    p5formula = Column(quoted_name('p5formula', True), String(255))
    p6formula = Column(quoted_name('p6formula', True), String(255))
    p7formula = Column(quoted_name('p7formula', True), String(255))
    p8formula = Column(quoted_name('p8formula', True), String(255))
    p9formula = Column(quoted_name('p9formula', True), String(255))
    p10formula = Column(quoted_name('p10formula', True), String(255))
    p1value = Column(quoted_name('p1value', True), Float, server_default=text("0"))
    p2value = Column(quoted_name('p2value', True), Float, server_default=text("0"))
    p3value = Column(quoted_name('p3value', True), Float, server_default=text("0"))
    p4value = Column(quoted_name('p4value', True), Float, server_default=text("0"))
    p5value = Column(quoted_name('p5value', True), Float, server_default=text("0"))
    p6value = Column(quoted_name('p6value', True), Float, server_default=text("0"))
    p7value = Column(quoted_name('p7value', True), Float, server_default=text("0"))
    p8value = Column(quoted_name('p8value', True), Float, server_default=text("0"))
    p9value = Column(quoted_name('p9value', True), Float, server_default=text("0"))
    p10value = Column(quoted_name('p10value', True), Float, server_default=text("0"))
    currid = Column(quoted_name('currid', True), Text(12), server_default=text("'0'"))


class Pricelink(Base):
    __tablename__ = quoted_name('pricelink', True)

    folderid = Column(quoted_name('folderid', True), Text(12), primary_key=True, server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), primary_key=True, index=True, server_default=text("'0'"))
    p1formula = Column(quoted_name('p1formula', True), String(255))
    p2formula = Column(quoted_name('p2formula', True), String(255))
    p3formula = Column(quoted_name('p3formula', True), String(255))
    p4formula = Column(quoted_name('p4formula', True), String(255))
    p5formula = Column(quoted_name('p5formula', True), String(255))
    p6formula = Column(quoted_name('p6formula', True), String(255))
    p7formula = Column(quoted_name('p7formula', True), String(255))
    p8formula = Column(quoted_name('p8formula', True), String(255))
    p9formula = Column(quoted_name('p9formula', True), String(255))
    p10formula = Column(quoted_name('p10formula', True), String(255))
    p1value = Column(quoted_name('p1value', True), Float, server_default=text("0"))
    p2value = Column(quoted_name('p2value', True), Float, server_default=text("0"))
    p3value = Column(quoted_name('p3value', True), Float, server_default=text("0"))
    p4value = Column(quoted_name('p4value', True), Float, server_default=text("0"))
    p5value = Column(quoted_name('p5value', True), Float, server_default=text("0"))
    p6value = Column(quoted_name('p6value', True), Float, server_default=text("0"))
    p7value = Column(quoted_name('p7value', True), Float, server_default=text("0"))
    p8value = Column(quoted_name('p8value', True), Float, server_default=text("0"))
    p9value = Column(quoted_name('p9value', True), Float, server_default=text("0"))
    p10value = Column(quoted_name('p10value', True), Float, server_default=text("0"))
    cell = Column(quoted_name('cell', True), String(100))
    currid = Column(quoted_name('currid', True), Text(12), server_default=text("'0'"))
    dtchange = Column(quoted_name('dtchange', True), DateTime)


class Pricetemplate(Base):
    __tablename__ = quoted_name('pricetemplate', True)
    __table_args__ = (
        Index('I_pricetemplate1', 'docid', 'modelid'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(quoted_name('docid', True), Text(12), nullable=False, server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), nullable=False, server_default=text("'0'"))
    p1formula = Column(quoted_name('p1formula', True), String(255))
    p2formula = Column(quoted_name('p2formula', True), String(255))
    p3formula = Column(quoted_name('p3formula', True), String(255))
    p4formula = Column(quoted_name('p4formula', True), String(255))
    p5formula = Column(quoted_name('p5formula', True), String(255))
    p6formula = Column(quoted_name('p6formula', True), String(255))
    p7formula = Column(quoted_name('p7formula', True), String(255))
    p8formula = Column(quoted_name('p8formula', True), String(255))
    p9formula = Column(quoted_name('p9formula', True), String(255))
    p10formula = Column(quoted_name('p10formula', True), String(255))
    p1value = Column(quoted_name('p1value', True), Float, nullable=False, server_default=text("0"))
    p2value = Column(quoted_name('p2value', True), Float, nullable=False, server_default=text("0"))
    p3value = Column(quoted_name('p3value', True), Float, nullable=False, server_default=text("0"))
    p4value = Column(quoted_name('p4value', True), Float, nullable=False, server_default=text("0"))
    p5value = Column(quoted_name('p5value', True), Float, nullable=False, server_default=text("0"))
    p6value = Column(quoted_name('p6value', True), Float, nullable=False, server_default=text("0"))
    p7value = Column(quoted_name('p7value', True), Float, nullable=False, server_default=text("0"))
    p8value = Column(quoted_name('p8value', True), Float, nullable=False, server_default=text("0"))
    p9value = Column(quoted_name('p9value', True), Float, nullable=False, server_default=text("0"))
    p10value = Column(quoted_name('p10value', True), Float, nullable=False, server_default=text("0"))
    count = Column(quoted_name('count', True), BigInteger)


class Pricetmpserv(Base):
    __tablename__ = quoted_name('pricetmpserv', True)
    __table_args__ = (
        Index('I_pricetmpserv1', 'docid', 'servid'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(quoted_name('docid', True), Text(12), nullable=False, server_default=text("'0'"))
    servid = Column(quoted_name('servid', True), Text(12), nullable=False, server_default=text("'0'"))
    p1formula = Column(quoted_name('p1formula', True), String(255))
    p2formula = Column(quoted_name('p2formula', True), String(255))
    p3formula = Column(quoted_name('p3formula', True), String(255))
    p4formula = Column(quoted_name('p4formula', True), String(255))
    p5formula = Column(quoted_name('p5formula', True), String(255))
    p6formula = Column(quoted_name('p6formula', True), String(255))
    p7formula = Column(quoted_name('p7formula', True), String(255))
    p8formula = Column(quoted_name('p8formula', True), String(255))
    p9formula = Column(quoted_name('p9formula', True), String(255))
    p10formula = Column(quoted_name('p10formula', True), String(255))
    p1value = Column(quoted_name('p1value', True), Float, nullable=False, server_default=text("0"))
    p2value = Column(quoted_name('p2value', True), Float, nullable=False, server_default=text("0"))
    p3value = Column(quoted_name('p3value', True), Float, nullable=False, server_default=text("0"))
    p4value = Column(quoted_name('p4value', True), Float, nullable=False, server_default=text("0"))
    p5value = Column(quoted_name('p5value', True), Float, nullable=False, server_default=text("0"))
    p6value = Column(quoted_name('p6value', True), Float, nullable=False, server_default=text("0"))
    p7value = Column(quoted_name('p7value', True), Float, nullable=False, server_default=text("0"))
    p8value = Column(quoted_name('p8value', True), Float, nullable=False, server_default=text("0"))
    p9value = Column(quoted_name('p9value', True), Float, nullable=False, server_default=text("0"))
    p10value = Column(quoted_name('p10value', True), Float, nullable=False, server_default=text("0"))
    count = Column(quoted_name('count', True), Float, server_default=text("0"))


class Rang(Base):
    __tablename__ = quoted_name('rang', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), Text(30))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    params = Column(quoted_name('params', True), String(5000))


t_regsn = Table(
    'regsn', metadata,
    Column(quoted_name('cclient', True), Integer),
    Column(quoted_name('snkey', True), BigInteger),
    Column(quoted_name('hwid', True), Text(20)),
    Column(quoted_name('sncode', True), BigInteger),
    Column(quoted_name('lasttime', True), DateTime),
    Column(quoted_name('enabled', True), Integer)
)


class Remindercount(Base):
    __tablename__ = quoted_name('remindercount', True)

    folderid = Column(quoted_name('folderid', True), Text(12), primary_key=True, server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), primary_key=True, server_default=text("'0'"))
    count = Column(quoted_name('count', True), BigInteger, server_default=text("0"))


t_revision = Table(
    'revision', metadata,
    Column(quoted_name('userid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('modelid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('count', True), BigInteger)
)

t_rezervorder = Table(
    'rezervorder', metadata,
    Column(quoted_name('compid', True), Integer),
    Column(quoted_name('firmid', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('folderid', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('order', True), Integer),
    Index('rezervorder_IDX1', 'compid', 'firmid', 'order')
)


class Round(Base):
    __tablename__ = quoted_name('rounds', True)

    currid = Column(quoted_name('currid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    maxvalue = Column(quoted_name('maxvalue', True), Float, primary_key=True, nullable=False)
    opt = Column(quoted_name('opt', True), Integer, primary_key=True, nullable=False, server_default=text("0"))
    roundvalue = Column(quoted_name('roundvalue', True), Float)
    direct = Column(quoted_name('direct', True), Integer)
    five = Column(quoted_name('five', True), Integer)


class RptPartnerlist(Base):
    __tablename__ = quoted_name('rpt_partnerlist', True)

    userid = Column(quoted_name('userid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    id = Column(quoted_name('id', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))


class RptSenderlist(Base):
    __tablename__ = quoted_name('rpt_senderlist', True)

    userid = Column(quoted_name('userid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    id = Column(quoted_name('id', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))


t_sellremains = Table(
    'sellremains', metadata,
    Column(quoted_name('userid', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('folderid', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('modelid', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('cognate', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('inputid', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('count', True), BigInteger),
    Column(quoted_name('countst', True), BigInteger),
    Index('sellremains_IDX1', 'userid', 'folderid', 'cognate'),
    Index('I_sellremains1', 'userid', 'folderid', 'modelid')
)

t_sellremainsmove = Table(
    'sellremainsmove', metadata,
    Column(quoted_name('userid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('foldersid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('folderdid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('modelid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('inputid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('count', True), BigInteger),
    Index('I_sellremainsmove1', 'userid', 'folderdid', 'modelid')
)

t_sellremainsprice = Table(
    'sellremainsprice', metadata,
    Column(quoted_name('userid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('folderid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('modelid', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('price', True), Float)
)


class Sernum(Base):
    __tablename__ = quoted_name('sernum', True)
    __table_args__ = (
        Index('I_sernum1', 'inputid', 'sernum'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    inputid = Column(quoted_name('inputid', True), Text(12), server_default=text("'0'"))
    sernum = Column(quoted_name('sernum', True), String(40), index=True)
    tmp = Column(quoted_name('tmp', True), Integer)


class Sernumlink(Base):
    __tablename__ = quoted_name('sernumlink', True)

    docid = Column(quoted_name('docid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    folderid = Column(quoted_name('folderid', True), Text(12), primary_key=True, nullable=False,
                      server_default=text("'0'"))
    snid = Column(quoted_name('snid', True), Text(12), primary_key=True, nullable=False, index=True,
                  server_default=text("'0'"))
    linkid = Column(quoted_name('linkid', True), Text(12), server_default=text("'0'"))


class Sernumlinktmp(Base):
    __tablename__ = quoted_name('sernumlinktmp', True)

    docid = Column(quoted_name('docid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    folderid = Column(quoted_name('folderid', True), Text(12), primary_key=True, nullable=False,
                      server_default=text("'0'"))
    snid = Column(quoted_name('snid', True), Text(12), primary_key=True, nullable=False, index=True,
                  server_default=text("'0'"))
    userid = Column(quoted_name('userid', True), Text(12), nullable=False, server_default=text("'0'"))
    linkid = Column(quoted_name('linkid', True), Text(12), server_default=text("'0'"))


class Servicedict(Base):
    __tablename__ = quoted_name('servicedict', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    typeid = Column(quoted_name('typeid', True), Text(12), nullable=False, server_default=text("'0'"))
    name = Column(quoted_name('name', True), Text(250))
    userid = Column(quoted_name('userid', True), Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    volid = Column(quoted_name('volid', True), Text(12), nullable=False, server_default=text("'0'"))
    nds = Column(quoted_name('nds', True), Float)
    nsp = Column(quoted_name('nsp', True), Float)
    pricezakup = Column(quoted_name('pricezakup', True), Float, server_default=text("0"))
    currid = Column(quoted_name('currid', True), Text(12), server_default=text("'0'"))
    discclose = Column(quoted_name('discclose', True), Integer)


t_setup = Table(
    'setup', metadata,
    Column(quoted_name('compid', True), Integer),
    Column(quoted_name('myfirm', True), Text(12), server_default=text("'0'")),
    Column(quoted_name('viewprices', True), Integer),
    Column(quoted_name('rezervday', True), SmallInteger, server_default=text("1")),
    Column(quoted_name('cd_price', True), Integer),
    Column(quoted_name('cd_count', True), Integer),
    Column(quoted_name('viewcode', True), Integer, server_default=text("1")),
    Column(quoted_name('nds', True), Float),
    Column(quoted_name('nsp', True), Float),
    Column(quoted_name('autorezdate', True), Date),
    Column(quoted_name('autorez', True), Integer),
    Column(quoted_name('viewsert', True), Integer, server_default=text("0")),
    Column(quoted_name('chlactive', True), Integer),
    Column(quoted_name('clmainprice', True), Integer),
    Column(quoted_name('params', True), String(2000)),
    Column(quoted_name('code1', True), String(128))
)

t_setupc = Table(
    'setupc', metadata,
    Column(quoted_name('compid', True), Integer),
    Column(quoted_name('iscurrency', True), SmallInteger),
    Column(quoted_name('multifirm', True), SmallInteger),
    Column(quoted_name('blackid', True), Integer),
    Column(quoted_name('flynetid', True), Integer),
    Column(quoted_name('id0', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('id1', True), Text(12), nullable=False, server_default=text("'0'")),
    Column(quoted_name('id2', True), Text(12), nullable=False, server_default=text("'0'"))
)


class Storage(Base,SerializerMixin):
    __tablename__ = quoted_name('storage', True)
    __table_args__ = (
        Index('storage_IDX3', 'folderid', 'cognate'),
        Index('IInputID_storage', 'inputid', 'folderid'),
        Index('storage_IDX1', 'folderid', 'modelid', 'cognate'),
        Index('storage_IDX2', 'folderid', 'modelid')
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    count = Column(quoted_name('count', True), BigInteger)
    folderid = Column(quoted_name('folderid', True), Text(12), server_default=text("'0'"))
    inputid = Column(quoted_name('inputid', True), Text(12), server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), index=True, server_default=text("'0'"))
    cognate = Column(quoted_name('cognate', True), Text(12), server_default=text("'0'"))
    p1formula = Column(quoted_name('p1formula', True), String(255))
    p2formula = Column(quoted_name('p2formula', True), String(255))
    p3formula = Column(quoted_name('p3formula', True), String(255))
    p4formula = Column(quoted_name('p4formula', True), String(255))
    p5formula = Column(quoted_name('p5formula', True), String(255))
    p6formula = Column(quoted_name('p6formula', True), String(255))
    p7formula = Column(quoted_name('p7formula', True), String(255))
    p8formula = Column(quoted_name('p8formula', True), String(255))
    p9formula = Column(quoted_name('p9formula', True), String(255))
    p10formula = Column(quoted_name('p10formula', True), String(255))
    p1value = Column(quoted_name('p1value', True), Float, server_default=text("0"))
    p2value = Column(quoted_name('p2value', True), Float, server_default=text("0"))
    p3value = Column(quoted_name('p3value', True), Float, server_default=text("0"))
    p4value = Column(quoted_name('p4value', True), Float, server_default=text("0"))
    p5value = Column(quoted_name('p5value', True), Float, server_default=text("0"))
    p6value = Column(quoted_name('p6value', True), Float, server_default=text("0"))
    p7value = Column(quoted_name('p7value', True), Float, server_default=text("0"))
    p8value = Column(quoted_name('p8value', True), Float, server_default=text("0"))
    p9value = Column(quoted_name('p9value', True), Float, server_default=text("0"))
    p10value = Column(quoted_name('p10value', True), Float, server_default=text("0"))
    cell = Column(quoted_name('cell', True), String(100))
    currid = Column(quoted_name('currid', True), Text(12), server_default=text("50"))


class StorageSel(Base):
    __tablename__ = quoted_name('storage_sel', True)
    __table_args__ = (
        Index('i_stor_sel_user_stor', 'userid', 'storageid', unique=True),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, unique=True, server_default=text("'0'"))
    userid = Column(quoted_name('userid', True), Text(12), index=True, server_default=text("'0'"))
    storageid = Column(quoted_name('storageid', True), Text(12), server_default=text("'0'"))
    count = Column(quoted_name('count', True), BigInteger)


class T1(Base):
    __tablename__ = quoted_name('t1', True)

    id = Column(quoted_name('id', True), Integer, primary_key=True)
    id1 = Column(quoted_name('id1', True), Integer)
    id2 = Column(quoted_name('id2', True), Integer)


class T2(Base):
    __tablename__ = quoted_name('t2', True)

    id = Column(quoted_name('id', True), Integer, primary_key=True)
    id1 = Column(quoted_name('id1', True), Integer)
    id2 = Column(quoted_name('id2', True), Integer)


class Telepack(Base):
    __tablename__ = quoted_name('telepack', True)

    id = Column(quoted_name('id', True), Integer, primary_key=True)
    time = Column(quoted_name('time', True), DateTime)
    note = Column(quoted_name('note', True), String(500))
    link = Column(quoted_name('link', True), String(500))


class Tempcompl(Base):
    __tablename__ = quoted_name('tempcompl', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    userid = Column(quoted_name('userid', True), Text(12), nullable=False, server_default=text("'0'"))
    complid = Column(quoted_name('complid', True), Text(12), nullable=False, server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), nullable=False, server_default=text("'0'"))
    defcount = Column(quoted_name('defcount', True), BigInteger)
    dcount = Column(quoted_name('dcount', True), BigInteger)
    mcount = Column(quoted_name('mcount', True), BigInteger)


class Tempinput(Base):
    __tablename__ = quoted_name('tempinput', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(quoted_name('docid', True), Text(12), server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), server_default=text("'0'"))
    count = Column(quoted_name('count', True), BigInteger)
    pricezakup = Column(quoted_name('pricezakup', True), Float)
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    nds = Column(quoted_name('nds', True), Float)
    nsp = Column(quoted_name('nsp', True), Float)
    gtdid = Column(quoted_name('gtdid', True), Text(12), server_default=text("'0'"))
    countryid = Column(quoted_name('countryid', True), Text(12), server_default=text("'0'"))
    params = Column(quoted_name('params', True), String(1000))
    numsert = Column(quoted_name('numsert', True), Text(40))
    orgsertid = Column(quoted_name('orgsertid', True), Text(12), nullable=False, server_default=text("'0'"))
    numsertblank = Column(quoted_name('numsertblank', True), Text(40))
    datesertout = Column(quoted_name('datesertout', True), Date)
    daterealiz = Column(quoted_name('daterealiz', True), Date)


class Tempstorage(Base):
    __tablename__ = quoted_name('tempstorage', True)
    __table_args__ = (
        Index('tempstorage_IDX1', 'docid', 'modelid', 'cognate', 'price'),
        Index('tempstorage_IDX3', 'docid', 'cognate', 'price'),
        Index('tempstorage_IDX2', 'docid', 'modelid', 'price')
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    folderid = Column(quoted_name('folderid', True), Text(12), server_default=text("'0'"))
    inputid = Column(quoted_name('inputid', True), Text(12), server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), server_default=text("'0'"))
    cognate = Column(quoted_name('cognate', True), Text(12), server_default=text("'0'"))
    count = Column(quoted_name('count', True), BigInteger)
    docid = Column(quoted_name('docid', True), Text(12), server_default=text("'0'"))
    typedoc = Column(quoted_name('typedoc', True), Integer)
    docsid = Column(quoted_name('docsid', True), Text(12), server_default=text("'0'"))
    docfromid = Column(quoted_name('docfromid', True), Text(12), nullable=False, server_default=text("'0'"))
    price = Column(quoted_name('price', True), Float)
    disc0 = Column(quoted_name('disc0', True), Float, server_default=text("0"))
    p1formula = Column(quoted_name('p1formula', True), Text(255))
    p2formula = Column(quoted_name('p2formula', True), Text(255))
    p3formula = Column(quoted_name('p3formula', True), Text(255))
    p4formula = Column(quoted_name('p4formula', True), Text(255))
    p5formula = Column(quoted_name('p5formula', True), Text(255))
    p6formula = Column(quoted_name('p6formula', True), Text(255))
    p7formula = Column(quoted_name('p7formula', True), Text(255))
    p8formula = Column(quoted_name('p8formula', True), Text(255))
    p9formula = Column(quoted_name('p9formula', True), Text(255))
    p10formula = Column(quoted_name('p10formula', True), Text(255))
    p1value = Column(quoted_name('p1value', True), Float)
    p2value = Column(quoted_name('p2value', True), Float)
    p3value = Column(quoted_name('p3value', True), Float)
    p4value = Column(quoted_name('p4value', True), Float)
    p5value = Column(quoted_name('p5value', True), Float)
    p6value = Column(quoted_name('p6value', True), Float)
    p7value = Column(quoted_name('p7value', True), Float)
    p8value = Column(quoted_name('p8value', True), Float)
    p9value = Column(quoted_name('p9value', True), Float)
    p10value = Column(quoted_name('p10value', True), Float)
    cell = Column(quoted_name('cell', True), String(100))
    currid = Column(quoted_name('currid', True), Text(12), server_default=text("'0'"))
    celldest = Column(quoted_name('celldest', True), String(100))
    disc1 = Column(quoted_name('disc1', True), Float, server_default=text("0"))


class Tmapping(Base):
    __tablename__ = quoted_name('tmapping', True)

    parentid = Column(quoted_name('parentid', True), String(150), primary_key=True, nullable=False)
    tablename = Column(quoted_name('tablename', True), String(20), primary_key=True, nullable=False)
    tid = Column(quoted_name('tid', True), Text(12), primary_key=True, nullable=False, server_default=text("'0'"))
    pid = Column(quoted_name('pid', True), String(150), primary_key=True, nullable=False)


class Tmpzajavka(Base):
    __tablename__ = quoted_name('tmpzajavka', True)

    firmpid = Column(quoted_name('firmpid', True), Text(12), primary_key=True, nullable=False,
                     server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), primary_key=True, nullable=False,
                     server_default=text("'0'"))
    count = Column(quoted_name('count', True), BigInteger)
    price = Column(quoted_name('price', True), Float)


class Typegood(Base):
    __tablename__ = quoted_name('typegoods', True)
    __table_args__ = (
        Index('IAlpha_typegoods', 'groupid', 'name'),
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    groupid = Column(quoted_name('groupid', True), Text(12), server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(60))
    printprior = Column(quoted_name('printprior', True), Integer)
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Typeservice(Base):
    __tablename__ = quoted_name('typeservices', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    groupid = Column(quoted_name('groupid', True), Text(12), nullable=False, server_default=text("'0'"))
    name = Column(quoted_name('name', True), String(500))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Uncompllink(Base):
    __tablename__ = quoted_name('uncompllink', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(quoted_name('docid', True), Text(12), server_default=text("'0'"))
    inputsid = Column(quoted_name('inputsid', True), Text(12), server_default=text("'0'"))
    inputdid = Column(quoted_name('inputdid', True), Text(12), server_default=text("'0'"))
    count = Column(quoted_name('count', True), BigInteger)
    price = Column(quoted_name('price', True), Float, server_default=text("0"))


class User(UserMixin, Base):
    __tablename__ = quoted_name('users', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    peopleid = Column(quoted_name('peopleid', True), Text(12), server_default=text("'0'"))
    rangid = Column(quoted_name('rangid', True), Text(12), server_default=text("'0'"))
    username = Column(quoted_name('username', True), Text(20), index=True)
    password = Column(quoted_name('password', True), Text(20))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    lasttime = Column(quoted_name('lasttime', True), DateTime)
    passcash = Column(quoted_name('passcash', True), Text(10))
    stop = Column(quoted_name('stop', True), Integer, server_default=text("0"))
    sid = Column(quoted_name('sid', True), String(2000))
    code = Column(quoted_name('code', True), String(128))
    lastsession = Column(quoted_name('lastsession', True), String(128))
    tdopen = Column(quoted_name('tdopen', True), Integer)
    params = Column(quoted_name('params', True), String(2000))


class Userssetup(Base):
    __tablename__ = quoted_name('userssetup', True)

    userid = Column(quoted_name('userid', True), Text(12), primary_key=True, server_default=text("'0'"))
    clmainprice = Column(quoted_name('clmainprice', True), Integer)
    goodsorder = Column(quoted_name('goodsorder', True), Text(30))
    goodsorderid = Column(quoted_name('goodsorderid', True), Integer)
    clgoods0 = Column(quoted_name('clgoods0', True), Integer, server_default=text("16777215"))
    clgoodswdisc = Column(quoted_name('clgoodswdisc', True), Integer, server_default=text("10941172"))
    clschet = Column(quoted_name('clschet', True), Integer, server_default=text("16777215"))
    autorekv = Column(quoted_name('autorekv', True), Integer)
    clgoodsdaction = Column(quoted_name('clgoodsdaction', True), Integer, server_default=text("10941172"))


class Vidpldict(Base):
    __tablename__ = quoted_name('vidpldict', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), Text(30))
    userid = Column(quoted_name('userid', True), Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)


class Vol(Base, SerializerMixin):
    __tablename__ = quoted_name('vol', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), Text(30), index=True)
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
    okei = Column(quoted_name('okei', True), Text(10))


class Vollink(Base,SerializerMixin):
    __tablename__ = quoted_name('vollink', True)
    __table_args__ = (
        Index('IAlpha_vollink', 'modelid', 'kmin'),
        Index('vollink_IDX1', 'modelid', 'level')
    )

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    modelid = Column(quoted_name('modelid', True), Text(12), server_default=text("'0'"))
    vol1id = Column(quoted_name('vol1id', True), Text(12), server_default=text("'0'"))
    vol2id = Column(quoted_name('vol2id', True), Text(12), server_default=text("'0'"))
    k12 = Column(quoted_name('k12', True), Float)
    kmin = Column(quoted_name('kmin', True), BigInteger)
    level = Column(quoted_name('level', True), Integer)
    codemodel = Column(quoted_name('codemodel', True), Text(30), nullable=False, index=True, server_default=text("''"))
    codeint = Column(quoted_name('codeint', True), BigInteger, index=True)
    weight = Column(quoted_name('weight', True), Float)
    gross = Column(quoted_name('gross', True), Float)
    barcode = Column(quoted_name('barcode', True), String(128), index=True)
    typebc = Column(quoted_name('typebc', True), Integer)


class ZInstall(Base):
    __tablename__ = quoted_name('z_install', True)

    id = Column(quoted_name('id', True), Integer, primary_key=True)
    distr = Column(quoted_name('distr', True), LargeBinary)
    dbstr = Column(quoted_name('dbstr', True), LargeBinary)


class Zatratdict(Base):
    __tablename__ = quoted_name('zatratdict', True)

    id = Column(quoted_name('id', True), Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(quoted_name('name', True), Text(100))
    userid = Column(quoted_name('userid', True), Text(12), server_default=text("'0'"))
    changedate = Column(quoted_name('changedate', True), DateTime)
