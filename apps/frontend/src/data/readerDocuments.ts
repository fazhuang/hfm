/**
 * Reader documents (UI-07) — real content only.
 *
 * Two FULL_TEXT documents transcribed faithfully from customer docx
 * (read-only text extraction, no OCR/rewriting):
 *  - houlun: 《后论》历史评价汇编（论其人 12 条带出处引文 + 演其人/讲其人/冠其名 三表）
 *  - qichuan: 其传史料来源整理（本源史料/地方志/类书/现代考据/谱系/图像遗存）
 * The four classical full texts (三都赋序/玄守论/释劝论/笃终论) are NOT in
 * customer materials — they remain METADATA_ONLY entries (DATA_GAP), never
 * fabricated into reader pages.
 */
import type { ReaderDocument } from '../types/reader'

export const READER_SOURCE_QICHIUAN = '客户提供：其传文稿（docx）'
export const READER_SOURCE_HOULUN = '客户提供：后论文稿（docx）'

export const READER_DOCUMENTS: ReaderDocument[] = [
  {
    id: 'houlun',
    title: '后论 · 历史评价汇编',
    subtitle: '后世对皇甫谧的评价、影视、研究著作与以皇甫谧命名的事物（客户资料汇编）',
    textType: '史料汇编',
    attribution: '后世学者（客户资料整理）',
    period: '晋至当代',
    description:
      '客户提供的后论文稿汇编：论其人（历代评价与出处）、演其人（影视作品）、讲其人（研究著作与文章）、冠其名（以皇甫谧命名的事物）。',
    source: READER_SOURCE_HOULUN,
    readingStatus: 'FULL_TEXT',
    contentStatus: 'AVAILABLE',
    relatedEntities: [
      { label: '皇甫谧人物档案', href: '/persons/person-huangfu-mi' },
      { label: '其言', href: '/yan' },
      { label: '《针灸甲乙经》', href: '/jiayi' },
      { label: '非遗传承', href: '/heritage' },
    ],
    sections: [
      {
        id: 'lunqiren',
        heading: '论其人',
        paragraphs: [
          {
            id: 'p1',
            text: '「男子皇甫谧沈静履素，守学好古，与流俗异趣。」',
            citation: {
              attribution: '晋武帝司马炎',
              source: '皇帝对其人品的官方定评，强调其沉静、好学、不随波逐流',
            },
          },
          {
            id: 'p2',
            text: '「皇甫谧素履幽贞，闲居养疾，留情笔削，敦悦丘坟，轩冕未足为荣，贫贱不以为耻，确乎不拔，斯固有晋之高人者欤！」',
            citation: {
              attribution: '唐代·房玄龄等',
              source: '《晋书》——史书对其高洁品德、安贫乐道、意志坚定的高度赞誉',
            },
          },
          {
            id: 'p3',
            text: '「洎乎《笃终》立论，薄葬昭俭，既戒奢于季氏，亦无取于王孙，可谓达存亡之机矣。」',
            citation: {
              attribution: '唐代·房玄龄等',
              source: '《晋书》——赞扬其著作《笃终论》提倡薄葬，看透生死存亡',
            },
          },
          {
            id: 'p4',
            text: '「士安好逸，栖心蓬荜。属意文雅，忘怀荣秩。遗制可称，养生乖术。」',
            citation: {
              attribution: '唐代·房玄龄等',
              source: '《晋书》——概括其性情：好静、寄情文学、淡泊官位',
            },
          },
          {
            id: 'p5',
            text: '「考晋时著书之富，无若皇甫谧者。」',
            citation: { attribution: '清代·李巨来', source: '肯定其著述极为丰富，在晋代无人能及' },
          },
          {
            id: 'p6',
            text: '「皇甫谧博采经传杂书以补史迁缺，所引《世本》诸子，今皆亡逸，断璧残圭，弥堪宝重。」',
            citation: {
              attribution: '清代·钱熙祚',
              source: '评价其史学著作《帝王世纪》等保存珍贵史料',
            },
          },
          {
            id: 'p7',
            text: '「大器晚成惊世人，屡辞皇诏做平民。发扬文史多高见，撰写诗书数匠心。甲乙针经心血铸，功名医学古今闻。身残岂囿志千里，稀世奇才睿智神。」',
            citation: {
              attribution: '现代学者·张发荣（诗评）',
              source: '以七律诗全面概括其生平、成就与精神',
            },
          },
          {
            id: 'p8',
            text: '其淡泊名利、屡拒征召的品格，被赞达到了「富贵不能淫，贫贱不能移，威武不能屈」的大丈夫境界。',
            citation: { attribution: '后世综合评价（精神风骨）', source: '引用《孟子》概括其风骨' },
          },
          {
            id: 'p9',
            text: '「或许，论经学他不如杜预之专精，专论文学他不如陆机之华丽，专论史学他不如陈寿严谨，但他贵在博通，贵在学术眼光，贵在精神风骨，更何况他还是规范千年的医学宗师呢。」',
            citation: {
              attribution: '后世综合评价（学术地位）',
              source: '对其博通文、史、医、哲的精准定位',
            },
          },
          {
            id: 'p10',
            text: '被誉为「针灸鼻祖」，其家训精神被概括为：悬壶济世、身残志坚、善于学习、蔑视权贵等。',
            citation: {
              attribution: '后世综合评价（历史地位）',
              source: '现代对其医学史地位与核心精神的总结',
            },
          },
          {
            id: 'p11',
            text: '世界卫生组织批准把针灸列为治疗专项，皇甫谧也因此成为「我国唯一与孔子齐名于世界文化史的历史名人」。',
            citation: {
              attribution: '国际影响评价',
              source: '对其世界性文化影响力的评价（客户资料转述）',
            },
          },
          {
            id: 'p12',
            text: '姑母之子梁柳赴任太守，人劝其饯行。皇甫谧答：「柳为布衣时过吾，吾送迎不出门，食不过盐菜，贫者不以酒肉为礼。今作郡而送之，是贵城阳太守而贱梁柳，岂中古人之道？是非吾心所安也。」',
            citation: {
              attribution: '《晋书》记载的轶事',
              source: '通过具体事例展现其不趋炎附势、待人始终如一的品格',
            },
          },
        ],
      },
      {
        id: 'yanqiren',
        heading: '演其人',
        entries: [
          {
            title: '电影《皇甫谧》',
            meta: '大型人物历史影片 · 2016 年 · 主演吕一丁',
            note: '以公元 268 年西晋名医皇甫谧为叙事主线，讲述其用针灸救治皇后后拒官归乡，历经磨难完成《针灸甲乙经》的故事。',
          },
          {
            title: '电视剧《皇甫谧传奇》（又名《皇甫神医》）',
            meta: '古装/传奇剧 · 2018 年 · 主演陈浩民',
            note: '讲述三国两晋时期，皇甫谧在乱世中钻研医术、著书立说的故事。',
          },
          {
            title: '新编大型秦腔剧《皇甫谧》',
            meta: '秦腔历史舞台剧 · 2011 年首演 · 陈拴昌',
            note: '由《序幕》《归途惊魂》《以身试针》等八场组成，荣获第五届中国秦腔艺术节优秀剧目奖。',
          },
          {
            title: '新编大型秦腔历史剧《济世布衣皇甫谧》',
            meta: '秦腔历史舞台剧（升级版） · 2012 年首演 · 邵炳德',
            note: '从皇甫谧 20 岁写起，全面展现其在文学、史学、医学等多方面的成就。',
          },
          {
            title: '纪录片《皇甫谧针灸》',
            meta: '非遗题材纪录片 · 2024 年获奖 · 李志锋执导',
            note: '系统阐述皇甫谧创立的针灸学术体系，荣获第六届香港国际青年电影节优秀导演奖等荣誉。',
          },
          {
            title: '电视纪录片《丝路非遗·皇甫谧针灸术》',
            meta: '电视纪录片 · 2020 年播出（甘肃电视台）',
            note: '以全新视角展现世界针灸医学发源地灵台，以及皇甫谧针灸术的非遗传承核心内容。',
          },
          {
            title: '《百家讲坛》之《名医是这样成名的·皇甫谧》',
            meta: '央视讲座节目（共 3 集） · 2013 年播出',
            note: '由中医学博士罗大中主讲，以讲座形式讲述皇甫谧的成长与著书历程。',
          },
          {
            title: '《远方的家》之「皇甫谧故乡的民间养生之道」',
            meta: '央视旅游文化节目 · 2015 年播出',
            note: '记者前往甘肃省灵台县，探访皇甫谧故里，探寻中医针灸的养生之道。',
          },
        ],
      },
      {
        id: 'jiangqiren',
        heading: '讲其人',
        entries: [
          {
            title: '《皇甫谧：文章光陇右 针灸冠中华》',
            meta: '综合性人物介绍文章 · 灵台县皇甫谧纪念馆 / 甘肃·灵台门户网',
            note: '全面介绍皇甫谧的生平、文学、史学、医学成就，评价其为「西晋一代影响最大的文化巨擘」。',
          },
          {
            title: '《皇甫谧著作述评》',
            meta: '著作评述文章 · 澎湃新闻·政务号',
            note: '系统评述皇甫谧在文、史、医、哲各方面的著作。',
          },
          {
            title: '《皇甫谧的「四大贡献」与「四大超越」》',
            meta: '成就总结文章 · 甘肃·灵台门户网',
            note: '概括皇甫谧在文学、史学、医学、哲学四大领域的贡献。',
          },
          {
            title: '《皇甫谧研究集成》',
            meta: '学术研究著作（论文集） · 2011 年 · 钱超尘、温长路主编',
            note: '汇集古往今来特别是近现代有关皇甫谧及其医学思想研究的著作和论文，全书 220 万字。',
          },
          {
            title: '《皇甫谧遗著集》（中文现代版、英文版）',
            meta: '著作汇编 · 史星海主编',
            note: '系统收录《针灸甲乙经》《帝王世纪》《高士传》等皇甫谧核心著述。',
          },
          {
            title: '《皇甫谧针灸》',
            meta: '学术专著 · 2025 年 · 李志锋',
            note: '系统阐述皇甫谧针灸学术体系，是「陇派中医」非遗项目的重要组成部分。',
          },
          {
            title: '《李志锋皇甫谧文化研究专集》',
            meta: '个人研究文集 · 李志锋',
            note: '作者历时八年完成，包含大量实地考证。',
          },
          {
            title: '《皇甫谧〈针灸甲乙经〉学术框架的解构》',
            meta: '学术论文 · 张建斌（南京中医药大学） · 《中国针灸》2015 年 01 期',
            note: '解构《针灸甲乙经》建立的针灸学术框架体系。',
          },
          {
            title: '《皇甫谧〈帝王世纪〉研究》',
            meta: '硕士学位论文 · 牛雁楠（北京师范大学） · 2014 年',
            note: '系统探讨《帝王世纪》的文献来源、思想继承和学术倾向。',
          },
          {
            title: '《皇甫谧〈三都赋序〉之真伪及其价值趋向》',
            meta: '学术期刊论文',
            note: '考证《三都赋序》的作者真伪问题，并分析其价值趋向。',
          },
          {
            title: '《皇甫谧徙居新安（今河南义马）的历史追踪》',
            meta: '学术论文 · 李志锋、方智敏 · 2024 年《中国故事》',
            note: '提出「义马是皇甫谧第二故乡」的结论。',
          },
          {
            title: '《世界历史文化名人皇甫谧研究》',
            meta: '学术论文 · 李志锋 · 2024 年《新楚文化》',
            note: '系统论证皇甫谧作为「中医针灸学之祖」的历史地位。',
          },
          {
            title: '《玄守论》研究及相关文章',
            meta: '单篇著作解析',
            note: '阐述其「安贫守道」的核心思想（全文见其言页）。',
          },
        ],
      },
      {
        id: 'guanqiming',
        heading: '冠其名',
        entries: [
          {
            title: '皇甫谧针灸医院',
            meta: '医疗机构 · 甘肃省平凉市灵台县',
            note: '位于皇甫谧故里的专业针灸医院。',
          },
          {
            title: '灵台县皇甫谧中医院',
            meta: '医疗机构 · 甘肃省平凉市灵台县',
            note: '县级中医医院，致力于中医药及针灸特色服务。',
          },
          {
            title: '皇甫谧养老服务中心',
            meta: '养老机构 · 甘肃省平凉市灵台县',
            note: '结合中医养生理念的养老服务机构。',
          },
          {
            title: '皇甫谧纪念馆',
            meta: '文化场馆 · 甘肃省平凉市灵台县',
            note: '全面展示皇甫谧生平、著作、成就及后世影响的专题纪念馆。',
          },
          {
            title: '皇甫谧文化园',
            meta: '文化园区 · 甘肃省平凉市灵台县',
            note: '包含纪念馆、墓址、广场等在内的综合性文化园区。',
          },
          {
            title: '皇甫谧大剧院',
            meta: '文化设施 · 甘肃省平凉市灵台县',
            note: '以皇甫谧命名的大型公共文化演出场所。',
          },
          {
            title: '皇甫谧小学 / 皇甫谧中学',
            meta: '教育机构 · 甘肃省平凉市灵台县',
            note: '以皇甫谧命名的学校，旨在传承地方先贤文化。',
          },
          {
            title: '平凉皇甫谧思平医院',
            meta: '医疗机构 · 甘肃省平凉市',
            note: '市级以皇甫谧命名的医疗机构。',
          },
          {
            title: '兰州皇甫谧中医医院',
            meta: '医疗机构 · 甘肃省兰州市',
            note: '省级医疗机构，体现皇甫谧在全省中医药领域的影响力。',
          },
          {
            title: '北京皇甫谧中医研究院',
            meta: '研究机构 · 北京市',
            note: '专门研究皇甫谧学术思想的中医研究机构。',
          },
          {
            title: '河南义马市皇甫谧中医院',
            meta: '医疗机构 · 河南省义马市',
            note: '印证其曾徙居河南的历史。',
          },
          {
            title: '「皇甫谧杯」全国中医药院校针灸推拿临床技能大赛',
            meta: '学术竞赛 · 全国性',
            note: '以皇甫谧命名的国家级针灸推拿专业技能竞赛。',
          },
          {
            title: '《皇甫谧研究》杂志/辑刊',
            meta: '学术出版物',
            note: '专门发表皇甫谧生平、著作及学术思想研究论文的刊物。',
          },
          {
            title: '皇甫谧雕像/广场',
            meta: '城市雕塑/广场 · 灵台县及多所中医药大学校园内',
            note: '常见的纪念性塑像和公共空间，成为文化地标。',
          },
        ],
      },
    ],
  },
  {
    id: 'qichuan',
    title: '其传 · 史料来源整理',
    subtitle: '皇甫谧传记史料来源的系统整理（客户资料）',
    textType: '史料整理',
    attribution: '平台整理（据客户资料）',
    period: '—',
    description:
      '客户提供的其传文稿为史料来源整理：本源核心史料、地方志、类书、现代学术考据、地方文史、家族谱系与图像遗存等门类。',
    source: READER_SOURCE_QICHIUAN,
    readingStatus: 'FULL_TEXT',
    contentStatus: 'AVAILABLE',
    relatedEntities: [
      { label: '皇甫谧人物档案', href: '/persons/person-huangfu-mi' },
      { label: '后论 · 历史评价汇编', href: '/reader/houlun' },
      { label: '《针灸甲乙经》', href: '/jiayi' },
    ],
    sections: [
      {
        id: 'benyuan',
        heading: '本源核心史料',
        paragraphs: [
          {
            id: 'p1',
            text: '《晋书·皇甫谧传》为本源核心史料，完整记载皇甫谧家世出身、年少游荡、折节向学、患痹疾困厄、多次拒征不仕、著书终老完整一生；参校《三国志》裴松之注引相关片段，考证其家族汉魏时代的家世脉络，皇甫氏西北士族。',
          },
        ],
      },
      {
        id: 'difangzhi',
        heading: '地方志',
        paragraphs: [
          {
            id: 'p1',
            text: '平凉、安定郡（今甘肃灵台）历代地方志，如明清《平凉府志》《灵台县志》，收录地方对皇甫谧的乡土记述、故里、墓葬、祠庙相关记载，对比官修史书与地方乡土叙事之间的差异。',
          },
        ],
      },
      {
        id: 'leishu',
        heading: '类书辑佚',
        paragraphs: [
          {
            id: 'p1',
            text: '《太平御览》《北堂书钞》等唐宋类书摘抄皇甫谧轶事、言论片段，搜集已经散佚古书中留存的皇甫谧逸事，补正史传缺失细节。',
          },
        ],
      },
      {
        id: 'xiandai',
        heading: '现代学术考据',
        paragraphs: [
          {
            id: 'p1',
            text: '现代学者针对生卒年、故里属地、疾病考证、征召事件时间线的考据文章，梳理学界主流观点与争议，例如皇甫谧到底生于建安年间还是正始年间，痹疾发病时间、病症辨析。',
          },
        ],
      },
      {
        id: 'difangwenshi',
        heading: '地方文史与传记',
        paragraphs: [
          {
            id: 'p1',
            text: '灵台、平凉地方文史资料，现代传记读本，人物评传；区分严谨学术考证与文学演绎类作品。',
          },
        ],
      },
      {
        id: 'jiazu',
        heading: '家族谱系',
        paragraphs: [
          {
            id: 'p1',
            text: '安定皇甫氏家族谱系，汉魏南北朝皇甫氏人物群体研究，把皇甫谧放置于魏晋士族大背景下看待。',
          },
        ],
      },
      {
        id: 'tuxiang',
        heading: '图像与形象',
        paragraphs: [
          {
            id: 'p1',
            text: '后世绘制皇甫谧画像、塑像，古今版画插图，各地纪念馆塑像，梳理不同时代皇甫谧形象塑造变化。',
          },
          {
            id: 'p2',
            text: '甘肃灵台皇甫谧故里、皇甫谧墓、祠堂遗址，碑刻拓片；后世各地纪念遗存照片、地方志版画。',
          },
          {
            id: 'p3',
            text: '后世《针灸甲乙经》配图，针灸图谱，后世将皇甫谧作为医家圣人的相关图像资料。',
          },
        ],
      },
    ],
  },
]

/**
 * Classical full texts NOT present in customer materials — METADATA_ONLY
 * entries (DATA_GAP). Never fabricated; reader pages for these show a clear
 * status and link to /yan.
 */
export const READER_METADATA_ONLY: Array<{ id: string; title: string; note: string }> = [
  { id: 'sandu-fu', title: '《三都赋》序（全文）', note: '古典全文未见于客户材料，整理中。' },
  { id: 'xuanshou-lun', title: '《玄守论》（全文）', note: '古典全文未见于客户材料，整理中。' },
  { id: 'shiquan-lun', title: '《释劝论》（全文）', note: '古典全文未见于客户材料，整理中。' },
  { id: 'duzhong-lun', title: '《笃终论》（全文）', note: '古典全文未见于客户材料，整理中。' },
]

export function getReaderDocument(id: string): ReaderDocument | undefined {
  return READER_DOCUMENTS.find((d) => d.id === id)
}
