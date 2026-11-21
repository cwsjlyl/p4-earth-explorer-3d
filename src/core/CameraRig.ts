import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export class CameraRig {
  public readonly controls: OrbitControls;
  private camera: THREE.PerspectiveCamera;
  private targetPos = new THREE.Vector3(4.2, 2.8, 4.8);
  private targetLookAt = new THREE.Vector3(0, 0, 0);
  private isTweening = false;

  constructor(camera: THREE.PerspectiveCamera, domElement: HTMLElement) {
    this.camera = camera;
    this.controls = new OrbitControls(camera, domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.07;
    this.controls.minDistance = 2.4;
    this.controls.maxDistance = 12.0;
    this.controls.enablePan = false;

    this.controls.addEventListener('start', () => {
      this.isTweening = false;
    });
  }

  public flyTo(position: THREE.Vector3, lookAt = new THREE.Vector3(0, 0, 0)): void {
    this.targetPos.copy(position);
    this.targetLookAt.copy(lookAt);
    this.isTweening = true;
  }

  public update(dt: number): void {
    if (this.isTweening) {
      const alpha = 1 - Math.exp(-5.0 * dt);
      this.camera.position.lerp(this.targetPos, alpha);
      this.controls.target.lerp(this.targetLookAt, alpha);
      if (this.camera.position.distanceTo(this.targetPos) < 0.03) {
        this.isTweening = false;
      }
    }
    this.controls.update();
  }
}
