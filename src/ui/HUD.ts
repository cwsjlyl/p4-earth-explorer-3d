import * as THREE from 'three';
import { EARTH_LAYERS, LayerId, ROCK_SAMPLES } from '../data/layersData';
import { QUIZ_QUESTIONS } from '../data/quizQuestions';
import { CameraRig } from '../core/CameraRig';
import { CutawayLabScene } from '../scenes/CutawayLabScene';
import { DrillMissionScene } from '../scenes/DrillMissionScene';
import { QuizArenaScene } from '../scenes/QuizArenaScene';

type GameMode = 'cutaway' | 'drill' | 'quiz';

export class HUD {
  private root: HTMLElement;
  private mode: GameMode = 'cutaway';
  private activeLayer: LayerId = 'crust';
  private exploded = false;
  private trueScale = false;

  private depthKm = 20;
  private thermalShield = true;
  private pressureHull = true;

  private quizIdx = 0;
  private answeredIdx: number | null = null;
  private score = 0;
  private rockIdx = 0;

  constructor(
    root: HTMLElement,
    private cameraRig: CameraRig,
    private cutawayScene: CutawayLabScene,
    private drillScene: DrillMissionScene,
    private quizScene: QuizArenaScene
  ) {
    this.root = root;

    this.cutawayScene.onLayerSelected((layer) => {
      this.activeLayer = layer;
      this.render();
    });

    this.render();
  }

  private speak(text: string): void {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'zh-HK';
    utter.rate = 0.98;
    window.speechSynthesis.speak(utter);
  }

  private switchMode(next: GameMode): void {
    this.mode = next;
    this.cutawayScene.root.visible = next === 'cutaway';
    this.drillScene.root.visible = next === 'drill';
    this.quizScene.root.visible = next === 'quiz';

    if (next === 'cutaway') {
      this.cameraRig.flyTo(new THREE.Vector3(4.2, 2.6, 4.6), new THREE.Vector3(0, 0, 0));
    } else if (next === 'drill') {
      this.cameraRig.flyTo(new THREE.Vector3(0, 0.4, 4.2), new THREE.Vector3(0, 0, 0));
    } else {
      this.cameraRig.flyTo(new THREE.Vector3(0, 1.3, 4.8), new THREE.Vector3(0, 0, 0));
    }

    this.render();
  }

  public render(): void {
    this.root.innerHTML = `
      <header class="hud-topbar">
        <div class="brand-badge">
          <h1>🌍 地心探險號 3D</h1>
          <span class="curriculum-tag">小四科學 4EA1</span>
        </div>
        <nav class="mode-tabs">
          <button class="tab-btn ${this.mode === 'cutaway' ? 'active' : ''}" data-mode="cutaway">
            1. 剖面工坊
          </button>
          <button class="tab-btn ${this.mode === 'drill' ? 'active' : ''}" data-mode="drill">
            2. 地心鑽探
          </button>
          <button class="tab-btn ${this.mode === 'quiz' ? 'active' : ''}" data-mode="quiz">
            3. 岩石與挑戰
          </button>
        </nav>
      </header>
      ${this.renderModeContent()}
    `;

    this.bindEvents();
  }

