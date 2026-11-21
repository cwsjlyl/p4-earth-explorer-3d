import * as THREE from 'three';
import { ROCK_SAMPLES, RockSampleInfo } from '../data/layersData';

export class QuizArenaScene {
  public readonly root = new THREE.Group();
  private rocksGroup: THREE.Group;
  private selectedIndex = 0;
  private spotLight: THREE.SpotLight;

  constructor(rocksAsset: THREE.Group) {
    this.root.visible = false;
    this.rocksGroup = rocksAsset.clone(true);
    this.root.add(this.rocksGroup);

    // Sleek museum exhibition stage platform beneath the 3 specimen plinths
    const stageGeo = new THREE.CylinderGeometry(3.8, 4.1, 0.18, 48);
    const stageMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a,
      metalness: 0.55,
      roughness: 0.25
    });
    const stage = new THREE.Mesh(stageGeo, stageMat);
    stage.position.y = -0.82;
    this.root.add(stage);

    const ringGeo = new THREE.TorusGeometry(3.82, 0.025, 12, 64);
    const ringMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      emissive: 0x0284c7,
      emissiveIntensity: 0.9
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI * 0.5;
    ring.position.y = -0.73;
    this.root.add(ring);

    // Dedicated museum specimen key spotlight tracking the selected rock!
    this.spotLight = new THREE.SpotLight(0xfffbeb, 5.5, 10, Math.PI * 0.28, 0.5, 1.0);
    this.spotLight.position.set(0, 3.6, 2.6);
    this.root.add(this.spotLight, this.spotLight.target);
  }

  public focusRock(index: number): { info: RockSampleInfo; targetX: number } {
    this.selectedIndex = THREE.MathUtils.clamp(index, 0, ROCK_SAMPLES.length - 1);
    const targetX = (this.selectedIndex - 1) * 2.1;
    this.spotLight.position.x = targetX;
    this.spotLight.target.position.set(targetX, 0, 0);
    return { info: ROCK_SAMPLES[this.selectedIndex], targetX };
  }

  public update(dt: number, elapsed: number): void {
    if (!this.root.visible) return;

    ROCK_SAMPLES.forEach((info, idx) => {
      const obj = this.rocksGroup.getObjectByName(info.meshName);
      if (!obj) return;
      obj.rotation.y += dt * (idx === this.selectedIndex ? 0.65 : 0.18);
      const targetScale = idx === this.selectedIndex ? 1.28 : 0.88;
      obj.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 1 - Math.exp(-6 * dt));
      obj.position.y = idx === this.selectedIndex ? 0.08 + Math.sin(elapsed * 2.4) * 0.04 : 0;
    });
  }
}
