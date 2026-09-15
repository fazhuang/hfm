/**
 * 其言四篇——生僻字注音与释义（P-8）
 *
 * 只收正文里**实际出现**的字，逐字核对过。收字尺度：面向公众门户的一般读者，
 * 不认识就该注；因此常用字（如「巾」「珠」「夭」）不收，避免满篇注音反而干扰阅读。
 *
 * 一字多音者取其在**本篇语境**中的读音，例如「繇」在「咎繇」中读 yáo。
 * 「謐」不收：它是传主之名，全篇高频，读者由站名与语境即可识得。
 *
 * 释义力求一句话说清，不做训诂展开——门户是信息展示，不是注释本。
 */
import type { YanGloss } from '../types/yan'

export const YAN_GLOSSES: Readonly<Record<string, YanGloss>> = {
  // 竹席、棺椁、丧葬
  籧: { pinyin: 'qú', gloss: '籧篨，粗竹席' },
  篨: { pinyin: 'chú', gloss: '籧篨，粗竹席' },
  椁: { pinyin: 'guǒ', gloss: '外棺' },
  唅: { pinyin: 'hán', gloss: '死者口中含的珠玉' },
  殯: { pinyin: 'bìn', gloss: '停柩待葬' },
  斂: { pinyin: 'liǎn', gloss: '收殓' },
  衾: { pinyin: 'qīn', gloss: '被子' },
  穢: { pinyin: 'huì', gloss: '污秽' },
  阬: { pinyin: 'kēng', gloss: '同「坑」' },

  // 玉石、器物
  璵: { pinyin: 'yú', gloss: '璵璠，美玉' },
  璠: { pinyin: 'fán', gloss: '璵璠，美玉' },
  瑰: { pinyin: 'guī', gloss: '瑰奇，珍贵奇异' },
  琦: { pinyin: 'qí', gloss: '美玉' },
  榱: { pinyin: 'cuī', gloss: '屋椽' },
  褐: { pinyin: 'hè', gloss: '粗布衣' },

  // 山川、地理
  岷: { pinyin: 'mín', gloss: '岷山' },
  岑: { pinyin: 'cén', gloss: '小而高的山' },
  垠: { pinyin: 'yín', gloss: '边际' },
  畿: { pinyin: 'jī', gloss: '王畿，国都周围地区' },
  藪: { pinyin: 'sǒu', gloss: '草泽' },
  圮: { pinyin: 'pǐ', gloss: '毁坏、坍塌' },

  // 人事、动作
  俟: { pinyin: 'sì', gloss: '等待' },
  佗: { pinyin: 'tuó', gloss: '同「他」' },
  儔: { pinyin: 'chóu', gloss: '同类、同辈' },
  徇: { pinyin: 'xùn', gloss: '曲从、顺从' },
  怵: { pinyin: 'chù', gloss: '恐惧' },
  捋: { pinyin: 'luō', gloss: '用手握住东西滑动' },
  捫: { pinyin: 'mén', gloss: '抚摸' },
  奄: { pinyin: 'yǎn', gloss: '忽然；覆盖' },
  曩: { pinyin: 'nǎng', gloss: '从前' },
  臻: { pinyin: 'zhēn', gloss: '到达' },
  訖: { pinyin: 'qì', gloss: '完毕' },
  觕: { pinyin: 'cū', gloss: '同「粗」' },
  寖: { pinyin: 'jìn', gloss: '同「浸」，逐渐' },
  穨: { pinyin: 'tuí', gloss: '同「颓」，衰败' },
  隕: { pinyin: 'yǔn', gloss: '坠落' },
  蠲: { pinyin: 'juān', gloss: '免除' },
  齎: { pinyin: 'jī', gloss: '携带' },
  濯: { pinyin: 'zhuó', gloss: '洗涤' },
  韜: { pinyin: 'tāo', gloss: '隐藏（韬光）' },

  // 占卜、礼制
  筮: { pinyin: 'shì', gloss: '用蓍草占卜' },
  蓍: { pinyin: 'shī', gloss: '蓍草，占卜所用' },
  彝: { pinyin: 'yí', gloss: '常道、常法' },
  謚: { pinyin: 'shì', gloss: '谥号' },
  夭: { pinyin: 'yāo', gloss: '早死、短命' },

  // 视听
  睨: { pinyin: 'nì', gloss: '斜视' },
  瞵: { pinyin: 'lín', gloss: '注视' },
  喑: { pinyin: 'yīn', gloss: '哑，不能言' },

  // 人名、国名、专名
  堯: { pinyin: 'yáo', gloss: '帝尧' },
  羲: { pinyin: 'xī', gloss: '伏羲' },
  莘: { pinyin: 'shēn', gloss: '有莘，古国名' },
  蠡: { pinyin: 'lǐ', gloss: '范蠡，越国大夫' },
  蒯: { pinyin: 'kuǎi', gloss: '蒯通，汉初辩士' },
  虢: { pinyin: 'guó', gloss: '古国名' },
  黔: { pinyin: 'qián', gloss: '黑色；黔首，百姓' },
  胥: { pinyin: 'xū', gloss: '皆、都；胥克，人名' },
  臏: { pinyin: 'bìn', gloss: '孙膑，战国军事家' },
  摯: { pinyin: 'zhì', gloss: '挚虞，皇甫谧门人' },
  繇: { pinyin: 'yáo', gloss: '咎繇，即皋陶' },
  刖: { pinyin: 'yuè', gloss: '断足之刑' },
  疢: { pinyin: 'chèn', gloss: '热病' },
  髣: { pinyin: 'fǎng', gloss: '髣髴，同「仿佛」' },
  髴: { pinyin: 'fú', gloss: '髣髴，同「仿佛」' },
  闔: { pinyin: 'hé', gloss: '门扇' },
  闥: { pinyin: 'tà', gloss: '门' },
  閶: { pinyin: 'chāng', gloss: '閶闔，传说中的天门' },
  萼: { pinyin: 'è', gloss: '花萼' },
}

/** 把一段正文切成若干段：有注音的走 ruby，其余原样输出。 */
export interface YanRun {
  text: string
  gloss?: YanGloss
}

export function segmentForGlosses(text: string): YanRun[] {
  const runs: YanRun[] = []
  let buffer = ''
  for (const char of text) {
    const gloss = YAN_GLOSSES[char]
    if (gloss) {
      if (buffer) {
        runs.push({ text: buffer })
        buffer = ''
      }
      runs.push({ text: char, gloss })
    } else {
      buffer += char
    }
  }
  if (buffer) runs.push({ text: buffer })
  return runs
}
