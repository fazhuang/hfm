/**
 * 其言 — faithful content from the customer 其言.docx (UI-06).
 *
 * Extracted verbatim from hfmzl/皇甫谧/其言/其言.docx (docx text extraction,
 * no OCR, no rewriting). The docx is a collation/introduction document: it
 * carries the collection intro, four section introductions (《三都赋》序 /
 * 《玄守论》 / 《释劝论》 / 《笃终论》) with content points, and a supplement
 * on 辑佚 (《帝王世纪》《高士传》《逸士传》《列女传》 fragments). The full
 * classical texts of the four works are NOT in the docx — fullTextStatus is
 * DATA_GAP and the page never fabricates them.
 */
import type { YanCollection } from '../types/yan'

export const YAN_SOURCE_NAME = '客户提供：其言文稿（docx）'

export const YAN_COLLECTION: YanCollection = {
  title: '其言',
  subtitle: '皇甫谧言论、文字与相关记载的数字整理（据客户正式材料）',
  intro: '皇甫谧本人存世文章、序跋、著作序言，是研究其思想的一手文本。',
  source: YAN_SOURCE_NAME,
  sections: [
    {
      id: 'sandu-fu',
      title: '《三都赋》序',
      fullTextStatus: 'DATA_GAP',
      records: [
        {
          id: 'sandu-fu-desc',
          section: '《三都赋》序',
          text: '皇甫谧为左思《三都赋》所作序言，是皇甫谧文学思想代表文献。',
          theme: '文学思想',
          themeClassification: 'PRESENTATION_CLASSIFICATION',
          source: YAN_SOURCE_NAME,
          sourceContext:
            '内容要点：序言体现皇甫谧文学审美观，崇尚写实，反对虚夸，主张辞赋取材于地理现实；反映魏晋时期文学风气；同时也可窥见皇甫谧在当时文坛的声望，左思专门请皇甫谧作序来抬高作品地位。',
          relatedWork: '《三都赋》序',
          relatedPerson: '皇甫谧 · 左思',
          status: 'AVAILABLE',
        },
      ],
    },
    {
      id: 'xuanshou-lun',
      title: '《玄守论》',
      fullTextStatus: 'DATA_GAP',
      records: [
        {
          id: 'xuanshou-lun-desc',
          section: '《玄守论》',
          text: '皇甫谧自述安贫乐道，拒绝出仕的论说文。陈述自己体弱多病，甘于隐居，不慕官禄的人生价值观，反映魏晋隐逸思潮。',
          theme: '出处与人生价值观',
          themeClassification: 'PRESENTATION_CLASSIFICATION',
          source: YAN_SOURCE_NAME,
          relatedWork: '《玄守论》',
          relatedPerson: '皇甫谧',
          status: 'AVAILABLE',
        },
      ],
    },
    {
      id: 'shiquan-lun',
      title: '《释劝论》',
      fullTextStatus: 'DATA_GAP',
      records: [
        {
          id: 'shiquan-lun-desc',
          section: '《释劝论》',
          text: '面对朝廷屡次征召，皇甫谧写下《释劝论》，申明自己不愿赴官的立场，辨析出仕与隐居，性命与功名之间取舍，是研究皇甫谧处世思想的核心文本。',
          theme: '处世思想',
          themeClassification: 'PRESENTATION_CLASSIFICATION',
          source: YAN_SOURCE_NAME,
          relatedWork: '《释劝论》',
          relatedPerson: '皇甫谧',
          status: 'AVAILABLE',
        },
      ],
    },
    {
      id: 'duzhong-lun',
      title: '《笃终论》',
      fullTextStatus: 'DATA_GAP',
      records: [
        {
          id: 'duzhong-lun-desc',
          section: '《笃终论》',
          text: '皇甫谧临终所作，薄葬思想名篇。反对厚葬，主张简约丧葬，剖析生死观念，体现魏晋时代的生死观，是思想史重要材料。',
          theme: '生死观与薄葬思想',
          themeClassification: 'PRESENTATION_CLASSIFICATION',
          source: YAN_SOURCE_NAME,
          relatedWork: '《笃终论》',
          relatedPerson: '皇甫谧',
          status: 'AVAILABLE',
        },
      ],
    },
  ],
  supplement:
    '补充：皇甫谧所著《帝王世纪》《高士传》《逸士传》《列女传》片段辑佚，大量散见于类书，搜集其书中议论，看皇甫谧的历史观、人物评判标准。',
}
