import * as THREE from 'three';

export class Engine {
  public readonly scene: THREE.Scene;
  public readonly camera: THREE.PerspectiveCamera;
  public readonly renderer: THREE.WebGLRenderer;
  private updateCallbacks: Array<(dt: number, elapsed: number) => void> = [];
  private clock = new THREE.Clock();

  constructor(canvas: HTMLCanvasElement) {
    this.scene = new THREE.Scene();

    this.camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      200
    );
    this.camera.position.set(4.2, 2.8, 4.8);

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
    this.renderer.toneMappingExposure = 1.15;

    this.setupLights();
    this.setupStarfield();

    window.addEventListener('resize', this.handleResize);
  }

  private setupLights(): void {
    const ambient = new THREE.HemisphereLight(0xdbeafe, 0x1e1b4b, 1.15);
    this.scene.add(ambient);

    const keyLight = new THREE.DirectionalLight(0xffffff, 2.1);
    keyLight.position.set(6, 8, 7);
    this.scene.add(keyLight);

    const rimLight = new THREE.DirectionalLight(0x38bdf8, 0.9);
    rimLight.position.set(-6, -3, -5);
    this.scene.add(rimLight);
  }

  private setupStarfield(): void {
    const count = 450;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 35 + Math.random() * 45;
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
      size: 0.16,
      transparent: true,
      opacity: 0.75
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
