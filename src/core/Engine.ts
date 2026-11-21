import * as THREE from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

export class Engine {
  public readonly scene: THREE.Scene;
  public readonly camera: THREE.PerspectiveCamera;
  public readonly renderer: THREE.WebGLRenderer;
  private updateCallbacks: Array<(dt: number, elapsed: number) => void> = [];
  private clock = new THREE.Clock();

  constructor(canvas: HTMLCanvasElement) {
    this.scene = new THREE.Scene();

    this.camera = new THREE.PerspectiveCamera(
      42,
      window.innerWidth / window.innerHeight,
      0.1,
      200
    );
    this.camera.position.set(3.8, 2.3, 4.7);

    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.18;

    // Studio Physically-Based Environment Lighting so metallic drills, ocean specular,
    // iron-nickel core & polished marble gleam realistically!
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    this.scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();

    this.setupLights();
    this.setupStarfield();

    window.addEventListener('resize', this.handleResize);
  }

  private setupLights(): void {
    const ambient = new THREE.HemisphereLight(0xe0f2fe, 0x1e1b4b, 0.95);
    this.scene.add(ambient);

    const sunLight = new THREE.DirectionalLight(0xfffbeb, 2.25);
    sunLight.position.set(-4.5, 6.5, 7.5);
    this.scene.add(sunLight);

    const cutawayFill = new THREE.DirectionalLight(0xffedd5, 1.35);
    cutawayFill.position.set(6.0, 2.5, 5.5);
    this.scene.add(cutawayFill);

    const rimLight = new THREE.DirectionalLight(0x38bdf8, 1.05);
    rimLight.position.set(-5.0, -4.0, -6.0);
    this.scene.add(rimLight);
  }

  private setupStarfield(): void {
    const count = 600;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 36 + Math.random() * 50;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const mat = new THREE.PointsMaterial({
      color: 0xe0f2fe,
      size: 0.15,
      transparent: true,
      opacity: 0.8
    });
    this.scene.add(new THREE.Points(geo, mat));
  }

  public onUpdate(cb: (dt: number, elapsed: number) => void): void {
    this.updateCallbacks.push(cb);
  }

  public start(): void {
    this.renderer.setAnimationLoop(() => {
      const dt = Math.min(this.clock.getDelta(), 0.05);
      const elapsed = this.clock.elapsedTime;
      for (const cb of this.updateCallbacks) {
        cb(dt, elapsed);
      }
      this.renderer.render(this.scene, this.camera);
    });
  }

  private handleResize = (): void => {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  };
}
