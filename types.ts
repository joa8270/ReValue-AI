
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

export interface HardwareSpecs {
  modelName: string; // 新增：產品型號/名稱
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
  specs: HardwareSpecs;
  valuation: ValuationResult;
  aiAdvice?: string;
}
