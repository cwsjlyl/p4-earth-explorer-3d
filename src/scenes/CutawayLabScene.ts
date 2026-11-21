import * as THREE from 'three';
import { EARTH_LAYERS, LayerId } from '../data/layersData';

export interface HkScreenProjection {
  visible: boolean;
  x: number;
  y: number;
}

export class CutawayLabScene {
  public readonly root = new THREE.Group();
  private layerMeshes: Record<'crust' | 'mantle' | 'core', THREE.Object3D | null> = {
    crust: null,
    mantle: null,
    core: null
  };
  private cloudsObj: THREE.Object3D | null = null;
  private hkMarkerObj: THREE.Object3D | null = null;
  private hkAnchorObj: THREE.Object3D | null = null;

  private exploded = false;
  private trueScale = false;
  private cloudsVisible = true;
  private selectedLayer: LayerId = 'crust';
  private raycaster = new THREE.Raycaster();
  private pointer = new THREE.Vector2();
  private onSelectCallback?: (layer: LayerId) => void;
  private cameraRef?: THREE.Camera;
  private tempVec = new THREE.Vector3();
  private tempNormal = new THREE.Vector3();
  private camDir = new THREE.Vector3();

  constructor(earthAsset: THREE.Group, canvas: HTMLCanvasElement) {
    const model = earthAsset.clone(true);
    this.root.add(model);

    this.layerMeshes.crust = model.getObjectByName(EARTH_LAYERS.crust.meshName) ?? null;
    this.layerMeshes.mantle = model.getObjectByName(EARTH_LAYERS.mantle.meshName) ?? null;
    this.layerMeshes.core = model.getObjectByName(EARTH_LAYERS.core.meshName) ?? null;
    this.cloudsObj = model.getObjectByName('Layer_Clouds') ?? null;
    this.hkMarkerObj = model.getObjectByName('HK_Marker') ?? null;
    this.hkAnchorObj = model.getObjectByName('anchor_hk') ?? null;

    model.traverse((child) => {
      if (child instanceof THREE.Mesh && child.material) {
        if (Array.isArray(child.material)) {
          child.material = child.material.map((m) => m.clone());
        } else {
          child.material = child.material.clone();
        }
        // Ensure transparent clouds render cleanly above crust without depth-fighting
        if (child.name === 'Layer_Clouds' && child.material instanceof THREE.MeshStandardMaterial) {
          child.material.transparent = true;
          child.material.depthWrite = false;
          child.renderOrder = 2;
        }
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
        if (hit.object.name === 'Layer_Clouds') continue;
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
      if (cur.name === 'HK_Marker') return 'hk';
      if (cur.name === 'Layer_Crust') return 'crust';
      if (cur.name === 'Layer_Mantle') return 'mantle';
      if (cur.name === 'Layer_Core' || cur.name === 'Inner_Core_Crystal') return 'core';
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

  public toggleClouds(): boolean {
    this.cloudsVisible = !this.cloudsVisible;
    if (this.cloudsObj) {
      this.cloudsObj.visible = this.cloudsVisible;
    }
    return this.cloudsVisible;
  }

  public getHongKongWorldFocus(): { camPos: THREE.Vector3; target: THREE.Vector3 } {
    if (this.hkMarkerObj) {
      this.hkMarkerObj.getWorldPosition(this.tempVec);
      const dir = this.tempVec.clone().normalize();
      return {
        camPos: dir.clone().multiplyScalar(3.55).add(new THREE.Vector3(0.35, 0.45, 0.35)),
        target: this.tempVec.clone()
      };
    }
    return {
      camPos: new THREE.Vector3(-1.8, 1.5, 3.1),
      target: new THREE.Vector3(-1.0, 0.75, 1.5)
    };
  }

  public getHkScreenPosition(canvas: HTMLCanvasElement): HkScreenProjection {
    if (!this.root.visible || !this.cameraRef || (!this.hkAnchorObj && !this.hkMarkerObj)) {
      return { visible: false, x: 0, y: 0 };
    }
    const targetNode = this.hkAnchorObj ?? this.hkMarkerObj!;
    targetNode.getWorldPosition(this.tempVec);

    // Hide floating badge when Hong Kong rotates to the far side of the globe
    this.tempNormal.copy(this.tempVec).normalize();
    this.camDir.copy(this.cameraRef.position).sub(this.tempVec).normalize();
    if (this.tempNormal.dot(this.camDir) < 0.08) {
      return { visible: false, x: 0, y: 0 };
    }

    const projected = this.tempVec.clone().project(this.cameraRef);
    if (projected.z > 1) {
      return { visible: false, x: 0, y: 0 };
    }

    const x = (projected.x * 0.5 + 0.5) * canvas.clientWidth;
    const y = (-projected.y * 0.5 + 0.5) * canvas.clientHeight;
    return { visible: true, x, y };
  }

  public update(dt: number, elapsed: number): void {
    if (!this.root.visible) return;

    const lerpFactor = 1 - Math.exp(-6 * dt);
    // Cutaway window faces (+X, +Z), so explode layers cleanly along the cutaway axis!
    const offsets: Record<'crust' | 'mantle' | 'core', THREE.Vector3> = {
      crust: this.exploded ? new THREE.Vector3(-0.65, 0.38, -0.65) : new THREE.Vector3(0, 0, 0),
      mantle: this.exploded ? new THREE.Vector3(0.12, 0.06, 0.12) : new THREE.Vector3(0, 0, 0),
      core: this.exploded ? new THREE.Vector3(0.75, -0.25, 0.75) : new THREE.Vector3(0, 0, 0)
    };

    if (this.cloudsObj) {
      const cloudTarget = this.exploded
        ? new THREE.Vector3(-0.92, 0.55, -0.92)
        : new THREE.Vector3(0, 0, 0);
      this.cloudsObj.position.lerp(cloudTarget, lerpFactor);
      // Gentle atmospheric cloud oscillation around polar Y axis
      this.cloudsObj.rotation.y = Math.sin(elapsed * 0.18) * 0.035;
    }

    // Gentle beacon pulse on Hong Kong Landmark
    if (this.hkMarkerObj) {
      const s = this.selectedLayer === 'hk' ? 1.28 + Math.sin(elapsed * 6) * 0.08 : 1.0 + Math.sin(elapsed * 3) * 0.04;
      this.hkMarkerObj.scale.lerp(new THREE.Vector3(s, s, s), lerpFactor);
    }

    (['crust', 'mantle', 'core'] as const).forEach((id) => {
      const obj = this.layerMeshes[id];
      if (!obj) return;
      obj.position.lerp(offsets[id], lerpFactor);

      obj.traverse((child) => {
        if (child === this.hkMarkerObj || child.parent === this.hkMarkerObj) return;
        if (child instanceof THREE.Mesh) {
          if (child.morphTargetInfluences && child.morphTargetInfluences.length > 0) {
            const targetMorph = this.trueScale ? 1.0 : 0.0;
            child.morphTargetInfluences[0] = THREE.MathUtils.lerp(
              child.morphTargetInfluences[0],
              targetMorph,
              lerpFactor
            );
          }

          // Preserve baked PBR textures; only modulate magma/core glow or subtle crust selection rim
          const mats = Array.isArray(child.material) ? child.material : [child.material];
          for (const mat of mats) {
            if (mat instanceof THREE.MeshStandardMaterial) {
              if (id === 'mantle') {
                mat.emissiveIntensity = this.selectedLayer === 'mantle' ? 1.65 + Math.sin(elapsed * 4) * 0.25 : 1.15;
              } else if (id === 'core') {
                mat.emissiveIntensity = this.selectedLayer === 'core' ? 1.55 + Math.sin(elapsed * 4.5) * 0.25 : 1.1;
              } else if (id === 'crust') {
                if (this.selectedLayer === 'crust') {
                  mat.emissive.setHex(0x0ea5e9);
                  mat.emissiveIntensity = 0.08 + Math.sin(elapsed * 4) * 0.04;
                } else {
                  mat.emissiveIntensity = 0.0;
                }
              }
            }
          }
        }
      });
    });
  }
}
