from sqlalchemy import BigInteger, Column, Computed, Date, DateTime, Float, Index, Integer, LargeBinary, SmallInteger, String, Table, Text, text, ForeignKey
from sqlalchemy.orm import declarative_base # from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()
metadata = Base.metadata


class Id(Base):
    __tablename__ = '__id'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))


class Okdoc(Base):
    __tablename__ = '__okdoc'
    userid = Column(Text(12), primary_key=True, server_default=text("'0'"))
    inputid = Column(Text(12), primary_key=True, server_default=text("'0'"))
    p1 = Column(Float, quote=True, name='p1')
    p2 = Column(Float, quote=True, name='p2')
    p3 = Column(Float, quote=True, name='p3')
    p4 = Column(Float, quote=True, name='p4')
    p5 = Column(Float, quote=True, name='p5')
    p6 = Column(Float, quote=True, name='p6')
    p7 = Column(Float, quote=True, name='p7')
    p8 = Column(Float, quote=True, name='p8')
    p9 = Column(Float, quote=True, name='p9')
    p10 = Column(Float, quote=True, name='p10')
    p1f = Column(String(255), quote=True, name='p1f')
    p2f = Column(String(255), quote=True, name='p2f')
    p3f = Column(String(255), quote=True, name='p3f')
    p4f = Column(String(255), quote=True, name='p4f')
    p5f = Column(String(255), quote=True, name='p5f')
    p6f = Column(String(255), quote=True, name='p6f')
    p7f = Column(String(255), quote=True, name='p7f')
    p8f = Column(String(255), quote=True, name='p8f')
    p9f = Column(String(255), quote=True, name='p9f')
    p10f = Column(String(255), quote=True, name='p10f')
    currid = Column(Text(12), quote=True, name='currid')


class DImport(Base):
    __tablename__ = '_d_import'
    id = Column(Integer, primary_key=True, quote=True, name='id')
    d_id = Column(Text(12), server_default=text("'0'"))
    d_td = Column(Integer, quote=True, name='d_td')
    d_date = Column(Date, quote=True, name='d_date')
    d_num = Column(String(200), quote=True, name='d_num')
    f_id = Column(Text(12), server_default=text("'0'"))
    f_inn = Column(String(40), quote=True, name='f_inn')
    f_name = Column(String(250), quote=True, name='f_name')
    f_rs = Column(String(125), quote=True, name='f_rs')
    f_bank = Column(String(250), quote=True, name='f_bank')
    f_bic = Column(String(20), quote=True, name='f_bic')
    f_ks = Column(String(125), quote=True, name='f_ks')
    f_kpp = Column(String(30), quote=True, name='f_kpp')
    p_id = Column(Text(12), server_default=text("'0'"))
    p_inn = Column(String(40), quote=True, name='p_inn')
    p_name = Column(String(250), quote=True, name='p_name')
    p_rs = Column(String(125), quote=True, name='p_rs')
    p_bank = Column(String(250), quote=True, name='p_bank')
    p_bic = Column(String(20), quote=True, name='p_bic')
    p_ks = Column(String(125), quote=True, name='p_ks')
    p_kpp = Column(String(30), quote=True, name='p_kpp')
    d_pt = Column(String(30), quote=True, name='d_pt')
    d_ot = Column(String(30), quote=True, name='d_ot')
    d_queue = Column(String(30), quote=True, name='d_queue')
    d_note = Column(String(250), quote=True, name='d_note')
    d_term = Column(Date, quote=True, name='d_term')
    d_sum = Column(Float, quote=True, name='d_sum')
    ids_opl = Column(String(250), quote=True, name='ids_opl')
    f_id_state = Column(Integer, quote=True, name='f_id_state')
    p_id_state = Column(Integer, quote=True, name='p_id_state')
    d_kbk = Column(String(30), quote=True, name='d_kbk')
    d_okato = Column(String(30), quote=True, name='d_okato')
    d_basis = Column(String(30), quote=True, name='d_basis')
    d_period = Column(String(30), quote=True, name='d_period')
    d_type = Column(String(30), quote=True, name='d_type')
    d_pnum = Column(String(30), quote=True, name='d_pnum')
    d_pdate = Column(String(30), quote=True, name='d_pdate')


class AccCash(Base):
    __tablename__ = 'acc_cash'
    rangid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    cashid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    access = Column(Integer, quote=True, name='access')
    accessout = Column(Integer, quote=True, name='accessout')


class AccFirmagoods(Base):
    __tablename__ = 'acc_firmagoods'
    rangid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    firmaid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))


class AccFolders(Base):
    __tablename__ = 'acc_folders'
    rangid = Column(Text(12), primary_key=True, nullable=False, quote=True,
        name='rangid')
    folderid = Column(Text(12), primary_key=True, nullable=False, quote=
        True, name='folderid')
    access = Column(Integer, quote=True, name='access')


class AccTid(Base):
    __tablename__ = 'acc_tid'
    rangid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    t = Column(Integer, primary_key=True, nullable=False, quote=True, name='t')
    tid = Column(Text(12), primary_key=True, nullable=False, server_default
        =text("'0'"))


