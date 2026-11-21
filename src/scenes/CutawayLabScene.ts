import * as THREE from 'three';
import { EARTH_LAYERS, LayerId } from '../data/layersData';

export class CutawayLabScene {
  public readonly root = new THREE.Group();
  private layerMeshes: Record<LayerId, THREE.Object3D | null> = {
    crust: null,
    mantle: null,
    core: null
  };
  private exploded = false;
  private trueScale = false;
  private selectedLayer: LayerId = 'crust';
  private raycaster = new THREE.Raycaster();
  private pointer = new THREE.Vector2();
  private onSelectCallback?: (layer: LayerId) => void;
  private cameraRef?: THREE.Camera;

  constructor(earthAsset: THREE.Group, canvas: HTMLCanvasElement) {
    const model = earthAsset.clone(true);
    this.root.add(model);

    this.layerMeshes.crust = model.getObjectByName(EARTH_LAYERS.crust.meshName) ?? null;
    this.layerMeshes.mantle = model.getObjectByName(EARTH_LAYERS.mantle.meshName) ?? null;
    this.layerMeshes.core = model.getObjectByName(EARTH_LAYERS.core.meshName) ?? null;

    model.traverse((child) => {
      if (child instanceof THREE.Mesh && child.material) {
        child.material = child.material.clone();
      }
    });

    canvas.addEventListener('pointerdown', (ev) => {
      if (!this.root.visible || !this.cameraRef) return;
      const rect = canvas.getBoundingClientRect();
      this.pointer.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
      this.pointer.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
      this.raycaster.setFromCamera(this.pointer, this.cameraRef);
      const hits = this.raycaster.intersectObjects(this.root.children, true);
      for (const hit of hits) {
        const hitLayer = this.resolveLayerFromObject(hit.object);
        if (hitLayer) {
          this.selectLayer(hitLayer);
          this.onSelectCallback?.(hitLayer);
          break;
        }
      }
    });
  }

  public attachCamera(cam: THREE.Camera): void {
    this.cameraRef = cam;
  }

  public onLayerSelected(cb: (layer: LayerId) => void): void {
    this.onSelectCallback = cb;
  }

  private resolveLayerFromObject(obj: THREE.Object3D | null): LayerId | null {
    let cur: THREE.Object3D | null = obj;
    while (cur) {
      if (cur.name === 'Layer_Crust') return 'crust';
      if (cur.name === 'Layer_Mantle') return 'mantle';
      if (cur.name === 'Layer_Core') return 'core';
      cur = cur.parent;
    }
    return null;
  }

  public selectLayer(layer: LayerId): void {
    this.selectedLayer = layer;
  }

  public toggleExplode(): boolean {
    this.exploded = !this.exploded;
    return this.exploded;
  }

  public toggleTrueScale(): boolean {
    this.trueScale = !this.trueScale;
    return this.trueScale;
  }

  public update(dt: number, elapsed: number): void {
    if (!this.root.visible) return;

    const lerpFactor = 1 - Math.exp(-6 * dt);
    const offsets: Record<LayerId, THREE.Vector3> = {
      crust: this.exploded ? new THREE.Vector3(0.85, 0.45, 0.85) : new THREE.Vector3(0, 0, 0),
      mantle: this.exploded ? new THREE.Vector3(0.32, 0.15, 0.32) : new THREE.Vector3(0, 0, 0),
      core: this.exploded ? new THREE.Vector3(-0.35, -0.2, -0.35) : new THREE.Vector3(0, 0, 0)
    };

    (['crust', 'mantle', 'core'] as LayerId[]).forEach((id) => {
      const obj = this.layerMeshes[id];
      if (!obj) return;
      obj.position.lerp(offsets[id], lerpFactor);

      obj.traverse((child) => {
        if (child instanceof THREE.Mesh) {
          if (child.morphTargetInfluences && child.morphTargetInfluences.length > 0) {
            const targetMorph = this.trueScale ? 1.0 : 0.0;
            child.morphTargetInfluences[0] = THREE.MathUtils.lerp(
              child.morphTargetInfluences[0],
              targetMorph,
              lerpFactor
            );
          } else if (this.trueScale) {
            const s = id === 'core' ? 1.15 : id === 'crust' ? 0.99 : 1.04;
            child.scale.lerp(new THREE.Vector3(s, s, s), lerpFactor);
          } else {
            child.scale.lerp(new THREE.Vector3(1, 1, 1), lerpFactor);
          }

          if (child.material instanceof THREE.MeshStandardMaterial) {
            const baseGlow = id === 'core' ? 0.75 : id === 'mantle' ? 0.4 : 0.08;
            const pulse =
              id === this.selectedLayer ? baseGlow + 0.28 + Math.sin(elapsed * 4.5) * 0.12 : baseGlow;
            child.material.emissiveIntensity = pulse;
          }
        }
      });
    });
  }
}
