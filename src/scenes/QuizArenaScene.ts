import * as THREE from 'three';
import { ROCK_SAMPLES, RockSampleInfo } from '../data/layersData';

export class QuizArenaScene {
  public readonly root = new THREE.Group();
  private rocksGroup: THREE.Group;
  private selectedIndex = 0;

  constructor(rocksAsset: THREE.Group) {
    this.root.visible = false;
    this.rocksGroup = rocksAsset.clone(true);
    this.root.add(this.rocksGroup);
  }

  public focusRock(index: number): RockSampleInfo {
    this.selectedIndex = THREE.MathUtils.clamp(index, 0, ROCK_SAMPLES.length - 1);
    return ROCK_SAMPLES[this.selectedIndex];
  }

  public update(dt: number, elapsed: number): void {
    if (!this.root.visible) return;

    ROCK_SAMPLES.forEach((info, idx) => {
      const obj = this.rocksGroup.getObjectByName(info.meshName);
      if (!obj) return;
      obj.rotation.y += dt * (idx === this.selectedIndex ? 1.1 : 0.35);
      const targetScale = idx === this.selectedIndex ? 1.35 : 0.85;
      obj.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 1 - Math.exp(-6 * dt));
      obj.position.y = idx === this.selectedIndex ? Math.sin(elapsed * 3) * 0.12 : 0;
    });
  }
}
