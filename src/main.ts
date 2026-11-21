import './style.css';
import { Engine } from './core/Engine';
import { CameraRig } from './core/CameraRig';
import { AssetLoader } from './core/AssetLoader';
import { CutawayLabScene } from './scenes/CutawayLabScene';
import { DrillMissionScene } from './scenes/DrillMissionScene';
import { QuizArenaScene } from './scenes/QuizArenaScene';
import { HUD } from './ui/HUD';

async function bootstrap(): Promise<void> {
  const canvas = document.getElementById('webgl-canvas') as HTMLCanvasElement;
  const uiRoot = document.getElementById('ui-root') as HTMLElement;
  const loadingOverlay = document.getElementById('loading-overlay') as HTMLElement;
  const loadingText = document.getElementById('loading-text') as HTMLElement;

  const engine = new Engine(canvas);
  const cameraRig = new CameraRig(engine.camera, canvas);
  const loader = new AssetLoader();

  const assets = await loader.loadAll((msg) => {
    if (loadingText) loadingText.textContent = msg;
  });

  const cutawayScene = new CutawayLabScene(assets.earthCutaway, canvas);
  cutawayScene.attachCamera(engine.camera);

  const drillScene = new DrillMissionScene(assets.drillPod);
  const quizScene = new QuizArenaScene(assets.rockSamples);

  engine.scene.add(cutawayScene.root, drillScene.root, quizScene.root);

  const hud = new HUD(uiRoot, canvas, cameraRig, cutawayScene, drillScene, quizScene);

  engine.onUpdate((dt, elapsed) => {
    cameraRig.update(dt);
    cutawayScene.update(dt, elapsed);
    drillScene.update(dt, elapsed);
    quizScene.update(dt, elapsed);
    hud.updateFloatingLabels();
  });

  loadingOverlay?.classList.add('hidden');
  engine.start();
}

bootstrap();
