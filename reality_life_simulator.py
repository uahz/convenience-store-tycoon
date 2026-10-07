# -*- coding: utf-8 -*-
"""现实人生模拟器 —— PyQt6 桌面版（Anti-Design 反设计风格）
用法：
  python reality_life_simulator.py            # 正常游戏
  python reality_life_simulator.py --selftest # 无界面逻辑自检（打完4段人生）
  python reality_life_simulator.py --shot     # 截图各页面到 _shots/ 供检查
"""
__version__='1.1.0'
import sys, os, json, random, math, threading, wave, struct

from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QPixmap,
                         QPainterPath, QPolygonF, QGuiApplication)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget,
                             QLabel, QPushButton, QLineEdit, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QFrame, QDialog,
                             QListWidget, QListWidgetItem, QTextBrowser,
                             QSizePolicy, QScrollArea, QGraphicsDropShadowEffect)

# ============================================================
# 静态数据
# ============================================================
SKINS=['#F2C9A5','#E0AC78','#C68B59','#9C6B43']
HAIRC=[('#2B2118','黑发'),('#4A3320','深棕'),('#7A5636','栗色'),('#B7B7B7','灰白')]
OUTFITS=['#1A1A1A','#8B0000','#000080','#3B3B3B','#4A4E2B','#5C4A5C']
HAIRSTYLES=[('short','短发'),('long','长发'),('bun','束发'),('curly','卷发')]
GENDERS=[('m','男'),('f','女')]
TRAITS=[('sunny','开朗','心情事件更受益，社交加分'),
        ('shy','内向','独处学习更专注，社交加成少'),
        ('dili','勤奋','知识成长+30%'),
        ('opt','乐观','坏消息影响减轻'),
        ('care','细心','考试与判定更稳'),
        ('adven','冒险家','机遇更多，偶尔翻车'),
        ('art','艺术细胞','魅力成长+30%'),
        ('sport','运动健将','体能成长+30%')]
TALENTS=[('memory','过目不忘','知识成长+60%'),('strong','天生活力','体能成长+60%'),
         ('pretty','出众相貌','初始魅力高，社交讨喜'),('rich','家境优渥','家庭存款+3万'),
         ('biz','生意头脑','理财收益更高'),('lucky','幸运星','每年有机会收到意外小惊喜'),
         ('social','社牛体质','社交行动效果大幅提升'),('night','精力充沛','每月行动点+1'),
         ('kid','玩家心态','娱乐放松效果更好'),('all','全面发展','所有成长+15%')]
FAMILIES=[('节俭家庭','日子紧巴巴，但笑声不少',1000,5,0),
          ('普通家庭','爸妈工资稳定，温馨平常',8000,0,0),
          ('小康家庭','吃穿不愁，偶尔全家旅行',30000,0,0),
          ('富裕家庭','从小见世面，资源多多',90000,0,10)]
CAREERS=[
 ('code','程序员',[('初级程序员',8000,{'major':'cs'}),('高级工程师',15000,{'smart':85,'y':2}),('技术总监',28000,{'smart':95,'fame':55,'y':5})]),
 ('doctor','医生',[('住院医师',9000,{'major':'med'}),('主治医师',16000,{'smart':88,'y':3}),('主任医师',26000,{'smart':95,'fame':65,'y':6})]),
 ('teacher','教师',[('人民教师',6000,{'major':'edu'}),('资深教师',10000,{'smart':82,'fame':45,'y':3}),('教导主任',16000,{'fame':60,'y':6})]),
 ('artist','设计师',[('助理设计师',5500,{'major':'art'}),('独立插画师',12000,{'fame':50,'y':3}),('知名艺术家',25000,{'fame':80,'y':8})]),
 ('coach','健身教练',[('健身教练',5000,{'fit':70}),('明星私教',10000,{'fit':85,'y':2}),('门店经理',18000,{'charm':65,'fame':50,'y':5})]),
 ('sales','商务',[('销售专员',5000,{'charm':55}),('销售经理',10000,{'charm':70,'fame':45,'y':3}),('区域总监',20000,{'fame':65,'y':6})]),
 ('food','餐饮',[('餐饮服务员',3500,{}),('门店领班',6000,{'charm':45,'y':1}),('门店店长',10000,{'fame':40,'y':3}),('餐厅合伙人',20000,{'money':150000,'fame':60,'y':5})]),
 ('barista','咖啡师',[('咖啡师',4000,{'charm':40}),('首席咖啡师',7000,{'charm':60,'y':2}),('咖啡店店长',12000,{'fame':45,'y':4})]),
 ('courier','快递',[('快递员',4500,{'fit':55}),('快递站长',7500,{'fit':70,'y':2}),('网点经理',12000,{'fame':40,'y':5})]),
 ('basic','零售',[('便利店员',3000,{}),('仓储组长',4500,{'fit':60,'y':1}),('区域督导',8000,{'fame':35,'y':4})]),
 ('gov','公务员',[('科员',4500,{'exam':True}),('副科长',7000,{'loyal':35,'y':2}),('科长',11000,{'loyal':55,'y':4}),('处长',18000,{'loyal':75,'fame':55,'y':6})]),
 ('media','自媒体',[('素人博主',500,{'charm':55}),('小网红',3000,{'fans':10000,'y':1}),('大V博主',12000,{'fans':100000,'y':2}),('顶流创作者',40000,{'fans':1000000,'y':3})])]
MAJORS=[('cs','计算机'),('med','医学'),('edu','师范'),('art','美术'),('biz','商科'),('pe','体育')]
PARTTIME=[('发传单',400,False),('餐厅小时工',700,False),('家教助理',900,True)]
NPCNAMES=['小雨','阿哲','婷婷','大伟','小雅','阿凯','悦悦','子豪','小林','静静','老王','小美','阿杰','圆圆','大力','朵朵']
BABYNAMES=['豆豆','糖糖','小满','乐乐','团团','安安']
ACHV={'job':('初入职场','找到第一份工作'),'grad':('学有所成','大学毕业'),'marry':('佳偶天成','步入婚姻'),
      'baby':('添丁之喜','迎来宝宝'),'house':('安居乐业','拥有自己的家'),'rich50':('小有积蓄','总资产达50万'),
      'rich200':('财富自由','总资产达200万'),'fame':('家喻户晓','声望达到80'),'zhuangyuan':('金榜题名','高考名列前茅'),
      'health':('健康之星','70岁仍硬朗'),'bond':('情深意重','家人感情深厚')}
EDU_NAME={'学前':'幼儿园','小学':'小学生','初中':'初中生','高中':'高中生','职校':'职校生',
          '大学':'大学生','大学毕业':'大学毕业','职校毕业':'职校毕业','社会':'社会人'}
STAGE_NAME={'child':'童年','teen':'少年','adult':'成年','senior':'花甲'}
def _safe_path(base_dir,name):
    """归一化路径并锁定在 base_dir 内，杜绝 '..' 路径穿越"""
    base=os.path.realpath(base_dir)
    p=os.path.realpath(os.path.join(base,name))
    if os.path.commonpath([base,p])!=base:
        p=os.path.join(base,os.path.basename(name))
    return p
def _appdata_file(name):
    return _safe_path(os.environ.get('APPDATA',os.path.expanduser('~')),os.path.join('RealityLifeSimulator',name))
def _data_dir():
    """存档目录：固定在 %APPDATA%/RealityLifeSimulator 内并校验包含关系"""
    d=_appdata_file('.')
    os.makedirs(d,exist_ok=True)
    return d
def _open_data(name,mode):
    """唯一的数据文件打开入口：路径经 _safe_path 归一化并锁定在数据目录内"""
    p=_appdata_file(name)
    if os.path.commonpath([os.path.realpath(_data_dir()),os.path.dirname(os.path.realpath(p))])!=os.path.realpath(_data_dir()):
        raise ValueError('数据路径越界: %s'%name)
    return open(p,mode,encoding='utf-8')
_BASE_DIR=os.path.dirname(os.path.abspath(__file__))
SAVE_PATH=_appdata_file('save.json')
SETTINGS_PATH=_appdata_file('settings.json')

def fmt_m(n):
    n=round(n)
    return ('%.1f'%(abs(n)/10000)).rstrip('0').rstrip('.')+'万' if abs(n)>=10000 else '¥'+str(n)

# ============================================================
# 游戏引擎（全局状态 G）
# ============================================================
G={'p':None,'over':False,'queue':[],'endData':None,'sound':True,'music':True}
THEME={'mode':'light'}  # 背景模式：light 白底 / dark 黑底（设置中切换）

def load_settings():
    try:
        with _open_data('settings.json','r') as f: d=json.load(f)
        THEME['mode']='dark' if d.get('theme')=='dark' else 'light'
        G['sound']=bool(d.get('sound',True))
        G['music']=bool(d.get('music',True))
    except Exception:
        THEME['mode']='light'

def save_settings():
    if G.get('nosave'): return
    try:
        with _open_data('settings.json','w') as f:
            json.dump({'theme':THEME['mode'],'sound':G['sound'],'music':G.get('music',True)},f,ensure_ascii=False)
    except Exception: pass

def stage_of(a): return 'child' if a<12 else 'teen' if a<18 else 'adult' if a<60 else 'senior'
def has_tr(p,t): return t in p['traits']
def has_tal(p,t): return t in p['talents']
def gm(p,k):
    m=1.0
    if has_tal(p,'all'): m+=0.15
    if k=='smart' and has_tal(p,'memory'): m+=0.6
    if k=='fit' and has_tal(p,'strong'): m+=0.6
    if k=='charm' and has_tal(p,'pretty'): m+=0.2
    if k=='smart' and has_tr(p,'dili'): m+=0.3
    if k=='fit' and has_tr(p,'sport'): m+=0.3
    if k=='charm' and has_tr(p,'art'): m+=0.3
    if k=='smart' and has_tr(p,'shy'): m+=0.15
    return m
def stg(p,k,v): p['stats'][k]=max(0,min(100,round(p['stats'][k]+v*gm(p,k))))
def sst(p,k,v): p['stats'][k]=max(0,min(100,p['stats'][k]+v))
def mny(p,v): p['money']=max(0,p['money']+v)
def famev(p,v): p['fame']=max(0,min(100,p['fame']+v))
def glog(p,ic,t): p['log'].insert(0,{'age':p['age'],'m':p['month'],'ic':ic,'t':t}) or p['log'].pop() if len(p['log'])>140 else None
def glog(p,ic,t):
    p['log'].insert(0,{'age':p['age'],'m':p['month'],'ic':ic,'t':t})
    if len(p['log'])>140: p['log'].pop()
def tl(p,t): p['timeline'].append({'age':p['age'],'t':t})
def achv(p,i):
    if i not in p['ach']:
        p['ach'].append(i); glog(p,'::','解锁成就【'+ACHV[i][0]+'】！'); snd_up()
def assets(p): return p['money']+p['bank']+p['fund']
def npc_by(p,part): return next((n for n in p['npcs'] if part in n['name']),None)
def bond_n(p,part,v):
    n=npc_by(p,part)
    if n: n['bond']=max(0,min(100,n['bond']+v))
def add_npc(p,o):
    if not any(n['name']==o['name'] for n in p['npcs']):
        p['npcs'].append(o); glog(p,o['ico'],'你认识了新朋友：'+o['name']+'。')
def uniq_name(p):
    used=[n['name'] for n in p['npcs']]
    pool=[n for n in NPCNAMES if n not in used]
    return random.choice(pool) if pool else random.choice(NPCNAMES)+'二世'
def req_met(p,r):
    if r.get('exam'): return False  # 考公岗位只能通过考公事件入职
    return ((not r.get('major') or r['major']==p['major']) and
            (not r.get('smart') or p['stats']['smart']>=r['smart']) and
            (not r.get('fit') or p['stats']['fit']>=r['fit']) and
            (not r.get('charm') or p['stats']['charm']>=r['charm']))
def promo_met(p,n):
    r=n[2]
    return ((not r.get('smart') or p['stats']['smart']>=r['smart']) and
            (not r.get('fit') or p['stats']['fit']>=r['fit']) and
            (not r.get('charm') or p['stats']['charm']>=r['charm']) and
            (not r.get('fame') or p['fame']>=r['fame']) and
            (not r.get('y') or p['yearsLvl']>=r['y']) and
            (not r.get('money') or assets(p)>=r['money']) and
            (not r.get('loyal') or p.get('loyal',0)>=r['loyal']) and
            (not r.get('fans') or p.get('fans',0)>=r['fans']))
def can_job(p): return (not p['job']) and (not p['pension']) and p['edu'] in ('社会','职校毕业','大学毕业')
def eligible_offers(p): return [c for c in CAREERS if req_met(p,c[2][0][2])]
def career_of(p): return next((c for c in CAREERS if c[0]==p['job']),None) if p['job'] else None
def chk(p,k,thr): return p['stats'][k]+random.randint(0,24)+(3 if has_tr(p,'care') else 0)>=thr
def child_of(p): return next((n for n in p['npcs'] if n['type']=='子女'),None)
def child_age(p):
    n=child_of(p)
    return (p['age']-n.get('born_age',p['age']-25)) if n else None
def world_of(p):
    return p.setdefault('world',{'cycle':'平稳','left':3})

# ---------------- 行动定义 ----------------
def build_actions(p):
    L=[];st=stage_of(p['age'])
    def A(i,ic,n,d,fn): L.append({'id':i,'ic':ic,'n':n,'d':d,'fn':fn})
    if st=='child':
        A('study','书','认真学习','知识成长，考试更稳',lambda:(stg(p,'smart',3),sst(p,'mood',-1),'你认真完成了一天的功课，进步看得见。')[2])
        A('play','玩','出去玩耍','心情+4 体能+1',lambda:(stg(p,'fit',1),sst(p,'mood',4),'你在外面玩得满头大汗，笑得像个小太阳。')[2])
        A('hobby','艺','培养兴趣','魅力+2 心情+1',lambda:(stg(p,'charm',2),sst(p,'mood',1),'你在兴趣班做了个小作品，被贴上展示墙。')[2])
        A('family','家','陪陪家人','父母好感+4 心情+2',lambda:(bond_n(p,'爸爸',4),bond_n(p,'妈妈',4),sst(p,'mood',2),'你和爸妈一起度过了温馨的时光。')[3])
        A('rest','休','好好休息','健康+2 心情+1',lambda:(sst(p,'health',2),sst(p,'mood',1),'你睡了个香甜的懒觉，精神满满。')[2])
    elif st=='teen':
        A('study','书','用功读书','知识成长，考试更稳',lambda:(stg(p,'smart',3),sst(p,'mood',-1),'你埋头刷完一套题，感觉脑子更好使了。')[2])
        A('exercise','炼','锻炼身体','体能+3 健康+1',lambda:(stg(p,'fit',3),sst(p,'health',1),'你在操场上奔跑跳跃，身体越来越棒。')[2])
        A('fun','乐','放松一下','花¥100 心情+4',lambda:_fun(p,100,6 if has_tal(p,'kid') else 4,'你痛痛快快地玩了一场，烦恼一扫而空。'))
        A('hobby','艺','发展爱好','魅力+2 心情+1',lambda:(stg(p,'charm',2),sst(p,'mood',1),'你坚持练习爱好，作品越来越有样子了。')[2])
        A('family','家','陪陪家人','父母好感+4 心情+2',lambda:(bond_n(p,'爸爸',4),bond_n(p,'妈妈',4),sst(p,'mood',2),'一家人吃了顿热乎饭，聊了好多学校趣事。')[3])
        A('rest','休','好好休息','健康+2 心情+1',lambda:(sst(p,'health',2),sst(p,'mood',1),'你补了个好觉，整个人都清爽了。')[2])
        if p['age']>=16: A('part','工','周末兼职','赚零花钱 心情-2',lambda:_part(p))
    elif st=='adult':
        A('study','书','进修学习','知识+3 为晋升蓄力',lambda:(stg(p,'smart',3),'你下班后坚持学习，专业能力又上台阶。')[1])
        A('exercise','炼','锻炼身体','体能+2 健康+2',lambda:(stg(p,'fit',2),sst(p,'health',2),'你挥汗如雨，感觉身体轻盈了不少。')[2])
        A('fun','乐','娱乐放松','花¥200 心情+5',lambda:_fun(p,200,7 if has_tal(p,'kid') else 5,'你看了一场电影、吃了顿好的，心情美丽。'))
        A('rest','休','好好休息','健康+3 心情+2',lambda:(sst(p,'health',3),sst(p,'mood',2),'你彻底放空了一下，精力回满。')[2])
        A('social','友','社交时光','聊天/送礼/约会/求婚',lambda:(open_social(),None)[1])
        if p['job']:
            A('work','职','加班赶工','多赚钱 但累',lambda:_overtime(p))
            if p['job']=='media': A('create','🎬','创作更新','涨粉（收入随粉丝增长）',lambda:_media_create())
        A('fin','财','理财规划','存款与基金打理',lambda:(open_fin(),None)[1])
        if not p['house']: A('house','房','安家置业','租房或买房',lambda:(open_house(),None)[1])
        if can_job(p): A('jobseek','聘','寻找工作','看看有哪些岗位',lambda:(open_job(),None)[1])
        A('shopping','购','奖励自己','花¥800 心情+4 魅力+1',lambda:_shopping(p))
        A('travel','行','来场旅行','花¥5000 大幅放松',lambda:_travel(p))
    else:
        A('exercise','炼','晨练锻炼','体能+2 健康+2',lambda:(stg(p,'fit',2),sst(p,'health',2),'清晨的空气特别好，你打完一套拳神清气爽。')[2])
        A('family','家','天伦之乐','家人好感+5 心情+4',lambda:_family_senior(p))
        A('social','友','老友叙旧','和老朋友聚聚',lambda:(open_social(),None)[1])
        A('fun','乐','社区活动','花¥100 心情+4 声望+1',lambda:_community(p))
        A('rest','休','休养身心','健康+3 心情+2',lambda:(sst(p,'health',3),sst(p,'mood',2),'你泡了壶茶晒着太阳，慢下来了。')[2])
        A('fin','财','理财规划','打理养老钱',lambda:(open_fin(),None)[1])
        A('travel','行','圆梦旅行','花¥5000 心情+10',lambda:_travel(p))
    return L

def _fun(p,cost,mood,msg):
    if p['money']<cost: return '钱包有点紧，这次先忍忍吧。'
    mny(p,-cost); sst(p,'mood',mood); return msg
def _part(p):
    opts=[x for x in PARTTIME if (not x[2]) or p['stats']['smart']>=55]
    o=opts[-1]; p['money']+=o[1]; sst(p,'mood',-2); sst(p,'health',-1)
    return '你周末去'+o[0]+'，赚了 '+fmt_m(o[1])+' 零花钱。'
def _overtime(p):
    c=career_of(p); g=round(c[2][p['jobLvl']][1]*0.15)
    p['money']+=g; sst(p,'mood',-2); sst(p,'health',-1)
    return '你加班赶完了项目，多拿了 '+fmt_m(g)+' 奖金。'
def _shopping(p):
    if p['money']<800: return '预算不够，这波先忍住。'
    mny(p,-800); sst(p,'mood',4); stg(p,'charm',1)
    return '你给自己添了新行头，整个人都在发光。'
def _travel(p):
    if p['money']<5000: return '旅行的预算还没攒够呢。'
    mny(p,-5000); sst(p,'mood',10); sst(p,'health',2); famev(p,1)
    return '你看过了山与海，心里装满了故事。'
def _community(p):
    if p['money']<100: return '先让钱包缓一缓。'
    mny(p,-100); sst(p,'mood',4); famev(p,1)
    return '你在社区活动里交了新朋友，还被夸精神好。'
def _family_senior(p):
    bond_n(p,'子女',5); bond_n(p,'配偶',5); bond_n(p,'爸爸',3); bond_n(p,'妈妈',3); sst(p,'mood',4)
    cn=child_of(p)
    if cn: cn.setdefault('dev',{'smart':35,'fit':35,'close':55})['close']=min(100,cn['dev']['close']+2)
    return '一家人围坐在一起，是最踏实的幸福。'

