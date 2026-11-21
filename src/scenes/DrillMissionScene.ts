import * as THREE from 'three';
import { LayerId } from '../data/layersData';

export interface DrillTelemetry {
  depthKm: number;
  temperatureC: number;
  pressureGPa: number;
  currentLayer: 'crust' | 'mantle' | 'core';
  shieldSafe: boolean;
  statusNote: string;
}

export class DrillMissionScene {
  public readonly root = new THREE.Group();
  private podGroup: THREE.Group;
  private drillHead: THREE.Object3D | null = null;
  private drillCollar: THREE.Object3D | null = null;
  private heatShield: THREE.Object3D | null = null;

  private cavernWall: THREE.Mesh;
  private crystalClusters = new THREE.Group();
  private magmaParticles: THREE.Points;
  private podSpotlight: THREE.SpotLight;

  private depthKm = 20;
  private hasThermalShield = true;
  private hasPressureHull = true;

  constructor(podAsset: THREE.Group) {
    this.root.visible = false;

    this.podGroup = podAsset.clone(true);
    this.root.add(this.podGroup);

    this.drillHead = this.podGroup.getObjectByName('Drill_Head') ?? null;
    this.drillCollar = this.podGroup.getObjectByName('Drill_Collar') ?? null;
    this.heatShield = this.podGroup.getObjectByName('Heat_Shield') ?? null;

    if (this.heatShield) {
      this.heatShield.traverse((c) => {
        if (c instanceof THREE.Mesh && c.material instanceof THREE.MeshStandardMaterial) {
          c.material.transparent = true;
          c.material.depthWrite = false;
        }
      });
    }

    // Downward high-intensity drill searchlight illuminating subterranean rocks
    this.podSpotlight = new THREE.SpotLight(0xfef08a, 6.5, 12, Math.PI * 0.36, 0.45, 1.2);
    this.podSpotlight.position.set(0, 0.8, 0.8);
    this.podSpotlight.target.position.set(0, -3.5, 0);
    this.root.add(this.podSpotlight, this.podSpotlight.target);

    // Sculpted 3D Jagged Subterranean Rock Cavern Shaft (NOT a smooth cylinder!)
    this.cavernWall = this.buildSculptedCavernShaft();
    this.root.add(this.cavernWall);

    // Passing 3D rock ledges & glowing mineral crystal clusters along the shaft walls
    this.populateWallOutcrops();
    this.root.add(this.crystalClusters);

    // Rising drill sparks & magma embers
    const count = 260;
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const rad = 0.75 + Math.random() * 2.1;
      pos[i * 3] = Math.cos(angle) * rad;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 12;
      pos[i * 3 + 2] = Math.sin(angle) * rad;
    }
    const pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const pMat = new THREE.PointsMaterial({
      color: 0xfbbf24,
      size: 0.1,
      transparent: true,
      opacity: 0.88
    });
    this.magmaParticles = new THREE.Points(pGeo, pMat);
    this.root.add(this.magmaParticles);
  }

  private buildSculptedCavernShaft(): THREE.Mesh {
    const geo = new THREE.CylinderGeometry(3.2, 3.2, 16, 48, 36, true);
    const pos = geo.attributes.position as THREE.BufferAttribute;
    const colors = new Float32Array(pos.count * 3);

    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i);
      const z = pos.getZ(i);
      const ang = Math.atan2(z, x);

      // Multi-frequency rocky crags & horizontal geological strata shelves
      const crag =
        Math.sin(ang * 7 + y * 1.4) * 0.28 +
        Math.cos(ang * 13 - y * 2.6) * 0.16 +
        Math.sin(y * 5.2) * 0.14;
      const scale = (3.2 + crag) / 3.2;
      pos.setXYZ(i, x * scale, y, z * scale);

      const shade = 0.55 + (crag + 0.58) * 0.45;
      colors[i * 3] = shade;
      colors[i * 3 + 1] = shade * 0.92;
      colors[i * 3 + 2] = shade * 0.88;
    }
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geo.computeVertexNormals();

    const mat = new THREE.MeshStandardMaterial({
      color: 0x64748b,
      vertexColors: true,
      emissive: 0x0f172a,
      emissiveIntensity: 0.2,
      roughness: 0.86,
      metalness: 0.12,
      flatShading: true,
      side: THREE.BackSide
    });
    return new THREE.Mesh(geo, mat);
  }

  private populateWallOutcrops(): void {
    const rockMat = new THREE.MeshStandardMaterial({
      color: 0x475569,
      roughness: 0.82,
      flatShading: true
    });
    const crystalMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      emissive: 0x0284c7,
      emissiveIntensity: 0.9,
      roughness: 0.15,
      metalness: 0.3
    });

    for (let i = 0; i < 22; i++) {
      const ang = (i * 2.39996) % (Math.PI * 2);
      // Leave front camera corridor clear around ang in [0.9..2.2] (+Z)
      if (Math.sin(ang) > 0.55) continue;

      const y = -7.5 + (i / 22) * 15.0;
      const r = 2.65;
      const cluster = new THREE.Group();
      cluster.position.set(Math.cos(ang) * r, y, Math.sin(ang) * r);
      cluster.lookAt(0, y, 0);

      const boulder = new THREE.Mesh(new THREE.DodecahedronGeometry(0.42, 0), rockMat);
      cluster.add(boulder);

      if (i % 2 === 0) {
        const shard = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.58, 5), crystalMat.clone());
        shard.rotation.x = Math.PI * 0.42;
        shard.position.z = 0.25;
        shard.name = 'Outcrop_Crystal';
        cluster.add(shard);
      }
      this.crystalClusters.add(cluster);
    }
  }

  public setDepth(km: number): DrillTelemetry {
    this.depthKm = THREE.MathUtils.clamp(km, 0, 6371);
    return this.getTelemetry();
  }

  public setEquipment(thermalShield: boolean, pressureHull: boolean): DrillTelemetry {
    this.hasThermalShield = thermalShield;
    this.hasPressureHull = pressureHull;
    if (this.heatShield) {
      this.heatShield.visible = thermalShield;
    }
    return this.getTelemetry();
  }

  public getTelemetry(): DrillTelemetry {
    const d = this.depthKm;
    let currentLayer: 'crust' | 'mantle' | 'core' = 'crust';
    let temp = 25;
    let pressure = 0.1;

    if (d <= 70) {
      currentLayer = 'crust';
      temp = Math.round(25 + (d / 70) * 375);
      pressure = Number((0.1 + (d / 70) * 1.8).toFixed(1));
    } else if (d <= 2900) {
      currentLayer = 'mantle';
      const t = (d - 70) / (2900 - 70);
      temp = Math.round(1000 + t * 2700);
      pressure = Math.round(2 + t * 135);
    } else {
      currentLayer = 'core';
      const t = (d - 2900) / (6371 - 2900);
      temp = Math.round(3800 + t * 1700);
      pressure = Math.round(138 + t * 225);
    }

    const needShield = d > 70;
    const shieldSafe = !needShield || (this.hasThermalShield && this.hasPressureHull);

    let statusNote = '✅ 正在鑽探堅硬的固態花崗岩地殼，鎢鋼雙螺旋鑽頭運作穩定。';
    if (currentLayer === 'mantle') {
      statusNote = shieldSafe
        ? '🔥 已深入熾熱地幔！四周出現緩慢流動的紅橙色岩漿與岩石塊，六角隔熱力場正常運作！'
        : '⚠️ 警告：地幔高溫超過 1,000°C！請立即開啟「隔熱護盾」與「抗壓外殼」！';
    } else if (currentLayer === 'core') {
      statusNote = shieldSafe
        ? '⚡ 抵達地球最中心的鐵鎳金屬地核！環境溫度高達 5,500°C，極限科學探測任務完成！'
        : '🚨 危險：地核極端高溫高壓！探測艙缺乏完整防護而劇烈震動！';
    }

    return {
      depthKm: Math.round(d),
      temperatureC: temp,
      pressureGPa: pressure,
      currentLayer,
      shieldSafe,
      statusNote
    };
  }

  public update(dt: number, elapsed: number): void {
    if (!this.root.visible) return;

    const tel = this.getTelemetry();
    const speedFactor = 1.0 + (this.depthKm / 6371) * 3.2;

    // Spin 3-blade spiral auger & counter-rotate crusher gear collar!
    if (this.drillHead) {
      this.drillHead.rotation.y += dt * 7.5 * speedFactor;
    }
    if (this.drillCollar) {
      this.drillCollar.rotation.y -= dt * 3.2 * speedFactor;
    }
    if (this.heatShield && this.heatShield.visible) {
      this.heatShield.rotation.y += dt * 0.45;
    }

    const shakeAmp = tel.shieldSafe ? 0.012 + (this.depthKm / 6371) * 0.022 : 0.085;
    this.podGroup.position.x = Math.sin(elapsed * 34) * shakeAmp;
    this.podGroup.position.y = Math.cos(elapsed * 29) * shakeAmp;

    // Scroll outcrops upward to give vivid sensation of descending into Earth
    const scrollSpeed = 1.8 * speedFactor;
    this.crystalClusters.children.forEach((c) => {
      c.position.y += dt * scrollSpeed;
      if (c.position.y > 7.5) c.position.y -= 15.0;

      const shard = c.getObjectByName('Outcrop_Crystal');
      if (shard instanceof THREE.Mesh && shard.material instanceof THREE.MeshStandardMaterial) {
        if (tel.currentLayer === 'crust') {
          shard.material.color.setHex(0x38bdf8);
          shard.material.emissive.setHex(0x0284c7);
        } else if (tel.currentLayer === 'mantle') {
          shard.material.color.setHex(0xf97316);
          shard.material.emissive.setHex(0xea580c);
        } else {
          shard.material.color.setHex(0xfef08a);
          shard.material.emissive.setHex(0xf59e0b);
        }
      }
    });

    // Transition sculpted cavern wall colors & magma glow smoothly
    const mat = this.cavernWall.material as THREE.MeshStandardMaterial;
    const targetColor =
      tel.currentLayer === 'crust'
        ? new THREE.Color(0x64748b)
        : tel.currentLayer === 'mantle'
        ? new THREE.Color(0xb91c1c)
        : new THREE.Color(0xd97706);
    const targetEmissive =
      tel.currentLayer === 'crust'
        ? new THREE.Color(0x0f172a)
        : tel.currentLayer === 'mantle'
        ? new THREE.Color(0xea580c)
        : new THREE.Color(0xfbbf24);

    mat.color.lerp(targetColor, dt * 4);
    mat.emissive.lerp(targetEmissive, dt * 4);
    mat.emissiveIntensity = tel.currentLayer === 'crust' ? 0.15 : tel.currentLayer === 'mantle' ? 0.58 : 0.92;

    const posAttr = this.magmaParticles.geometry.getAttribute('position') as THREE.BufferAttribute;
    for (let i = 0; i < posAttr.count; i++) {
      let y = posAttr.getY(i) + dt * (2.5 * speedFactor);
      if (y > 6) y = -6;
      posAttr.setY(i, y);
    }
    posAttr.needsUpdate = true;
  }
}
