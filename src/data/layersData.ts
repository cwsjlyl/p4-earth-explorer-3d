export type LayerId = 'crust' | 'mantle' | 'core' | 'hk';

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
    positionDesc: '最外層（陸地與海底表層）',
    thicknessDesc: '最薄（約 5 – 70 公里）',
    composition: '堅硬的岩石（火成岩、沉積岩、變質岩）',
    stateAndTemp: '固態｜地表常溫至地底約 400°C',
    summary:
      '地殼是地球的最外層，也是最薄的一層。高山、大陸和深海海床都屬於地殼，由堅硬的岩石組成，是人類與萬物生活的家園。',
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
      '地幔位於地殼下面，佔了地球最大的體積！這裡非常熾熱，部分岩石受高溫影響像濃稠糖漿一樣緩慢對流流動，火山噴出的岩漿也源自地底深處。',
    eggAnalogy: '🥚 熟雞蛋比喻：就像包在蛋殼裡面厚厚一層的「蛋白」！',
    badgeColor: '#f97316'
  },
  core: {
    id: 'core',
    meshName: 'Layer_Core',
    zhName: '地核',
    enName: 'Core',
    positionDesc: '地球最中心位置',
    thicknessDesc: '半徑約 3,480 公里',
    composition: '高密度金屬（主要為鐵和鎳）',
    stateAndTemp: '極高溫、極高壓（外核液態金屬、內核固態結晶）｜高達約 5,500°C',
    summary:
      '地核位於地球的最中心位置，主要由鐵和鎳等金屬組成。這裡的溫度和壓力都是全地球最高的，熱度甚至接近太陽表面！',
    eggAnalogy: '🥚 熟雞蛋比喻：就像熟雞蛋最中心的金黃色「蛋黃」！',
    badgeColor: '#fbbf24'
  },
  hk: {
    id: 'hk',
    meshName: 'HK_Marker',
    zhName: '香港地標（本地地殼連結）',
    enName: 'Hong Kong (22.3°N, 114.2°E)',
    positionDesc: '歐亞大陸東南沿海地殼之上',
    thicknessDesc: '香港地殼厚度約 30 公里',
    composition: '主要為堅硬的花崗岩、火山岩及沉積岩',
    stateAndTemp: '穩定固態大陸地殼｜遠離板塊邊界，較少大型地震',
    summary:
      '我們身處的香港位於歐亞板塊內部的陸地「地殼」上！獅子山、維港兩岸主要由堅硬的「花崗岩」及火山岩構成，而香港聯合國教科文組織世界地質公園（如赤洲）則能觀察到紅褐色的「砂岩」層理。',
    eggAnalogy: '🇭🇰 課堂小觀察：下次經過獅子山或地鐵站石牆時，仔細找找花崗岩上黑白相間的礦物斑點吧！',
    badgeColor: '#f43f5e'
  }
};

export const ROCK_SAMPLES: RockSampleInfo[] = [
  {
    id: 'granite',
    meshName: 'Rock_Granite',
    zhName: '花崗岩（Granite）',
    category: '火成岩（延伸重點 4EA2）',
    features: '質地非常堅硬，表面有明顯粉紅（長石）、灰白（石英）與黑色（黑雲母）的礦物結晶斑點。',
    usage: '香港最常見岩石（如獅子山、維港兩岸基岩）！廣泛用於建築石材與海堤。'
  },
  {
    id: 'sandstone',
    meshName: 'Rock_Sandstone',
    zhName: '砂岩（Sandstone）',
    category: '沉積岩（延伸重點 4EA2）',
    features: '由細小沙粒與鐵質經長時間壓實而成，表面粗糙，有清晰的一層層紅褐色與金黃色條紋（層理）。',
    usage: '常見於香港地質公園赤洲（「海上丹霞」景觀），亦可用作特色建築石材。'
  },
  {
    id: 'marble',
    meshName: 'Rock_Marble',
    zhName: '大理岩（Marble）',
    category: '變質岩（延伸重點 4EA2）',
    features: '原本的岩石在地殼深處受高溫高壓改變而成，打磨切面光滑亮麗，帶有自然流體雲彩花紋。',
    usage: '香港元朗及馬鞍山一帶地底亦有大理岩分佈；常用於雕刻藝術品、大堂地板與桌面。'
  }
];