  private renderModeContent(): string {
    if (this.mode === 'cutaway') {
      const info = EARTH_LAYERS[this.activeLayer];
      return `
        <section class="control-panel">
          <h3 class="panel-title">🔍 點選或切換地球圈層</h3>
          <div class="btn-row">
            <button class="action-btn ${this.activeLayer === 'crust' ? 'selected' : ''}" data-layer="crust">地殼 Crust</button>
            <button class="action-btn ${this.activeLayer === 'mantle' ? 'selected' : ''}" data-layer="mantle">地幔 Mantle</button>
            <button class="action-btn ${this.activeLayer === 'core' ? 'selected' : ''}" data-layer="core">地核 Core</button>
          </div>
          <div class="btn-row">
            <button class="action-btn primary" id="btn-explode">
              ${this.exploded ? '🧩 合併地球剖面' : '💥 拆開三層結構'}
            </button>
            <button class="action-btn" id="btn-scale">
              ${this.trueScale ? '📐 目前：真實科學比例' : '🔎 目前：教學放大比例'}
            </button>
          </div>
        </section>

        <aside class="info-card">
          <h2>
            <span>${info.zhName}（${info.enName}）</span>
            <button class="action-btn speak-btn" id="btn-speak" style="flex:0 0 auto;min-height:36px;">🔊 粵語朗讀</button>
          </h2>
          <div class="prop-grid">
            <div class="prop-item">
              <div class="prop-label">所在位置</div>
              <div class="prop-value">${info.positionDesc}</div>
            </div>
            <div class="prop-item">
              <div class="prop-label">相對厚度</div>
              <div class="prop-value">${info.thicknessDesc}</div>
            </div>
            <div class="prop-item">
              <div class="prop-label">主要組成物質</div>
              <div class="prop-value">${info.composition}</div>
            </div>
            <div class="prop-item">
              <div class="prop-label">狀態與溫度</div>
              <div class="prop-value">${info.stateAndTemp}</div>
            </div>
          </div>
          <p style="margin:8px 0;font-size:0.9rem;line-height:1.5;">${info.summary}</p>
          <div class="egg-analogy">${info.eggAnalogy}</div>
        </aside>
      `;
    }

    if (this.mode === 'drill') {
      const tel = this.drillScene.setDepth(this.depthKm);
      const layerInfo = EARTH_LAYERS[tel.currentLayer];
      return `
        <section class="control-panel">
          <h3 class="panel-title">
            <span>🛠️ PDAR 地心鑽探控制艙</span>
            <span>所在圈層：${layerInfo.zhName}</span>
          </h3>
          <label style="font-size:0.85rem;">下潛深度滑桿（0 – 6,371 公里）：</label>
          <input type="range" id="depth-slider" class="depth-slider" min="0" max="6371" step="10" value="${this.depthKm}" />
          <div class="telemetry-bar">
            <div class="telemetry-box">
              <span class="prop-label">深度</span>
              <strong id="tel-depth">${tel.depthKm} km</strong>
            </div>
            <div class="telemetry-box">
              <span class="prop-label">環境溫度</span>
              <strong id="tel-temp">${tel.temperatureC} °C</strong>
            </div>
            <div class="telemetry-box">
              <span class="prop-label">地底壓力</span>
              <strong id="tel-pres">${tel.pressureGPa} GPa</strong>
            </div>
          </div>
          <div class="btn-row">
            <button class="action-btn ${this.thermalShield ? 'selected' : ''}" id="btn-shield">
              🛡️ 隔熱護盾：${this.thermalShield ? '開啟' : '關閉'}
            </button>
            <button class="action-btn ${this.pressureHull ? 'selected' : ''}" id="btn-hull">
              🔩 抗壓外殼：${this.pressureHull ? '開啟' : '關閉'}
            </button>
          </div>
        </section>

        <aside class="info-card">
          <h2>📡 探測艙即時科學紀錄</h2>
          <p id="tel-status" style="font-size:0.95rem;line-height:1.55;font-weight:700;">${tel.statusNote}</p>
          <div class="egg-analogy">
            💡 <strong>探究思考（PDAR）：</strong>拉動滑桿比較地殼、地幔和地核的溫度與壓力數據，你發現深度越深，物理特性有甚麼規律？
          </div>
        </aside>
      `;
    }

    const q = QUIZ_QUESTIONS[this.quizIdx];
    const rock = this.quizScene.focusRock(this.rockIdx);
    return `
      <section class="control-panel">
        <h3 class="panel-title">🪨 地殼三大岩石 3D 標本（延伸 4EA2）</h3>
        <div class="btn-row">
          ${ROCK_SAMPLES.map(
            (r, idx) => `
              <button class="action-btn ${this.rockIdx === idx ? 'selected' : ''}" data-rock="${idx}">
                ${r.zhName.split('（')[0]}
              </button>
            `
          ).join('')}
        </div>
        <div class="prop-item">
          <div class="prop-label">${rock.category}</div>
          <div class="prop-value" style="margin-bottom:4px;">${rock.zhName}</div>
          <div style="font-size:0.84rem;line-height:1.45;">${rock.features}<br/>📍 ${rock.usage}</div>
        </div>
      </section>

      <aside class="info-card">
        <h2>
          <span>🏆 地質小博士挑戰（${this.quizIdx + 1}/${QUIZ_QUESTIONS.length}）</span>
          <span style="font-size:0.9rem;color:#34d399;">得分：${this.score}</span>
        </h2>
        <p style="font-size:0.95rem;font-weight:700;line-height:1.45;margin:8px 0;">${q.question}</p>
        <div class="quiz-options">
          ${q.options
            .map((opt, idx) => {
              let cls = 'quiz-opt-btn';
              if (this.answeredIdx !== null) {
                if (idx === q.correctIndex) cls += ' correct';
                else if (idx === this.answeredIdx) cls += ' wrong';
              }
              return `<button class="${cls}" data-opt="${idx}">${opt}</button>`;
            })
            .join('')}
        </div>
        ${
          this.answeredIdx !== null
            ? `
            <div class="egg-analogy" style="margin-top:10px;">
              ${this.answeredIdx === q.correctIndex ? '🎉 答對了！' : '💪 再接再厲！'} ${q.explanation}
            </div>
            <button class="action-btn primary" id="btn-next-q" style="width:100%;margin-top:10px;">
              ${this.quizIdx < QUIZ_QUESTIONS.length - 1 ? '下一題 ➡️' : '重新挑戰 🔄'}
            </button>
          `
            : ''
        }
      </aside>
    `;
  }

