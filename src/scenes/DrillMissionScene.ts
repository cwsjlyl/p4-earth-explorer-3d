import * as THREE from 'three';
import { LayerId } from '../data/layersData';

export interface DrillTelemetry {
  depthKm: number;
  temperatureC: number;
  pressureGPa: number;
  currentLayer: LayerId;
  shieldSafe: boolean;
  statusNote: string;
}

export class DrillMissionScene {
  public readonly root = new THREE.Group();
  private podGroup: THREE.Group;
  private drillHead: THREE.Object3D | null = null;
  private heatShield: THREE.Object3D | null = null;
  private tunnelWall: THREE.Mesh;
  private magmaParticles: THREE.Points;

  private depthKm = 0;
  private hasThermalShield = true;
  private hasPressureHull = true;

  constructor(podAsset: THREE.Group) {
    this.root.visible = false;

    this.podGroup = podAsset.clone(true);
    this.root.add(this.podGroup);

    this.drillHead = this.podGroup.getObjectByName('Drill_Head') ?? null;
    this.heatShield = this.podGroup.getObjectByName('Heat_Shield') ?? null;

    const wallGeo = new THREE.CylinderGeometry(2.5, 2.5, 14, 32, 1, true);
    const wallMat = new THREE.MeshStandardMaterial({
      color: 0x3b82f6,
      emissive: 0x1e3a8a,
      emissiveIntensity: 0.25,
      roughness: 0.75,
      side: THREE.BackSide
    });
    this.tunnelWall = new THREE.Mesh(wallGeo, wallMat);
    this.root.add(this.tunnelWall);

    const count = 180;
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const rad = 0.9 + Math.random() * 1.4;
      pos[i * 3] = Math.cos(angle) * rad;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 10;
      pos[i * 3 + 2] = Math.sin(angle) * rad;
    }
    const pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const pMat = new THREE.PointsMaterial({
      color: 0xfbbf24,
      size: 0.11,
      transparent: true,
      opacity: 0.8
    });
    this.magmaParticles = new THREE.Points(pGeo, pMat);
    this.root.add(this.magmaParticles);
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
    let currentLayer: LayerId = 'crust';
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

    let statusNote = '✅ 正在鑽探堅硬的固態岩石地殼，艙體狀態穩定。';
    if (currentLayer === 'mantle') {
      statusNote = shieldSafe
        ? '🔥 已進入地幔！周圍出現熾熱且緩慢流動的岩漿物質，隔熱抗壓護盾運作正常！'
        : '⚠️ 警告：地幔高溫超過 1,000°C！請立即開啟「隔熱護盾」與「抗壓外殼」！';
    } else if (currentLayer === 'core') {
      statusNote = shieldSafe
        ? '⚡ 抵達地球最中心的金屬地核！鐵鎳核心溫度高達 5,500°C，探測數據紀錄完成！'
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

    if (this.drillHead) {
      this.drillHead.rotation.y += dt * (4.0 + (this.depthKm / 6371) * 10.0);
    }

    const shakeAmp = tel.shieldSafe ? 0.015 + (this.depthKm / 6371) * 0.025 : 0.09;
    this.podGroup.position.x = Math.sin(elapsed * 32) * shakeAmp;
    this.podGroup.position.y = Math.cos(elapsed * 27) * shakeAmp;

    const mat = this.tunnelWall.material as THREE.MeshStandardMaterial;
    const targetColor =
      tel.currentLayer === 'crust'
        ? new THREE.Color(0x334155)
        : tel.currentLayer === 'mantle'
        ? new THREE.Color(0xc2410c)
        : new THREE.Color(0xd97706);
    const targetEmissive =
      tel.currentLayer === 'crust'
        ? new THREE.Color(0x0f172a)
        : tel.currentLayer === 'mantle'
        ? new THREE.Color(0xea580c)
        : new THREE.Color(0xfbbf24);

    mat.color.lerp(targetColor, dt * 4);
    mat.emissive.lerp(targetEmissive, dt * 4);
    mat.emissiveIntensity = tel.currentLayer === 'crust' ? 0.15 : tel.currentLayer === 'mantle' ? 0.55 : 0.85;

    const posAttr = this.magmaParticles.geometry.getAttribute('position') as THREE.BufferAttribute;
    const speed = 2.0 + (this.depthKm / 6371) * 6.0;
    for (let i = 0; i < posAttr.count; i++) {
      let y = posAttr.getY(i) + dt * speed;
      if (y > 5) y = -5;
      posAttr.setY(i, y);
    }
    posAttr.needsUpdate = true;
  }
}