# ---------------- 事件 ----------------
EVENTS=[
 {'ic':'郊游','t':'学校组织郊游','txt':'班里要组织去公园郊游，费用20元。','w':10,
  'when':lambda p:stage_of(p['age'])=='child','cs':[
  {'t':'一起去玩！','fn':lambda:(mny(G['p'],-20),sst(G['p'],'mood',6),bond_n(G['p'],'同学',3),'你在草地上和同学们玩了一下午，开心极了！')[3]},
  {'t':'留在教室看书','fn':lambda:(stg(G['p'],'smart',3),'你安静地读完了半本故事书，收获满满。')[1]}]},
 {'ic':'兴趣','t':'兴趣班报名','txt':'少年宫在招兴趣班，你想学点什么？','w':8,
  'when':lambda p:stage_of(p['age'])=='child','cs':[
  {'t':'学钢琴（¥200）','fn':lambda:_hobby_class(200,3,0,'你的琴声越来越动听了。')},
  {'t':'学画画（¥150）','fn':lambda:_hobby_class(150,2,1,'你的画在校园画展上得了小星星！')},
  {'t':'在家自由玩','fn':lambda:(sst(G['p'],'mood',2),'你用纸箱搭了一座城堡，也很有趣。')[1]}]},
 {'ic':'别扭','t':'和小伙伴闹别扭','txt':'你和朋友因为一点小事吵起来了。','w':8,
  'when':lambda p:stage_of(p['age'])=='child','cs':[
  {'t':'主动和好','fn':lambda:(bond_n(G['p'],'同学',6),stg(G['p'],'charm',1),'你先伸出了手，你们的友谊反而更深了。')[2]},
  {'t':'等TA先道歉','fn':lambda:(bond_n(G['p'],'同学',-4),sst(G['p'],'mood',-1),'你们冷战了好几天，心里都不好受。')[2]},
  {'t':'请老师帮忙','fn':lambda:(bond_n(G['p'],'同学',2),famev(G['p'],1),'老师帮你们和好了，还夸你懂事。')[2]}]},
 {'ic':'钱包','t':'捡到一个钱包','txt':'放学路上，你捡到一个鼓鼓的钱包。','w':6,
  'when':lambda p:stage_of(p['age'])=='child','cs':[
  {'t':'交给老师','fn':lambda:(famev(G['p'],4),sst(G['p'],'mood',2),'失主特地来道谢，你成了班里的小英雄！')[2]},
  {'t':'买文具分给大家','fn':lambda:(stg(G['p'],'smart',1),bond_n(G['p'],'同学',3),sst(G['p'],'mood',2),'同学们都很开心，虽然你有点心虚。')[3]}]},
 {'ic':'运动','t':'学校运动会','txt':'一年一度的运动会开始报名啦！','w':7,
  'when':lambda p:stage_of(p['age'])=='child','cs':[
  {'t':'报名短跑','fn':lambda:_sports_day()},
  {'t':'当啦啦队','fn':lambda:(sst(G['p'],'mood',2),bond_n(G['p'],'同学',2),'你的加油声最响亮，大家都很感谢你。')[2]}]},
 {'ic':'竞赛','t':'数学竞赛通知','txt':'学校要选拔同学参加数学竞赛。','w':6,
  'when':lambda p:9<=p['age']<=17,'cs':[
  {'t':'报名挑战','fn':lambda:_math_contest()},
  {'t':'在台下鼓掌','fn':lambda:'你默默记下了那些难题，准备下次再战。'}]},
 {'ic':'独处','t':'独自在家的傍晚','txt':'爸妈加班，家里只有你一个人。','w':6,
  'when':lambda p:stage_of(p['age'])=='child','cs':[
  {'t':'看纪录片','fn':lambda:(sst(G['p'],'mood',4),'你看完了两集纪录片，大开眼界。')[1]},
  {'t':'预习功课','fn':lambda:(stg(G['p'],'smart',3),'你把明天的课预习了一遍，自信满满。')[1]},
  {'t':'做航模','fn':lambda:(stg(G['p'],'charm',2),'你拼了一架橡皮筋飞机，飞过了整个客厅。')[1]}]},
 {'ic':'选举','t':'班干部选举','txt':'新学期要选班干部，要不要试试？','w':7,
  'when':lambda p:stage_of(p['age'])=='teen','cs':[
  {'t':'上台竞选','fn':lambda:_election()},
  {'t':'为好友投票','fn':lambda:(bond_n(G['p'],'同学',6),'好友当选后第一个感谢了你。')[1]}]},
 {'ic':'手机','t':'手机的诱惑','txt':'写作业时，手机一直在旁边闪光。','w':8,
  'when':lambda p:stage_of(p['age'])=='teen','cs':[
  {'t':'就刷一会儿…','fn':lambda:(sst(G['p'],'mood',4),stg(G['p'],'smart',-1),'一转眼两个小时没了，作业还空着。')[2]},
  {'t':'把手机收起来','fn':lambda:(stg(G['p'],'smart',2),sst(G['p'],'mood',1),'你专注地完成了作业，还有时间打了会球。')[2]}]},
 {'ic':'义卖','t':'爱心义卖','txt':'学校组织义卖活动，同学们各显神通。','w':6,
  'when':lambda p:stage_of(p['age'])=='teen','cs':[
  {'t':'去帮忙摆摊','fn':lambda:(G['p'].__setitem__('money',G['p']['money']+100),famev(G['p'],3),stg(G['p'],'charm',2),'你帮义卖筹了不少钱，还被授予了爱心徽章。')[3]},
  {'t':'买件手工艺品','fn':lambda:(mny(G['p'],-100),sst(G['p'],'mood',3),'你买到的小陶笛吹起来呜呜响，超可爱。')[2]}]},
 {'ic':'心动','t':'心动的感觉','txt':'班里有个同学，总让你想多看两眼。','w':6,
  'when':lambda p:stage_of(p['age'])=='teen' and p['age']>=13,'cs':[
  {'t':'把心思放进学习','fn':lambda:(stg(G['p'],'smart',4),'你把这份悸动写进了日记，成绩反而更好了。')[1]},
  {'t':'大方做朋友','fn':lambda:(add_npc(G['p'],{'name':uniq_name(G['p']),'type':'同学','bond':55,'ico':'同'}),'青涩的友谊开始了，一起放学回家的路都变短了。')[1]}]},
 {'ic':'复习','t':'考试前夜','txt':'明天有重要考试，现在还不困。','w':6,
  'when':lambda p:stage_of(p['age'])=='teen','cs':[
  {'t':'开夜车复习','fn':lambda:(stg(G['p'],'smart',3),sst(G['p'],'health',-2),'你复习到凌晨，知识进脑子了，黑眼圈也来了。')[2]},
  {'t':'按时睡觉','fn':lambda:(sst(G['p'],'health',2),stg(G['p'],'smart',1),'睡饱的你第二天思路格外清晰。')[2]}]},
 {'ic':'真相','t':'看见真相','txt':'你看到有同学被误会了，真相和你想的不同。','w':5,
  'when':lambda p:p['age']<18,'cs':[
  {'t':'站出来说明','fn':lambda:(famev(G['p'],4),bond_n(G['p'],'同学',2),'真相大白，被误会的同学含泪谢了你。')[2]},
  {'t':'私下安慰TA','fn':lambda:(bond_n(G['p'],'同学',5),sst(G['p'],'mood',1),'你悄悄递上一张纸条：我信你。')[2]}]},
 {'ic':'聚餐','t':'同事聚餐','txt':'下班后同事们喊你一起聚餐。','w':8,
  'when':lambda p:stage_of(p['age'])=='adult' and p['job'],'cs':[
  {'t':'大方请客','fn':lambda:(mny(G['p'],-300),_bond_type('同事',6),famev(G['p'],2),sst(G['p'],'mood',2),'这顿饭吃得热热闹闹，团队气氛更好了。')[4]},
  {'t':'婉拒回家','fn':lambda:(sst(G['p'],'mood',-1),'你回家煮了碗面，早早休息了。')[1]}]},
 {'ic':'谈判','t':'加薪谈判','txt':'年度面谈，你鼓起勇气想聊聊薪资。','w':6,
  'when':lambda p:stage_of(p['age'])=='adult' and p['job'],'cs':[
  {'t':'大胆争取','fn':lambda:_raise_talk()},
  {'t':'继续默默努力','fn':lambda:(stg(G['p'],'smart',2),'你把劲头放回了工作里，稳扎稳打。')[1]}]},
 {'ic':'重逢','t':'旧友重逢','txt':'街头转角，你撞见了多年不见的老朋友。','w':6,
  'when':lambda p:p['age']>=18,'cs':[
  {'t':'坐下叙叙旧','fn':lambda:(bond_n(G['p'],'朋友',8),sst(G['p'],'mood',3),'你们聊到了打烊，好像从未分开过。')[2]},
  {'t':'约一场旅行','fn':lambda:_reunion_trip()}]},
 {'ic':'心动','t':'心动瞬间','txt':'咖啡店里，有人多看了你一眼，你也多看了回去。','w':7,
  'when':lambda p:p['age']>=18 and not p['flags']['married'] and not any(n['type']=='恋人' for n in p['npcs']),'cs':[
  {'t':'上前认识一下','fn':lambda:(add_npc(G['p'],{'name':uniq_name(G['p']),'type':'朋友','bond':60,'ico':'友'}),sst(G['p'],'mood',3),'你们交换了联系方式，故事也许才刚刚开始。')[2]},
  {'t':'微笑错过','fn':lambda:(sst(G['p'],'mood',1),'有些人适合留在故事里。你继续向前走。')[1]}]},
 {'ic':'体检','t':'体检提醒','txt':'年度体检报告出来了，医生皱了皱眉。','w':6,
  'when':lambda p:p['age']>=25,'cs':[
  {'t':'开始锻炼计划','fn':lambda:(stg(G['p'],'fit',3),sst(G['p'],'health',3),'你办了张健身卡，身体数据慢慢好看了。')[2]},
  {'t':'问题不大吧','fn':lambda:(sst(G['p'],'health',-1),'你把报告塞回抽屉，希望明年别再这样。')[1]}]},
 {'ic':'理财','t':'理财讲座','txt':'银行在办理财讲座，送一桶油。','w':6,
  'when':lambda p:p['age']>=20 and assets(G['p'])>20000,'cs':[
  {'t':'存笔定期','fn':lambda:(mny(G['p'],-5000),G['p'].__setitem__('bank',G['p']['bank']+5000),'你存了 5000 元定期，睡觉都踏实了。')[2]},
  {'t':'试试基金','fn':lambda:(mny(G['p'],-5000),G['p'].__setitem__('fund',G['p']['fund']+5000),'你拿出 5000 元试水基金，涨跌皆是学问。')[2]},
  {'t':'听完就拿油走','fn':lambda:(sst(G['p'],'mood',1),'油是真香，理财明天再说。')[1]}]},
 {'ic':'马拉松','t':'城市马拉松','txt':'一年一度的马拉松开始报名了。','w':6,
  'when':lambda p:p['age']>=16 and p['stats']['fit']>=50 and not p['flags']['mara'],'cs':[
  {'t':'报名参赛','fn':lambda:_marathon()},
  {'t':'路边助威','fn':lambda:(sst(G['p'],'mood',2),'你举着牌子给跑者加油，也被这份热血感染。')[1]}]},
 {'ic':'生日','t':'爸妈的生日','txt':'日历提醒你：今天是爸妈的生日。','w':6,
  'when':lambda p:p['age']>=18,'cs':[
  {'t':'精心准备礼物','fn':lambda:(mny(G['p'],-500),bond_n(G['p'],'爸爸',10),bond_n(G['p'],'妈妈',10),sst(G['p'],'mood',4),'爸妈嘴上说乱花钱，却把礼物摆在了最显眼的地方。')[4]},
  {'t':'打个电话','fn':lambda:(bond_n(G['p'],'爸爸',4),bond_n(G['p'],'妈妈',4),sst(G['p'],'mood',1),'电话那头笑声不断，爸妈说听到声音就高兴。')[3]}]},
 {'ic':'感冒','t':'重感冒','txt':'你喉咙发痒，头昏昏沉沉。','w':6,'when':lambda p:True,'cs':[
  {'t':'及时就医','fn':lambda:(mny(G['p'],-300),sst(G['p'],'health',2),'吃了药休息两天，很快满血复活。')[2]},
  {'t':'硬扛过去','fn':lambda:(sst(G['p'],'health',-3),sst(G['p'],'mood',-2),'拖了一周才好，身体被掏空。')[2]}]},
 {'ic':'志愿','t':'社区志愿者','txt':'社区在招募周末志愿者。','w':5,
  'when':lambda p:p['age']>=12,'cs':[
  {'t':'报名参加','fn':lambda:(famev(G['p'],5),sst(G['p'],'mood',3),'你帮独居老人修了水管，收到了一面小锦旗。')[2]},
  {'t':'下次一定','fn':lambda:'你收藏了报名链接，打算下次再去。'}]},
 {'ic':'中场','t':'人生中场','txt':'站在人生的半山腰，你想起点什么。','w':6,
  'when':lambda p:40<=p['age']<60,'cs':[
  {'t':'重拾年轻时的爱好','fn':lambda:(stg(G['p'],'charm',3),sst(G['p'],'mood',5),'你翻出落灰的吉他，指尖还记得旋律。')[2]},
  {'t':'认真做养老规划','fn':lambda:(mny(G['p'],-5000),G['p'].__setitem__('bank',G['p']['bank']+5000),stg(G['p'],'smart',1),'你理清了账本，未来的路清晰了不少。')[3]}]},
 {'ic':'晨光','t':'清晨的广场','txt':'清晨的广场上，队伍正练得整齐热闹。','w':6,
  'when':lambda p:p['age']>=55,'cs':[
  {'t':'加入他们','fn':lambda:(sst(G['p'],'health',3),sst(G['p'],'mood',3),add_npc(G['p'],{'name':uniq_name(G['p']),'type':'朋友','bond':45,'ico':'友'}),'你成了队伍里的领队，认识了一群活力满满的朋友。')[3]},
  {'t':'安静散步','fn':lambda:(sst(G['p'],'health',1),'你沿着河边走了一大圈，浑身舒展。')[1]}]},
 {'ic':'让贤','t':'升职让贤','txt':'部门有个晋升名额，你和老搭档都够格。','w':5,
  'when':lambda p:stage_of(p['age'])=='adult' and p['job'] and p['yearsLvl']>=2,'cs':[
  {'t':'推荐老搭档','fn':lambda:(famev(G['p'],3),_bond_type('同事',6),sst(G['p'],'mood',2),'你的大度传遍了公司，人缘值拉满。')[3]},
  {'t':'自己全力争取','fn':lambda:_promotion_fight()}]},
 {'ic':'读书','t':'读书月','txt':'图书馆的读书月活动开始了。','w':5,
  'when':lambda p:p['age']>=12,'cs':[
  {'t':'精读一本好书','fn':lambda:(stg(G['p'],'smart',4),'你做了满满一本笔记，感觉脑子被喂饱了。')[1]},
  {'t':'听书放松','fn':lambda:(sst(G['p'],'mood',3),'你边散步边听书，惬意又充实。')[1]}]},
 {'ic':'新面孔','t':'新面孔','txt':'生活里出现了一张新面孔。','w':6,'when':lambda p:True,'cs':[
  {'t':'主动打个招呼','fn':lambda:_new_face()},
  {'t':'保持礼貌距离','fn':lambda:'你点头微笑，各自继续赶路。'}]},
# ---- v1.1 扩充：金钱坑 / 子女 / 晚年 / 婚恋 / 人生标签 ----
 {'ic':'学区','t':'学区房','txt':'为了孩子上学，中介推来一套学区房，首付+总价约120万。','w':7,
  'when':lambda p:p['flags']['married'] and p['flags']['child'] and 28<=p['age']<=40 and assets(p)>=1200000,'cs':[
  {'t':'咬牙买下','fn':lambda:(mny(G['p'],-1200000),bond_n(G['p'],'子女',12),famev(G['p'],5),sst(G['p'],'mood',3),tl(G['p'],'为孩子买下学区房'),'掏空积蓄换来了重点学校的入场券。')[5]},
  {'t':'理性观望','fn':lambda:(stg(G['p'],'smart',1),sst(G['p'],'mood',1),'你算了算账，决定再看看。')[2]}]},
 {'ic':'琴键','t':'孩子的兴趣班','txt':'孩子吵着要学钢琴，一期的费用不便宜。','w':7,
  'when':lambda p:p['flags']['child'] and 28<=p['age']<=38,'cs':[
  {'t':'报！一年8000','fn':lambda:((lambda p:(mny(p,-8000),bond_n(p,'子女',8),stg(p,'charm',2),'家里有了琴声，孩子学得有模有样。'))(G['p']))[2]},
  {'t':'公园放养','fn':lambda:(bond_n(G['p'],'子女',4),sst(G['p'],'mood',2),'你和孩子在公园疯跑了一个周末，也很快乐。')[2]}]},
 {'ic':'大学','t':'孩子考上大学','txt':'孩子拿到了录取通知书，学费生活费是一笔大开支。','w':8,
  'when':lambda p:p['flags']['child'] and 45<=p['age']<=52,'cs':[
  {'t':'全额支持（8万）','fn':lambda:_child_college(True)},
  {'t':'助学贷款+生活费','fn':lambda:_child_college(False)}]},
 {'ic':'青春','t':'青春期的孩子','txt':'孩子最近把房门一关，和你没话说。','w':6,
  'when':lambda p:p['flags']['child'] and 38<=p['age']<=46,'cs':[
  {'t':'平等对话','fn':lambda:(bond_n(G['p'],'子女',5),sst(G['p'],'mood',-1),'你学会了先听再说，门重新打开了。')[2]},
  {'t':'立下规矩','fn':lambda:(bond_n(G['p'],'子女',-4),famev(G['p'],1),'规矩立住了，关系却僵了一阵。')[2]}]},
 {'ic':'病房','t':'父母住院','txt':'爸妈之一突然住院，需要人手和钱。','w':6,
  'when':lambda p:p['age']>=50,'cs':[
  {'t':'尽全力救治（3万）','fn':lambda:_parents_hosp(True)},
  {'t':'医保方案（3千）','fn':lambda:_parents_hosp(False)}]},
 {'ic':'体检','t':'高端体检套餐','txt':'体检中心推来一份深度筛查套餐。','w':5,
  'when':lambda p:p['age']>=60,'cs':[
  {'t':'做个全面的（2千）','fn':lambda:(mny(G['p'],-2000),sst(G['p'],'health',4),'两项隐患被提前发现，值。')[2]},
  {'t':'基础体检就好','fn':lambda:(sst(G['p'],'health',1),'常规项目，一切尚可。')[1]}]},
 {'ic':'金婚','t':'金婚纪念','txt':'转眼和伴侣携手走过了半个世纪。','w':6,
  'when':lambda p:p['flags']['married'] and p['age']>=75 and (bond_n(G['p'],'配偶',0) or next((n['bond'] for n in p['npcs'] if n['type']=='配偶'),0)>=60),'cs':[
  {'t':'办一场金婚宴（2万）','fn':lambda:(mny(G['p'],-20000),famev(G['p'],6),bond_n(G['p'],'配偶',10),sst(G['p'],'mood',10),tl(G['p'],'金婚宴'),'满堂儿孙举杯，你们笑出了一脸褶子。')[5]},
  {'t':'两个人简单过','fn':lambda:(bond_n(G['p'],'配偶',5),sst(G['p'],'mood',5),'一壶茶，两个人，一下午。')[2]}]},
 {'ic':'老友','t':'病榻前的老友','txt':'老友病重住院，家人说他念叨你的名字。','w':5,
  'when':lambda p:p['age']>=65,'cs':[
  {'t':'去病房坐坐','fn':lambda:(bond_n(G['p'],'朋友',8),sst(G['p'],'mood',-2),'你们聊了一下午年轻时候的事，他笑了很多。')[2]},
  {'t':'遥寄一束花','fn':lambda:(bond_n(G['p'],'朋友',3),'你托人送去了花和卡片。')[1]}]},
 {'ic':'回忆','t':'写回忆录','txt':'社区文化站邀请老人留下人生故事。','w':5,
  'when':lambda p:p['age']>=68,'cs':[
  {'t':'动笔写一本','fn':lambda:(mny(G['p'],-2000),stg(G['p'],'smart',2),famev(G['p'],4),tl(G['p'],'出版回忆录'),'你的人生被装订成册，社区传阅。')[4]},
  {'t':'口述给孙辈','fn':lambda:(bond_n(G['p'],'子女',6),sst(G['p'],'mood',3),'孩子们听得入迷，比任何故事书都好看。')[2]}]},
 {'ic':'棋局','t':'巷口棋局','txt':'巷口的象棋摊缺一个对手。','w':6,
  'when':lambda p:p['age']>=60,'cs':[
  {'t':'坐下杀一盘','fn':lambda:_chess_game()}]},
 {'ic':'催生','t':'长辈的关心','txt':'家里长辈又开始旁敲侧击："什么时候要孩子？"','w':6,
  'when':lambda p:p['flags']['married'] and not p['flags']['child'] and not p['flags']['dink'] and 28<=p['age']<=38,'cs':[
  {'t':'过好二人世界','fn':lambda:(G['p']['flags'].__setitem__('dink',True),sst(G['p'],'mood',3),bond_n(G['p'],'配偶',3),'你想清楚了：你们的生活方式自己定。')[3]},
  {'t':'顺其自然','fn':lambda:(sst(G['p'],'mood',2),'缘分到了自然会有。')[1]}]},
 {'ic':'危机','t':'婚姻的坎','txt':'最近和伴侣总为琐事争吵，感觉越来越远。','w':4,
  'when':lambda p:p['flags']['married'] and (bond_n(G['p'],'配偶',0) or next((n['bond'] for n in p['npcs'] if n['type']=='配偶'),0)>=40),'cs':[
  {'t':'一次深刻的谈话','fn':lambda:(bond_n(G['p'],'配偶',8),sst(G['p'],'mood',2),'你们把话说开了，比婚前还默契。')[2]},
  {'t':'冷战一周','fn':lambda:(bond_n(G['p'],'配偶',-8),sst(G['p'],'mood',-4),'同一屋檐下的两个陌生人。')[2]}]},
 {'ic':'创业','t':'辞职创业？','txt':'一个靠谱的创业想法找上了你，启动资金约20万。','w':6,
  'when':lambda p:30<=p['age']<=50 and p['job'] and assets(p)>=300000 and not (set(p['tags']) & {'创业成功','创业失败','东山再起'}),'cs':[
  {'t':'放手一搏','fn':lambda:_startup()},
  {'t':'安心打工','fn':lambda:(sst(G['p'],'mood',1),'你把想法记在了本子上。')[1]}]},
 {'ic':'再起','t':'东山再起','txt':'当年创业失败的坑，你一直想填上。','w':7,
  'when':lambda p:'创业失败' in p['tags'] and p['age']<60,'cs':[
  {'t':'带着经验再来','fn':lambda:_comeback()},
  {'t':'让它过去','fn':lambda:(sst(G['p'],'mood',3),'你与自己和解了，也是一种成功。')[1]}]},
 {'ic':'代言','t':'品牌代言','txt':'跑马拉松的照片被运动品牌看中了。','w':5,
  'when':lambda p:p['flags']['mara'] and p['age']>=18 and p['age']<65,'cs':[
  {'t':'接下代言','fn':lambda:(G['p'].__setitem__('money',G['p']['money']+15000),famev(G['p'],5),sst(G['p'],'mood',1),'你穿上了印着自己名字的跑鞋。')[3]},
  {'t':'只为热爱而跑','fn':lambda:(famev(G['p'],1),'你婉拒了，跑鞋还是旧的舒服。')[1]}]},
 {'ic':'回响','t':'学霸的回响','txt':'同学聚会，你当年金榜题名的事又被提起。','w':5,
  'when':lambda p:'zhuangyuan' in p['ach'] and p['age']>=30,'cs':[
  {'t':'笑着举杯','fn':lambda:(sst(G['p'],'mood',4),famev(G['p'],2),'那段拼命的岁月，值得被反复提起。')[2]}]},
 {'ic':'大赛','t':'技能大赛','txt':'行业技能大赛开始报名，有奖金和名次。','w':7,
  'when':lambda p:p['edu'] in ('职校','职校毕业') and 17<=p['age']<=30,'cs':[
  {'t':'报名参赛','fn':lambda:_skill_contest()},
  {'t':'去观摩学习','fn':lambda:(stg(G['p'],'smart',1),'你看高手过招，偷偷记了三招。')[1]}]},
 {'ic':'拜师','t':'拜师学艺','txt':'车间里的老师傅说看你踏实，愿意带带你。','w':7,
  'when':lambda p:p['edu']=='职校' and 15<=p['age']<=17,'cs':[
  {'t':'正式拜师','fn':lambda:(stg(G['p'],'smart',3),bond_n(G['p'],'同学',4),'师傅倾囊相授，你的手艺突飞猛进。')[2]},
  {'t':'自己摸索','fn':lambda:(stg(G['p'],'smart',2),sst(G['p'],'mood',-1),'你走了一些弯路，也练出了自己的路子。')[2]}]},
# ---- v1.2 扩充：时代背景 / 公务员 / 自媒体 / 子女探望 ----
 {'ic':'考场','t':'公务员招考','txt':'公务员招考公告发布，报名通道开启。','w':5,
  'when':lambda p:22<=p['age']<=35 and p['edu'] in ('大学毕业','社会','职校毕业') and p['stats']['smart']>=60 and p['job']!='gov','cs':[
  {'t':'报名应考','fn':lambda:_gov_exam()},
  {'t':'今年不考','fn':lambda:(sst(G['p'],'mood',1),'你把公告收藏了起来。')[1]}]},
 {'ic':'送礼','t':'一份“心意”','txt':'办事对象塞来一份厚礼，四下无人。','w':5,
  'when':lambda p:p['job']=='gov' and p.get('loyal',0)>=0,'cs':[
  {'t':'收下','fn':lambda:(G['p'].__setitem__('money',G['p']['money']+20000),G['p'].__setitem__('loyal',G['p'].get('loyal',0)-15),G['p']['tags'].append('贪腐风险'),'你把礼物搬回了家，心里有点发虚。')[3]},
  {'t':'原封退回','fn':lambda:(G['p'].__setitem__('loyal',G['p'].get('loyal',0)+10),famev(G['p'],2),'你把礼退了回去，心里踏实。')[2]},
  {'t':'上交组织','fn':lambda:(G['p'].__setitem__('loyal',G['p'].get('loyal',0)+15),famev(G['p'],4),'组织通报表扬了你的做法。')[2]}]},
 {'ic':'审查','t':'纪委的谈话','txt':'有人实名举报了你当年的问题，纪委找你谈话。','w':8,
  'when':lambda p:p['age']>=60 and ('贪腐风险' in p['tags'] or p.get('loyal',0)<0),'cs':[
  {'t':'主动交代，退缴款项','fn':lambda:(mny(G['p'],-100000),
      [G['p']['tags'].remove(t) for t in ('贪腐风险',) if t in G['p']['tags']],
      G['p'].__setitem__('loyal',0),tl(G['p'],'主动交代问题'),'你退缴了全部款项，组织给了你改过的机会。')[4]},
  {'t':'心存侥幸','fn':lambda:_xinger()}]},
 {'ic':'裁员','t':'裁员潮','txt':'经济下行，公司开始“人员优化”，名单里有你的名字。','w':8,
  'when':lambda p:world_of(p)['cycle']=='衰退' and p['job'] and p['job']!='gov' and 22<=p['age']<=58,'cs':[
  {'t':'接受补偿，另谋出路','fn':lambda:_layoff(True)},
  {'t':'主动降薪苟住','fn':lambda:(G['p'].__setitem__('raise',G['p']['raise']*0.9),sst(G['p'],'mood',-3),'你保住了工作，工资降了一成。')[2]}]},
 {'ic':'风口','t':'时代风口','txt':'新技术浪潮席卷而来，身边人都在聊新机会。','w':6,
  'when':lambda p:world_of(p)['cycle']=='浪潮' and p['stats']['smart']>=60 and p['age']>=18,'cs':[
  {'t':'认真学习新技能','fn':lambda:(stg(G['p'],'smart',3),stg(G['p'],'charm',1),'你啃下了新领域的入门课，站上了风口。')[2]},
  {'t':'再看看再说','fn':lambda:(sst(G['p'],'mood',1),'风口年年有，你先观望。')[1]}]},
 {'ic':'爆款','t':'突然爆了','txt':'你随手发的一条内容被顶上了热门！','w':6,
  'when':lambda p:p['job']=='media' and p['fans']>=1000,'cs':[
  {'t':'乘胜追击连更三条','fn':lambda:(G['p'].__setitem__('fans',G['p']['fans']+max(2000,G['p']['fans']//3)),sst(G['p'],'mood',4),sst(G['p'],'health',-2),'粉丝暴涨，你熬了三个大夜。')[3]},
  {'t':'稳住心态慢慢来','fn':lambda:(G['p'].__setitem__('fans',G['p']['fans']+max(500,G['p']['fans']//6)),'流量慢慢沉淀，涨得稳。')[1]}]},
 {'ic':'商单','t':'商单上门','txt':'品牌方发来合作邀约，报价五位数。','w':5,
  'when':lambda p:p['job']=='media' and p['fans']>=10000,'cs':[
  {'t':'接下商单','fn':lambda:(G['p'].__setitem__('money',G['p']['money']+max(3000,G['p']['fans']//20)),G['p'].__setitem__('fans',int(G['p']['fans']*0.98)),'广告发出去，掉了一点粉，赚了一笔钱。')[2]},
  {'t':'只接真心喜欢的产品','fn':lambda:(G['p'].__setitem__('fans',int(G['p']['fans']*1.02)),'粉丝夸你广告都清流。')[1]}]},
 {'ic':'热搜','t':'黑热搜','txt':'一段被掐头去尾的视频把你顶上了黑热搜。','w':4,
  'when':lambda p:p['job']=='media' and p['fans']>=50000,'cs':[
  {'t':'发律师函+危机公关','fn':lambda:(mny(G['p'],-20000),G['p'].__setitem__('fans',int(G['p']['fans']*0.90)),'公关团队火速灭火，掉了一成粉，风波过去。')[2]},
  {'t':'冷处理不回应','fn':lambda:(G['p'].__setitem__('fans',int(G['p']['fans']*0.70)),sst(G['p'],'mood',-5),'舆论发酵了一周，粉丝掉了三成。')[2]}]},
 {'ic':'绕膝','t':'儿孙绕膝','txt':'孩子带着小家伙回家吃饭，满屋子都是笑声。','w':6,
  'when':lambda p:p['age']>=65 and (lambda cn:cn and cn['dev']['close']>=75)(child_of(p)),'cs':[
  {'t':'大展厨艺','fn':lambda:(sst(G['p'],'mood',8),bond_n(G['p'],'子女',3),'小家伙夸你的红烧肉天下第一。')[2]}]},
 {'ic':'电话','t':'一通电话','txt':'孩子打来电话，聊了半小时家常。','w':6,
  'when':lambda p:p['age']>=65 and (lambda cn:cn and 45<=cn['dev']['close']<75)(child_of(p)),'cs':[
  {'t':'多聊一会儿','fn':lambda:(sst(G['p'],'mood',3),bond_n(G['p'],'子女',2),'挂了电话，屋里好像也暖和了一点。')[2]}]},
 {'ic':'冷清','t':'冷清的周末','txt':'说好的回家探望，又临时被加班取消了。','w':6,
  'when':lambda p:p['age']>=65 and (lambda cn:cn and cn['dev']['close']<45)(child_of(p)),'cs':[
  {'t':'主动修复关系','fn':lambda:_reconnect()},
  {'t':'习惯了','fn':lambda:(sst(G['p'],'mood',-3),'你对着空荡荡的客厅，坐了一下午。')[1]}]}]

def _hobby_class(cost,ch,sm,msg):
    p=G['p']
    if p['money']+p['bank']<cost: sst(p,'mood',-1); return '家里暂时拿不出学费，你有点失落。'
    mny(p,-cost); stg(p,'charm',ch); stg(p,'smart',sm); return msg
def _sports_day():
    p=G['p']
    if chk(p,'fit',40):
        stg(p,'fit',3); famev(p,3); sst(p,'mood',3); return '你冲过终点拿了名次，全班都在为你欢呼！'
    stg(p,'fit',2); return '虽然没拿到名次，但你坚持跑完了全程。'
def _math_contest():
    p=G['p']
    if chk(p,'smart',45):
        stg(p,'smart',3); famev(p,4); return '你捧回了奖状，全家人都为你骄傲！'
    stg(p,'smart',2); sst(p,'mood',-1); return '虽然没获奖，但你也学到了很多。'
def _election():
    p=G['p']
    if chk(p,'charm',45):
        stg(p,'charm',3); famev(p,4); bond_n(p,'同学',2); return '你当选了班干部，演讲赢得了满堂掌声！'
    sst(p,'mood',-2); stg(p,'charm',1); return '虽然落选了，但你克服了怯场，下次更从容。'
def _raise_talk():
    p=G['p']
    if chk(p,'charm',55):
        p['raise']=min(1.5,p['raise']*1.1); famev(p,2); tl(p,'谈判加薪成功'); return '老板欣赏你的勇气，给你加薪 10%！'
    sst(p,'mood',-2); return '老板打了个太极，说下次一定。'
def _reunion_trip():
    p=G['p']
    if p['money']<1500: sst(p,'mood',2); return '钱包不允许，你们约好了下次一定。'
    mny(p,-1500); sst(p,'mood',8); bond_n(p,'朋友',10); return '你们来了一场说走就走的短途旅行！'
def _marathon():
    p=G['p']
    if chk(p,'fit',65):
        p['flags']['mara']=True; famev(p,6); stg(p,'fit',3); tl(p,'跑完马拉松全程'); return '你戴着奖牌冲过终点，朋友圈刷屏了！'
    stg(p,'fit',2); sst(p,'health',-1); sst(p,'mood',-1); return '你在 30 公里处抽了筋，遗憾但值得。'
def _promotion_fight():
    p=G['p']
    if chk(p,'charm',50):
        famev(p,5); p['money']+=2000; return '你用一场漂亮的汇报赢下了名额！'
    sst(p,'mood',-2); return '这次差了点运气，但你积累了经验。'
def _new_face():
    p=G['p']; st=stage_of(p['age'])
    t='同学' if st in('child','teen') else ('同事' if (st=='adult' and p['job']) else '朋友')
    ico={'同学':'同','同事':'职'}.get(t,'友')
    add_npc(p,{'name':uniq_name(p),'type':t,'bond':40,'ico':ico})
    return '你们互相认识了，说不定以后会有故事。'
def _bond_type(tp,v):
    for n in G['p']['npcs']:
        if n['type']==tp: n['bond']=max(0,min(100,n['bond']+v))

def _child_college(full):
    p=G['p']
    if full and assets(p)>=80000:
        mny(p,-80000); bond_n(p,'子女',10); famev(p,2); sst(p,'mood',4)
        tl(p,'送孩子上大学'); return '你把攒下的钱拍在桌上："安心读书，家里有我。"'
    bond_n(p,'子女',6); sst(p,'mood',-3)
    return '孩子办了助学贷款，暑期去打工。你既欣慰又有点心酸。'
def _parents_hosp(full):
    p=G['p']
    if full and p['money']+p['bank']>=30000:
        mny(p,-30000); bond_n(p,'爸爸',10); bond_n(p,'妈妈',10); sst(p,'mood',-2); famev(p,1)
        return '你选了最好的方案，爸妈出院那天念叨了半个月。'
    mny(p,-3000); bond_n(p,'爸爸',3); bond_n(p,'妈妈',3)
    return '医保报销了大头，你隔三差五去陪床。'
def _chess_game():
    p=G['p']
    if chk(p,'smart',50):
        sst(p,'mood',4); stg(p,'smart',1); return '一步妙手反杀，围观大爷集体喝彩。'
    sst(p,'mood',2); return '输了棋，赢了一圈棋友。'
def _startup():
    p=G['p']
    prob=0.22+p['stats']['smart']/250+(0.1 if has_tr(p,'adven') else 0)
    cyc=world_of(p)['cycle']
    if cyc in ('繁荣','浪潮'): prob+=0.10
    elif cyc=='衰退': prob-=0.10
    if random.random()<prob:
        p['money']+=300000; famev(p,12); p['raise']=min(1.5,p['raise']*1.3)
        p['tags'].append('创业成功'); tl(p,'创业成功'); snd_up()
        return '你的小生意活了下来，订单越排越满！'
    mny(p,-200000); sst(p,'mood',-8); sst(p,'health',-2)
    p['tags'].append('创业失败'); tl(p,'创业失败'); snd_bad()
    return '项目黄了，20万学费买了个明白。'
def _comeback():
    p=G['p']
    if chk(p,'smart',60):
        p['money']+=80000; famev(p,8)
        if '创业失败' in p['tags']: p['tags'].remove('创业失败')
        p['tags'].append('东山再起'); tl(p,'东山再起'); snd_up()
        return '同样的坑，这次你绕了过去，还赚了一笔。'
    sst(p,'mood',-3); return '再度受挫，但这次你输得起。'
def _skill_contest():
    p=G['p']
    if chk(p,'smart',55):
        p['money']+=2000; famev(p,6); tl(p,'技能大赛获奖'); snd_up()
        return '你捧回了奖杯和2000元奖金，厂里贴了喜报！'
    stg(p,'fit',1); return '止步复赛，但你的手法被评委记住了。'
def _gov_exam():
    p=G['p']
    if chk(p,'smart',65): return _gov_take()
    sst(p,'mood',-2); return '笔试差了 2 分，来年再战。'
def _xinger():
    p=G['p']
    if random.random()<0.5:
        famev(p,1); return '查了半天没查出问题，你有惊无险。'
    famev(G['p'],-40); sst(G['p'],'mood',-20); G['p']['tags'].append('晚节不保'); tl(G['p'],'晚节不保'); snd_bad()
    return '问题坐实，通报全城。半辈子的名声，毁于一旦。'
def _layoff(with_pack):
    p=G['p']; c=career_of(p)
    if with_pack and c:
        pay=c[2][p['jobLvl']][1]; p['money']+=pay*2
    p['job']=None; p['jobLvl']=0; sst(p,'mood',-10); tl(p,'遭遇裁员')
    return '你拿着'+fmt_m(c[2][0][1]*2 if c else 0)+'补偿金走出了写字楼，简历重新挂上了招聘网站。'
def _reconnect():
    p=G['p']; cn=child_of(p)
    if cn:
        cn['dev']['close']=min(100,cn['dev']['close']+6); bond_n(p,'子女',3)
    sst(p,'mood',-1)
    return '你买了TA小时候最爱吃的点心，登了门。'
def _gov_take():
    p=G['p']; p['job']='gov'; p['jobLvl']=0; p['yearsLvl']=0; p['loyal']=20
    tl(p,'考上公务员'); achv(p,'job')
    glog(p,'考公','笔试面试双双过关，你成了一名公务员！铁饭碗到手。'); snd_up()
    return '你考上了公务员，成为一名科员。'
def _media_create():
    p=G['p']
    base=max(1500,350+p['fame']*25)  # 保底基数：起步就够一条播放量，随声望放大
    if p['era'] in (1990,2000): base=int(base*1.4)
    if world_of(p)['cycle']=='浪潮': base=int(base*1.5)
    gain=int(base*random.uniform(0.5,2.5))
    p['fans']+=gain; sst(p,'mood',-1)
    if random.random()<0.12:
        p['fans']+=gain*5; sst(p,'mood',3)
        return '🔥 视频爆了！这条直接涨粉 %s，粉丝总量 %s。'%(fmt_m(gain*5),fmt_m(p['fans']))
    return '你更新了一条作品，涨粉 %s，粉丝总量 %s。'%(fmt_m(gain),fmt_m(p['fans']))
def ev_child_enroll(cn):
    return {'ic':'入学','t':'孩子上小学','txt':cn['name']+'背上小书包，成为一名小学生了。','cs':[
      {'t':'花时间陪伴入学','fn':lambda:(cn['dev'].__setitem__('close',min(100,cn['dev']['close']+6)),cn['dev'].__setitem__('smart',min(100,cn['dev']['smart']+3)),sst(G['p'],'mood',3),'你牵着TA走进校园，TA回头看你的眼神亮亮的。')[3]},
      {'t':'工作太忙','fn':lambda:(cn['dev'].__setitem__('close',max(0,cn['dev']['close']-3)),'你只是转了转账，心里有点亏欠。')[1]}]}
def ev_child_zk(cn):
    ok=cn['dev']['smart']+random.randint(0,25)>=55
    if ok:
        cn['dev']['smart']=min(100,cn['dev']['smart']+3); tl(G['p'],cn['name']+'考上重点高中')
        return {'ic':'中考','t':cn['name']+'的中考','txt':'放榜了！','cs':[{'t':'查看结果','fn':lambda:'孩子考上了重点高中！亲戚朋友都来道贺。'}]}
    cn['dev']['fit']=min(100,cn['dev']['fit']+2)
    return {'ic':'中考','t':cn['name']+'的中考','txt':'放榜了。','cs':[{'t':'查看结果','fn':lambda:'孩子上了普通高中，TA说高中三年再拼。'}]}
def ev_child_gk(cn):
    sc=round(cn['dev']['smart']*0.8+random.randint(0,29)+cn['dev']['close']/10)
    if sc>=70:
        tl(G['p'],cn['name']+'考上重点大学'); famev(G['p'],4)
        return {'ic':'高考','t':cn['name']+'的高考','txt':'孩子考出 %d 分，被重点大学录取！'%sc,'cs':[
          {'t':'全力支持学费（5万）','fn':lambda:(mny(G['p'],-50000),cn['dev'].__setitem__('close',min(100,cn['dev']['close']+6)),'你包了TA四年的学费生活费。')[2]},
          {'t':'相信TA自己能行','fn':lambda:(cn['dev'].__setitem__('smart',min(100,cn['dev']['smart']+3)),'TA申请了奖学金，说不想花家里太多钱。')[1]}]}
    if sc>=45:
        return {'ic':'高考','t':cn['name']+'的高考','txt':'孩子考出 %d 分，过了本科线。'%sc,'cs':[{'t':'为孩子骄傲','fn':lambda:(cn['dev'].__setitem__('close',min(100,cn['dev']['close']+3)),'平凡也是好前程。')[1]}]}
    cn['dev']['fit']=min(100,cn['dev']['fit']+3)
    return {'ic':'高考','t':cn['name']+'的高考','txt':'孩子考了 %d 分，决定去学一门手艺。'%sc,'cs':[{'t':'尊重TA的选择','fn':lambda:'三百六十行，行行出状元。'}]}
def ev_child_job(cn):
    d=cn['dev']
    if d['smart']>=60:
        famev(G['p'],3); d['close']=min(100,d['close']+3); tl(G['p'],cn['name']+'入职大厂')
        return {'ic':'择业','t':cn['name']+'的offer','txt':'孩子拿到大厂 offer 了！','cs':[{'t':'为孩子高兴','fn':lambda:'TA说第一个月工资给你买礼物。'}]}
    if d['fit']>=60:
        famev(G['p'],2); tl(G['p'],cn['name']+'成为公务员')
        return {'ic':'择业','t':cn['name']+'的offer','txt':'孩子考上了公务员，端上了铁饭碗。','cs':[{'t':'操办一桌好菜','fn':lambda:(bond_n(G['p'],'子女',4),'一家人的日子越来越有奔头。')[1]}]}
    d['close']=min(100,d['close']+2)
    return {'ic':'择业','t':cn['name']+'的工作','txt':'孩子找了份普通工作，开始自食其力。','cs':[{'t':'支持TA','fn':lambda:'日子普通，但踏实。'}]}
def ev_child_wed(cn):
    return {'ic':'婚嫁','t':cn['name']+'要结婚了','txt':'孩子到了谈婚论嫁的年纪，对方家里希望小两口有个首付。','cs':[
      {'t':'帮衬一笔首付（30万）','fn':lambda:_child_wed_pay(cn)},
      {'t':'让孩子自己奋斗','fn':lambda:(cn['dev'].__setitem__('close',max(0,cn['dev']['close']-4)),sst(G['p'],'mood',-2),'孩子说能理解，但你知道TA眼里有过失落。')[2]}]}
def _child_wed_pay(cn):
    p=G['p']
    if assets(p)>=300000:
        mny(p,-300000); cn['dev']['close']=min(100,cn['dev']['close']+10); famev(p,2); tl(p,'为孩子付了婚房首付')
        return '你把攒了半辈子的钱交到孩子手上。'
    cn['dev']['close']=max(0,cn['dev']['close']-3)
    return '家里拿不出首付，孩子说没关系，你却一夜没睡好。'
def weighted_pick(pool):
    def wgt(e): return e.get('w',5) if isinstance(e,dict) else e[1]
    tot=sum(wgt(e) for e in pool); r=random.random()*tot
    for e in pool:
        r-=wgt(e)
        if r<=0: return e[0] if isinstance(e,tuple) else e
    return pool[0][0] if isinstance(pool[0],tuple) else pool[0]
def queue_random():
    p=G['p']; pool=[e for e in EVENTS if (not e.get('when')) or e['when'](p)]
    if pool: G['queue'].append(weighted_pick(pool))

# ---------------- 年度事件工厂 ----------------
def mk_exam():
    return {'ic':'期末','t':'期末考试','txt':'又到了检验学习成果的时候。','cs':[
     {'t':'稳扎稳打','fn':lambda:_exam_steady()},
     {'t':'冲一冲高分','fn':lambda:_exam_rush()}]}
def _exam_steady():
    p=G['p']; sc=p['stats']['smart']+random.randint(0,19)+(5 if has_tr(p,'care') else 0)
    if sc>=80: sst(p,'mood',3); stg(p,'smart',2); famev(p,1); return '成绩优秀！老师当众表扬了你。'
    if sc>=60: stg(p,'smart',2); return '成绩良好，稳中有进。'
    sst(p,'mood',-2); stg(p,'smart',1); return '成绩一般，你暗下决心要更努力。'
def _exam_rush():
    p=G['p']
    if random.random()<0.35:
        stg(p,'smart',3); sst(p,'mood',2); famev(p,1); return '你超常发挥，名字登上了光荣榜！'
    sst(p,'mood',-2); return '有点紧张，发挥平平。下次稳一点。'
def mk_gaokao():
    p=G['p']; sc=round(p['stats']['smart']*0.9+random.randint(0,24)+(3 if has_tr(p,'dili') else 0))
    p['gaokaoTries']+=1
    majors=[{'t':'报读 '+m[1]+' 专业','fn':(lambda mm:(lambda:(G['p'].__setitem__('edu','大学'),G['p'].__setitem__('major',mm),
            G['p'].__setitem__('uniYears',0),tl(G['p'],'考入大学（'+dict(MAJORS)[mm]+'专业）'),'你正式成为'+dict(MAJORS)[mm]+'专业的大学生！')[4]))(m[0])} for m in MAJORS]
    work={'t':'直接工作，不读大学了','fn':lambda:(G['p'].__setitem__('edu','社会'),tl(G['p'],'早早进入社会'),'你决定早点进入社会闯荡。')[2]}
    if sc>=80:
        famev(p,3); sst(p,'smart',8)
        if sc>=95: achv(p,'zhuangyuan')
        return {'ic':'高考','t':'高考放榜','txt':'你考出了 '+str(sc)+' 分的好成绩，重点大学向你招手！选择专业：','cs':majors+[work]}
    if sc>=60:
        sst(p,'smart',4); return {'ic':'高考','t':'高考放榜','txt':'你考了 '+str(sc)+' 分，过了本科线！选择专业：','cs':majors+[work]}
    return {'ic':'高考','t':'高考放榜','txt':'这次考了 '+str(sc)+' 分，没能上线。','cs':[
        {'t':'复读一年，再战高考','fn':lambda:(stg(G['p'],'smart',5),'你选择再拼一年，背水一战！')[1]},work]}
def mk_offers(title,txt,lst):
    return {'ic':'招聘','t':title,'txt':txt,'cs':[{'t':c[1]+' · '+c[2][0][0]+'（月薪 '+fmt_m(c[2][0][1])+'）',
        'fn':(lambda cc:(lambda:(G['p'].__setitem__('job',cc[0]),G['p'].__setitem__('jobLvl',0),G['p'].__setitem__('yearsLvl',0),
              tl(G['p'],'成为'+cc[2][0][0]),achv(G['p'],'job'),'你成功入职，成为一名'+cc[2][0][0]+'！')[5]))(c)} for c in lst]+
        [{'t':'再等等看','fn':lambda:'你决定再观望一下机会。'}]}
def mk_promo(nxt):
    return {'ic':'晋升','t':'晋升机会','txt':'年度评审结果出来了：你符合晋升「'+nxt[0]+'」的条件！','cs':[
     {'t':'接受晋升！','fn':lambda:_do_promo(nxt)},
     {'t':'再积累一年','fn':lambda:'你选择继续沉淀，机会还会再来。'}]}
def _do_promo(nxt):
    p=G['p']; p['jobLvl']+=1; p['yearsLvl']=0; famev(p,5); tl(p,'晋升为'+nxt[0])
    return '恭喜！你现在是'+nxt[0]+'，月薪 '+fmt_m(nxt[1])+'。'
def mk_retire():
    return {'ic':'退休','t':'退休的选择','txt':'到了可以放慢脚步的年纪了。','cs':[
     {'t':'退休吧，领取养老金','fn':lambda:_do_retire()},
     {'t':'我还想再干几年','fn':lambda:'你选择继续发光发热。'}]}
def _do_retire():
    p=G['p']; c=career_of(p)
    p['pension']=round(c[2][p['jobLvl']][1]*(0.6 if p['job']=='gov' else 0.4)); p['job']=None; p['flags']['retired']=True
    tl(p,'光荣退休'); return '你退休了，每月养老金 '+fmt_m(p['pension'])+'。'
def mk_notice(ic,t,txt,msg):
    return {'ic':ic,'t':t,'txt':txt,'cs':[{'t':'继续','fn':lambda:msg}]}

# ---------------- 年度/月度推进 ----------------
def push_milestones():
    p=G['p']
    if p['age']==12 and p['edu']=='小学':
        p['edu']='初中'; tl(p,'升入初中'); G['queue'].append(mk_notice('升学','升入初中','你成了一名初中生，课业渐渐变重。','新的老师、新的同学，都在等你。'))
    if p['age']==15 and p['edu']=='初中':
        if p['stats']['smart']>=50:
            p['edu']='高中'; tl(p,'考入高中'); G['queue'].append(mk_notice('升学','中考放榜','你考上了心仪的高中！','新校园，新起点。'))
        else:
            p['edu']='职校'; tl(p,'进入职校'); G['queue'].append(mk_notice('升学','中考放榜','你进入职业学校，学一门实用技术。','一技傍身，走遍天下。'))
    if p['age']>=18 and p['edu']=='高中': G['queue'].append(mk_gaokao())
    if p['edu']=='职校' and p['age']>=17:
        p['edu']='职校毕业'; tl(p,'职校毕业')
        lst=[c for c in eligible_offers(p) if c[0] in ('food','barista','courier','basic','coach')]
        G['queue'].append(mk_offers('职校毕业！','带着一门手艺，这些岗位在等你：',lst))
    if p['edu'] in ('小学','初中') or (p['edu']=='高中' and p['age']<18): G['queue'].append(mk_exam())
    if p['edu']=='大学':
        if p['age']==19:
            G['queue'].append({'ic':'社团','t':'大学社团','txt':'百团大战，社团招新啦！','cs':[
              {'t':'加入文艺社','fn':lambda:(stg(G['p'],'charm',3),sst(G['p'],'mood',3),'你在晚会上表演了节目，收获了掌声和朋友。')[2]},
              {'t':'加入球队','fn':lambda:(stg(G['p'],'fit',3),sst(G['p'],'mood',2),'你每周和队友打球，身体倍儿棒。')[2]},
              {'t':'泡图书馆','fn':lambda:(stg(G['p'],'smart',4),'你把图书馆当成了第二个家。')[1]}]})
        if p['age']==21:
            G['queue'].append({'ic':'实习','t':'毕业实习','txt':'实习季到了，去体验真实的职场吧。','cs':[
              {'t':'认真实习','fn':lambda:(stg(G['p'],'smart',3),stg(G['p'],'charm',2),famev(G['p'],2),'你的实习报告被主管当众表扬！')[3]},
              {'t':'边实习边玩','fn':lambda:(sst(G['p'],'mood',5),'你把实习城市逛了个遍，也算不虚此行。')[1]}]})
    if p['age']==60 and p['job']: G['queue'].append(mk_retire())
    if p['age']==65 and p['job']:
        c=career_of(p); p['pension']=round(c[2][p['jobLvl']][1]*(0.6 if p['job']=='gov' else 0.4)); p['job']=None; p['flags']['retired']=True
        tl(p,'到龄退休'); G['queue'].append(mk_notice('退休','到龄退休','你光荣退休了。','每月养老金 '+fmt_m(p['pension'])+'，好好享受生活吧。'))
    if p['age']>=25 and p['age']%3==0:
        G['queue'].append({'ic':'回家','t':'常回家看看','txt':'爸妈又老了一岁，你有多久没好好陪陪他们了？','cs':[
          {'t':'回家陪他们吃饭','fn':lambda:(bond_n(G['p'],'爸爸',8),bond_n(G['p'],'妈妈',8),sst(G['p'],'mood',4),'一桌热腾腾的饭菜，爸妈笑得合不拢嘴。')[3]},
          {'t':'寄点钱表心意','fn':lambda:(mny(G['p'],-1000),bond_n(G['p'],'爸爸',4),bond_n(G['p'],'妈妈',4),'你给家里汇了钱，电话里爸妈直说不需要。')[3]}]})
    # 子女里程碑链（按孩子年龄确定性触发）
    cn=child_of(p)
    if cn:
        ca=p['age']-cn.get('born_age',p['age']-25)
        cn.setdefault('dev',{'smart':35,'fit':35,'close':55})
        fl=p['flags']
        chain=[('c_enroll',6,ev_child_enroll),('c_zk',15,ev_child_zk),('c_gk',18,ev_child_gk),
               ('c_job',22,ev_child_job),('c_wed',27,ev_child_wed)]
        for key,age_need,fac in chain:
            if ca>=age_need and not fl.get(key):
                fl[key]=True; G['queue'].append(fac(cn))
    if p['job'] and p['age']<65:
        c=career_of(p)
        if p['jobLvl']+1<len(c[2]):
            nxt=c[2][p['jobLvl']+1]
            if promo_met(p,nxt): G['queue'].append(mk_promo(nxt))
def check_ach():
    p=G['p']; a=assets(p)
    if a>=500000: achv(p,'rich50')
    if a>=2000000: achv(p,'rich200')
    if p['fame']>=80: achv(p,'fame')
    if p['age']>=70 and p['stats']['health']>=70: achv(p,'health')
    fam=[n for n in p['npcs'] if n['type'] in ('家人','配偶','子女')]
    if fam and sum(n['bond'] for n in fam)/len(fam)>=85: achv(p,'bond')
def year_end():
    p=G['p']; p['age']+=1
    if p['job']: p['yearsLvl']+=1
    if p['job']=='gov': p['loyal']=min(100,p.get('loyal',0)+3)  # 工龄资历保底增长
    # 世界经济周期推进
    w=world_of(p); w['left']-=1
    if w['left']<=0:
        w['cycle']=weighted_pick([('繁荣',3),('平稳',4),('衰退',2),('浪潮',3)])
        w['left']=2+random.randint(0,3)
        cyc_ico={'繁荣':'📈','平稳':'➖','衰退':'📉','浪潮':'🚀'}[w['cycle']]
        glog(p,'时代',cyc_ico+' 大环境进入「'+w['cycle']+'期」。')
    if p['edu']=='大学':
        stg(p,'smart',6); p['uniYears']+=1
        if p['uniYears']>=4:
            p['edu']='大学毕业'; tl(p,'大学毕业'); achv(p,'grad')
            G['queue'].append(mk_offers('大学毕业！','学位到手，这些Offer向你招手：',eligible_offers(p)))
    if p['bank']>0:
        it=round(p['bank']*0.025); p['bank']+=it
        if it>0: glog(p,'利息','存款利息 +'+fmt_m(it)+'。')
    if p['fund']>0:
        r=-0.12+random.random()*0.40+(0.06 if has_tal(p,'biz') else 0)
        cyc=world_of(p)['cycle']
        if cyc=='繁荣': r+=0.10
        elif cyc=='衰退': r-=0.12
        elif cyc=='浪潮': r+=0.06
        ch=round(p['fund']*r); p['fund']=max(0,p['fund']+ch)
        glog(p,'基金',('基金上涨，收益 ' if ch>=0 else '基金回调，亏损 ')+fmt_m(abs(ch))+'（现值 '+fmt_m(p['fund'])+'）。')
    for n in p['npcs']:
        if n['type'] not in ('家人','配偶','子女','恋人') and p['lastY'].get(n['name'],0)<p['age']-1:
            n['bond']=max(0,n['bond']-3)
    if p['age']>=50:
        d=(p['age']-45)//10
        if d>0: sst(p,'health',-d); glog(p,'岁月','岁月不饶人，健康略有下降（-'+str(d)+'）。')
    if p['stats']['mood']<30: sst(p,'health',-2)
    if has_tal(p,'lucky') and random.random()<0.4:
        m=200+random.randint(0,799); p['money']+=m; glog(p,'幸运','幸运星发光！意外小惊喜 +'+fmt_m(m)+'。')
    push_milestones()
    if random.random()<0.7: queue_random()
    check_ach()
    if p['stats']['health']<=0: die('health'); return
    if p['age']>=80 and random.random()<0.18: die('age'); return
def end_month():
    p=G['p']
    if G['over']: return
    income=0
    if p['job']:
        c=career_of(p)
        if p['job']=='media':
            f=p.get('fans',0)
            income+= 40000 if f>=1000000 else 12000 if f>=100000 else 3000 if f>=10000 else 500
        else:
            income+=round(c[2][p['jobLvl']][1]*p['raise'])
    elif p['pension']: income+=p['pension']
    exp=0
    if p['house']:
        exp+=p['house']['monthly']
        if p['house']['left']>0:
            p['house']['left']-=1
            if p['house']['left']==0 and not p['house'].get('done'):
                p['house']['done']=True; glog(p,'房贷','房贷还清了！这套房子真正属于你了。'); famev(p,3)
    elif p['rent']=='share': exp+=1500
    elif p['rent']=='solo': exp+=3000
    if p['age']>=18: exp+=(300 if p['rent']=='parents' else 1200)
    p['money']+=income-exp
    if p['money']<0:
        if p['bank']+p['money']>=0:
            p['bank']+=p['money']; p['money']=0
            glog(p,'收支','这个月入不敷出，动用了存款。'); sst(p,'mood',-4)
        else:
            p['money']=0; p['bank']=0; p['bankrupts']+=1
            glog(p,'收支','收支吃紧，你靠打零工勉强撑了过去。'); sst(p,'mood',-4); sst(p,'health',-1)
    elif income-exp>0 and income>0:
        glog(p,'收支','本月结余 '+fmt_m(income-exp)+'，钱包鼓了一点。')
    p['moodSum']+=p['stats']['mood']; p['moodN']+=1
    p['month']+=1
    p['ap']=3+(1 if has_tal(p,'night') else 0)
    if p['month']>12:
        p['month']=1; year_end()
    elif random.random()<0.5: queue_random()
    check_ach()

def first_eligible(ev):
    for i,c in enumerate(ev['cs']):
        if not c.get('when') or c['when'](G['p']): return i
    return 0
def choose_event(ev,i):
    G['cur']=None
    msg=ev['cs'][i]['fn']() or ''
    if msg: glog(G['p'],ev['ic'],msg)
def drain_queue(auto=False):
    """事件队列消费器：auto=True（快进/托管）自动选第一个可用选项并记入日记；
    auto=False 时停下交由 UI 弹窗逐个处理（调用方负责弹出）。"""
    while G['queue'] and not G['over']:
        if not auto:
            return
        ev=G['queue'].pop(0)
        ok=[i for i,c in enumerate(ev['cs']) if not c.get('when') or c['when'](G['p'])]
        i=ok[0] if ok else 0
        try:
            msg=ev['cs'][i]['fn']() or ''
        except Exception as e:
            msg='（该事件处理出错已跳过：%s）'%e
        glog(G['p'],ev['ic'],'（自动）'+ev['t']+'：'+msg)
def _tier(v,pairs,base):
    for th,pts in pairs:
        if v>=th: return pts
    return base
def die(kind):
    p=G['p']; G['queue']=[]; G['cur']=None; G['over']=True
    fam=[n for n in p['npcs'] if n['type'] in ('家人','配偶','子女')]
    avg=round(sum(n['bond'] for n in fam)/len(fam)) if fam else 60
    a=assets(p)
    # 分项计分（S 应稀缺：分层制 + 稀有成就加权 + 扣分项）
    wealth=_tier(a,[(30000000,30),(15000000,26),(8000000,22),(4000000,19),(2000000,15),(800000,11),(300000,6),(100000,3)],1)
    fp=_tier(p['fame'],[(98,15),(85,11),(65,8),(45,5),(25,3)],1)
    fpam=_tier(avg,[(95,15),(85,11),(70,8),(50,5),(30,3)],1)
    rare={'rich200':3,'zhuangyuan':5,'fame':2,'health':2}
    ap_=min(15,round(sum(rare.get(i,1.2) for i in p['ach'])))
    hp=_tier(p['stats']['health'],[(95,15),(85,12),(60,9),(40,6),(20,3)],0)
    mood_avg=p['moodSum']/max(1,p['moodN'])
    mp=_tier(mood_avg,[(85,10),(70,8),(50,6),(35,4)],2)
    total=wealth+fp+fpam+ap_+hp+mp
    # 加分：登顶职业梯 +5；儿孙满堂 +5
    c=career_of(p); top_job=bool(p['job'] and c and p['jobLvl']==len(c[2])-1)
    if top_job: total+=5
    spouse=next((n for n in p['npcs'] if n['type']=='配偶'),None)
    kid=next((n for n in p['npcs'] if n['type']=='子女'),None)
    happy_family=bool(spouse and kid and spouse['bond']>=85 and kid['bond']>=85)
    if happy_family: total+=5
    # 扣分：破产史、英年早逝
    total-=min(9,p['bankrupts']*3)
    if kind=='health' and p['age']<60: total-=10
    total=max(0,min(100,round(total)))
    if total>=90: grade=('S','传奇人生')
    elif total>=70: grade=('A','精彩人生')
    elif total>=50: grade=('B','充实人生')
    else: grade=('C','平凡而温暖')
    top=sorted(['smart','fit','charm'],key=lambda k:-p['stats'][k])[0]
    kw=grade[1]
    if p['fame']>=70: kw='闪耀人生'
    elif a>=1000000: kw='财富人生'
    elif top=='smart': kw='学霸人生'
    elif top=='fit': kw='活力人生'
    elif top=='charm': kw='魅力人生'
    elif p['flags']['married'] and p['flags']['child']: kw='幸福家庭'
    elif not p['flags']['married'] and a>=500000: kw='独立人生'
    kind_txt={'health':'身体亮起了红灯，你在亲友的陪伴中提前谢幕了。',
              'age':'在亲友的祝福中，你安详地走完了完整而丰盈的一生。',
              'settle':'你笑着和这个世界挥手：这一生，值得。'}[kind]
    job_name=c[2][p['jobLvl']][0] if p['job'] else ('退休生活' if p['pension'] else '自由人生')
    G['endData']={'grade':grade[0],'gradeName':grade[1],'kw':kw,'kindTxt':kind_txt,'total':total,
                  'as':a,'avgBond':avg,'jobName':job_name,
                  'wealth':wealth,'fame':fp,'fam':fpam,'ach':ap_,'hp':hp,'mood':mp,
                  'topJob':top_job,'happyFamily':happy_family,
                  'deduct':min(9,p['bankrupts']*3)+(10 if (kind=='health' and p['age']<60) else 0)}
    record_album(p,G['endData'])
def settle_ask():
    G['queue'].append({'ic':'谢幕','t':'圆满谢幕','txt':'要在此刻为这段人生画上句号，查看人生总结吗？','cs':[
      {'t':'画上句号，看看人生总结','fn':lambda:(die('settle'),'人生总结已生成。')[1]},
      {'t':'再活一阵子','fn':lambda:'生活还在继续，明天又是新的一天。'}]})

# ---------------- 存档（带版本迁移） ----------------
SAVE_V=3
def _migrate_p(p):
    """旧档补齐新增字段，保证向前兼容"""
    st=p.setdefault('stats',{})
    for k,defv in (('health',80),('mood',60),('smart',40),('fit',40),('charm',40)):
        st.setdefault(k,defv)
    p.setdefault('tags',[]); p.setdefault('raise',1.0); p.setdefault('uniYears',0)
    p.setdefault('gaokaoTries',0); p.setdefault('lastY',{}); p.setdefault('bankrupts',0)
    p.setdefault('moodSum',st['mood']); p.setdefault('moodN',1)
    p.setdefault('era',1990); p.setdefault('fans',0); p.setdefault('loyal',0)
    p.setdefault('world',{'cycle':'平稳','left':3})
    fl=p.setdefault('flags',{})
    for k in ('married','child','retired','mara','dink','boss'): fl.setdefault(k,False)
    for n in p.get('npcs',[]):
        n.setdefault('ico','友'); n.setdefault('type','朋友'); n.setdefault('bond',50)
        if n['type']=='子女':
            n.setdefault('dev',{'smart':35,'fit':35,'close':55})
            n.setdefault('born_age',p.get('age',30)-25)
    return p

def save_game():
    if G.get('nosave'): return
    try:
        with _open_data('save.json','w') as f:
            json.dump({'v':SAVE_V,'p':G['p'],'over':G['over'],'sound':G['sound'],'music':G.get('music',True)},f,ensure_ascii=False)
    except Exception: pass
def has_save(): return os.path.exists(SAVE_PATH)
def load_game():
    try:
        with _open_data('save.json','r') as f:
            d=json.load(f)
        if d.get('v',1)<SAVE_V: d=_migrate_save(d)
        p=d.get('p')
        if not p: return False
        G['p']=_migrate_p(p); G['over']=d.get('over',False)
        return True
    except Exception: return False
def _migrate_save(d):
    if 'sound' in d and isinstance(d['sound'],bool): pass
    return d

# ---------------- 跨周目图鉴 ----------------
def album_path(): return _appdata_file('album.json')
def load_album():
    try:
        with _open_data('album.json','r') as f: a=json.load(f)
    except Exception:
        a={}
    a.setdefault('v',1); a.setdefault('lives',0); a.setdefault('bestScore',0)
    a.setdefault('bestGrade',''); a.setdefault('grades',{}); a.setdefault('keywords',{})
    a.setdefault('achs',{}); a.setdefault('jobs',{}); a.setdefault('topAssets',0)
    a.setdefault('bestAge',0); a.setdefault('tutorial',False); a.setdefault('eras',{})
    return a
def save_album(a):
    try:
        with _open_data('album.json','w') as f:
            json.dump(a,f,ensure_ascii=False)
    except Exception: pass
def record_album(p,d):
    """人生结束时写入跨周目图鉴（测试模式下跳过）"""
    if G.get('nosave'): return
    a=load_album()
    a['lives']+=1
    a['bestScore']=max(a['bestScore'],d['total'])
    order={'S':4,'A':3,'B':2,'C':1}
    if order.get(d['grade'],0)>order.get(a['bestGrade'],0): a['bestGrade']=d['grade']
    a['grades'][d['grade']]=a['grades'].get(d['grade'],0)+1
    a['keywords'][d['kw']]=a['keywords'].get(d['kw'],0)+1
    for i in p['ach']: a['achs'][i]=a['achs'].get(i,0)+1
    a['topAssets']=max(a['topAssets'],assets(p))
    a['bestAge']=max(a['bestAge'],p['age'])
    c=career_of(p)
    if p['job']: a['jobs'][c[2][p['jobLvl']][0]]=a['jobs'].get(c[2][p['jobLvl']][0],0)+1
    elif d['jobName'] not in ('自由人生',): a['jobs'][d['jobName']]=a['jobs'].get(d['jobName'],0)+1
    save_album(a)

# ---------------- 五声音阶 BGM（本地合成，循环播放） ----------------
def _bgm_path(): return _appdata_file('bgm.wav')
def ensure_bgm():
    p=_bgm_path()
    if os.path.exists(p): return p
    try:
        sr=22050; step=0.6; steps=16; dur=step*steps; n=int(sr*dur)
        notes=[220.0,261.63,293.66,329.63,392.0,440.0,523.25]
        seq=[0,2,4,3, 1,2,5,4, 6,4,2,1, 0,2,4,2]
        buf=bytearray()
        for i in range(n):
            t=i/sr; k=int(t/step); tin=t-k*step
            f=notes[seq[k%len(seq)]]
            s=0.16*math.sin(2*math.pi*f*t)*math.exp(-2.6*tin)
            s+=0.045*math.sin(2*math.pi*f*2*t)*math.exp(-3.5*tin)
            fade=min(1.0,t/0.05,(dur-t)/0.3)  # 循环缝淡入淡出
            buf+=struct.pack('<h',int(max(-1,min(1,s*fade))*32767))
        w=wave.open(p,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(bytes(buf)); w.close()
    except Exception: pass
    return p
def music_apply():
    try:
        import winsound
        if G.get('music'): winsound.PlaySound(ensure_bgm(),winsound.SND_ASYNC|winsound.SND_LOOP)
        else: winsound.PlaySound(None,winsound.SND_PURGE)
    except Exception: pass

# ---------------- 音效（winsound 后台线程） ----------------
def _beep(freq,ms):
    try: threading.Thread(target=_beep_sync,args=(freq,ms),daemon=True).start()
    except Exception: pass
def _beep_sync(freq,ms):
    try:
        import winsound
        if G['sound']: winsound.Beep(freq,ms)
    except Exception: pass
def snd_click(): _beep(600,40)
def snd_good(): _beep(700,60); threading.Timer(0.07,lambda:_beep(900,70)).start()
def snd_bad(): _beep(300,70)
def snd_up():
    for i,f in enumerate((600,800,1000)):
        threading.Timer(0.09*i,lambda ff=f:_beep(ff,80)).start()

# ---------------- 自动托管 ----------------
def auto_one():
    p=G['p']
    if can_job(p):
        lst=[c for c in eligible_offers(p) if c[0]!=p['job']]
        if lst:
            c=lst[0]; p['job']=c[0]; p['jobLvl']=0; p['yearsLvl']=0
            tl(p,'成为'+c[2][0][0]); achv(p,'job'); glog(p,'招聘','（自动）你入职成为一名'+c[2][0][0]+'。')
    if not p['house'] and p['age']>=25 and assets(p)>=260000: house_buy(0)
    if p['age']>=20 and not p['flags']['married'] and not any(n['type']=='恋人' for n in p['npcs']):
        n=next((x for x in p['npcs'] if x['type'] in ('朋友','同学','同事') and x['bond']>=70),None)
        if n:
            n['type']='恋人'; n['bond']=78; tl(p,'和'+n['name']+'在一起了'); glog(p,'心动','（自动）你和'+n['name']+'在一起了！'); snd_up()
    if p['age']>=22 and not p['flags']['married']:
        n=next((x for x in p['npcs'] if x['type']=='恋人' and x['bond']>=85),None)
        if n and p['job'] and assets(p)>=20000:
            n['type']='配偶'; p['flags']['married']=True; mny(p,-20000); famev(p,5)
            tl(p,'与'+n['name']+'步入婚姻'); achv(p,'marry'); glog(p,'婚礼','（自动）你和'+n['name']+'结婚了！'); snd_up()
    if p['flags']['married'] and not p['flags']['child'] and 25<=p['age']<=40:
        if any(x['type']=='配偶' for x in p['npcs']):
            p['flags']['child']=True
            add_npc(p,{'name':random.choice(BABYNAMES),'type':'子女','bond':90,'ico':'娃','born_age':p['age'],
                       'dev':{'smart':30+random.randint(0,15),'fit':30+random.randint(0,15),'close':60}})
            sst(p,'mood',8); tl(p,'家里迎来了小宝宝'); achv(p,'baby'); glog(p,'宝宝','（自动）宝宝出生了，家里热闹起来！'); snd_up()
    if p['npcs'] and random.random()<0.3:
        n=random.choice(p['npcs']); n['bond']=max(0,min(100,n['bond']+3))
        p['lastY'][n['name']]=p['age']; glog(p,'社交','（自动）和'+n['name']+'聊了聊天。'); p['ap']-=1; return
    acts=build_actions(p); has=lambda i:next((a for a in acts if a['id']==i),None)
    pick=None
    if p['stats']['mood']<35 and has('fun'): pick='fun'
    elif p['stats']['health']<45 and has('rest'): pick='rest'
    else:
        st=stage_of(p['age'])
        pref=['study','play','hobby','family','rest'] if st=='child' else (['study','exercise','hobby','family','rest'] if st=='teen' else ['study','exercise','fun','rest','shopping'])
        for x in pref:
            if has(x): pick=x; break
    if not pick:
        if not acts: p['ap']=0; return
        pick=acts[0]['id']
    do_action_core(pick,True)
def auto_all():
    p=G['p']; g=0
    while p['ap']>0 and g<8: auto_one(); g+=1
def fast_year():
    p=G['p']
    if G['over']: return
    a0=p['age']; g=0
    while not G['over'] and p['age']<a0+1 and g<60:
        auto_all(); end_month(); g+=1
        drain_queue(auto=True)
    if not G['over']: save_game()

# ---------------- 房产/求职/社交 ----------------
HOUSES=[('温馨小窝',600000),('宽敞大房',1200000)]
def house_buy(i):
    p=G['p']; name,price=HOUSES[i]; a=assets(p); need=round(price*0.3)
    if a<need: return False
    d=need; um=min(p['money'],d); p['money']-=um; d-=um; p['bank']-=d
    loan=price-need
    p['house']={'n':name,'monthly':round(loan/240),'left':240}; p['rent']=None
    sst(p,'mood',5); famev(p,3); tl(p,'买下了'+name); achv(p,'house')
    glog(p,'置业','首付 '+fmt_m(need)+' 买下'+name+'，月供 '+fmt_m(p['house']['monthly'])+'，日子有了着落！'); snd_up()
    return True
def set_rent(r):
    p=G['p']; p['rent']=r
    names={'parents':'和父母同住','share':'搬去合租','solo':'独居公寓'}
    glog(p,'搬家','搬家了：'+names[r]+'。'); snd_click()
def take_job(cid):
    p=G['p']
    if p['ap']<1: return False
    c=next(x for x in CAREERS if x[0]==cid)
    p['ap']-=1; p['job']=cid; p['jobLvl']=0; p['yearsLvl']=0
    tl(p,'成为'+c[2][0][0]); achv(p,'job')
    glog(p,'招聘','你通过面试，成为一名'+c[2][0][0]+'！月薪 '+fmt_m(c[2][0][1])+'。'); snd_up()
    return True
def soc_act(kind,idx):
    p=G['p']
    if p['ap']<1: return '行动点不足'
    n=p['npcs'][idx]
    p['ap']-=1
    bonus=(2 if has_tr(p,'sunny') else 0)+(3 if has_tal(p,'social') else 0)+(1 if has_tal(p,'pretty') else 0)
    if kind=='chat':
        n['bond']=max(0,min(100,n['bond']+3+bonus)); sst(p,'mood',1)
        glog(p,'社交','和'+n['name']+'聊了聊天，关系更近了。'); snd_good()
    elif kind=='play':
        n['bond']=max(0,min(100,n['bond']+5+bonus)); sst(p,'mood',2)
        if p['age']>=18: mny(p,-100)
        glog(p,'社交','和'+n['name']+'玩了一下午，笑声不断。'); snd_good()
    elif kind=='gift':
        n['bond']=max(0,min(100,n['bond']+8+bonus//2)); mny(p,-500)
        glog(p,'社交','你给'+n['name']+'挑了份礼物，TA开心极了。'); snd_good()
    elif kind=='love':
        n['type']='恋人'; n['bond']=78; tl(p,'和'+n['name']+'在一起了')
        glog(p,'心动','你鼓起勇气表白，'+n['name']+'红着脸答应了！'); snd_up()
    elif kind=='marry':
        if n['bond']<85 and random.random()<0.5:
            n['bond']=max(0,n['bond']-5); sst(p,'mood',-3)
            glog(p,'求婚',n['name']+'红着眼眶说还需要一点时间，你被婉拒了（好感略降）。'); snd_bad()
        else:
            n['type']='配偶'; p['flags']['married']=True; mny(p,-20000); famev(p,5)
            tl(p,'与'+n['name']+'步入婚姻'); achv(p,'marry')
            glog(p,'婚礼','在亲友的祝福中，你和'+n['name']+'结婚了！'); snd_up()
    elif kind=='baby':
        p['flags']['child']=True
        add_npc(p,{'name':random.choice(BABYNAMES),'type':'子女','bond':90,'ico':'娃','born_age':p['age'],
                   'dev':{'smart':30+random.randint(0,15),'fit':30+random.randint(0,15),'close':60}})
        sst(p,'mood',8); tl(p,'家里迎来了小宝宝'); achv(p,'baby')
        glog(p,'宝宝','宝宝出生了，家里一下子热闹起来！'); snd_up()
    if n['type']=='子女':
        dv=n.setdefault('dev',{'smart':35,'fit':35,'close':55})
        if kind=='chat': dv['smart']=min(100,dv['smart']+1)
        elif kind=='play': dv['fit']=min(100,dv['fit']+2); dv['close']=min(100,dv['close']+1)
        elif kind=='gift': dv['close']=min(100,dv['close']+2)
    p['lastY'][n['name']]=p['age']
    return None
def fin_op(op):
    p=G['p']
    if op=='save' and p['money']>=10000: p['money']-=10000; p['bank']+=10000; glog(p,'理财','存入银行 1 万元。')
    elif op=='take' and p['bank']>=10000: p['bank']-=10000; p['money']+=10000; glog(p,'理财','从银行取出 1 万元。')
    elif op=='buy' and p['money']>=10000: p['money']-=10000; p['fund']+=10000; glog(p,'理财','买入 1 万元基金。')
    elif op=='sell' and p['fund']>=10000: p['fund']-=10000; p['money']+=10000; glog(p,'理财','赎回 1 万元基金。')
    snd_click()

def do_action_core(pid,auto=False):
    p=G['p']; a=next((x for x in build_actions(p) if x['id']==pid),None)
    if not a: return None
    msg=a['fn']()
    if msg is None: return None
    p['ap']=max(0,p['ap']-1)
    if msg: glog(p,a['ic'],('（自动）' if auto else '')+msg)
    return msg

# ---------------- 开局 ----------------
def roll_talents():
    pool=list(TALENTS); out=[]
    for _ in range(2): out.append(pool.pop(random.randint(0,len(pool)-1))[0])
    return out
def begin_life(c):
    fam=FAMILIES[c['family']]
    p={'name':(c['name'] or '').strip() or random.choice(['小阳','小禾','阿澄','乐知','安然']),
       'gender':c['gender'],'skin':c['skin'],'hair':c['hair'],'hairC':c['hairC'],'outfit':c['outfit'],
       'family':c['family'],'traits':list(c['traits']),'talents':list(c['talents']),
       'era':c.get('era',1990),
       'age':6,'month':1,'edu':'小学','major':None,'uniYears':0,
       'stats':{'health':92,'mood':75+fam[3],'smart':15,'fit':30,'charm':35},
       'money':0,'bank':fam[2],'fund':0,'fame':10+fam[4],'ap':0,
       'job':None,'jobLvl':0,'yearsLvl':0,'pension':0,'raise':1.0,'fans':0,'loyal':0,
       'world':{'cycle':'平稳','left':2+random.randint(0,2)},
       'house':None,'rent':'parents','gaokaoTries':0,
       'tags':[],'bankrupts':0,'moodSum':75+fam[3],'moodN':1,
       'npcs':[],'log':[],'timeline':[],'ach':[],'lastY':{},
       'flags':{'married':False,'child':False,'retired':False,'mara':False,'dink':False,'boss':False}}
    if p['era']==1970: p['bank']=max(500,p['bank']//2)
    if p['era']==2000: p['bank']+=20000
    if has_tal(p,'pretty'): p['stats']['charm']=min(100,p['stats']['charm']+15)
    if has_tal(p,'rich'): p['bank']+=30000
    p['npcs'].append({'name':'爸爸','type':'家人','bond':65+random.randint(0,14),'ico':'父'})
    p['npcs'].append({'name':'妈妈','type':'家人','bond':72+random.randint(0,14),'ico':'母'})
    p['npcs'].append({'name':uniq_name(p),'type':'同学','bond':45+random.randint(0,14),'ico':'同'})
    p['ap']=3+(1 if has_tal(p,'night') else 0)
    tl(p,'在'+fam[0]+'中长大'); tl(p,'背起书包上小学')
    tl(p,'出生于%d年代'%p['era'])
    glog(p,'开局','你 6 岁了，人生的小火车出发啦！')
    glog(p,'开局','9月，你成为了一名小学生。')
    G['p']=p; G['over']=False; G['queue']=[]; G['cur']=None; G['endData']=None
    if not G.get('nosave'):
        a=load_album(); a.setdefault('eras',{})
        a['eras'][str(p['era'])]=a['eras'].get(str(p['era']),0)+1
        save_album(a)
    save_game()

# ============================================================
# UI：反设计组件
# ============================================================
C_RED='#FF0000'; C_BLUE='#0000FF'; C_YEL='#FFFF00'; C_MAG='#FF00FF'; C_CYA='#00FFFF'; C_GRN='#00FF00'
C_BLACK='#000000'; C_WHITE='#FFFFFF'; C_GRAY='#555555'

# ---------------- 黑/白背景主题（设置中切换） ----------------
def is_dark(): return THEME['mode']=='dark'
def BD():   return '#FFFFFF' if is_dark() else '#000000'   # 边框
def FG():   return '#FFFFFF' if is_dark() else '#000000'   # 正文
def CARD(): return '#0A0A0A' if is_dark() else '#FFFFFF'   # 卡片底
def ROOT(): return '#000000' if is_dark() else '#FFFFFF'   # 页面底
def FIELD():return '#0A0A0A' if is_dark() else '#FFFFFF'   # 输入框底
def SUB():  return '#AAAAAA' if is_dark() else '#555555'   # 弱化文字
def SHADOW_C(): return '#FFFFFF' if is_dark() else '#000000'

def round_window(w):
    """Windows 11 DWM：把顶层窗口四角切成圆弧（用户要求 GUI 四角圆弧）"""
    try:
        import ctypes
        hwnd=int(w.winId())
        pref=ctypes.c_int(2)  # DWMWCP_ROUND
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd,33,ctypes.byref(pref),4)
    except Exception: pass

def hard_shadow(w,dx=6,dy=6):
    e=QGraphicsDropShadowEffect(); e.setBlurRadius(0); e.setOffset(dx,dy); e.setColor(QColor(SHADOW_C()))
    w.setGraphicsEffect(e)

class TiltLabel(QWidget):
    """旋转文字标签（反设计：元素倾斜制造冲突），fg=None 时按主题自动取色"""
    def __init__(self,text,deg=-2.0,px=54,bg=None,fg=None,parent=None):
        super().__init__(parent)
        self.text=text; self.deg=deg; self.px=px; self.bg=bg
        self.fg=fg if fg is not None else (FG() if (bg is None or bg==CARD()) else '#000000')
        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)
        from PyQt6.QtGui import QFontMetrics
        f=QFont('Microsoft YaHei',int(px),QFont.Weight.Black)
        fm=QFontMetrics(f)
        w=fm.horizontalAdvance(text)+int(px*1.4); h=int(px*1.7)
        rad=math.radians(abs(deg))
        self.setFixedSize(int(w*math.cos(rad)+h*math.sin(rad))+24,int(w*math.sin(rad)+h*math.cos(rad))+12)
    def paintEvent(self,ev):
        pt=QPainter(self); pt.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.bg:
            path=QPainterPath(); path.addRoundedRect(QRectF(self.rect()),10,10)
            pt.fillPath(path,QColor(self.bg))
        pt.translate(self.width()//2,self.height()//2); pt.rotate(self.deg)
        f=QFont('Microsoft YaHei',int(self.px),QFont.Weight.Black)
        pt.setFont(f); pt.setPen(QColor(self.fg))
        pt.drawText(QRectF(-self.width(),-self.height(),self.width()*2,self.height()*2),
                    Qt.AlignmentFlag.AlignCenter,self.text)
        pt.end()

class StatBar(QWidget):
    def __init__(self,label,color,parent=None):
        super().__init__(parent); self.label=label; self.color=color; self.val=50
        self.setFixedHeight(22); self.setMinimumWidth(140)
    def set_val(self,v): self.val=max(0,min(100,v)); self.update()
    def paintEvent(self,ev):
        pt=QPainter(self); pt.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        pt.setBrush(QColor(CARD()))
        pt.setPen(QPen(QColor(BD()),3))
        pt.drawRoundedRect(QRectF(2,2,self.width()-4,self.height()-4),7,7)
        pt.setBrush(QColor(self.color)); pt.setPen(Qt.PenStyle.NoPen)
        pt.drawRoundedRect(QRectF(5,5,(self.width()-10)*self.val/100,self.height()-10),4,4)
        pt.setFont(QFont('Microsoft YaHei',9,QFont.Weight.Black))
        txt=self.label+' '+str(self.val)
        core=QColor(FG()); halo=QColor('#000000' if is_dark() else '#FFFFFF')
        rect=QRectF(10,0,self.width()-20,self.height())
        for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
            pt.setPen(halo)
            pt.drawText(QRectF(rect.x()+dx,rect.y()+dy,rect.width(),rect.height()),Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,txt)
        pt.setPen(core)
        pt.drawText(rect,Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,txt)
        pt.end()

class APSquares(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent); self.total=3; self.left=3
        self.setFixedSize(150,30)
    def set_ap(self,total,left): self.total=total; self.left=left; self.update()
    def paintEvent(self,ev):
        pt=QPainter(self); pt.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        pt.setFont(QFont('Microsoft YaHei',9,QFont.Weight.Black))
        pt.setPen(QColor(FG())); pt.drawText(0,2,60,20,Qt.AlignmentFlag.AlignVCenter,'行动点')
        for i in range(self.total):
            x=62+i*28
            pt.setPen(QPen(QColor(BD()),3))
            pt.setBrush(QColor(C_RED) if i<self.left else QColor(CARD()))
            pt.drawRoundedRect(QRectF(x,4,20,20),5,5)
        pt.end()

class Portrait(QWidget):
    """写实比例木刻风肖像：眼在头高1/2，有眉/鼻/唇/耳/颈肩，平涂+黑描边"""
    def __init__(self,get_params,parent=None):
        super().__init__(parent); self.get_params=get_params
        self.setMinimumSize(120,140)
    def set_size(self,w,h): self.setFixedSize(w,h)
    def paintEvent(self,ev):
        prm=self.get_params()
        if not prm: return
        pt=QPainter(self); pt.setRenderHint(QPainter.RenderHint.Antialiasing)
        W,H=self.width(),self.height()
        skin=QColor(SKINS[prm['skin']]); hair=QColor(HAIRC[prm['hairC']][0]); outfit=QColor(OUTFITS[prm['outfit']])
        mood=prm.get('mood',70)
        pen=QPen(QColor(C_BLACK),max(2,W//90)); pt.setPen(pen)
        if is_dark(): bgc='#101010' if W>180 else CARD()
        else: bgc=C_YEL if W>180 else C_WHITE
        clip=QPainterPath(); clip.addRoundedRect(QRectF(0,0,W,H),16,16)
        pt.setClipPath(clip); pt.fillPath(clip,QColor(bgc))
        cx=W*0.5
        # 肩部/外套（写实肩宽）
        body_top=H*0.66
        path=QPainterPath()
        path.moveTo(cx-W*0.34,H)
        path.lineTo(cx-W*0.32,body_top+H*0.06)
        path.quadTo(cx-W*0.26,body_top,cx-W*0.10,body_top-H*0.015)
        path.lineTo(cx+W*0.10,body_top-H*0.015)
        path.quadTo(cx+W*0.26,body_top,cx+W*0.32,body_top+H*0.06)
        path.lineTo(cx+W*0.34,H)
        path.closeSubpath()
        pt.setBrush(QBrush(outfit)); pt.drawPath(path)
        # 领口白三角
        pt.setBrush(QBrush(QColor(C_WHITE)))
        pt.drawPolygon(QPolygonF([QPointF(cx-W*0.055,body_top-H*0.01),QPointF(cx+W*0.055,body_top-H*0.01),QPointF(cx,body_top+H*0.09)]))
        # 颈
        pt.setBrush(QBrush(skin))
        pt.drawRect(QRectF(cx-W*0.055,H*0.52,W*0.11,H*0.16))
        pt.setBrush(QBrush(skin.darker(115))); pt.drawRect(QRectF(cx-W*0.055,H*0.52,W*0.11,H*0.035))
        # 头（写实比例：略椭圆）
        hx,hy,hrx,hry=cx,H*0.335,W*0.165,H*0.20
        # 耳
        pt.setBrush(QBrush(skin))
        pt.drawEllipse(QPointF(hx-hrx*1.02,hy+hry*0.05),W*0.028,H*0.045)
        pt.drawEllipse(QPointF(hx+hrx*1.02,hy+hry*0.05),W*0.028,H*0.045)
        pt.setBrush(QBrush(skin)); pt.drawEllipse(QRectF(hx-hrx,hy-hry,hrx*2,hry*2))
        # 发型（自然轮廓，非Q版）
        pt.setBrush(QBrush(hair))
        if prm['hair']==0:  # 短发
            hp=QPainterPath()
            hp.moveTo(hx-hrx*1.04,hy+hry*0.18)
            hp.quadTo(hx-hrx*1.12,hy-hry*1.05,hx,hy-hry*1.08)
            hp.quadTo(hx+hrx*1.12,hy-hry*1.05,hx+hrx*1.04,hy+hry*0.18)
            hp.quadTo(hx+hrx*0.86,hy-hry*0.42,hx+hrx*0.30,hy-hry*0.48)
            hp.lineTo(hx-hrx*0.20,hy-hry*0.46)
            hp.quadTo(hx-hrx*0.80,hy-hry*0.40,hx-hrx*1.04,hy+hry*0.18)
            pt.drawPath(hp)
        elif prm['hair']==1:  # 长发
            hp=QPainterPath()
            hp.moveTo(hx-hrx*1.10,hy+hry*1.5)
            hp.quadTo(hx-hrx*1.22,hy-hry*1.0,hx,hy-hry*1.10)
            hp.quadTo(hx+hrx*1.22,hy-hry*1.0,hx+hrx*1.10,hy+hry*1.5)
            hp.lineTo(hx+hrx*0.86,hy+hry*1.42)
            hp.quadTo(hx+hrx*0.96,hy-hry*0.2,hx+hrx*0.5,hy-hry*0.52)
            hp.lineTo(hx-hrx*0.5,hy-hry*0.52)
            hp.quadTo(hx-hrx*0.96,hy-hry*0.2,hx-hrx*0.86,hy+hry*1.42)
            hp.closeSubpath()
            pt.drawPath(hp)
        elif prm['hair']==2:  # 束发
            pt.drawEllipse(QPointF(hx,hy-hry*1.28),W*0.075,H*0.055)
            hp=QPainterPath()
            hp.moveTo(hx-hrx*1.04,hy+hry*0.15)
            hp.quadTo(hx-hrx*1.12,hy-hry*1.05,hx,hy-hry*1.08)
            hp.quadTo(hx+hrx*1.12,hy-hry*1.05,hx+hrx*1.04,hy+hry*0.15)
            hp.quadTo(hx+hrx*0.8,hy-hry*0.45,hx,hy-hry*0.5)
            hp.quadTo(hx-hrx*0.8,hy-hry*0.45,hx-hrx*1.04,hy+hry*0.15)
            pt.drawPath(hp)
        else:  # 卷发
            for dx,dy,r in [(-0.78,-0.55,0.30),(-0.3,-0.82,0.34),(0.3,-0.82,0.34),(0.78,-0.55,0.30),
                            (-1.0,-0.05,0.26),(1.0,-0.05,0.26),(-0.95,0.45,0.24),(0.95,0.45,0.24)]:
                pt.drawEllipse(QPointF(hx+hrx*dx,hy+hry*dy),W*0.055*r*3.2,H*0.038*r*3.2)
        # 眉
        brow_y=hy-hry*0.22
        pt.setBrush(Qt.BrushStyle.NoBrush); pt.setPen(QPen(QColor(C_BLACK),max(2,W//80)))
        for s in (-1,1):
            pt.drawLine(QPointF(hx+s*hrx*0.62,brow_y+(2 if mood<35 else 0)),QPointF(hx+s*hrx*0.24,brow_y-(4 if mood<35 else 2)))
        # 眼（写实：眼白+虹膜+瞳孔）
        eye_y=hy+hry*0.02
        for s in (-1,1):
            ex=hx+s*hrx*0.42
            pt.setBrush(QBrush(QColor(C_WHITE)))
            pt.drawEllipse(QPointF(ex,eye_y),W*0.045,H*0.026)
            pt.setBrush(QBrush(QColor('#5A3A22')))
            pt.drawEllipse(QPointF(ex,eye_y),W*0.021,H*0.020)
            pt.setBrush(QBrush(QColor(C_BLACK)))
            pt.drawEllipse(QPointF(ex,eye_y),W*0.010,H*0.010)
        # 鼻
        pt.setBrush(Qt.BrushStyle.NoBrush)
        pt.drawLine(QPointF(hx+hrx*0.04,eye_y+H*0.028),QPointF(hx+hrx*0.07,hy+hry*0.30))
        pt.drawLine(QPointF(hx+hrx*0.07,hy+hry*0.30),QPointF(hx-hrx*0.05,hy+hry*0.32))
        # 唇
        my=hy+hry*0.52
        pt.setBrush(QBrush(QColor('#B0605A'))); pt.setPen(QPen(QColor(C_BLACK),max(1,W//110)))
        mp=QPainterPath()
        mp.moveTo(hx-hrx*0.22,my)
        if mood>=65: mp.quadTo(hx,my+H*0.035,hx+hrx*0.22,my)
        elif mood>=35: mp.lineTo(hx+hrx*0.22,my)
        else: mp.quadTo(hx,my-H*0.03,hx+hrx*0.22,my)
        mp.quadTo(hx,my+H*0.018,hx-hrx*0.22,my)
        pt.drawPath(mp)
        # 面侧硬阴影（平涂，无渐变）
        pt.setBrush(QBrush(QColor(0,0,0,26))); pt.setPen(Qt.PenStyle.NoPen)
        pt.drawEllipse(QRectF(hx+hrx*0.45,hy-hry*0.85,hrx*0.62,hry*1.75))
        pt.setPen(QPen(QColor(C_BLACK),max(2,W//90)))
        pt.setClipping(False)
        pt.setBrush(Qt.BrushStyle.NoBrush); pt.setPen(QPen(QColor(BD()),max(2,W//90)))
        pt.drawRect(QRectF(1,1,W-2,H-2))
        pt.end()

# ============================================================
# 弹窗
# ============================================================
class AntiDialog(QDialog):
    def __init__(self,title,color=C_YEL,parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setStyleSheet('QDialog{background:%s;border:6px solid #000;}'%C_WHITE)
        self.v=QVBoxLayout(self); self.v.setContentsMargins(18,18,18,18); self.v.setSpacing(12)
        t=TiltLabel(title,-1.2,26,bg=color)
        self.v.addWidget(t)
LIGHT_BG=(C_YEL,C_GRN,C_CYA,C_WHITE,'#FFB3B3')
def qss_btn(name,color,fg=None):
    if fg is None: fg=C_BLACK if color in LIGHT_BG else C_WHITE
    b=QPushButton(name)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(
        'QPushButton{background:%s;color:%s;border:4px solid %s;border-width:4px 6px 6px 4px;border-radius:12px;'
        'font-weight:900;font-size:14px;padding:9px 14px;}'
        'QPushButton:hover{background:#0000FF;color:#FFFFFF;border-width:6px 8px 8px 6px;}'
        'QPushButton:pressed{background:%s;color:%s;border-width:2px 3px 3px 2px;}'
        'QPushButton:disabled{background:%s;color:%s;border-width:4px 6px 6px 4px;}'
        'QPushButton:focus{border-color:#0000FF;}'%(color,fg,BD(),C_YEL if not is_dark() else '#333333',
                                                    '#000000' if not is_dark() else '#FFFFFF',
                                                    '#BBBBBB' if not is_dark() else '#2A2A2A',
                                                    '#666666' if not is_dark() else '#777777'))
    return b
CHIP_QSS=('QPushButton{background:%(card)s;color:%(fg)s;border:4px solid %(bd)s;border-width:4px 6px 6px 4px;border-radius:12px;'
          'font-weight:900;font-size:13px;padding:7px 13px;}'
          'QPushButton:hover{background:%(cya)s;border-width:6px 8px 8px 6px;}'
          'QPushButton:checked{background:%(chkbg)s;color:%(chkfg)s;border-width:4px 6px 6px 4px;}'
          'QPushButton:focus{border-color:#0000FF;}')
def chip(name):
    b=QPushButton(name); b.setCheckable(True)
    b.setStyleSheet(CHIP_QSS%{'card':CARD(),'fg':FG(),'bd':BD(),'cya':C_CYA,
                              'chkbg':C_WHITE if is_dark() else C_BLACK,
                              'chkfg':C_BLACK if is_dark() else C_YEL})
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b
def card_qss(bg):
    return 'QFrame#card{background:%s;border:4px solid %s;border-width:4px 6px 6px 4px;border-radius:16px;}'%(bg,BD())
def apply_card(frame,bg,shadow=(6,6)):
    frame.setObjectName('card'); frame.setStyleSheet(card_qss(bg))
    if shadow: hard_shadow(frame,*shadow)

class RDialog(QDialog):
    """弹窗基类：底色随主题"""
    def __init__(self,parent=None):
        super().__init__(parent)
    def showEvent(self,e):
        super().showEvent(e); round_window(self)

class EventDialog(RDialog):
    """事件弹窗：选择后应用结果"""
    def __init__(self,ev,parent=None):
        super().__init__(parent)
        self.ev=ev
        self.setWindowTitle(ev['t'])
        self.setModal(True)
        self.setStyleSheet('QDialog{background:%s;}'%CARD())
        self.setFixedWidth(560)
        v=QVBoxLayout(self); v.setContentsMargins(16,16,16,16); v.setSpacing(10)
        head=QFrame(); head.setStyleSheet('background:%s;border:4px solid %s;border-width:4px 6px 6px 4px;border-radius:14px;'%(random.choice([C_YEL,C_CYA,C_GRN,C_MAG]),BD()))
        hv=QVBoxLayout(head); hv.setContentsMargins(10,8,10,8)
        hv.addWidget(TiltLabel('【'+ev['t']+'】',-1.5,22))
        lab=QLabel(ev['txt']); lab.setWordWrap(True); lab.setStyleSheet('font-weight:700;font-size:14px;border:none;color:#000000;')
        hv.addWidget(lab)
        hard_shadow(head,5,5)
        v.addWidget(head)
        cols=[C_RED,C_BLUE,'#7A00B8',C_BLACK]
        for i,c in enumerate(ev['cs']):
            b=qss_btn(c['t'],cols[i%len(cols)])
            b.clicked.connect(lambda _,ix=i:self._pick(ix))
            v.addWidget(b)
    def _pick(self,i):
        snd_click(); choose_event(self.ev,i); self.accept()

class SocialDialog(RDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('社交时光')
        self.setStyleSheet('QDialog{background:%s;}'%CARD())
        self.setFixedSize(640,600)
        self.idx=0
        self.v=QVBoxLayout(self); self.v.setContentsMargins(14,14,14,14); self.v.setSpacing(10)
        self.v.addWidget(TiltLabel('【社交时光】',-1.2,24,bg=C_MAG))
        self.h=QHBoxLayout(); self.v.addLayout(self.h)
        self.lst=QListWidget(); self.lst.setFixedWidth(210)
        self.lst.setStyleSheet('QListWidget{border:4px solid %s;font-weight:700;font-size:13px;background:%s;color:%s;}'
                               'QListWidget::item{padding:7px;border-bottom:2px solid %s;}'
                               'QListWidget::item:selected{background:%s;color:#000000;}'%(BD(),CARD(),FG(),BD(),C_YEL))
        self.lst.currentRowChanged.connect(self._sel)
        self.h.addWidget(self.lst)
        self.right=QVBoxLayout(); self.h.addLayout(self.right,1)
        self.info=QLabel(); self.info.setStyleSheet('font-weight:900;font-size:16px;')
        self.right.addWidget(self.info)
        self.devlab=QLabel(); self.devlab.setWordWrap(True)
        self.devlab.setStyleSheet('font-weight:700;font-size:12px;'); self.devlab.setVisible(False)
        self.right.addWidget(self.devlab)
        self.bondbar=StatBar('好感',C_RED); self.right.addWidget(self.bondbar)
        self.btns={}
        for key,lab,sub in [('chat','聊聊天','好感+3 心情+1'),('play','一起玩','好感+5 心情+2（成年花¥100）'),
                            ('gift','送礼物','好感+8 花¥500'),('love','表白','好感≥70 才有底气'),
                            ('marry','求婚','好感85稳成 / 75-84五五开 花¥2万'),('baby','迎接新生命','已婚未育 20-45岁')]:
            b=qss_btn(lab+'　'+sub,C_RED if key in('chat','play','gift') else C_BLUE)
            b.clicked.connect(lambda _,k=key:self._act(k))
            self.right.addWidget(b); self.btns[key]=b
        closeb=qss_btn('先不了',C_BLACK)
        closeb.clicked.connect(self.reject); self.v.addWidget(closeb)
        self._refresh()
    def _sel(self,row):
        if row<0: return
        self.idx=row; self._refresh()
    def _act(self,k):
        msg=soc_act(k,self.idx)
        if msg:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self,'提示',msg)
            self._refresh(); return
        save_game()
        if k in ('love','marry','baby') or G['over']: self.accept()
        else:
            self._refresh()
            p=self.parent()
            if hasattr(p,'refresh'): p.refresh()
    def _refresh(self):
        p=G['p']; self.lst.blockSignals(True); self.lst.clear()
        for n in p['npcs']:
            self.lst.addItem('%s %s（%s %d）'%(n['ico'],n['name'],n['type'],n['bond']))
        self.lst.setCurrentRow(self.idx)
        self.lst.blockSignals(False)
        idx=min(self.idx,len(p['npcs'])-1); self.idx=max(0,idx)
        n=p['npcs'][self.idx]
        self.info.setText(n['ico']+' '+n['name']+'　'+n['type'])
        if n['type']=='子女':
            dv=n.setdefault('dev',{'smart':35,'fit':35,'close':55})
            ca=p['age']-n.get('born_age',p['age']-25)
            self.info.setText(self.info.text()+'　<span style="font-size:12px">%d岁</span>'%ca)
            self.devlab.setText('<b style="font-size:12.5px">聪慧 %d · 体质 %d · 亲密 %d</b>　<span style="font-size:11px;color:%s">（聊天涨聪慧，一起玩涨体质，送礼涨亲密）</span>'%(
                dv['smart'],dv['fit'],dv['close'],SUB()))
            self.devlab.setVisible(True)
        else:
            self.devlab.setVisible(False)
        self.bondbar.set_val(n['bond'])
        self.btns['love'].setEnabled(p['age']>=18 and n['type'] in ('朋友','同学','同事') and n['bond']>=70)
        self.btns['marry'].setEnabled(n['type']=='恋人' and n['bond']>=75 and bool(p['job']) and assets(p)>=20000)
        self.btns['baby'].setEnabled(p['flags']['married'] and not p['flags']['child'] and n['type']=='配偶' and 20<=p['age']<=45)

class FinDialog(RDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('理财规划')
        self.setStyleSheet('QDialog{background:%s;}'%CARD())
        self.setFixedWidth(540)
        self.v=QVBoxLayout(self); self.v.setContentsMargins(16,16,16,16); self.v.setSpacing(10)
        self.v.addWidget(TiltLabel('【理财规划】',-1.2,24,bg=C_GRN))
        self.info=QLabel(); self.info.setWordWrap(True); self.info.setStyleSheet('font-weight:700;font-size:14px;')
        self.v.addWidget(self.info)
        self.fbtns={}
        for op,lab,col in [('save','存入 1 万（年息2.5%）',C_BLUE),('take','取出 1 万',C_BLACK),
                           ('buy','买入 1 万基金（年化-12%~+28%）',C_RED),('sell','赎回 1 万基金',C_MAG)]:
            b=qss_btn(lab,col); b.clicked.connect(lambda _,o=op:self._op(o)); self.v.addWidget(b)
            self.fbtns[op]=b
        cb=qss_btn('搞定，收工',C_BLACK); cb.clicked.connect(self.accept); self.v.addWidget(cb)
        self._refresh()
    def _op(self,o):
        fin_op(o); self._refresh()
        p=self.parent()
        if hasattr(p,'refresh'): p.refresh()
    def _refresh(self):
        p=G['p']
        self.info.setText('现金 %s · 存款 %s · 基金 %s'%(fmt_m(p['money']),fmt_m(p['bank']),fmt_m(p['fund'])))
        self.fbtns['save'].setEnabled(p['money']>=10000)
        self.fbtns['take'].setEnabled(p['bank']>=10000)
        self.fbtns['buy'].setEnabled(p['money']>=10000)
        self.fbtns['sell'].setEnabled(p['fund']>=10000)
class HouseDialog(RDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('安家置业')
        self.setStyleSheet('QDialog{background:%s;}'%CARD())
        self.setFixedWidth(560)
        self.v=QVBoxLayout(self); self.v.setContentsMargins(16,16,16,16); self.v.setSpacing(10)
        self.v.addWidget(TiltLabel('【安家置业】',-1.2,24,bg=C_CYA))
        p=G['p']
        cur=p['house']['n'] if p['house'] else {'parents':'与父母同住','share':'合租（月租¥1500）','solo':'独居（月租¥3000）'}[p['rent']]
        info=QLabel('当前：%s · 可用资金 %s'%(cur,fmt_m(assets(p))))
        info.setStyleSheet('font-weight:700;font-size:14px;'); self.v.addWidget(info)
        if not p['house']:
            for i,(name,price) in enumerate(HOUSES):
                b=qss_btn('买下%s（%s，首付30%%，月供%s）'%(name,fmt_m(price),fmt_m(round(price*0.7/240))),C_RED)
                b.clicked.connect(lambda _,ix=i:self._buy(ix)); self.v.addWidget(b)
        if p['house'] and assets(p)>=1500000:
            b=qss_btn('🏆 置换江景大平层（150万全款，住进人生新阶段）',C_MAG)
            b.clicked.connect(self._upgrade); self.v.addWidget(b)
        for r,lab in [('share','搬去合租（月租¥1500）'),('solo','独居公寓（月租¥3000）'),('parents','回家和父母同住')]:
            b=qss_btn(lab,C_BLUE); b.clicked.connect(lambda _,rr=r:self._rent(rr)); self.v.addWidget(b)
        cb=qss_btn('先看看再说',C_BLACK); cb.clicked.connect(self.accept); self.v.addWidget(cb)
    def _upgrade(self):
        p=G['p']
        d=min(1500000,p['money'])
        p['money']-=d; p['bank']-=(1500000-d)
        p['house']={'n':'江景大平层','monthly':0,'left':0}
        sst(p,'mood',8); famev(p,4); tl(p,'置换江景大平层'); glog(p,'置业','卖掉旧居，全款置换江景大平层！生活焕然一新。'); snd_up()
        save_game(); self.accept()
    def _buy(self,i):
        if not house_buy(i):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self,'提示','首付不够，再攒攒吧'); return
        self.accept()
    def _rent(self,r):
        set_rent(r); self.accept()
class JobDialog(RDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('寻找工作')
        self.setStyleSheet('QDialog{background:%s;}'%CARD())
        self.setFixedWidth(600)
        self.v=QVBoxLayout(self); self.v.setContentsMargins(16,16,16,16); self.v.setSpacing(10)
        self.v.addWidget(TiltLabel('【招聘市场】',-1.2,24,bg=C_YEL))
        lst=eligible_offers(G['p'])
        info=QLabel('以下岗位与你匹配（入职消耗 1 行动点）：' if lst else '暂无匹配岗位——先提升知识/体能/魅力。')
        info.setWordWrap(True); info.setStyleSheet('font-weight:700;font-size:14px;'); self.v.addWidget(info)
        for c in lst:
            b=qss_btn('%s · %s（月薪 %s）'%(c[1],c[2][0][0],fmt_m(c[2][0][1])),C_RED)
            b.clicked.connect(lambda _,cid=c[0]:self._take(cid)); self.v.addWidget(b)
        cb=qss_btn('再想想',C_BLACK); cb.clicked.connect(self.accept); self.v.addWidget(cb)
    def _take(self,cid):
        if not take_job(cid):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self,'提示','行动点不足'); return
        self.accept()

class SettingsDialog(RDialog):
    """设置：黑/白背景切换、音效开关（即时生效并持久化）"""
    def __init__(self,mw,parent=None):
        super().__init__(parent or mw)
        self.mw=mw
        self.setWindowTitle('设置')
        self.setStyleSheet('QDialog{background:%s;}'%CARD())
        self.setFixedWidth(460)
        v=QVBoxLayout(self); v.setContentsMargins(18,16,18,16); v.setSpacing(12)
        v.addWidget(TiltLabel('【设置】',-1.2,26,bg=C_CYA))
        v.addWidget(QLabel('<b style="font-size:14px">背景模式</b>'))
        trow=QHBoxLayout()
        self.b_light=chip('☀ 白色背景'); self.b_dark=chip('🌙 黑色背景')
        self.b_light.clicked.connect(lambda:self._theme('light'))
        self.b_dark.clicked.connect(lambda:self._theme('dark'))
        trow.addWidget(self.b_light); trow.addWidget(self.b_dark); trow.addStretch(1)
        v.addLayout(trow)
        v.addWidget(QLabel('<b style="font-size:14px">音效</b>'))
        srow=QHBoxLayout()
        self.b_on=chip('🔊 开'); self.b_off=chip('🔇 关')
        self.b_on.clicked.connect(lambda:self._sound(True))
        self.b_off.clicked.connect(lambda:self._sound(False))
        srow.addWidget(self.b_on); srow.addWidget(self.b_off); srow.addStretch(1)
        v.addLayout(srow)
        v.addWidget(QLabel('<b style="font-size:14px">背景音乐（五声音阶）</b>'))
        mrow=QHBoxLayout()
        self.b_mon=chip('🎵 开'); self.b_moff=chip('🎵 关')
        self.b_mon.clicked.connect(lambda:self._music(True))
        self.b_moff.clicked.connect(lambda:self._music(False))
        mrow.addWidget(self.b_mon); mrow.addWidget(self.b_moff); mrow.addStretch(1)
        v.addLayout(mrow)
        tip=QLabel('切换背景立即生效，并自动保存到本机，下次启动保持你的选择。')
        tip.setWordWrap(True); tip.setStyleSheet('font-weight:700;font-size:12px;color:%s;'%SUB())
        v.addWidget(tip)
        cb=qss_btn('完成',C_RED); cb.clicked.connect(self.accept); v.addWidget(cb)
        self._sync()
    def _sync(self):
        self.b_light.setChecked(not is_dark()); self.b_dark.setChecked(is_dark())
        self.b_on.setChecked(G['sound']); self.b_off.setChecked(not G['sound'])
    def _theme(self,mode):
        snd_click()
        if mode!=THEME['mode']:
            self.mw.apply_theme(mode)
        self._sync()
    def _sound(self,on):
        G['sound']=on; save_settings()
        if G['p']: save_game()
        self._sync()
    def _music(self,on):
        G['music']=on; save_settings(); music_apply()
        self._sync()
    def _sync2(self):
        self.b_mon.setChecked(G.get('music',True)); self.b_moff.setChecked(not G.get('music',True))

# 打开弹层的钩子（引擎 → UI）
_UI=None
def open_social():
    if _UI: _UI.open_dialog(SocialDialog(_UI))
def open_fin():
    if _UI: _UI.open_dialog(FinDialog(_UI))
def open_house():
    if _UI: _UI.open_dialog(HouseDialog(_UI))
def open_job():
    if _UI: _UI.open_dialog(JobDialog(_UI))

# ============================================================
# 跨周目图鉴面板
# ============================================================
class AlbumDialog(RDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('人生图鉴')
        self.setStyleSheet('QDialog{background:%s;}'%CARD())
        self.setFixedWidth(600)
        v=QVBoxLayout(self); v.setContentsMargins(18,16,18,16); v.setSpacing(12)
        v.addWidget(TiltLabel('【人生图鉴】',-1.5,28,bg=C_GRN))
        a=load_album()
        st=QLabel('<b style="font-size:15px">已经历 %d 段人生 · 最高评分 %d · 最高评级 %s · 最长寿 %d 岁 · 峰值资产 %s</b>'%(
            a['lives'],a['bestScore'],a['bestGrade'] or '—',a['bestAge'],fmt_m(a['topAssets'])))
        st.setWordWrap(True); v.addWidget(st)
        v.addWidget(QLabel('<b style="font-size:14px">结局评级收集</b>'))
        g=QLabel(' '.join('<b style="background:%s;border:3px solid %s;padding:3px 10px;color:#000">%s ×%d</b>'%(
            {'S':C_YEL,'A':C_CYA,'B':C_GRN,'C':C_WHITE}.get(k,C_YEL),BD(),k,n) for k,n in sorted(a['grades'].items())) or '<span style="color:%s">还没有完成过一段人生</span>'%SUB())
        g.setWordWrap(True); v.addWidget(g)
        v.addWidget(QLabel('<b style="font-size:14px">人生关键词</b>'))
        kw=QLabel(' '.join('<b style="background:%s;border:3px solid %s;padding:3px 10px">「%s」×%d</b>'%(
            [C_YEL,C_CYA,C_GRN,C_MAG][i%4],BD(),k,n) for i,(k,n) in enumerate(a['keywords'].items())) or '<span style="color:%s">—</span>'%SUB())
        kw.setWordWrap(True); v.addWidget(kw)
        v.addWidget(QLabel('<b style="font-size:14px">成就收集（%d/%d）</b>'%(len(a['achs']),len(ACHV))))
        ac=QLabel(' '.join(('<b style="background:%s;border:3px solid %s;padding:3px 10px">%s ×%d</b>'%(
            [C_YEL,C_CYA,C_GRN,C_MAG][i%4],BD(),ACHV[k][0],n) if k in a['achs']
            else '<span style="color:%s;border:3px dashed %s;padding:3px 10px">🔒 %s</span>'%(SUB(),BD(),ACHV[k][0]))
            for i,k in enumerate(ACHV)))
        ac.setWordWrap(True); v.addWidget(ac)
        v.addWidget(QLabel('<b style="font-size:14px">职业巅峰录</b>'))
        jb=QLabel(' '.join('<b style="background:%s;border:3px solid %s;padding:3px 10px">%s ×%d</b>'%(
            C_WHITE,BD(),k,n) for k,n in a['jobs'].items()) or '<span style="color:%s">—</span>'%SUB())
        jb.setWordWrap(True); v.addWidget(jb)
        v.addWidget(QLabel('<b style="font-size:14px">体验过的年代</b>'))
        er=QLabel(' '.join('<b style="background:%s;border:3px solid %s;padding:3px 10px">%s年代 ×%d</b>'%(
            C_CYA,BD(),k,n) for k,n in sorted(a.get('eras',{}).items())) or '<span style="color:%s">—</span>'%SUB())
        er.setWordWrap(True); v.addWidget(er)
        cb=qss_btn('合上图鉴',C_RED); cb.clicked.connect(self.accept); v.addWidget(cb)

# ============================================================
# 人生总结导出图
# ============================================================
def export_summary_image(path):
    d=G['endData']; p=G['p']
    if not d or not p: return False
    n_tl=min(22,len(p['timeline']))
    W,H=900,330+n_tl*30+(len(p['ach'])//3+1)*46+70
    pm=QPixmap(W,H); pm.fill(QColor('#FFFDF6'))
    pt=QPainter(pm); pt.setRenderHint(QPainter.RenderHint.Antialiasing)
    pt.fillRect(0,0,W,86,QColor(C_BLACK))
    pt.setFont(QFont('Microsoft YaHei',26,QFont.Weight.Black)); pt.setPen(QColor(C_YEL))
    pt.drawText(30,58,'现实人生模拟器 · 人生总结')
    pt.setFont(QFont('Microsoft YaHei',11,QFont.Weight.Bold)); pt.setPen(QColor('#FFFFFF'))
    pt.drawText(30,80,'Life Simulator v'+__version__+' · github.com/uahz/life-simulator')
    pt.fillRect(0,0,10,86,QColor(C_RED))
    pt.setPen(QPen(QColor(C_BLACK),5)); pt.setBrush(QColor(C_RED))
    pt.drawRect(40,120,140,140)
    pt.setFont(QFont('Microsoft YaHei',64,QFont.Weight.Black)); pt.setPen(QColor(C_WHITE))
    pt.drawText(QRectF(40,120,140,140),Qt.AlignmentFlag.AlignCenter,d['grade'])
    pt.setFont(QFont('Microsoft YaHei',30,QFont.Weight.Black)); pt.setPen(QColor(C_BLACK))
    pt.drawText(210,160,'「%s」'%d['kw'])
    pt.setFont(QFont('Microsoft YaHei',15,QFont.Weight.Bold))
    pt.drawText(210,196,'综合评分 %d/100 · %s'%(d['total'],d['gradeName']))
    pt.setFont(QFont('Microsoft YaHei',12,QFont.Weight.Bold)); pt.setPen(QColor('#555555'))
    pt.drawText(210,224,d['kindTxt'])
    stats=[('享年','%d 岁'%p['age']),('职业巅峰',d['jobName']),('总资产',fmt_m(d['as'])),
           ('家人好感',str(d['avgBond'])),('成就','%d 项'%len(p['ach']))]
    x=40
    for lab,val in stats:
        pt.setPen(QColor(C_BLACK)); pt.setFont(QFont('Microsoft YaHei',10,QFont.Weight.Bold))
        pt.drawText(x,300,lab); pt.setFont(QFont('Microsoft YaHei',16,QFont.Weight.Black))
        pt.drawText(x,326,val); x+=168
    y=380
    pt.setFont(QFont('Microsoft YaHei',15,QFont.Weight.Black)); pt.drawText(40,y,'— 人生时间线 —'); y+=34
    pt.setFont(QFont('Microsoft YaHei',12,QFont.Weight.Bold))
    for t in p['timeline'][:n_tl]:
        pt.setPen(QColor(C_RED)); pt.drawText(50,y,'%d岁'%t['age'])
        pt.setPen(QColor('#333333')); pt.drawText(110,y,t['t'][:52]); y+=30
    y+=12
    pt.setFont(QFont('Microsoft YaHei',15,QFont.Weight.Black)); pt.drawText(40,y,'— 成就 —'); y+=32
    x=40
    for i,aid in enumerate(p['ach']):
        pt.setPen(QColor('#9A6B00')); pt.setFont(QFont('Microsoft YaHei',11,QFont.Weight.Bold))
        pt.drawText(x,y,'%s %s'%(ACHV[aid][0],ACHV[aid][1][:12])); x+=290
        if i%3==2: x=40; y+=28
    y+=34
    pt.setFont(QFont('Microsoft YaHei',10,QFont.Weight.Bold)); pt.setPen(QColor('#999999'))
    pt.drawText(40,y,'由 现实人生模拟器 生成 · 一次出生，万种人生')
    pt.end()
    return pm.save(path)

# ============================================================
# 页面
# ============================================================
def app_qss():
    return '''
*{font-family:"Microsoft YaHei";outline:none;}
QWidget#root{background:%(root)s;}
QLabel{color:%(fg)s;font-weight:700;}
QListWidget{color:%(fg)s;}
QDialog{color:%(fg)s;}
QLineEdit{border:4px solid %(bd)s;border-width:4px 6px 6px 4px;border-radius:10px;font-weight:900;font-size:15px;
 padding:8px;background:%(field)s;}
QLineEdit:focus{border-color:#0000FF;background:#FFFF00;color:#000000;}
QTextEdit,QTextBrowser{border:4px solid %(bd)s;border-width:4px 6px 6px 4px;border-radius:10px;font-weight:700;font-size:12px;background:%(field)s;}
QScrollBar:vertical{background:%(root)s;width:14px;border:3px solid %(bd)s;border-radius:8px;}
QScrollBar::handle:vertical{background:#FF0000;min-height:30px;border-radius:4px;}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}
'''%{'fg':FG(),'root':ROOT(),'bd':BD(),'field':FIELD()}

class TitleScreen(QWidget):
    def __init__(self,mw):
        super().__init__(); self.mw=mw
        self.setObjectName('root'); self.setStyleSheet('QWidget#root{background:%s;}'%(ROOT() if is_dark() else C_YEL))
        v=QVBoxLayout(self); v.setContentsMargins(30,30,30,30); v.setSpacing(14)
        v.addStretch(1)
        row=QHBoxLayout(); row.addStretch(1)
        row.addWidget(TiltLabel('现实人生',-2.5,74))
        row.addSpacing(20)
        row.addWidget(TiltLabel('模拟器',2.0,74,fg=C_RED))
        row.addStretch(1)
        v.addLayout(row)
        sub=QLabel('从 6 岁到白头 · 一段温暖又真实的人生')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet('font-weight:900;font-size:16px;background:%s;color:%s;padding:8px;min-height:20px;border-radius:8px;'%(C_BLACK if not is_dark() else C_YEL,C_YEL if not is_dark() else C_BLACK))
        v.addWidget(sub)
        v.addSpacing(10)
        btns=QHBoxLayout(); btns.addStretch(1)
        b1=qss_btn('开始新人生',C_RED); b1.setFixedSize(220,58); b1.clicked.connect(self._new)
        btns.addWidget(b1)
        if has_save():
            b2=qss_btn('继续上次人生',C_BLUE); b2.setFixedSize(220,58); b2.clicked.connect(self._cont)
            btns.addWidget(b2)
        b3=qss_btn('⚙ 设置',C_BLACK); b3.setFixedSize(150,58); b3.clicked.connect(self._settings)
        btns.addWidget(b3)
        b4=qss_btn('📖 人生图鉴',C_GRN); b4.setFixedSize(150,58); b4.clicked.connect(self._album)
        btns.addWidget(b4)
        btns.addStretch(1)
        v.addLayout(btns)
        hint=QLabel('免安装单机版 · 自动存档于本机 · 全年龄友好')
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter); hint.setStyleSheet('font-weight:700;font-size:12px;')
        v.addWidget(hint)
        v.addStretch(1)
        bar=QHBoxLayout(); bar.setSpacing(0)
        for c in (C_RED,C_BLUE,C_MAG,C_GRN):
            f=QFrame(); f.setFixedHeight(22); f.setStyleSheet('background:%s;border:3px solid %s;border-radius:8px;'%(c,BD()))
            bar.addWidget(f,1)
        v.addLayout(bar)
    def _new(self):
        snd_click(); self.mw.goto_create()
    def _cont(self):
        snd_click()
        if load_game(): self.mw.goto_game()
    def _settings(self):
        snd_click(); SettingsDialog(self.mw).exec()
    def _album(self):
        snd_click(); AlbumDialog(self.mw).exec()

class CreateScreen(QWidget):
    def __init__(self,mw,state=None):
        super().__init__(); self.mw=mw; self.setObjectName('root')
        self.c=state or {'name':'','gender':'m','skin':0,'hair':0,'hairC':0,'outfit':0,
                'traits':[],'talents':roll_talents(),'rerolls':3,'family':random.randint(0,3),'era':1990}
        outer=QVBoxLayout(self); outer.setContentsMargins(16,12,16,12); outer.setSpacing(10)
        head=QHBoxLayout()
        head.addWidget(TiltLabel('创造你的角色',-1.6,34,bg=C_MAG))
        head.addStretch(1)
        back=qss_btn('← 返回',C_BLACK); back.clicked.connect(lambda:self.mw.goto_title()); head.addWidget(back)
        outer.addLayout(head)
        cols=QHBoxLayout(); outer.addLayout(cols,1)
        # 左列：肖像预览 + 家庭卡
        left=QVBoxLayout()
        self.portrait=Portrait(lambda:self._prev_params()); self.portrait.set_size(230,270)
        pb=QFrame(); apply_card(pb,CARD(),(8,8))
        pl=QVBoxLayout(pb); pl.setContentsMargins(8,8,8,8); pl.addWidget(self.portrait)
        left.addWidget(pb)
        fam=FAMILIES[self.c['family']]
        self.famcard=QFrame(); apply_card(self.famcard,C_YEL if not is_dark() else CARD(),(6,6))
        fl=QVBoxLayout(self.famcard); fl.setContentsMargins(10,8,10,8)
        self.famname=QLabel(); self.famname.setStyleSheet('font-weight:900;font-size:16px;border:none;background:transparent;')
        self.famdesc=QLabel(); self.famdesc.setWordWrap(True); self.famdesc.setStyleSheet('font-weight:700;font-size:12px;border:none;background:transparent;')
        fl.addWidget(self.famname); fl.addWidget(self.famdesc)
        hard_shadow(self.famcard,6,6)
        left.addWidget(self.famcard)
        left.addStretch(1)
        cols.addLayout(left)
        # 右列滚动区
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet('QScrollArea{border:none;background:transparent;}')
        panel=QWidget(); panel.setStyleSheet('background:%s;'%CARD())
        right=QVBoxLayout(panel); right.setSpacing(12)
        scroll.setWidget(panel); cols.addWidget(scroll,1)
        right.addWidget(self._sec('姓名'))
        nrow=QHBoxLayout()
        self.nameEdit=QLineEdit(); self.nameEdit.setMaxLength(8); self.nameEdit.setPlaceholderText('你的名字')
        self.nameEdit.textChanged.connect(self._name_changed)
        nrow.addWidget(self.nameEdit,1)
        rb=qss_btn('随机',C_BLUE); rb.clicked.connect(self._rand_name); nrow.addWidget(rb)
        self.gender_btns={}
        for gid,gn in GENDERS:
            gb=chip(gn); gb.setChecked(self.c['gender']==gid)
            gb.clicked.connect(lambda _,g=gid:self._set_gender(g)); nrow.addWidget(gb)
            self.gender_btns[gid]=gb
        right.addLayout(nrow)
        right.addWidget(self._sec('出生年代（决定你经历的时代）'))
        erow=QHBoxLayout()
        self.era_btns={}
        for e in (1970,1980,1990,2000):
            eb=chip(str(e)+' 年代'); eb.setChecked(self.c.get('era',1990)==e)
            eb.clicked.connect(lambda _,ee=e:self._set_era(ee)); erow.addWidget(eb)
            self.era_btns[e]=eb
        right.addLayout(erow)
        right.addWidget(self._sec('发型'))
        hrow=QHBoxLayout()
        self.hair_btns=[]
        for i,(hid,hn) in enumerate(HAIRSTYLES):
            b=chip(hn); b.setChecked(self.c['hair']==i)
            b.clicked.connect(lambda _,ix=i:self._set_hair(ix))
            hrow.addWidget(b); self.hair_btns.append(b)
        right.addLayout(hrow)
        right.addWidget(self._sec('发色 / 肤色 / 服装'))
        crow=QHBoxLayout()
        for i,(hc,hn) in enumerate(HAIRC):
            b=self._swatch(hc); b.clicked.connect(lambda _,ix=i:self._set_hairC(ix)); crow.addWidget(b)
        crow.addSpacing(12)
        for i,sc in enumerate(SKINS):
            b=self._swatch(sc); b.clicked.connect(lambda _,ix=i:self._set_skin(ix)); crow.addWidget(b)
        crow.addSpacing(12)
        for i,oc in enumerate(OUTFITS):
            b=self._swatch(oc); b.clicked.connect(lambda _,ix=i:self._set_outfit(ix)); crow.addWidget(b)
        right.addLayout(crow)
        right.addWidget(self._sec('性格特征（选 2 个）'))
        trow=QHBoxLayout()
        self.trait_btns={}
        for tid,tn,td in TRAITS:
            b=chip(tn)
            b.setToolTip(td); b.clicked.connect(lambda _,t=tid:self._toggle_trait(t))
            self.trait_btns[tid]=b; trow.addWidget(b)
        right.addLayout(trow)
        self.trait_desc=QLabel('性格会影响属性成长和事件走向'); self.trait_desc.setWordWrap(True)
        self.trait_desc.setStyleSheet('font-weight:700;font-size:12px;')
        right.addWidget(self.trait_desc)
        right.addWidget(self._sec('天赋（可重抽 '+str(self.c['rerolls'])+' 次）'))
        self.tal_labels=[]
        for _ in range(2):
            l=QLabel(); l.setStyleSheet('font-weight:900;font-size:15px;color:#000000;background:%s;border:3px solid %s;border-radius:8px;padding:8px;'%(C_CYA,BD()))
            right.addWidget(l); self.tal_labels.append(l)
        rr=qss_btn('换一批天赋',C_MAG); rr.clicked.connect(self._reroll); right.addWidget(rr)
        self.rr_btn=rr
        right.addSpacing(6)
        go=qss_btn('出发，开始这段人生！',C_RED); go.setFixedHeight(54)
        go.clicked.connect(self._begin); right.addWidget(go)
        right.addStretch(1)
        self._refresh()
    def _sec(self,t):
        l=TiltLabel('▸ '+t,random.choice([-1.2,1.2]),17,bg=CARD())
        return l
    def _swatch(self,color):
        b=QPushButton(); b.setFixedSize(34,34)
        b.setStyleSheet('QPushButton{background:%s;border:4px solid %s;border-radius:8px;}QPushButton:hover{border-color:#0000FF;border-width:6px;}'%(color,BD()))
        return b
    def _prev_params(self):
        return {'skin':self.c['skin'],'hair':self.c['hair'],'hairC':self.c['hairC'],'outfit':self.c['outfit'],'mood':75}
    def _name_changed(self,t): self.c['name']=t
    def _rand_name(self):
        snd_click(); self.c['name']=random.choice(['小阳','小禾','阿澄','乐知','安然','知夏','一诺','星野','可可','沐辰'])
        self.nameEdit.setText(self.c['name'])
    def _set_gender(self,g):
        snd_click(); self.c['gender']=g; self._refresh()
    def _set_era(self,e):
        snd_click(); self.c['era']=e; self._refresh()
    def _set_hair(self,i): snd_click(); self.c['hair']=i; self._refresh()
    def _set_hairC(self,i): snd_click(); self.c['hairC']=i; self._refresh()
    def _set_skin(self,i): snd_click(); self.c['skin']=i; self._refresh()
    def _set_outfit(self,i): snd_click(); self.c['outfit']=i; self._refresh()
    def _toggle_trait(self,t):
        snd_click()
        if t in self.c['traits']: self.c['traits'].remove(t)
        else:
            if len(self.c['traits'])>=2: return
            self.c['traits'].append(t)
        self._refresh()
    def _reroll(self):
        if self.c['rerolls']<1: return
        snd_click(); self.c['rerolls']-=1; self.c['talents']=roll_talents(); self._refresh()
    def _refresh(self):
        fam=FAMILIES[self.c['family']]
        self.famname.setText('家庭：'+fam[0]); self.famdesc.setText(fam[1]+'　初始存款 '+fmt_m(fam[2]))
        for gid,b in self.gender_btns.items(): b.setChecked(gid==self.c['gender'])
        for e,b in self.era_btns.items(): b.setChecked(e==self.c.get('era',1990))
        for i,b in enumerate(self.hair_btns): b.setChecked(i==self.c['hair'])
        for tid,b in self.trait_btns.items(): b.setChecked(tid in self.c['traits'])
        td=[]
        for tid in self.c['traits']:
            t=next(x for x in TRAITS if x[0]==tid); td.append(t[1]+'：'+t[2])
        self.trait_desc.setText('　'.join(td) if td else '性格会影响属性成长和事件走向')
        for i,ix in enumerate(self.c['talents']):
            t=next(x for x in TALENTS if x[0]==ix)
            self.tal_labels[i].setText('✦ '+t[1]+'　'+t[2])
        self.rr_btn.setText('换一批天赋（剩 '+str(self.c['rerolls'])+' 次）')
        self.rr_btn.setEnabled(self.c['rerolls']>0)
        self.portrait.update()
    def _begin(self):
        if len(self.c['traits'])!=2: return
        snd_up(); begin_life(self.c); self.mw.goto_game()

class ActionButton(QPushButton):
    """行动按钮：内部 QLabel 承载富文本（QPushButton 本身不渲染 HTML）"""
    def __init__(self,name,desc,accent,parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(66)
        self.setStyleSheet(
            'QPushButton{background:%(card)s;border:4px solid %(bd)s;border-width:4px 6px 6px 4px;text-align:left;}'
            'QPushButton:hover{background:%(acc)s;border-width:6px 8px 8px 6px;}'
            'QPushButton:pressed{background:%(prs)s;border-width:2px 3px 3px 2px;}'
            'QPushButton:disabled{background:%(dis)s;border-width:4px 6px 6px 4px;}'%
            {'card':CARD(),'bd':BD(),'acc':accent,'prs':C_YEL if not is_dark() else '#333333',
             'dis':'#DDDDDD' if not is_dark() else '#222222'})
        v=QVBoxLayout(self); v.setContentsMargins(8,4,8,4); v.setSpacing(0)
        self.nlab=QLabel('<b style="font-size:14px;color:%s">%s</b>'%(FG(),name)); self.nlab.setStyleSheet('border:none;background:transparent;')
        self.dlab=QLabel('<span style="font-size:10px;color:%s">%s</span>'%(SUB(),desc)); self.dlab.setStyleSheet('border:none;background:transparent;')
        v.addWidget(self.nlab); v.addWidget(self.dlab)
    def set_enabled_view(self,on):
        self.setEnabled(on)
        self.nlab.setStyleSheet('border:none;background:transparent;color:%s;'%(FG() if on else SUB()))
        self.dlab.setStyleSheet('border:none;background:transparent;color:%s;'%SUB())

class GameScreen(QWidget):
    def __init__(self,mw):
        super().__init__(); self.mw=mw; self.setObjectName('root')
        self.v=QVBoxLayout(self); self.v.setContentsMargins(14,10,14,10); self.v.setSpacing(10)
        self.top=QFrame(); self.top.setObjectName('card')
        self.top.setStyleSheet(card_qss(CARD())); hard_shadow(self.top,7,7)
        self.top.setMinimumHeight(112); self.top.setMaximumHeight(132)
        topinn=QVBoxLayout(self.top); topinn.setContentsMargins(12,8,12,8); topinn.setSpacing(6)
        row1=QHBoxLayout(); row1.setSpacing(16)
        self.mini=Portrait(lambda:self._portrait_params()); self.mini.set_size(56,68)
        row1.addWidget(self.mini)
        self.nmlab=QLabel(); self.nmlab.setStyleSheet('border:none;background:transparent;')
        row1.addWidget(self.nmlab)
        self.moneylab=QLabel(); self.moneylab.setStyleSheet('border:none;background:transparent;')
        row1.addWidget(self.moneylab)
        self.famelab=QLabel(); self.famelab.setStyleSheet('border:none;background:transparent;')
        row1.addWidget(self.famelab)
        self.worldlab=QLabel(); self.worldlab.setStyleSheet('border:none;background:transparent;')
        row1.addWidget(self.worldlab)
        self.fanslab=QLabel(); self.fanslab.setStyleSheet('border:none;background:transparent;')
        row1.addWidget(self.fanslab); self.fanslab.setVisible(False)
        self.ap=APSquares(); row1.addWidget(self.ap)
        row1.addStretch(1)
        topinn.addLayout(row1)
        row2=QHBoxLayout(); row2.setSpacing(8)
        self.stat_bars={}
        for lab,key,col in [('健康','health',C_GRN),('心情','mood',C_YEL),('知识','smart',C_BLUE),('体能','fit',C_RED),('魅力','charm',C_MAG)]:
            b=StatBar(lab,col); b.setMinimumWidth(150); b.setFixedHeight(24)
            self.stat_bars[key]=b; row2.addWidget(b,1)
        topinn.addLayout(row2)
        self.v.addWidget(self.top)
        # 首局引导横幅（完成过一局或点过"知道了"后不再显示）
        _al=load_album()
        if not _al.get('tutorial') and _al.get('lives',0)==0:
            bf=QFrame(); apply_card(bf,C_YEL,(4,4))
            bl=QHBoxLayout(bf); bl.setContentsMargins(12,6,12,6); bl.setSpacing(10)
            bt=QLabel('<b style="font-size:12.5px">🎒 新手指南：每月有 3 点行动点，点行动卡消耗；安排完点【结束本月】进入下个月；遇到事件弹窗做选择即可。祝你人生顺利！</b>')
            bt.setWordWrap(True); bt.setStyleSheet('border:none;background:transparent;')
            okb=qss_btn('知道了',C_BLACK); okb.setFixedHeight(40)
            def _dismiss_tut():
                _a=load_album(); _a['tutorial']=True; save_album(_a); bf.setVisible(False); snd_click()
            okb.clicked.connect(_dismiss_tut)
            bl.addWidget(bt,1); bl.addWidget(okb)
            self.v.insertWidget(1,bf)
        cols=QHBoxLayout(); cols.setSpacing(10); self.v.addLayout(cols,1)
        # 左：档案
        left=QVBoxLayout()
        self.leftcard=QFrame(); apply_card(self.leftcard,C_YEL if not is_dark() else CARD(),(6,6))
        self.leftcard.setFixedWidth(250)
        lv=QVBoxLayout(self.leftcard); lv.setContentsMargins(10,10,10,10); lv.setSpacing(8)
        self.portrait=Portrait(lambda:self._portrait_params()); self.portrait.set_size(200,235)
        lv.addWidget(self.portrait,0,Qt.AlignmentFlag.AlignHCenter)
        self.tags=QLabel(); self.tags.setWordWrap(True)
        self.tags.setStyleSheet('font-weight:900;font-size:12px;border:none;background:transparent;')
        lv.addWidget(self.tags)
        self.kvs=QLabel(); self.kvs.setWordWrap(True)
        self.kvs.setStyleSheet('font-weight:700;font-size:13px;border:none;background:transparent;')
        lv.addWidget(self.kvs)
        lv.addStretch(1)
        left.addWidget(self.leftcard)
        cols.addLayout(left,0)
        # 中：行动
        mid=QVBoxLayout()
        self.actcard=QFrame(); apply_card(self.actcard,CARD(),(7,7))
        av=QVBoxLayout(self.actcard); av.setContentsMargins(10,8,10,10); av.setSpacing(8)
        self.monthlab=TiltLabel('本月安排',-1.2,17,bg=C_YEL)
        av.addWidget(self.monthlab)
        self.gridhost=QWidget(); self.grid=QGridLayout(self.gridhost)
        self.grid.setSpacing(8)
        av.addWidget(self.gridhost)
        nav=QHBoxLayout(); nav.setSpacing(8)
        self.b_end=qss_btn('🌙 结束本月',C_RED); self.b_end.clicked.connect(self.end_month_flow)
        self.b_auto=qss_btn('🤖 自动过月',C_BLUE); self.b_auto.clicked.connect(self.auto_month_flow)
        self.b_fast=qss_btn('⏩ 快进一年',C_MAG); self.b_fast.clicked.connect(self.fast_year_flow)
        nav.addWidget(self.b_end); nav.addWidget(self.b_auto); nav.addWidget(self.b_fast); nav.addStretch(1)
        av.addLayout(nav)
        nav2=QHBoxLayout(); nav2.setSpacing(8)
        self.b_sound=qss_btn('音效:开',C_BLACK); self.b_sound.clicked.connect(self.toggle_sound)
        self.b_settle=qss_btn('圆满谢幕',C_GRN); self.b_settle.clicked.connect(self.settle_flow)
        self.b_set=qss_btn('⚙ 设置',C_BLACK); self.b_set.clicked.connect(self.open_settings)
        self.b_alb=qss_btn('📖 图鉴',C_GRN); self.b_alb.clicked.connect(lambda:AlbumDialog(self).exec())
        self.b_home=qss_btn('主菜单',C_CYA); self.b_home.clicked.connect(lambda:self.mw.goto_title())
        for b in (self.b_sound,self.b_settle,self.b_set,self.b_alb,self.b_home): nav2.addWidget(b)
        nav2.addStretch(1)
        av.addLayout(nav2)
        self.hint=QLabel('提示：社交/理财/置业/求职会打开面板；自动托管会替你做平衡选择。')
        self.hint.setStyleSheet('font-weight:700;font-size:11px;color:%s;border:none;background:transparent;'%SUB())
        av.addWidget(self.hint)
        av.addStretch(1)
        mid.addWidget(self.actcard)
        mid.addStretch(1)
        cols.addLayout(mid,1)
        # 右：关系 + 日志
        right=QVBoxLayout()
        self.relcard=QFrame(); apply_card(self.relcard,CARD(),(5,5))
        self.relcard.setFixedWidth(300)
        rv=QVBoxLayout(self.relcard); rv.setContentsMargins(10,8,10,10); rv.setSpacing(6)
        relt=QLabel('<b style="font-size:14px">人际关系</b>'); relt.setStyleSheet('border:none;background:transparent;')
        rv.addWidget(relt)
        self.relhost=QVBoxLayout(); self.relhost.setSpacing(5); rv.addLayout(self.relhost)
        rv.addStretch(1)
        right.addWidget(self.relcard)
        self.logcard=QFrame(); apply_card(self.logcard,C_BLACK,(5,5))
        lv2=QVBoxLayout(self.logcard); lv2.setContentsMargins(10,8,10,10); lv2.setSpacing(6)
        t=QLabel('<b style="color:%s;font-size:14px">人生日记</b>'%C_YEL)
        t.setStyleSheet('border:none;background:transparent;'); lv2.addWidget(t)
        self.logbox=QTextBrowser()
        self.logbox.setStyleSheet('QTextBrowser{background:#111;color:%s;border:3px solid #000;font-weight:700;font-size:12px;}'%C_YEL)
        lv2.addWidget(self.logbox,1)
        self.logcard.setMinimumHeight(300)
        right.addWidget(self.logcard,1)
        cols.addLayout(right,0)
    # ---------- 工具 ----------
    def _portrait_params(self):
        p=G['p']
        return {'skin':p['skin'],'hair':p['hair'],'hairC':p['hairC'],'outfit':p['outfit'],'mood':p['stats']['mood']}
    def open_dialog(self,dlg):
        dlg.exec(); self.refresh()
    def clear_layout(self,l):
        while l.count():
            it=l.takeAt(0); w=it.widget()
            if w: w.deleteLater()
    def refresh(self):
        p=G['p']
        if not p: return
        st=stage_of(p['age'])
        # 顶栏（持久控件，只更新数值）
        self.nmlab.setText('<b style="font-size:18px">%s</b><br><span style="font-size:12px;color:%s">%s · %d岁 · %d月</span>'%(p['name'],SUB(),STAGE_NAME[st],p['age'],p['month']))
        self.moneylab.setText('<b style="font-size:17px;color:%s">资产 %s</b>'%(C_RED,fmt_m(p['money']+p['bank'])))
        self.famelab.setText('<b style="font-size:14px">声望 %d</b>'%p['fame'])
        cyc_ico={'繁荣':'📈','平稳':'➖','衰退':'📉','浪潮':'🚀'}.get(world_of(p)['cycle'],'➖')
        self.worldlab.setText('<b style="font-size:13px">%s %d年代 · %s期</b>'%(cyc_ico,p['era'],world_of(p)['cycle']))
        if p['job']=='media':
            self.fanslab.setVisible(True)
            self.fanslab.setText('<b style="font-size:14px;color:%s">👥 %s</b>'%(C_MAG,fmt_m(p['fans'])))
        else:
            self.fanslab.setVisible(False)
        self.ap.set_ap(3+(1 if has_tal(p,'night') else 0),p['ap'])
        for key,bar in self.stat_bars.items(): bar.set_val(p['stats'][key])
        # 左栏
        tt=['性格：'+' / '.join(next(x for x in TRAITS if x[0]==t)[1] for t in p['traits']),
            '天赋：'+' / '.join(next(x for x in TALENTS if x[0]==t)[1] for t in p['talents'])]
        self.tags.setText('<br>'.join(tt))
        edu=EDU_NAME.get(p['edu'],p['edu'])
        job=career_of(p)[2][p['jobLvl']][0] if p['job'] else ('退休（养老金%s/月）'%fmt_m(p['pension']) if p['pension'] else '暂无工作')
        house=p['house']['n']+'（月供%s）'%fmt_m(p['house']['monthly']) if p['house'] else {'parents':'与父母同住','share':'合租公寓','solo':'独居公寓'}[p['rent']]
        self.kvs.setText('<br>'.join(['身份：<b>%s</b>'%edu,'职业：<b>%s</b>'%job,'住房：<b>%s</b>'%house,
            '存款：<b>%s</b>　基金：<b>%s</b>'%(fmt_m(p['bank']),fmt_m(p['fund']))]+
            (['房贷剩余：<b>%d 期</b>'%p['house']['left']] if p['house'] else [])))
        # 中栏行动
        self.clear_layout(self.grid)
        acts=build_actions(p)
        colors=[C_RED,C_BLUE,C_MAG,C_GRN]
        for i,a in enumerate(acts):
            b=ActionButton(a['n'],a['d'],colors[i%len(colors)])
            b.clicked.connect(lambda _,pid=a['id']:self.do_action(pid))
            b.set_enabled_view(p['ap']>0)
            self.grid.addWidget(b,i//3,i%3)
        self.monthlab=self._retitle('本月安排 · %d月 · 剩 %d 行动点'%(p['month'],p['ap']))
        self.b_settle.setVisible(p['age']>=65)
        self.b_sound.setText('音效:开' if G['sound'] else '音效:关')
        self.b_end.setEnabled(not G['over'])
        # 右栏关系（固定宽度，好感条可见）
        self.clear_layout(self.relhost)
        for n in p['npcs']:
            host=QWidget(); host.setStyleSheet('background:transparent;')
            row=QHBoxLayout(host); row.setContentsMargins(0,0,0,0); row.setSpacing(8)
            lab=QLabel('<b style="font-size:12px;color:%s">%s %s</b><br><span style="font-size:10px;color:%s">%s</span>'%(FG(),n['ico'],n['name'],SUB(),n['type']))
            lab.setFixedWidth(112); lab.setStyleSheet('border:none;background:transparent;')
            bar=StatBar('',C_RED); bar.set_val(n['bond']); bar.setFixedHeight(18); bar.setMinimumWidth(120)
            row.addWidget(lab); row.addWidget(bar,1)
            self.relhost.addWidget(host)
        # 日志
        html=''
        for l in p['log'][:60]:
            html+='<div style="margin:2px 0"><span style="color:#888">[%d岁%d月]</span> <b>%s</b> %s</div>'%(l['age'],l['m'],l['ic'],l['t'])
        self.logbox.setHtml(html)
        self.logbox.verticalScrollBar().setValue(0)
        self.portrait.update()
    def _retitle(self,text):
        # 替换月标签
        old=self.monthlab
        old.setParent(None); old.deleteLater()
        new=TiltLabel(text,-1.2,17,bg=C_YEL)
        self.actcard.layout().insertWidget(0,new)
        return new
    # ---------- 流程 ----------
    def do_action(self,pid):
        p=G['p']
        if p['ap']<1: return
        msg=do_action_core(pid)
        if msg is None: return  # 打开了弹窗
        snd_click(); save_game(); self.refresh()
    def end_month_flow(self):
        end_month(); save_game()
        self._drain_and_maybe_end()
    def auto_month_flow(self):
        auto_all(); end_month(); save_game()
        self._drain_and_maybe_end()
    def fast_year_flow(self):
        fast_year()
        self._drain_and_maybe_end()
    def settle_flow(self):
        settle_ask(); self._drain_and_maybe_end()
    def _drain_and_maybe_end(self):
        while G['queue'] and not G['over']:
            ev=G['queue'].pop(0)
            dlg=EventDialog(ev,self)
            dlg.exec()
        if G['over']:
            self.mw.goto_end(); return
        self.refresh()
    def toggle_sound(self):
        G['sound']=not G['sound']; save_settings()
        if G['p']: save_game()
        self.refresh()
        self.b_sound.setText('音效:开' if G['sound'] else '音效:关')
    def open_settings(self):
        snd_click(); SettingsDialog(self.mw).exec()

class EndScreen(QWidget):
    def __init__(self,mw):
        super().__init__(); self.mw=mw; self.setObjectName('root')
        self.setStyleSheet('background:%s;'%ROOT())
        outer=QVBoxLayout(self); outer.setContentsMargins(20,16,20,16); outer.setSpacing(10)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet('border:none;')
        host=QWidget(); v=QVBoxLayout(host); v.setSpacing(12)
        scroll.setWidget(host); outer.addWidget(scroll)
        self.v=v
    def refresh(self):
        while self.v.count():
            it=self.v.takeAt(0); w=it.widget()
            if w: w.deleteLater()
        d=G['endData']; p=G['p']
        row=QHBoxLayout(); self.v.addLayout(row)
        grade=GradeBox(d['grade']); row.addWidget(grade)
        col=QVBoxLayout()
        t1=TiltLabel('人生总结',-2,40,bg=C_YEL); col.addWidget(t1)
        kw=QLabel('「%s」 · 综合评分 %d/100 · %s'%(d['kw'],d['total'],d['gradeName']))
        kw.setStyleSheet('font-weight:900;font-size:18px;'); col.addWidget(kw)
        kind=QLabel(d['kindTxt']); kind.setWordWrap(True); kind.setStyleSheet('font-weight:700;font-size:13px;')
        col.addWidget(kind)
        row.addLayout(col,1)
        grid=QGridLayout()
        for i,(lab,val) in enumerate([('享年','%d 岁'%p['age']),('职业巅峰',d['jobName']),('总资产',fmt_m(d['as'])),('家人平均好感',str(d['avgBond']))]):
            card=QFrame(); card.setStyleSheet('QFrame{background:%s;border:4px solid %s;border-radius:12px;}'%((C_YEL if i%2 else C_WHITE) if not is_dark() else (CARD() if i%2 else '#141414'),BD()))
            cl=QVBoxLayout(card); cl.setContentsMargins(8,6,8,6)
            a=QLabel('<span style="font-size:11px">%s</span><br><b style="font-size:17px">%s</b>'%(lab,val))
            a.setStyleSheet('border:none;'); cl.addWidget(a)
            hard_shadow(card,4,4)
            grid.addWidget(card,i//4,i%4)
        self.v.addLayout(grid)
        if p['ach']:
            ac=QFrame(); ac.setStyleSheet('QFrame{background:%s;border:4px solid %s;}'%(CARD(),BD()))
            al=QVBoxLayout(ac); al.setContentsMargins(10,8,10,8)
            al.addWidget(QLabel('<b style="font-size:14px">成就（%d）</b>'%len(p['ach'])))
            chips=QHBoxLayout(); chips.setSpacing(6)
            for i,aid in enumerate(p['ach']):
                ch=QLabel('<b style="font-size:12px">%s · %s</b>'%(ACHV[aid][0],ACHV[aid][1]))
                ch.setStyleSheet('color:#000000;background:%s;border:3px solid %s;border-radius:8px;padding:4px 8px;'%([C_YEL,C_CYA,C_GRN,C_MAG][i%4],BD()))
                chips.addWidget(ch)
            chips.addStretch(1); al.addLayout(chips)
            hard_shadow(ac,5,5); self.v.addWidget(ac)
        tlw=QTextBrowser(); tlw.setStyleSheet('QTextBrowser{border:4px solid %s;border-radius:10px;font-weight:700;font-size:13px;background:%s;color:%s;}'%(BD(),CARD(),FG()))
        html=''.join('<div style="margin:3px 0"><b style="color:%s">%d岁</b>　%s</div>'%(C_RED,t['age'],t['t']) for t in p['timeline'])
        tlw.setHtml('<b>人生时间线</b><br>'+html)
        tlw.setFixedHeight(min(320,60+len(p['timeline'])*24))
        self.v.addWidget(tlw)
        btnrow=QHBoxLayout(); btnrow.addStretch(1)
        exp=qss_btn('🖼 导出总结图',C_BLUE); exp.setFixedHeight(50); exp.clicked.connect(self._export)
        btnrow.addWidget(exp)
        btnrow.addSpacing(14)
        again=qss_btn('再来一段新人生',C_RED); again.setFixedHeight(50); again.clicked.connect(self._again)
        btnrow.addWidget(again); btnrow.addStretch(1)
        self.v.addLayout(btnrow)
        self.v.addStretch(1)
    def _export(self):
        out=os.path.join(os.path.expanduser('~'),'Desktop')
        if not os.path.isdir(out): out=_BASE_DIR
        fp=os.path.join(out,'人生总结_%s_%d岁.png'%(G['p']['name'],G['p']['age']))
        from PyQt6.QtWidgets import QMessageBox
        if export_summary_image(fp):
            QMessageBox.information(self,'导出成功','总结图已保存到：\n'+fp)
        else:
            QMessageBox.warning(self,'导出失败','生成图片时出错，请重试。')
    def _again(self):
        snd_click()
        try: os.remove(SAVE_PATH)
        except Exception: pass
        G['p']=None; G['over']=False; G['endData']=None; G['queue']=[]
        self.mw.goto_title()

class GradeBox(QWidget):
    def __init__(self,letter):
        super().__init__(); self.letter=letter; self.setFixedSize(150,150)
    def paintEvent(self,ev):
        pt=QPainter(self); pt.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        rct=QRectF(3,3,self.width()-6,self.height()-6)
        pt.setPen(Qt.PenStyle.NoPen); pt.setBrush(QColor(C_RED))
        pt.drawRoundedRect(rct,22,22)
        pt.setBrush(Qt.BrushStyle.NoBrush); pt.setPen(QPen(QColor(BD()),6))
        pt.drawRoundedRect(rct,22,22)
        pt.setFont(QFont('Microsoft YaHei',64,QFont.Weight.Black))
        pt.setPen(QColor(C_WHITE))
        pt.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,self.letter)
        pt.end()

# ============================================================
# 主窗口
# ============================================================
class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('现实人生模拟器 v'+__version__)
        self.resize(1180,760); self.setMinimumSize(1080,680)
        self.title=None
        self.create=CreateScreen(self); self.addWidget(self.create)
        self.game=GameScreen(self); self.addWidget(self.game)
        self.end=EndScreen(self); self.addWidget(self.end)
        self.goto_title()
    def showEvent(self,e):
        super().showEvent(e); round_window(self)
    def goto_title(self):
        if self.title is not None:
            self.removeWidget(self.title); self.title.deleteLater()
        self.title=TitleScreen(self); self.insertWidget(0,self.title)
        self.setCurrentWidget(self.title)
    def goto_create(self): self.setCurrentWidget(self.create)
    def goto_game(self):
        self.game.refresh(); self.setCurrentWidget(self.game)
        self._drain_pending()
    def _drain_pending(self):
        while G['queue'] and not G['over']:
            ev=G['queue'].pop(0)
            EventDialog(ev,self).exec()
        if G['over']: self.goto_end()
        else: self.game.refresh()
    def goto_end(self):
        self.end.refresh(); self.setCurrentWidget(self.end)
    def apply_theme(self,mode):
        THEME['mode']=mode; save_settings()
        QApplication.instance().setStyleSheet(app_qss())
        self._rebuild()
    def _rebuild(self):
        global _UI
        cur='title'
        if self.currentWidget() is self.create: cur='create'
        elif self.currentWidget() is self.game and G['p']: cur='game'
        elif self.currentWidget() is self.end: cur='end'
        for w in (self.title,self.create,self.game,self.end):
            self.removeWidget(w); w.deleteLater()
        self.title=TitleScreen(self); self.addWidget(self.title)
        self.create=CreateScreen(self); self.addWidget(self.create)
        self.game=GameScreen(self); self.addWidget(self.game)
        self.end=EndScreen(self); self.addWidget(self.end)
        _UI=self.game
        {'title':self.goto_title,'create':self.goto_create,'game':self.goto_game,'end':self.goto_end}[cur]()

def run_gui():
    global _UI
    app=QApplication(sys.argv)
    # 崩溃保险丝：未捕获异常默认会让 PyQt 直接 abort 进程（表现为闪退）。
    # 换成自定义钩子：记录日志 + 弹窗提示，游戏可以继续玩。
    def _crash_hook(etype,value,tb):
        import traceback
        txt=''.join(traceback.format_exception(etype,value,tb))
        try:
            with open(_appdata_file('crash.log'),'a',encoding='utf-8') as f:
                f.write(txt+'\n\n')
        except Exception: pass
        try:
            from PyQt6.QtWidgets import QMessageBox
            box=QMessageBox(QMessageBox.Icon.Critical,'出了一个内部错误',
                            '游戏已从错误中恢复，可以继续玩。\n\n'
                            '错误摘要：'+str(value)[:300]+'\n\n'
                            '详细日志：%s\n\n若反复出现，请把日志发给作者。'%_appdata_file('crash.log'))
            box.exec()
        except Exception: pass
    sys.excepthook=_crash_hook
    app.setStyleSheet(app_qss())
    mw=MainWindow(); _UI=mw.game
    mw.show()
    music_apply()  # 若设置开启了背景音乐则开始循环播放
    sys.exit(app.exec())

def _shot_path(name):
    """开发期输出（截图/日志）：固定在源码目录 _shots/ 内，经 _safe_path 归一化校验"""
    return _safe_path(_BASE_DIR, os.path.join('_shots', name))

def _open_shot(name,mode='r'):
    """打开 _shots/ 下文件的唯一入口：内联包含性校验，杜绝 '..' 越界"""
    p=_shot_path(name)
    root=os.path.realpath(_shot_path('.'))
    if os.path.commonpath([root,os.path.dirname(os.path.realpath(p))])!=root:
        raise ValueError('输出路径越界: %s'%name)
    return open(p,mode,encoding='utf-8')

def run_shot():
    global _UI
    app=QApplication(sys.argv)
    app.setStyleSheet(app_qss())
    mw=MainWindow(); _UI=mw.game
    G['nosave']=True
    mw.resize(1180,760); mw.show()
    out=_shot_path('.'); os.makedirs(out,exist_ok=True)
    def snap(name,w):
        for _ in range(8): app.processEvents()
        pm=w.grab(); pm.save(_shot_path(name+'.png'))
    def seq():
        try:
            snap('1-title',mw.title)
            mw.goto_create(); snap('2-create',mw.create)
            # 开局进入游戏
            cs=mw.create; cs.c['name']='截图员'; cs.c['traits']=['dili','sunny']; cs._begin()
            mw.game.refresh()
            for _ in range(6):
                if G['p']['ap']>0: do_action_core('study' if G['p']['age']<12 else 'exercise')
            end_month()
            while G['queue']:
                ev=G['queue'].pop(0); i=first_eligible(ev); m=ev['cs'][i]['fn']() or ''
                glog(G['p'],ev['ic'],'（自动）'+ev['t']+'：'+m)
            mw.game.refresh()
            snap('3-game',mw.game)
            G['p']['age']=70; G['p']['stats']['health']=60; G['p']['ach']=['job','grad','marry','house','baby','rich50']
            G['endData']={'grade':'A','gradeName':'精彩人生','kw':'学霸人生','kindTxt':'你笑着和这个世界挥手：这一生，值得。','total':78,'as':1234567,'avgBond':90,'jobName':'技术总监'}
            G['p']['timeline'].append({'age':70,'t':'示例节点'})
            mw.end.refresh(); mw.setCurrentWidget(mw.end); snap('4-end',mw.end)
            mw.setCurrentWidget(mw.game)
            dlg=SocialDialog(mw.game); dlg.show(); dlg._refresh()
            for _ in range(8): app.processEvents()
            dlg.grab().save(os.path.join(out,'5-social.png')); dlg.close()
            ev=mk_notice('测试','事件弹窗示例','这是一次事件弹窗的样式预览。','预览完成。')
            d2=EventDialog(ev,mw.game); d2.show()
            for _ in range(8): app.processEvents()
            d2.grab().save(os.path.join(out,'6-event.png')); d2.close()
            # 黑色背景模式预览
            mw.apply_theme('dark'); _UI=mw.game
            snap('7-dark-title',mw.title)
            if G['p']:
                mw.goto_game(); mw.game.refresh(); snap('8-dark-game',mw.game)
                mw.goto_end(); mw.end.refresh(); snap('9-dark-end',mw.end)
            mw.apply_theme('light'); _UI=mw.game
            # v1.1：总结图导出 + 图鉴面板预览
            mw.goto_end(); mw.end.refresh()
            export_summary_image(_shot_path('10-summary.png'))
            ad=AlbumDialog(mw); ad.show()
            for _ in range(8): app.processEvents()
            ad.grab().save(_shot_path('11-album.png')); ad.close()
        except BaseException:
            import traceback
            with _open_shot('crash.txt','w') as f:
                f.write(traceback.format_exc())
            raise
        finally:
            app.quit()
    QTimer.singleShot(600,seq)
    sys.exit(app.exec())

def run_selftest():
    try:
        if sys.stdout is None:
            sys.stdout=_open_shot('_selftest.log','w')
        else:
            sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    except Exception: pass
    G['nosave']=True
    profiles=[('A',['dili','sunny'],1,{}),('B',['sport','adven'],0,{}),
              ('C',['sunny','care'],3,{'bank':600000,'money':100000,'charm':95,'smart':95,'fit':95,'fame':90}),
              ('D',['care','art'],2,{})]
    ok=True
    for name,tr,fam,boost in profiles:
        c={'name':'测试'+name,'gender':'m','skin':1,'hair':0,'hairC':0,'outfit':0,
           'traits':tr,'talents':roll_talents(),'rerolls':0,'family':fam}
        begin_life(c)
        p=G['p']
        for k,v in boost.items():
            if k in p['stats']: p['stats'][k]=v
            else: p[k]=v
        guard=0
        while not G['over'] and guard<3000:
            guard+=1
            auto_all(); end_month()
            while G['queue']:
                ev=G['queue'].pop(0)
                msg=ev['cs'][first_eligible(ev)]['fn']() or ''
                glog(p,ev['ic'],'（自动）'+ev['t']+'：'+msg)
        d=G['endData']
        if not G['over']:
            print('TEST %s FAIL: 未在3000回合内结束'%name); ok=False; continue
        print('TEST %s: age=%d grade=%s(%s) score=%d 资产=%s 成就=%d 时间线=%d 结局=%s'%(
            name,p['age'],d['grade'],d['kw'],d['total'],fmt_m(d['as']),len(p['ach']),len(p['timeline']),d['jobName']))
    print('SELFTEST_'+('PASS' if ok else 'FAIL'))
    sys.exit(0 if ok else 1)

def main():
    G['sound']=True
    load_settings()
    if '--selftest' in sys.argv: run_selftest()
    elif '--shot' in sys.argv: run_shot()
    else: run_gui()

if __name__=='__main__':
    main()
