export type LayerId = 'crust' | 'mantle' | 'core';

export interface EarthLayerInfo {
  id: LayerId;
  meshName: string;
  zhName: string;
  enName: string;
  positionDesc: string;
  thicknessDesc: string;
  composition: string;
  stateAndTemp: string;
  summary: string;
  eggAnalogy: string;
  badgeColor: string;
}

export interface RockSampleInfo {
  id: 'granite' | 'sandstone' | 'marble';
  meshName: string;
  zhName: string;
  category: string;
  features: string;
  usage: string;
}

export const EARTH_LAYERS: Record<LayerId, EarthLayerInfo> = {
  crust: {
    id: 'crust',
    meshName: 'Layer_Crust',
    zhName: '地殼',
    enName: 'Crust',
    positionDesc: '最外層（表層）',
    thicknessDesc: '最薄（約 5 – 70 公里）',
    composition: '堅硬的岩石（火成岩、沉積岩、變質岩）',
    stateAndTemp: '固態｜常溫至約 400°C',
    summary:
      '地殼是地球的最外層，也是最薄的一層。高山、平原和海底都屬於地殼，由堅硬的岩石組成，是我們和動植物生活的家園。',
    eggAnalogy: '🥚 熟雞蛋比喻：就像熟雞蛋最外面薄薄、脆脆的「蛋殼」！',
    badgeColor: '#38bdf8'
  },
  mantle: {
    id: 'mantle',
    meshName: 'Layer_Mantle',
    zhName: '地幔',
    enName: 'Mantle',
    positionDesc: '中間層（地殼之下）',
    thicknessDesc: '最厚（約 2,900 公里）',
    composition: '岩石塊與熾熱的岩漿物質',
    stateAndTemp: '固態岩石與可緩慢流動的熾熱物質｜約 1,000 – 3,700°C',
    summary:
      '地幔位於地殼下面，佔了地球最大的體積！這裡非常熾熱，部分岩石受高溫影響像濃稠糖漿一樣緩慢流動，火山爆發噴出的岩漿也與此有關。',
    eggAnalogy: '🥚 熟雞蛋比喻：就像包在蛋殼裡面厚厚一層的「蛋白」！',
    badgeColor: '#f97316'
  },
  core: {
    id: 'core',
    meshName: 'Layer_Core',
    zhName: '地核',
    enName: 'Core',
    positionDesc: '最中心位置',
    thicknessDesc: '半徑約 3,480 公里',
    composition: '高密度金屬（主要為鐵和鎳）',
    stateAndTemp: '極高溫、極高壓（外核液態金屬、內核固態金屬）｜高達約 5,500°C',
    summary:
      '地核位於地球的最中心位置，主要由鐵和鎳等金屬組成。這裡的溫度和壓力都是全地球最高的，熱度甚至接近太陽表面！',
    eggAnalogy: '🥚 熟雞蛋比喻：就像熟雞蛋最中心的金黃色「蛋黃」！',
    badgeColor: '#fbbf24'
  }
};

export const ROCK_SAMPLES: RockSampleInfo[] = [
  {
    id: 'granite',
    meshName: 'Rock_Granite',
    zhName: '花崗岩（Granite）',
    category: '火成岩（延伸重點 4EA2）',
    features: '質地非常堅硬，表面有明顯黑、白、粉紅或灰色的礦物顆粒斑點。',
    usage: '香港常見岩石！廣泛用於建築石材、海堤與鋪路石。'
  },
  {
    id: 'sandstone',
    meshName: 'Rock_Sandstone',
    zhName: '砂岩（Sandstone）',
    category: '沉積岩（延伸重點 4EA2）',
    features: '由細小沙粒經過長時間壓實而成，摸起來粗糙，常有一層層的條紋（層理）。',
    usage: '常見於香港赤洲等地質公園景觀，可用作建築裝飾石材。'
  },
  {
    id: 'marble',
    meshName: 'Rock_Marble',
    zhName: '大理岩（Marble）',
    category: '變質岩（延伸重點 4EA2）',
    features: '原本的岩石在地底受高溫高壓改變而成，打磨後光滑亮麗，帶有自然雲彩花紋。',
    usage: '常用於雕刻藝術品、大堂地板與桌面。'
  }
];