  private bindEvents(): void {
    this.root.querySelectorAll<HTMLButtonElement>('[data-mode]').forEach((btn) => {
      btn.addEventListener('click', () => {
        this.switchMode(btn.dataset.mode as GameMode);
      });
    });

    this.root.querySelectorAll<HTMLButtonElement>('[data-layer]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const layer = btn.dataset.layer as LayerId;
        this.activeLayer = layer;
        this.cutawayScene.selectLayer(layer);
        this.render();
      });
    });

    this.root.querySelector('#btn-explode')?.addEventListener('click', () => {
      this.exploded = this.cutawayScene.toggleExplode();
      this.render();
    });

    this.root.querySelector('#btn-scale')?.addEventListener('click', () => {
      this.trueScale = this.cutawayScene.toggleTrueScale();
      this.render();
    });

    this.root.querySelector('#btn-speak')?.addEventListener('click', () => {
      const info = EARTH_LAYERS[this.activeLayer];
      this.speak(`${info.zhName}。${info.summary} ${info.eggAnalogy.replace('🥚 ', '')}`);
    });

    const slider = this.root.querySelector<HTMLInputElement>('#depth-slider');
    slider?.addEventListener('input', () => {
      this.depthKm = Number(slider.value);
      const tel = this.drillScene.setDepth(this.depthKm);
      const dEl = this.root.querySelector('#tel-depth');
      const tEl = this.root.querySelector('#tel-temp');
      const pEl = this.root.querySelector('#tel-pres');
      const sEl = this.root.querySelector('#tel-status');
      if (dEl) dEl.textContent = `${tel.depthKm} km`;
      if (tEl) tEl.textContent = `${tel.temperatureC} °C`;
      if (pEl) pEl.textContent = `${tel.pressureGPa} GPa`;
      if (sEl) sEl.textContent = tel.statusNote;
    });

    this.root.querySelector('#btn-shield')?.addEventListener('click', () => {
      this.thermalShield = !this.thermalShield;
      this.drillScene.setEquipment(this.thermalShield, this.pressureHull);
      this.render();
    });

    this.root.querySelector('#btn-hull')?.addEventListener('click', () => {
      this.pressureHull = !this.pressureHull;
      this.drillScene.setEquipment(this.thermalShield, this.pressureHull);
      this.render();
    });

    this.root.querySelectorAll<HTMLButtonElement>('[data-rock]').forEach((btn) => {
      btn.addEventListener('click', () => {
        this.rockIdx = Number(btn.dataset.rock);
        this.quizScene.focusRock(this.rockIdx);
        this.render();
      });
    });

    this.root.querySelectorAll<HTMLButtonElement>('[data-opt]').forEach((btn) => {
      btn.addEventListener('click', () => {
        if (this.answeredIdx !== null) return;
        const picked = Number(btn.dataset.opt);
        this.answeredIdx = picked;
        if (picked === QUIZ_QUESTIONS[this.quizIdx].correctIndex) {
          this.score += 1;
        }
        this.render();
      });
    });

    this.root.querySelector('#btn-next-q')?.addEventListener('click', () => {
      if (this.quizIdx < QUIZ_QUESTIONS.length - 1) {
        this.quizIdx += 1;
      } else {
        this.quizIdx = 0;
        this.score = 0;
      }
      this.answeredIdx = null;
      this.render();
    });
  }
}
