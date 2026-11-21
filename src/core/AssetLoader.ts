import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

export interface LoadedGameAssets {
  earthCutaway: THREE.Group;
  drillPod: THREE.Group;
  rockSamples: THREE.Group;
}

export class AssetLoader {
  private loader = new GLTFLoader();

  public async loadAll(onProgress?: (msg: string) => void): Promise<LoadedGameAssets> {
    onProgress?.('正在載入 Blender 地球剖面模型...');
    const earthCutaway = await this.loadOrFallback(
      './models/earth_cutaway.glb',
      () => this.buildFallbackEarth()
    );

    onProgress?.('正在載入地心鑽探艙模型...');
    const drillPod = await this.loadOrFallback(
      './models/drill_pod.glb',
      () => this.buildFallbackPod()
    );

    onProgress?.('正在載入香港地殼岩石標本...');
    const rockSamples = await this.loadOrFallback(
      './models/rock_samples.glb',
      () => this.buildFallbackRocks()
    );

    return { earthCutaway, drillPod, rockSamples };
  }

  private async loadOrFallback(
    url: string,
    fallbackFactory: () => THREE.Group
  ): Promise<THREE.Group> {
    try {
      const gltf = await this.loader.loadAsync(url);
      return gltf.scene;
    } catch {
      console.info(`[AssetLoader] Using procedural fallback for ${url}`);
      return fallbackFactory();
    }
  }

  private buildFallbackEarth(): THREE.Group {
    const group = new THREE.Group();

    const makeCutawayShell = (
      name: string,
      rOut: number,
      color: number,
      emissive: number,
      emissiveIntensity: number,
      metalness = 0.1,
      roughness = 0.5
    ) => {
      const geo = new THREE.SphereGeometry(rOut, 40, 28, Math.PI * 0.5, Math.PI * 1.5, 0, Math.PI);
      const mat = new THREE.MeshStandardMaterial({
        color,
        emissive,
        emissiveIntensity,
        metalness,
        roughness,
        side: THREE.DoubleSide
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.name = name;
      return mesh;
    };

    const core = makeCutawayShell('Layer_Core', 0.85, 0xfbbf24, 0xf59e0b, 0.55, 0.85, 0.25);
    const mantle = makeCutawayShell('Layer_Mantle', 1.72, 0xea580c, 0xdc2626, 0.35, 0.05, 0.45);
    const crust = makeCutawayShell('Layer_Crust', 2.0, 0x2563eb, 0x0284c7, 0.1, 0.05, 0.55);

    group.add(core, mantle, crust);
    return group;
  }

  private buildFallbackPod(): THREE.Group {
    const group = new THREE.Group();
    const hull = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.55, 0.5, 12, 24),
      new THREE.MeshStandardMaterial({ color: 0xfbbf24, metalness: 0.45, roughness: 0.28 })
    );
    hull.position.y = 0.3;
    hull.name = 'Pod_Body';

    const viewport = new THREE.Mesh(
      new THREE.SphereGeometry(0.32, 20, 16),
      new THREE.MeshStandardMaterial({
        color: 0x38bdf8,
        emissive: 0x0ea5e9,
        emissiveIntensity: 0.6,
        roughness: 0.1
      })
    );
    viewport.position.set(0, 0.42, 0.42);
    viewport.name = 'Pod_Viewport';

    const drill = new THREE.Mesh(
      new THREE.ConeGeometry(0.5, 0.95, 18),
      new THREE.MeshStandardMaterial({ color: 0xcbd5e1, metalness: 0.9, roughness: 0.22 })
    );
    drill.rotation.x = Math.PI;
    drill.position.y = -0.75;
    drill.name = 'Drill_Head';

    const shield = new THREE.Mesh(
      new THREE.TorusGeometry(0.74, 0.07, 12, 28),
      new THREE.MeshStandardMaterial({
        color: 0x2dd4bf,
        emissive: 0x14b8a6,
        emissiveIntensity: 0.55
      })
    );
    shield.rotation.x = Math.PI * 0.5;
    shield.position.y = -0.1;
    shield.name = 'Heat_Shield';

    group.add(hull, viewport, drill, shield);
    return group;
  }

  private buildFallbackRocks(): THREE.Group {
    const group = new THREE.Group();
    const specs: Array<{ name: string; x: number; color: number; rough: number; flat: boolean }> = [
      { name: 'Rock_Granite', x: -1.8, color: 0xcbd5e1, rough: 0.65, flat: true },
      { name: 'Rock_Sandstone', x: 0, color: 0xd97706, rough: 0.92, flat: true },
      { name: 'Rock_Marble', x: 1.8, color: 0xf8fafc, rough: 0.22, flat: false }
    ];
    for (const s of specs) {
      const geo = new THREE.DodecahedronGeometry(0.65, s.flat ? 1 : 2);
      const mat = new THREE.MeshStandardMaterial({
        color: s.color,
        roughness: s.rough,
        flatShading: s.flat
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.name = s.name;
      mesh.position.set(s.x, 0, 0);
      group.add(mesh);
    }
    return group;
  }
}