class Addons(Base):
    __tablename__ = 'addons'
    __table_args__ = Index('addons_IDX1', 'docid', 'type'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(Text(12), server_default=text("'0'"))
    type = Column(Integer, quote=True, name='type')
    sum = Column(Float, quote=True, name='sum')
    sum2 = Column(Integer, quote=True, name='sum2')


t_analog = Table('analog', metadata, Column('modelid1', Text(12), quote=
    True), Column('modelid2', Text(12), quote=True))


class Cash(Base):
    __tablename__ = 'cash'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(String(100), quote=True, name='name')
    prorder = Column(SmallInteger, quote=True, name='prorder')
    rashorder = Column(SmallInteger, quote=True, name='rashorder')
    prplatpor = Column(SmallInteger, quote=True, name='prplatpor')
    rashplatpor = Column(SmallInteger, quote=True, name='rashplatpor')
    summa = Column(Float, server_default=text('0'))
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Cashdevice(Base):
    __tablename__ = 'cashdevice'
    id = Column(Text(12), primary_key=True, unique=True, server_default=
        text("'0'"))
    name = Column(String(50), quote=True, name='name')
    cashid = Column(Text(12), nullable=False, server_default=text("'0'"))
    params = Column(String(5000), quote=True, name='params')
    firmid = Column(Text(12), nullable=False, server_default=text("'0'"))
    typecheck = Column(Integer, quote=True, name='typecheck')
    cash2id = Column(Text(12), server_default=text("'0'"))


class Certificate(Base):
    __tablename__ = 'certificate'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(String(250), index=True, quote=True, name='name')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    price = Column(Float, server_default=text('0'))
    currid = Column(Text(12), server_default=text("'0'"))


class Certstorage(Base):
    __tablename__ = 'certstorage'
    __table_args__ = Index('certstorage_IDX2', 'certid', 'code'), {'quote':
        True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    certid = Column(Text(12), server_default=text("'0'"))
    code = Column(String(128), index=True, quote=True, name='code')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Changeslist(Base):
    __tablename__ = 'changeslist'
    id = Column(Integer, primary_key=True, quote=True, name='id')
    tablename = Column(Text(50), nullable=False, quote=True, name='tablename')
    tid = Column(Text(12), nullable=False, server_default=text("'0'"))
    action = Column(Integer, quote=True, name='action')
    userid = Column(Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(DateTime, nullable=False, index=True, quote=True,
        name='changedate')
    message = Column(String(30000), quote=True, name='message')


class Changessn(Base):
    __tablename__ = 'changessn'
    id = Column(Integer, primary_key=True, quote=True, name='id')
    docid = Column(Text(12), server_default=text("'0'"))
    inputid = Column(Text(12), server_default=text("'0'"))
    folderid = Column(Text(12), server_default=text("'0'"))
    linkid = Column(Text(12), server_default=text("'0'"))
    act = Column(Integer, quote=True, name='act')
    snid = Column(Text(12), server_default=text("'0'"))


class Compllink(Base):
    __tablename__ = 'compllink'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    modelid = Column(Text(12), primary_key=True, server_default=text("'0'"))
    count = Column(BigInteger, quote=True, name='count')


class Country(Base):
    __tablename__ = 'country'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(String(30), index=True, quote=True, name='name')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    code = Column(String(15), quote=True, name='code')


class Currency(Base):
    __tablename__ = 'currency'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(String(50), index=True, quote=True, name='name')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    s_g_0 = Column(String(50), quote=True, name='s_g_0')
    s_g_1 = Column(String(50), quote=True, name='s_g_1')
    s_g_56789 = Column(String(40), quote=True, name='s_g_56789')
    s_g_234 = Column(String(50), quote=True, name='s_g_234')
    s_m_0 = Column(String(50), quote=True, name='s_m_0')
    s_m_1 = Column(String(50), quote=True, name='s_m_1')
    s_m_56789 = Column(String(50), quote=True, name='s_m_56789')
    s_m_234 = Column(String(50), quote=True, name='s_m_234')
    code = Column(String(15), quote=True, name='code')


class Curslink(Base):
    __tablename__ = 'curslink'
    docid = Column(Text(12), primary_key=True, server_default=text("'0'"))
    currid = Column(Text(12), primary_key=True, server_default=text("'0'"))
    value = Column(Float, quote=True, name='value')
    userid = Column(Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    # Обратная связь с Storage
    storages = relationship("Storage", back_populates="curslink")


t_dbconsts = Table('dbconsts', metadata, Column('trgactive', Integer, quote
    =True), Column('version', Text(12), quote=True, server_default=text(
    "'3.0.0.57'")), Column('accessbd', Text(12), quote=True, nullable=False,
    server_default=text("'0'")), Column('chlst', Integer, quote=True))


class Devices(Base):
    __tablename__ = 'devices'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    typedev = Column(Integer, quote=True, name='typedev')
    name = Column(Text(50), quote=True, name='name')
    indexdev = Column(Integer, quote=True, name='indexdev')
    namedev = Column(String(250), quote=True, name='namedev')
    params = Column(String(1000), quote=True, name='params')


class Disccomplink(Base):
    __tablename__ = 'disccomplink'
    __table_args__ = Index('disccomplink_IDX1', 'did', 'cid'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    did = Column(Text(12), server_default=text("'0'"))
    cid = Column(Integer, nullable=False, server_default=text('0'))


class Disclink(Base):
    __tablename__ = 'disclink'
    __table_args__ = Index('disclink_IDX2', 'did', 'groupid', 'typeid',
        'firmaid', 'modelid'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    did = Column(Text(12), index=True, server_default=text("'0'"))
    groupid = Column(Text(12), server_default=text("'0'"))
    typeid = Column(Text(12), server_default=text("'0'"))
    firmaid = Column(Text(12), server_default=text("'0'"))
    modelid = Column(Text(12), server_default=text("'0'"))


class Discount(Base):
    __tablename__ = 'discount'
    __table_args__ = (Index('discount_IDX1', 'compid', 'fdate', 'ldate'), {
        'quote': True})
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    compid = Column(Integer, nullable=False, server_default=text('0'))
    fdate = Column(Date, nullable=False, quote=True, name='fdate')
    ldate = Column(Date, nullable=False, index=True, quote=True, name='ldate')
    state = Column(Integer, nullable=False, server_default=text('0'))
    name = Column(String(30), quote=True, name='name')
    value = Column(Float, server_default=text('0'))


t_discsetup = Table('discsetup', metadata, Column('id', Integer, quote=True
    ), Column('sum', Float, server_default=text('0')), Column('value',
    Float, server_default=text('0')))


class Doccert(Base):
    __tablename__ = 'doccert'
    __table_args__ = Index('doccert_IDX2', 'code', 'type'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(Text(12), index=True, server_default=text("'0'"))
    type = Column(Integer, quote=True, name='type')
    certid = Column(Text(12), server_default=text("'0'"))
    code = Column(String(128), quote=True, name='code')
    price = Column(Float, quote=True, name='price')
    usedocid = Column(Text(12), server_default=text("'0'"))


class Docs(Base):
    __tablename__ = 'docs'
    __table_args__ = Index('I_docs1', 'subtd', 'typedoc', 'docdate', 'number'
        ), Index('iCash_docs_2', 'cashid', 'docdate', 'typedoc', 'number',
        'currid'), Index('I_docs2', 'subtd', 'typedoc', 'docdate', 'number'
        ), Index('I_docs3', 'docdate', 'number'), Index('docs_IDX1',
        'docdate', 'number'), Index('docs_IDX2', 'partnerid', 'typedoc',
        'docdate', 'changedate0'), Index('iCash_docs', 'cashid', 'docdate',
        'typedoc', 'number', 'currid'), Index('IParent_docs', 'parentdocid',
        'typedoc'), Index('iPartner_docs', 'partnerid', 'typedoc', 'docdate'
        ), Index('IAlpha_docs', 'typedoc', 'docdate', 'number'), {'quote': True
        }
    id = Column(Text(12), primary_key=True, server_default=text("'0'"), quote=True, name='id')
    subtd = Column(Integer, nullable=False, server_default=text('0'), quote=True, name='subtd')
    typedoc = Column(Integer, quote=True, name='typedoc')
    number = Column(Integer, quote=True, name='number')
    number_str = Column(String(200), quote=True, name='number_str')
    docdate = Column(Date, quote=True, name='docdate')
    parentdocid = Column(Text(12), server_default=text("'0'"), quote=True, name='parentdocid')
    userid = Column(Text(12), server_default=text("'0'"), quote=True, name='userid')
    changedate = Column(DateTime, index=True, quote=True, name='changedate')
    folderid = Column(Text(12), server_default=text("'0'"), quote=True, name='folderid')
    summa = Column(Float, server_default=text('0'), quote=True, name='summa')
    dateoplat = Column(Date, quote=True, name='dateoplat')
    dateprihod = Column(Date, quote=True, name='dateprihod')
    cashid = Column(Text(12), server_default=text("'0'"), quote=True, name='cashid')
    currid = Column(Text(12), nullable=False, server_default=text("'50'"), quote=True, name='currid')
    firmid = Column(Text(12), server_default=text("'0'"), quote=True, name='firmid')
    partnerid = Column(Text(12), server_default=text("'0'"), quote=True, name='partnerid')
    peopleid = Column(Text(12), server_default=text("'0'"), quote=True, name='peopleid')
    nds = Column(Float, quote=True, name='nds')
    nsp = Column(Float, quote=True, name='nsp')
    params0 = Column(String(1000), quote=True, name='params0')
    params1 = Column(String(1000), quote=True, name='params1')
    note = Column(String(250), quote=True, name='note')
    userid0 = Column(Text(12), server_default=text("'0'"), quote=True, name='userid0')
    changedate0 = Column(DateTime, quote=True, name='changedate0')
    algosum = Column(Integer, quote=True, name='algosum')
    docstorage = relationship("Docstorage", back_populates="docs")


class Docservices(Base):
    __tablename__ = 'docservices'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    count = Column(Float, quote=True, name='count')
    nmcount = Column(Float, quote=True, name='nmcount')
    typedoc = Column(Integer, quote=True, name='typedoc')
    docid = Column(Text(12), index=True, server_default=text("'0'"))
    usedocid = Column(Text(12), index=True, server_default=text("'0'"))
    price = Column(Float, quote=True, name='price')
    discount = Column(Float, server_default=text('0'))
    servid = Column(Text(12), server_default=text("'0'"))
    nds = Column(Float, quote=True, name='nds')
    nsp = Column(Float, quote=True, name='nsp')
    priced = Column(Float, quote=True, name='priced')
    pricez = Column(Float, quote=True, name='pricez')
    pzcurrid = Column(Text(12), server_default=text("'0'"))


class Docstorage(Base):
    __tablename__ = 'docstorage'
    __table_args__ = Index('docstorage_IDX8', 'typedoc', 'nmcount'), Index(
        'docstorage_IDX3', 'usedocid', 'inputid'), Index('docstorage_IDX1',
        'modelid', 'typedoc'), Index('docstorage_IDX7', 'folderid',
        'typedoc', 'nmcount'), Index('docstorage_IDX2', 'inputid',
        'folderid', 'typedoc', 'nmcount'), Index('docstorage_IDX6',
        'cognate', 'folderid', 'typedoc', 'nmcount'), Index('docstorage_IDX5',
        'modelid', 'folderid', 'typedoc', 'nmcount'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"), quote=True, name='id')
    count = Column(BigInteger, quote=True, name='count')
    nmcount = Column(BigInteger, quote=True, name='nmcount')
    typedoc = Column(Integer, quote=True, name='typedoc')
    folderid = Column(Text(12), server_default=text("'0'"), quote=True, name='folderid')
    inputid = Column(Text(12), index=True, server_default=text("'0'"), quote=True, name='inputid')
    docid = Column(Text(12), ForeignKey('docs.id'), index=True, server_default=text("'0'"), quote=True, name='docid')
    usedocid = Column(Text(12), server_default=text("'0'"), quote=True, name='usedocid')
    price = Column(Float, quote=True, name='price')
    modelid = Column(Text(12), ForeignKey('modelgoods.id'), server_default=text("'0'"), quote=True, name='modelid')
    cognate = Column(Text(12), server_default=text("'0'"), quote=True, name='cognate')
    nds = Column(Float, quote=True, name='nds')
    nsp = Column(Float, quote=True, name='nsp')
    pricer = Column(Float, quote=True, name='pricer')
    linkid = Column(Text(12), server_default=text("'0'"), quote=True, name='linkid')
    disc0 = Column(Float, server_default=text('0'), quote=True, name='disc0')
    disc1 = Column(Float, server_default=text('0'), quote=True, name='disc1')
    discount = Column(Float,  quote=True, name='discount')
    priced = Column(Float, quote=True, name='priced')
    docs = relationship("Docs", back_populates="docstorage")
    modelgoods = relationship("Modelgoods", back_populates="docstorage")


t_exportid = Table('exportid', metadata, Column('partnerid', Text(12), quote
    =True, nullable=False, server_default=text("'0'")), Column('value',
    String(500), quote=True, nullable=False), Column('modelid', Text(12),
    quote=True, server_default=text("'0'")), Index('exportid_IDX1',
    'partnerid', 'value'))


class Firmagoods(Base):
    __tablename__ = 'firmagoods'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(String(60), index=True, quote=True, name='name')
    printprior = Column(Integer, quote=True, name='printprior')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Firmp(Base):
    __tablename__ = 'firmp'
    __table_args__ = Index('IAlpha_firmp', 'myfirm', 'shortname'), Index(
        'firmp_IDX2', 'myfirm', 'inn'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    myfirm = Column(Text(12), server_default=text("'0'"))
    shortname = Column(String(30), quote=True, name='shortname')
    name = Column(String(250), quote=True, name='name')
    inn = Column(String(40), quote=True, name='inn')
    kpp = Column(String(30), quote=True, name='kpp')
    address = Column(String(250), quote=True, name='address')
    gruzaddress = Column(String(300), quote=True, name='gruzaddress')
    rsno = Column(String(125), quote=True, name='rsno')
    ksno = Column(String(125), quote=True, name='ksno')
    bik = Column(String(20), quote=True, name='bik')
    bank = Column(String(250), quote=True, name='bank')
    cp = Column(SmallInteger, quote=True, name='cp')
    svseria = Column(String(15), quote=True, name='svseria')
    svnumber = Column(String(15), quote=True, name='svnumber')
    svdate = Column(Date, quote=True, name='svdate')
    svovd = Column(String(250), quote=True, name='svovd')
    paspseria = Column(String(15), quote=True, name='paspseria')
    paspnumber = Column(String(15), quote=True, name='paspnumber')
    paspdate = Column(Date, quote=True, name='paspdate')
    paspovd = Column(String(250), quote=True, name='paspovd')
    okpo = Column(String(150), quote=True, name='okpo')
    okonh = Column(String(250), quote=True, name='okonh')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    summa = Column(Float, server_default=text('0'))
    secondpodp = Column(SmallInteger, quote=True, name='secondpodp')
    pechat = Column(SmallInteger, quote=True, name='pechat')
    discount = Column(Float, quote=True, name='discount')
    params = Column(String(5000), quote=True, name='params')
    ogrn = Column(String(20), quote=True, name='ogrn')
    note1 = Column(String(255), quote=True, name='note1')
    note2 = Column(String(255), quote=True, name='note2')
    note3 = Column(String(255), quote=True, name='note3')
    note4 = Column(String(255), quote=True, name='note4')
    note5 = Column(String(255), quote=True, name='note5')
    note6 = Column(String(255), quote=True, name='note6')
    noted1 = Column(Text(12), nullable=False, server_default=text("'0'"))
    noted2 = Column(Text(12), nullable=False, server_default=text("'0'"))
    noted3 = Column(Text(12), nullable=False, server_default=text("'0'"))
    noted4 = Column(Text(12), nullable=False, server_default=text("'0'"))
    state = Column(Integer, nullable=False, server_default=text('0'))
    parentid = Column(Text(12), nullable=False, server_default=text("'0'"))
    alerton = Column(Integer, quote=True, name='alerton')
    alertvalue = Column(String(500), quote=True, name='alertvalue')
    iscard = Column(Integer, nullable=False, server_default=text('0'))
    cardnumber = Column(String(128), index=True, quote=True, name='cardnumber')
    ownership = Column(String(255), quote=True, name='ownership')
    gruz0 = Column(Integer, quote=True, name='gruz0')
    disccard = Column(Float, quote=True, name='disccard')
    code = Column(Text(12), quote=True, name='code')
    note7 = Column(String(255), quote=True, name='note7')
    note8 = Column(String(255), quote=True, name='note8')
    note9 = Column(String(255), quote=True, name='note9')
    note10 = Column(String(255), quote=True, name='note10')
    note11 = Column(String(255), quote=True, name='note11')
    note12 = Column(String(255), quote=True, name='note12')
    note13 = Column(String(255), quote=True, name='note13')
    note14 = Column(String(255), quote=True, name='note14')
    note15 = Column(String(255), quote=True, name='note15')
    note16 = Column(String(255), quote=True, name='note16')
    note17 = Column(String(255), quote=True, name='note17')
    note18 = Column(String(255), quote=True, name='note18')
    noted5 = Column(Text(12), server_default=text("'0'"))
    noted6 = Column(Text(12), server_default=text("'0'"))
    noted7 = Column(Text(12), server_default=text("'0'"))
    noted8 = Column(Text(12), server_default=text("'0'"))
    noted9 = Column(Text(12), server_default=text("'0'"))
    noted10 = Column(Text(12), server_default=text("'0'"))
    noted11 = Column(Text(12), server_default=text("'0'"))
    noted12 = Column(Text(12), server_default=text("'0'"))
    noted13 = Column(Text(12), server_default=text("'0'"))
    noted14 = Column(Text(12), server_default=text("'0'"))
    noted15 = Column(Text(12), server_default=text("'0'"))
    noted16 = Column(Text(12), server_default=text("'0'"))
    noted17 = Column(Text(12), server_default=text("'0'"))
    noted18 = Column(Text(12), server_default=text("'0'"))
    noted19 = Column(Text(12), server_default=text("'0'"))
    noted20 = Column(Text(12), server_default=text("'0'"))
    noted21 = Column(Text(12), server_default=text("'0'"))
    noted22 = Column(Text(12), server_default=text("'0'"))
    email = Column(String(100), quote=True, name='email')
    priceid = Column(Text(12), server_default=text("'0'"))
    rezerv = Column(Float, quote=True, name='rezerv')
    slimit = Column(Float, quote=True, name='slimit')
    discex = Column(Float, quote=True, name='discex')
    docnote = Column(String(250), quote=True, name='docnote')


class Firmpgruz(Base):
    __tablename__ = 'firmpgruz'
    __table_args__ = Index('IAlpha_firmpgruz', 'firmpid', 'shortname'), {
        'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    firmpid = Column(Text(12), server_default=text("'0'"))
    shortname = Column(String(30), quote=True, name='shortname')
    name = Column(String(250), quote=True, name='name')
    inn = Column(String(40), quote=True, name='inn')
    kpp = Column(String(30), quote=True, name='kpp')
    address = Column(String(250), quote=True, name='address')
    rsno = Column(String(125), quote=True, name='rsno')
    ksno = Column(String(125), quote=True, name='ksno')
    bik = Column(String(20), quote=True, name='bik')
    bank = Column(String(250), quote=True, name='bank')
    okpo = Column(String(150), quote=True, name='okpo')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


t_flyconst = Table('flyconst', metadata, Column('compid', Integer, quote=
    True), Column('flyid', Integer, quote=True), Column('flydate', DateTime,
    quote=True), Column('myflyid', Integer, quote=True), Column('myflydate',
    DateTime, quote=True))


class Flytable(Base):
    __tablename__ = 'flytable'
    __table_args__ = Index('I_flytable1', 'compid', 'pid', 'id'), {'quote':
        True}
    id = Column(Integer, primary_key=True, quote=True, name='id')
    pid = Column(Integer, nullable=False, server_default=text('0'))
    compid = Column(Integer, quote=True, name='compid')
    tablename = Column(Text(20), quote=True, name='tablename')
    uid = Column(Text(12), server_default=text("'0'"))
    action = Column(Integer, quote=True, name='action')
    str = Column(String(30000), quote=True, name='str')
    memo = Column(LargeBinary, quote=True, name='memo')
    dtsave = Column(DateTime, quote=True, name='dtsave')


class Folders(Base):
    __tablename__ = 'folders'
    __table_args__ = Index('ITrailer', 'folder_type', 'istrailer'), {'quote':
        True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"), quote=True, name='id')
    parentid = Column(Text(12), index=True, server_default=text("'0'"), quote=True, name='parentid')
    folder_type = Column(Integer, quote=True, name='folder_type')
    name = Column(String(100), index=True, quote=True, name='name')
    istrailer = Column(SmallInteger, nullable=False, server_default=text('0'), quote=True, name='istrailer')
    userid = Column(Text(12), server_default=text("'0'"), quote=True, name='userid')
    changedate = Column(DateTime, quote=True, name='changedate')
    companyid = Column(Text(12), server_default=text("'0'"), quote=True, name='companyid')
    compid = Column(Integer, quote=True, name='compid')
    ip = Column(String(30), quote=True, name='ip')
    pref_num = Column(Text(10), quote=True, name='pref_num')
    state = Column(Integer, quote=True, name='state')
    flyid = Column(Integer, quote=True, name='flyid')
    tcpsrvid = Column(String(40), quote=True, name='tcpsrvid')
    storages = relationship("Storage", back_populates="folder")


t_formvollink = Table('formvollink', metadata, Column('userid', Text(12),
    quote=True, server_default=text("'0'")), Column('formname', Text(20),
    quote=True), Column('modelid', Text(12), quote=True, server_default=
    text("'0'")), Column('vollinkid', Text(12), quote=True, server_default=
    text("'0'")), Index('IPrimary_fvl', 'userid', 'formname', 'modelid'))


class Fpcargo(Base):
    __tablename__ = 'fpcargo'
    __table_args__ = Index('IAlpha_fpcargo', 'firmid', 'shortname'), {'quote':
        True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    firmid = Column(Text(12), server_default=text("'0'"))
    shortname = Column(String(30), quote=True, name='shortname')
    name = Column(String(250), quote=True, name='name')
    inn = Column(String(40), quote=True, name='inn')
    kpp = Column(String(30), quote=True, name='kpp')
    address = Column(String(250), quote=True, name='address')
    rsno = Column(String(125), quote=True, name='rsno')
    ksno = Column(String(125), quote=True, name='ksno')
    bik = Column(String(20), quote=True, name='bik')
    bank = Column(String(250), quote=True, name='bank')
    okpo = Column(String(150), quote=True, name='okpo')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Fpnote(Base):
    __tablename__ = 'fpnote'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    ind = Column(Integer, quote=True, name='ind')
    value = Column(String(255), quote=True, name='value')


class Groupfirmp(Base):
    __tablename__ = 'groupfirmp'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(String(30), quote=True, name='name')
    userid = Column(Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    note1 = Column(String(255), quote=True, name='note1')
    note2 = Column(String(255), quote=True, name='note2')
    noted1 = Column(Text(12), nullable=False, server_default=text("'0'"))
    noted2 = Column(Text(12), nullable=False, server_default=text("'0'"))
    noted3 = Column(Text(12), nullable=False, server_default=text("'0'"))
    slimit = Column(Float, quote=True, name='slimit')


class Groupflink(Base):
    __tablename__ = 'groupflink'
    groupid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    firmpid = Column(Text(12), primary_key=True, nullable=False, index=True,
        server_default=text("'0'"))


class Groupgoods(Base):
    __tablename__ = 'groupgoods'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(String(60), index=True, quote=True, name='name')
    printprior = Column(Integer, quote=True, name='printprior')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Groupservices(Base):
    __tablename__ = 'groupservices'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(String(60), quote=True, name='name')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Groupzatrat(Base):
    __tablename__ = 'groupzatrat'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(String(30), quote=True, name='name')
    userid = Column(Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Groupzlink(Base):
    __tablename__ = 'groupzlink'
    groupid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    zatratid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))


class Gtd(Base):
    __tablename__ = 'gtd'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    countryid = Column(Text(12), server_default=text("'0'"))
    value = Column(String(50), quote=True, name='value')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Historydb(Base):
    __tablename__ = 'historydb'
    changedate = Column(DateTime, primary_key=True, quote=True, name=
        'changedate')
    verdb = Column(String(12), quote=True, name='verdb')
    action = Column(Integer, quote=True, name='action')


class Input(Base):
    __tablename__ = 'input'
    id = Column(Text(12), primary_key=True, index=True, server_default=text
        ("'0'"))
    docid = Column(Text(12), index=True, server_default=text("'0'"))
    modelid = Column(Text(12), index=True, server_default=text("'0'"))
    count = Column(BigInteger, quote=True, name='count')
    pricezakup = Column(Float, quote=True, name='pricezakup')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    nds = Column(Float, quote=True, name='nds')
    nsp = Column(Float, quote=True, name='nsp')
    gtdid = Column(Text(12), server_default=text("'0'"))
    countryid = Column(Text(12), server_default=text("'0'"))
    numsert = Column(String(80), quote=True, name='numsert')
    orgsertid = Column(Text(12), nullable=False, server_default=text("'0'"))
    numsertblank = Column(String(80), quote=True, name='numsertblank')
    datesertout = Column(Date, quote=True, name='datesertout')
    daterealiz = Column(Date, quote=True, name='daterealiz')
    datemanuf = Column(Date, quote=True, name='datemanuf')


class Label(Base):
    __tablename__ = 'label'
    __table_args__ = Index('label_IDX1', 'docid', 'modelid'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    value = Column(String(255), index=True, quote=True, name='value')
    docid = Column(Text(12), server_default=text("'0'"))
    modelid = Column(Text(12), server_default=text("'0'"))


class Linkedid(Base):
    __tablename__ = 'linkedid'
    id = Column(Integer, primary_key=True, quote=True, name='id')
    strid = Column(String(100), nullable=False, unique=True, quote=True,
        name='strid')


class Modelgoods(Base):
    __tablename__ = 'modelgoods'
    __table_args__ = Index('IAlpha2_modelgoods', 'typeid', 'firmaid',
        'cognate', 'name'), Index('ICognate_modelgoods', 'cognate', 'name'
        ), Index('IAlpha_modelgoods', 'typeid', 'firmaid', 'name'), {'quote':
        True}
    id = Column(String(12), primary_key=True, server_default=text("'0'"), quote=True, name='id')
    typeid = Column(Text(12), server_default=text("'0'"),quote=True,name='typeid')
    firmaid = Column(Text(12), index=True, server_default=text("'0'"),quote=True,name='firmaid')
    name = Column(String(250), index=True, quote=True, name='name')
    userid = Column(Text(12), server_default=text("'0'"),quote=True,name='userid')
    changedate = Column(DateTime, quote=True, name='changedate')
    imgext = Column(String(7), quote=True, name='imgext')
    price_card = Column(Text(50), quote=True, name='price_card')
    cognate = Column(Text(12), server_default=text("'0'"),quote=True,name='cognate')
    name2 = Column(String(200), quote=True, name='name2')
    size = Column(Text(20), quote=True, name='size')
    note1id = Column(Text(12), server_default=text("'0'"),quote=True,name='note1id')
    note2id = Column(Text(12), server_default=text("'0'"),quote=True,name='note2id')
    koef = Column(Float, server_default=text('0'),quote=True,name='koef')
    nds = Column(Float,quote=True,name='nds')
    nsp = Column(Float, quote=True, name='nsp')
    russize = Column(Text(20), quote=True, name='russize')
    issn = Column(Integer, quote=True, name='issn')
    imgext2 = Column(String(7), quote=True, name='imgext2')
    discclose = Column(Float, quote=True, name='discclose')
    comment = Column(String(2000), quote=True, name='comment')
    wlink = Column(String(200), quote=True, name='wlink')
    labeled = Column(Integer, quote=True, name='labeled')
    m2021 = Column(Integer, quote=True, name='m2021')
    excise = Column(Integer, quote=True, name='excise')
    ismilk = Column(Integer, quote=True, name='ismilk')
    storages = relationship("Storage", back_populates="modelgoods")
    docstorage = relationship("Docstorage", back_populates="modelgoods")

t_movings = Table('movings', metadata, Column('id', Text(12), quote=True,
    nullable=False, server_default=text("'0'")), Column('foldersid', Text(
    12), quote=True, nullable=False, server_default=text("'0'")), Column(
    'folderdid', Text(12), quote=True, nullable=False, server_default=text(
    "'0'")), Column('inputid', Text(12), quote=True, nullable=False, index=
    True, server_default=text("'0'")), Column('count', BigInteger, quote=
    True), Column('datemove', Date, quote=True), Column('userid', Text(12),
    quote=True, nullable=False, server_default=text("'0'")), Index(
    'I_movings1', 'foldersid', 'folderdid', 'datemove'))


class Netevents(Base):
    __tablename__ = 'netevents'
    id = Column(Integer, primary_key=True, index=True, quote=True, name='id')
    tablename = Column(Text(50), quote=True, name='tablename')
    params = Column(String(500), quote=True, name='params')
    action = Column(Integer, quote=True, name='action')


class Netusers(Base):
    __tablename__ = 'netusers'
    compid = Column(Integer, primary_key=True, nullable=False,
        server_default=text('1'))
    userid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    email = Column(String(100), quote=True, name='email')
    stop = Column(SmallInteger, quote=True, name='stop')


class Note(Base):
    __tablename__ = 'note'
    __table_args__ = Index('IAlpha_note', 'groupid', 'name'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    groupid = Column(Text(12), server_default=text("'0'"))
    name = Column(String(300), quote=True, name='name')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Numdoclink(Base):
    __tablename__ = 'numdoclink'
    parentid = Column(Text(12), primary_key=True, server_default=text("'0'"))
    fpid = Column(Text(12), primary_key=True, server_default=text("'0'"))


class Numdocs(Base):
    __tablename__ = 'numdocs'
    td = Column(Integer, primary_key=True, nullable=False, quote=True, name
        ='td')
    firmid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    value = Column(Integer, quote=True, name='value')


t_opllink = Table('opllink', metadata, Column('id', Text(12), quote=True,
    unique=True, server_default=text("'0'")), Column('doc1id', Text(12),
    quote=True, server_default=text("'0'")), Column('doc2id', Text(12),
    quote=True, server_default=text("'0'")), Column('summa', Float,
    server_default=text('0')), Index('IDoc1_opllink', 'doc1id', 'doc2id'),
    Index('IDoc2_opllink', 'doc2id', 'doc1id'))


class Oplplan(Base):
    __tablename__ = 'oplplan'
    __table_args__ = Index('I_oplplan1', 'docid', 'dateopl'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(Text(12), server_default=text("'0'"))
    dateopl = Column(Date, quote=True, name='dateopl')
    sumopl = Column(Float, server_default=text('0'))


class Orgsert(Base):
    __tablename__ = 'orgsert'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(String(100), quote=True, name='name')
    userid = Column(Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Paydevice(Base):
    __tablename__ = 'paydevice'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(String(50), quote=True, name='name')
    params = Column(String(5000), quote=True, name='params')


class People(Base):
    __tablename__ = 'people'
    __table_args__ = Index('people_IDX1', 'firmid', 'secondname',
        'firstname', 'lastname'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    firmid = Column(Text(12), server_default=text("'0'"))
    firstname = Column(String(30), quote=True, name='firstname')
    secondname = Column(String(30), quote=True, name='secondname')
    lastname = Column(String(30), quote=True, name='lastname')
    paspseria = Column(String(15), quote=True, name='paspseria')
    paspnumber = Column(String(15), quote=True, name='paspnumber')
    paspdate = Column(Date, quote=True, name='paspdate')
    paspovd = Column(String(150), quote=True, name='paspovd')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    phone = Column(String(30), quote=True, name='phone')
    email = Column(String(30), quote=True, name='email')
    inn = Column(String(40), quote=True, name='inn')


class Pricedict(Base):
    __tablename__ = 'pricedict'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(Text(30), quote=True, name='name')


class Pricehistory(Base):
    __tablename__ = 'pricehistory'
    folderid = Column(Text(12), primary_key=True, server_default=text("'0'"))
    modelid = Column(Text(12), primary_key=True, index=True, server_default
        =text("'0'"))
    dt = Column(DateTime, primary_key=True, nullable=False, quote=True,
        name='dt')
    userid = Column(Text(12), quote=True, name='userid')
    p1formula = Column(String(255), quote=True, name='p1formula')
    p2formula = Column(String(255), quote=True, name='p2formula')
    p3formula = Column(String(255), quote=True, name='p3formula')
    p4formula = Column(String(255), quote=True, name='p4formula')
    p5formula = Column(String(255), quote=True, name='p5formula')
    p6formula = Column(String(255), quote=True, name='p6formula')
    p7formula = Column(String(255), quote=True, name='p7formula')
    p8formula = Column(String(255), quote=True, name='p8formula')
    p9formula = Column(String(255), quote=True, name='p9formula')
    p10formula = Column(String(255), quote=True, name='p10formula')
    p1value = Column(Float, server_default=text('0'))
    p2value = Column(Float, server_default=text('0'))
    p3value = Column(Float, server_default=text('0'))
    p4value = Column(Float, server_default=text('0'))
    p5value = Column(Float, server_default=text('0'))
    p6value = Column(Float, server_default=text('0'))
    p7value = Column(Float, server_default=text('0'))
    p8value = Column(Float, server_default=text('0'))
    p9value = Column(Float, server_default=text('0'))
    p10value = Column(Float, server_default=text('0'))
    currid = Column(Text(12), server_default=text("'0'"))


class Pricelink(Base):
    __tablename__ = 'pricelink'
    folderid = Column(Text(12), primary_key=True, server_default=text("'0'"))
    modelid = Column(Text(12), primary_key=True, index=True, server_default
        =text("'0'"))
    p1formula = Column(String(255), quote=True, name='p1formula')
    p2formula = Column(String(255), quote=True, name='p2formula')
    p3formula = Column(String(255), quote=True, name='p3formula')
    p4formula = Column(String(255), quote=True, name='p4formula')
    p5formula = Column(String(255), quote=True, name='p5formula')
    p6formula = Column(String(255), quote=True, name='p6formula')
    p7formula = Column(String(255), quote=True, name='p7formula')
    p8formula = Column(String(255), quote=True, name='p8formula')
    p9formula = Column(String(255), quote=True, name='p9formula')
    p10formula = Column(String(255), quote=True, name='p10formula')
    p1value = Column(Float, server_default=text('0'))
    p2value = Column(Float, server_default=text('0'))
    p3value = Column(Float, server_default=text('0'))
    p4value = Column(Float, server_default=text('0'))
    p5value = Column(Float, server_default=text('0'))
    p6value = Column(Float, server_default=text('0'))
    p7value = Column(Float, server_default=text('0'))
    p8value = Column(Float, server_default=text('0'))
    p9value = Column(Float, server_default=text('0'))
    p10value = Column(Float, server_default=text('0'))
    cell = Column(String(100), quote=True, name='cell')
    currid = Column(Text(12), server_default=text("'0'"))
    dtchange = Column(DateTime, quote=True, name='dtchange')


class Pricetemplate(Base):
    __tablename__ = 'pricetemplate'
    __table_args__ = Index('I_pricetemplate1', 'docid', 'modelid'), {'quote':
        True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(Text(12), nullable=False, server_default=text("'0'"))
    modelid = Column(Text(12), nullable=False, server_default=text("'0'"))
    p1formula = Column(String(255), quote=True, name='p1formula')
    p2formula = Column(String(255), quote=True, name='p2formula')
    p3formula = Column(String(255), quote=True, name='p3formula')
    p4formula = Column(String(255), quote=True, name='p4formula')
    p5formula = Column(String(255), quote=True, name='p5formula')
    p6formula = Column(String(255), quote=True, name='p6formula')
    p7formula = Column(String(255), quote=True, name='p7formula')
    p8formula = Column(String(255), quote=True, name='p8formula')
    p9formula = Column(String(255), quote=True, name='p9formula')
    p10formula = Column(String(255), quote=True, name='p10formula')
    p1value = Column(Float, nullable=False, server_default=text('0'))
    p2value = Column(Float, nullable=False, server_default=text('0'))
    p3value = Column(Float, nullable=False, server_default=text('0'))
    p4value = Column(Float, nullable=False, server_default=text('0'))
    p5value = Column(Float, nullable=False, server_default=text('0'))
    p6value = Column(Float, nullable=False, server_default=text('0'))
    p7value = Column(Float, nullable=False, server_default=text('0'))
    p8value = Column(Float, nullable=False, server_default=text('0'))
    p9value = Column(Float, nullable=False, server_default=text('0'))
    p10value = Column(Float, nullable=False, server_default=text('0'))
    count = Column(BigInteger, quote=True, name='count')


class Pricetmpserv(Base):
    __tablename__ = 'pricetmpserv'
    __table_args__ = Index('I_pricetmpserv1', 'docid', 'servid'), {'quote':
        True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(Text(12), nullable=False, server_default=text("'0'"))
    servid = Column(Text(12), nullable=False, server_default=text("'0'"))
    p1formula = Column(String(255), quote=True, name='p1formula')
    p2formula = Column(String(255), quote=True, name='p2formula')
    p3formula = Column(String(255), quote=True, name='p3formula')
    p4formula = Column(String(255), quote=True, name='p4formula')
    p5formula = Column(String(255), quote=True, name='p5formula')
    p6formula = Column(String(255), quote=True, name='p6formula')
    p7formula = Column(String(255), quote=True, name='p7formula')
    p8formula = Column(String(255), quote=True, name='p8formula')
    p9formula = Column(String(255), quote=True, name='p9formula')
    p10formula = Column(String(255), quote=True, name='p10formula')
    p1value = Column(Float, nullable=False, server_default=text('0'))
    p2value = Column(Float, nullable=False, server_default=text('0'))
    p3value = Column(Float, nullable=False, server_default=text('0'))
    p4value = Column(Float, nullable=False, server_default=text('0'))
    p5value = Column(Float, nullable=False, server_default=text('0'))
    p6value = Column(Float, nullable=False, server_default=text('0'))
    p7value = Column(Float, nullable=False, server_default=text('0'))
    p8value = Column(Float, nullable=False, server_default=text('0'))
    p9value = Column(Float, nullable=False, server_default=text('0'))
    p10value = Column(Float, nullable=False, server_default=text('0'))
    count = Column(Float, server_default=text('0'))


class Rang(Base):
    __tablename__ = 'rang'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(Text(30), quote=True, name='name')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    params = Column(String(5000), quote=True, name='params')


t_regsn = Table('regsn', metadata, Column('cclient', Integer, quote=True),
    Column('snkey', BigInteger, quote=True), Column('hwid', Text(20), quote
    =True), Column('sncode', BigInteger, quote=True), Column('lasttime',
    DateTime, quote=True), Column('enabled', Integer, quote=True))


class Remindercount(Base):
    __tablename__ = 'remindercount'
    folderid = Column(Text(12), primary_key=True, server_default=text("'0'"))
    modelid = Column(Text(12), primary_key=True, server_default=text("'0'"))
    count = Column(BigInteger, server_default=text('0'))


t_revision = Table('revision', metadata, Column('userid', Text(12), quote=
    True, server_default=text("'0'")), Column('modelid', Text(12), quote=
    True, server_default=text("'0'")), Column('count', BigInteger, quote=True)
    )
t_rezervorder = Table('rezervorder', metadata, Column('compid', Integer,
    quote=True), Column('firmid', Text(12), quote=True, nullable=False,
    server_default=text("'0'")), Column('folderid', Text(12), quote=True,
    nullable=False, server_default=text("'0'")), Column('order', Integer,
    quote=True), Index('rezervorder_IDX1', 'compid', 'firmid', 'order'))


class Rounds(Base):
    __tablename__ = 'rounds'
    currid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    maxvalue = Column(Float, primary_key=True, nullable=False, quote=True,
        name='maxvalue')
    opt = Column(Integer, primary_key=True, nullable=False, server_default=
        text('0'))
    roundvalue = Column(Float, quote=True, name='roundvalue')
    direct = Column(Integer, quote=True, name='direct')
    five = Column(Integer, quote=True, name='five')


class RptPartnerlist(Base):
    __tablename__ = 'rpt_partnerlist'
    userid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    id = Column(Text(12), primary_key=True, nullable=False, server_default=
        text("'0'"))


class RptSenderlist(Base):
    __tablename__ = 'rpt_senderlist'
    userid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    id = Column(Text(12), primary_key=True, nullable=False, server_default=
        text("'0'"))


t_sellremains = Table('sellremains', metadata, Column('userid', Text(12),
    quote=True, nullable=False, server_default=text("'0'")), Column(
    'folderid', Text(12), quote=True, nullable=False, server_default=text(
    "'0'")), Column('modelid', Text(12), quote=True, nullable=False,
    server_default=text("'0'")), Column('cognate', Text(12), quote=True,
    nullable=False, server_default=text("'0'")), Column('inputid', Text(12),
    quote=True, nullable=False, server_default=text("'0'")), Column(
    'count', BigInteger, quote=True), Column('countst', BigInteger, quote=
    True), Index('I_sellremains1', 'userid', 'folderid', 'modelid'), Index(
    'sellremains_IDX1', 'userid', 'folderid', 'cognate'))
t_sellremainsmove = Table('sellremainsmove', metadata, Column('userid',
    Text(12), quote=True, server_default=text("'0'")), Column('foldersid',
    Text(12), quote=True, server_default=text("'0'")), Column('folderdid',
    Text(12), quote=True, server_default=text("'0'")), Column('modelid',
    Text(12), quote=True, server_default=text("'0'")), Column('inputid',
    Text(12), quote=True, server_default=text("'0'")), Column('count',
    BigInteger, quote=True), Index('I_sellremainsmove1', 'userid',
    'folderdid', 'modelid'))
t_sellremainsprice = Table('sellremainsprice', metadata, Column('userid',
    Text(12), quote=True, server_default=text("'0'")), Column('folderid',
    Text(12), quote=True, server_default=text("'0'")), Column('modelid',
    Text(12), quote=True, server_default=text("'0'")), Column('price',
    Float, quote=True))


class Sernum(Base):
    __tablename__ = 'sernum'
    __table_args__ = Index('I_sernum1', 'inputid', 'sernum'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    inputid = Column(Text(12), server_default=text("'0'"))
    sernum = Column(String(40), index=True, quote=True, name='sernum')
    tmp = Column(Integer, quote=True, name='tmp')


class Sernumlink(Base):
    __tablename__ = 'sernumlink'
    docid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    folderid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    snid = Column(Text(12), primary_key=True, nullable=False, index=True,
        server_default=text("'0'"))
    linkid = Column(Text(12), server_default=text("'0'"))


class Sernumlinktmp(Base):
    __tablename__ = 'sernumlinktmp'
    docid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    folderid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    snid = Column(Text(12), primary_key=True, nullable=False, index=True,
        server_default=text("'0'"))
    userid = Column(Text(12), nullable=False, server_default=text("'0'"))
    linkid = Column(Text(12), server_default=text("'0'"))


class Servicedict(Base):
    __tablename__ = 'servicedict'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    typeid = Column(Text(12), nullable=False, server_default=text("'0'"))
    name = Column(Text(250), quote=True, name='name')
    userid = Column(Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    volid = Column(Text(12), nullable=False, server_default=text("'0'"))
    nds = Column(Float, quote=True, name='nds')
    nsp = Column(Float, quote=True, name='nsp')
    pricezakup = Column(Float, server_default=text('0'))
    currid = Column(Text(12), server_default=text("'0'"))
    discclose = Column(Integer, quote=True, name='discclose')


t_setup = Table('setup', metadata, Column('compid', Integer, quote=True),
    Column('myfirm', Text(12), quote=True, server_default=text("'0'")),
    Column('viewprices', Integer, quote=True), Column('rezervday',
    SmallInteger, server_default=text('1')), Column('cd_price', Integer,
    quote=True), Column('cd_count', Integer, quote=True), Column('viewcode',
    Integer, server_default=text('1')), Column('nds', Float, quote=True),
    Column('nsp', Float, quote=True), Column('autorezdate', Date, quote=
    True), Column('autorez', Integer, quote=True), Column('viewsert',
    Integer, server_default=text('0')), Column('chlactive', Integer, quote=
    True), Column('clmainprice', Integer, quote=True), Column('params',
    String(2000), quote=True), Column('code1', String(128), quote=True))
t_setupc = Table('setupc', metadata, Column('compid', Integer, quote=True),
    Column('iscurrency', SmallInteger, quote=True), Column('multifirm',
    SmallInteger, quote=True), Column('blackid', Integer, quote=True),
    Column('flynetid', Integer, quote=True), Column('id0', Text(12), quote=
    True, nullable=False, server_default=text("'0'")), Column('id1', Text(
    12), quote=True, nullable=False, server_default=text("'0'")), Column(
    'id2', Text(12), quote=True, nullable=False, server_default=text("'0'")))


class Storage(Base):
    __tablename__ = 'storage'
    __table_args__ = (Index('IInputID_storage', 'inputid', 'folderid'), Index(
        'storage_IDX1', 'folderid', 'modelid', 'cognate'), Index('storage_IDX3'
        , 'folderid', 'cognate'), Index('storage_IDX2', 'folderid', 'modelid'
        ), {'quote': True})
    id = Column(Text(12), primary_key=True, server_default=text("'0'"), quote=True,name='id')
    count = Column(BigInteger, quote=True, name='count')
    folderid = Column(Text(12), ForeignKey("folders.id"), server_default=text("'0'"), quote=True, name='folderid')
    inputid = Column(Text(12), server_default=text("'0'"), quote=True,name='inputid')
    modelid = Column(Text(12), ForeignKey("modelgoods.id"), index=True, server_default=text("'0'"), quote=True, name='modelid' )
    cognate = Column(Text(12), server_default=text("'0'"), quote=True,name='cognate')
    p1formula = Column(String(255), quote=True, name='p1formula')
    p2formula = Column(String(255), quote=True, name='p2formula')
    p3formula = Column(String(255), quote=True, name='p3formula')
    p4formula = Column(String(255), quote=True, name='p4formula')
    p5formula = Column(String(255), quote=True, name='p5formula')
    p6formula = Column(String(255), quote=True, name='p6formula')
    p7formula = Column(String(255), quote=True, name='p7formula')
    p8formula = Column(String(255), quote=True, name='p8formula')
    p9formula = Column(String(255), quote=True, name='p9formula')
    p10formula = Column(String(255), quote=True, name='p10formula')
    p1value = Column(Float, server_default=text('0'), quote=True, name='p1value')
    p2value = Column(Float, server_default=text('0'), quote=True, name='p2value')
    p3value = Column(Float, server_default=text('0'), quote=True, name='p3value')
    p4value = Column(Float, server_default=text('0'), quote=True, name='p4value')
    p5value = Column(Float, server_default=text('0'), quote=True, name='p5value')
    p6value = Column(Float, server_default=text('0'), quote=True, name='p6value')
    p7value = Column(Float, server_default=text('0'), quote=True, name='p7value')
    p8value = Column(Float, server_default=text('0'), quote=True, name='p8value')
    p9value = Column(Float, server_default=text('0'), quote=True, name='p9value')
    p10value = Column(Float, server_default=text('0'), quote=True, name='p10value')
    cell = Column(String(100), quote=True, name='cell')
    currid = Column(Text(12), ForeignKey("curslink.currid"), server_default=text('50'), quote=True, name='currid')
    modelgoods = relationship("Modelgoods", back_populates="storages")
    folder = relationship("Folders", back_populates="storages")
    curslink = relationship("Curslink", back_populates="storages")


class StorageSel(Base):
    __tablename__ = 'storage_sel'
    __table_args__ = (Index('i_stor_sel_user_stor', 'userid', 'storageid',
        unique=True), {'quote': True})
    id = Column(Text(12), primary_key=True, unique=True, server_default=
        text("'0'"))
    userid = Column(Text(12), index=True, server_default=text("'0'"))
    storageid = Column(Text(12), server_default=text("'0'"))
    count = Column(BigInteger, quote=True, name='count')


class T1(Base):
    __tablename__ = 't1'
    id = Column(Integer, primary_key=True, quote=True, name='id')
    id1 = Column(Integer, quote=True, name='id1')
    id2 = Column(Integer, quote=True, name='id2')


class T2(Base):
    __tablename__ = 't2'
    id = Column(Integer, primary_key=True, quote=True, name='id')
    id1 = Column(Integer, quote=True, name='id1')
    id2 = Column(Integer, quote=True, name='id2')


class Telepack(Base):
    __tablename__ = 'telepack'
    id = Column(Integer, primary_key=True, quote=True, name='id')
    time = Column(DateTime, quote=True, name='time')
    note = Column(String(500), quote=True, name='note')
    link = Column(String(500), quote=True, name='link')


class Tempcompl(Base):
    __tablename__ = 'tempcompl'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    userid = Column(Text(12), nullable=False, server_default=text("'0'"))
    complid = Column(Text(12), nullable=False, server_default=text("'0'"))
    modelid = Column(Text(12), nullable=False, server_default=text("'0'"))
    defcount = Column(BigInteger, quote=True, name='defcount')
    dcount = Column(BigInteger, quote=True, name='dcount')
    mcount = Column(BigInteger, quote=True, name='mcount')


class Tempinput(Base):
    __tablename__ = 'tempinput'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(Text(12), server_default=text("'0'"))
    modelid = Column(Text(12), server_default=text("'0'"))
    count = Column(BigInteger, quote=True, name='count')
    pricezakup = Column(Float, quote=True, name='pricezakup')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    nds = Column(Float, quote=True, name='nds')
    nsp = Column(Float, quote=True, name='nsp')
    gtdid = Column(Text(12), server_default=text("'0'"))
    countryid = Column(Text(12), server_default=text("'0'"))
    params = Column(String(1000), quote=True, name='params')
    numsert = Column(String(80), quote=True, name='numsert')
    orgsertid = Column(Text(12), nullable=False, server_default=text("'0'"))
    numsertblank = Column(String(80), quote=True, name='numsertblank')
    datesertout = Column(Date, quote=True, name='datesertout')
    daterealiz = Column(Date, quote=True, name='daterealiz')
    datemanuf = Column(Date, quote=True, name='datemanuf')


class Tempstorage(Base):
    __tablename__ = 'tempstorage'
    __table_args__ = Index('tempstorage_IDX2', 'docid', 'modelid', 'price'
        ), Index('tempstorage_IDX3', 'docid', 'cognate', 'price'), Index(
        'tempstorage_IDX1', 'docid', 'modelid', 'cognate', 'price'), {'quote':
        True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    userid = Column(Text(12), server_default=text("'0'"))
    folderid = Column(Text(12), server_default=text("'0'"))
    inputid = Column(Text(12), server_default=text("'0'"))
    modelid = Column(Text(12), server_default=text("'0'"))
    cognate = Column(Text(12), server_default=text("'0'"))
    count = Column(BigInteger, quote=True, name='count')
    docid = Column(Text(12), server_default=text("'0'"))
    typedoc = Column(Integer, quote=True, name='typedoc')
    docsid = Column(Text(12), server_default=text("'0'"))
    docfromid = Column(Text(12), nullable=False, server_default=text("'0'"))
    price = Column(Float, quote=True, name='price')
    disc0 = Column(Float, server_default=text('0'))
    p1formula = Column(String(255), quote=True, name='p1formula')
    p2formula = Column(String(255), quote=True, name='p2formula')
    p3formula = Column(String(255), quote=True, name='p3formula')
    p4formula = Column(String(255), quote=True, name='p4formula')
    p5formula = Column(String(255), quote=True, name='p5formula')
    p6formula = Column(String(255), quote=True, name='p6formula')
    p7formula = Column(String(255), quote=True, name='p7formula')
    p8formula = Column(String(255), quote=True, name='p8formula')
    p9formula = Column(String(255), quote=True, name='p9formula')
    p10formula = Column(String(255), quote=True, name='p10formula')
    p1value = Column(Float, quote=True, name='p1value')
    p2value = Column(Float, quote=True, name='p2value')
    p3value = Column(Float, quote=True, name='p3value')
    p4value = Column(Float, quote=True, name='p4value')
    p5value = Column(Float, quote=True, name='p5value')
    p6value = Column(Float, quote=True, name='p6value')
    p7value = Column(Float, quote=True, name='p7value')
    p8value = Column(Float, quote=True, name='p8value')
    p9value = Column(Float, quote=True, name='p9value')
    p10value = Column(Float, quote=True, name='p10value')
    cell = Column(String(100), quote=True, name='cell')
    currid = Column(Text(12), server_default=text("'0'"))
    celldest = Column(String(100), quote=True, name='celldest')
    disc1 = Column(Float, server_default=text('0'))


class Tmapping(Base):
    __tablename__ = 'tmapping'
    parentid = Column(String(150), primary_key=True, nullable=False, quote=
        True, name='parentid')
    tablename = Column(String(20), primary_key=True, nullable=False, quote=
        True, name='tablename')
    tid = Column(Text(12), primary_key=True, nullable=False, server_default
        =text("'0'"))
    pid = Column(String(150), primary_key=True, nullable=False, quote=True,
        name='pid')


class Tmpzajavka(Base):
    __tablename__ = 'tmpzajavka'
    firmpid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    modelid = Column(Text(12), primary_key=True, nullable=False,
        server_default=text("'0'"))
    count = Column(BigInteger, quote=True, name='count')
    price = Column(Float, quote=True, name='price')


class Typegoods(Base):
    __tablename__ = 'typegoods'
    __table_args__ = Index('IAlpha_typegoods', 'groupid', 'name'), {'quote':
        True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    groupid = Column(Text(12), server_default=text("'0'"))
    name = Column(String(60), quote=True, name='name')
    printprior = Column(Integer, quote=True, name='printprior')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Typeservices(Base):
    __tablename__ = 'typeservices'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    groupid = Column(Text(12), nullable=False, server_default=text("'0'"))
    name = Column(String(500), quote=True, name='name')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Uncompllink(Base):
    __tablename__ = 'uncompllink'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    docid = Column(Text(12), server_default=text("'0'"))
    inputsid = Column(Text(12), server_default=text("'0'"))
    inputdid = Column(Text(12), server_default=text("'0'"))
    count = Column(BigInteger, quote=True, name='count')
    price = Column(Float, server_default=text('0'))


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {'quote':
        True}
    id = Column(String(50), primary_key=True, quote=True, name='id')
    peopleid = Column(String(50), quote=True, name='peopleid')
    rangid = Column(String(50), quote=True, name='rangid')
    username = Column(String(50), unique=True, index=True, quote=True, name='username', comment='TRIM_WHITESPACE')
    password = Column(String(100), quote=True, name='password', comment='TRIM_WHITESPACE') 
    userid = Column(String(50), quote=True, name='userid')
    changedate = Column(DateTime, quote=True, name='changedate')
    lasttime = Column(DateTime, quote=True, name='lasttime')
    passcash = Column(String(10), quote=True, name='passcash')
    stop = Column(Integer, default=0, quote=True, name='stop')
    sid = Column(String(2000), quote=True, name='sid')
    code = Column(String(128), quote=True, name='code')
    lastsession = Column(String(128), quote=True, name='lastsession')
    tdopen = Column(Integer, quote=True, name='tdopen')
    params = Column(String(2000), quote=True, name='params')


class Userssetup(Base):
    __tablename__ = 'userssetup'
    userid = Column(Text(12), primary_key=True, server_default=text("'0'"))
    clmainprice = Column(Integer, quote=True, name='clmainprice')
    goodsorder = Column(Text(30), quote=True, name='goodsorder')
    goodsorderid = Column(Integer, quote=True, name='goodsorderid')
    clgoods0 = Column(Integer, server_default=text('16777215'))
    clgoodswdisc = Column(Integer, server_default=text('10941172'))
    clschet = Column(Integer, server_default=text('16777215'))
    autorekv = Column(Integer, quote=True, name='autorekv')
    clgoodsdaction = Column(Integer, server_default=text('10941172'))
    clgoodswdisc0 = Column(Integer, server_default=text('10941172'))
    fontsize = Column(Integer, server_default=text('100'))


class Vidpldict(Base):
    __tablename__ = 'vidpldict'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(Text(30), quote=True, name='name')
    userid = Column(Text(12), nullable=False, server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')


class Vol(Base):
    __tablename__ = 'vol'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(Text(30), index=True, quote=True, name='name')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
    okei = Column(Text(10), quote=True, name='okei')


class Vollink(Base):
    __tablename__ = 'vollink'
    __table_args__ = Index('IAlpha_vollink', 'modelid', 'kmin'), Index(
        'vollink_IDX1', 'modelid', 'level'), {'quote': True}
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    modelid = Column(Text(12), server_default=text("'0'"))
    vol1id = Column(Text(12), server_default=text("'0'"))
    vol2id = Column(Text(12), server_default=text("'0'"))
    k12 = Column(Float, quote=True, name='k12')
    kmin = Column(BigInteger, quote=True, name='kmin')
    level = Column(Integer, quote=True, name='level')
    codemodel = Column(Text(30), nullable=False, index=True, server_default
        =text("''"))
    codeint = Column(BigInteger, index=True, quote=True, name='codeint')
    weight = Column(Float, quote=True, name='weight')
    gross = Column(Float, quote=True, name='gross')
    barcode = Column(String(128), index=True, quote=True, name='barcode')
    typebc = Column(Integer, quote=True, name='typebc')
    dimension = Column(String(30), quote=True, name='dimension')


class Vrflabel(Base):
    __tablename__ = 'vrflabel'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    endtime = Column(DateTime, quote=True, name='endtime')
    inn = Column(String(40), nullable=False, index=True, quote=True, name='inn'
        )
    mydata = Column(LargeBinary, quote=True, name='mydata')
    token = Column(LargeBinary, quote=True, name='token')
    cdndate = Column(Date, quote=True, name='cdndate')
    e203 = Column(Date, quote=True, name='e203')


class Vrflabelcdn(Base):
    __tablename__ = 'vrflabelcdn'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    url = Column(String(200), quote=True, name='url')
    ms = Column(Integer, index=True, quote=True, name='ms')
    errortime = Column(DateTime, quote=True, name='errortime')


t_vrflabellog = Table('vrflabellog', metadata, Column('id', Text(12), quote
    =True, server_default=text("'0'")), Column('dt', DateTime, nullable=
    False, quote=True), Column('label', String(255), quote=True, nullable=
    False), Column('result', String(1000), quote=True), Column('url',
    String(200), quote=True))


class ZInstall(Base):
    __tablename__ = 'z_install'
    id = Column(Integer, primary_key=True, quote=True, name='id')
    distr = Column(LargeBinary, quote=True, name='distr')
    dbstr = Column(LargeBinary, quote=True, name='dbstr')


class Zatratdict(Base):
    __tablename__ = 'zatratdict'
    id = Column(Text(12), primary_key=True, server_default=text("'0'"))
    name = Column(Text(100), quote=True, name='name')
    userid = Column(Text(12), server_default=text("'0'"))
    changedate = Column(DateTime, quote=True, name='changedate')
