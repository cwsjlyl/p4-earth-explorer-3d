export interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export const QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: 1,
    question: '地球由外至內可以分成哪三個主要圈層？',
    options: [
      '地核 → 地幔 → 地殼',
      '地殼 → 地幔 → 地核',
      '地幔 → 地殼 → 地核',
      '岩石圈 → 大氣層 → 地核'
    ],
    correctIndex: 1,
    explanation: '地球由最外層往中心依序是：最薄的「地殼」、最厚的「地幔」，以及最中心的「地核」。'
  },
  {
    id: 2,
    question: '在三個圈層當中，哪一層最薄，並且由堅硬的岩石組成？',
    options: ['地殼', '地幔', '地核', '岩漿層'],
    correctIndex: 0,
    explanation: '「地殼」位於地球最外層，厚度最薄（就像熟雞蛋的蛋殼），由堅硬的固態岩石組成。'
  },
  {
    id: 3,
    question: '「地幔」具有以下哪一項物理特性？',
    options: [
      '全部由冰塊和水組成',
      '溫度比地面還要冰冷',
      '位於地殼下面，含有岩石塊和熾熱、可緩慢流動的岩漿物質',
      '是地球最薄的一層'
    ],
    correctIndex: 2,
    explanation: '「地幔」位於地殼下方，體積最大，溫度極高，含有岩石塊與可緩慢流動的熾熱岩漿物質。'
  },
  {
    id: 4,
    question: '位於地球最中心位置的「地核」，主要由甚麼物質組成？',
    options: ['泥土和樹葉', '鐵和鎳等金屬', '空氣和水蒸氣', '柔軟的沙粒'],
    correctIndex: 1,
    explanation: '「地核」位於地球最中心，主要由高密度的鐵和鎳等金屬組成，溫度與壓力極高！'
  },
  {
    id: 5,
    question: '【PDAR 工程探究】如果探測艙要潛入地幔與地核交界，最需要哪兩種保護設計？',
    options: [
      '太陽能帆板與捕魚網',
      '超強隔熱護盾與抗高壓金屬外殼',
      '木製外殼與紙降落傘',
      '普通塑膠外殼與風扇'
    ],
    correctIndex: 1,
    explanation: '越往地球內部深入，溫度與壓力都會急劇上升，因此探測艙必須具備超強隔熱與抗高壓設計！'
  },
  {
    id: 6,
    question: '【延伸挑戰 4EA2】香港常見、表面有明顯黑白顆粒斑點且非常堅硬的地殼岩石是哪一種？',
    options: ['花崗岩', '泥膠塊', '冰塊', '煤炭'],
    correctIndex: 0,
    explanation: '香港大部分地區都有花崗岩（火成岩的一種），質地堅硬且有明顯的礦物斑點顆粒！'
  }
];
