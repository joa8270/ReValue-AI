
// 設備類型：用於區分手機與電腦的不同評估欄位
export type DeviceCategory = 'phone' | 'tablet' | 'computer' | 'mac';

// 舊版 DeviceType 保留相容性
export enum DeviceType {
  IOS = 'iOS',
  ANDROID = 'Android',
  WINDOWS = 'Windows',
  MACOS = 'MacOS'
}

export enum VisualGrade {
  A = 'A',
  B = 'B',
  C = 'C',
  D = 'D'
}

export enum StorageType {
  SSD = 'ssd',
  HDD = 'hdd',
  EMMC = 'emmc'
}

export interface GroundingSource {
  title: string;
  uri: string;
}

// 基礎規格（共用欄位）
export interface BaseSpecs {
  deviceCategory: DeviceCategory;
  brand: string;           // 品牌
  modelName: string;       // 型號
  releaseYear: string;     // 發布年份
  storageCapacity: string; // 儲存容量
  condition?: string;      // 外觀狀態
  searchKeywords: string;  // 搜尋關鍵字
}

// 手機/平板規格
export interface PhoneSpecs extends BaseSpecs {
  deviceCategory: 'phone' | 'tablet';
  processor: string;       // 處理器 (A19 Pro)
  screenSize?: string;     // 螢幕尺寸
  batteryCapacity?: string;// 電池容量
}

// 電腦/Mac 規格
export interface ComputerSpecs extends BaseSpecs {
  deviceCategory: 'computer' | 'mac';
  cpu: string;             // CPU
  ram: string;             // RAM
  gpu: string;             // GPU
  storageType: StorageType;// 儲存類型
}

// 統一規格介面（用於前端 state，包含所有可能的欄位）
export interface UnifiedSpecs {
  deviceCategory: DeviceCategory;
  brand: string;
  modelName: string;
  releaseYear: string;
  storageCapacity: string;
  searchKeywords: string;
  condition?: string;
  // 手機專用欄位
  processor?: string;
  screenSize?: string;
  batteryCapacity?: string;
  // 電腦專用欄位
  cpu?: string;
  ram?: string;
  gpu?: string;
  storageType?: StorageType;
  // 額外欄位
  aiKeywords?: string;
}

// 統一硬體規格類型
export type HardwareSpecs = PhoneSpecs | ComputerSpecs;

// 舊版相容介面（用於漸進式遷移）
export interface LegacyHardwareSpecs {
  modelName: string;
  os: DeviceType | 'Unknown';
  ram: string;
  cpu: string;
  gpu: string;
  battery: string;
  storage: StorageType;
  storageCapacity: string;
  grade: VisualGrade;
  defects: string[];
  userAgent: string;
}

export interface ValuationResult {
  scrapPrice: number;
  potentialPrice: number;
  finalOffer: number;
  marketAnalysis: string;
  sources: GroundingSource[];
  notes: string[];
}

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface HistoryEntry {
  id: string;
  timestamp: number;
  specs: UnifiedSpecs;
  valuation: ValuationResult;
  aiAdvice?: string;
}
