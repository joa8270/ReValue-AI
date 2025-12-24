/**
 * 行動裝置規格對照表
 * 當 AI 無法從截圖中識別出 CPU/RAM/GPU 時，根據型號自動填入已知規格
 */

export interface DeviceSpec {
  cpu: string;
  ram: string;
  gpu: string;
}

/**
 * 已知裝置規格資料庫
 * Key: 裝置型號名稱 (需與 AI 識別結果匹配)
 */
export const DEVICE_SPECS: Record<string, DeviceSpec> = {
  // ========== iPhone 系列 ==========
  // iPhone 17 系列 (2025)
  "iPhone 17 Pro Max": { cpu: "A19 Pro", ram: "12GB", gpu: "Apple GPU (6-core)" },
  "iPhone 17 Pro": { cpu: "A19 Pro", ram: "8GB", gpu: "Apple GPU (6-core)" },
  "iPhone 17": { cpu: "A19", ram: "8GB", gpu: "Apple GPU (5-core)" },

  // iPhone 16 系列 (2024)
  "iPhone 16 Pro Max": { cpu: "A18 Pro", ram: "8GB", gpu: "Apple GPU (6-core)" },
  "iPhone 16 Pro": { cpu: "A18 Pro", ram: "8GB", gpu: "Apple GPU (6-core)" },
  "iPhone 16 Plus": { cpu: "A18", ram: "8GB", gpu: "Apple GPU (5-core)" },
  "iPhone 16": { cpu: "A18", ram: "8GB", gpu: "Apple GPU (5-core)" },

  // iPhone 15 系列 (2023)
  "iPhone 15 Pro Max": { cpu: "A17 Pro", ram: "8GB", gpu: "Apple GPU (6-core)" },
  "iPhone 15 Pro": { cpu: "A17 Pro", ram: "8GB", gpu: "Apple GPU (6-core)" },
  "iPhone 15 Plus": { cpu: "A16 Bionic", ram: "6GB", gpu: "Apple GPU (5-core)" },
  "iPhone 15": { cpu: "A16 Bionic", ram: "6GB", gpu: "Apple GPU (5-core)" },

  // iPhone 14 系列 (2022)
  "iPhone 14 Pro Max": { cpu: "A16 Bionic", ram: "6GB", gpu: "Apple GPU (5-core)" },
  "iPhone 14 Pro": { cpu: "A16 Bionic", ram: "6GB", gpu: "Apple GPU (5-core)" },
  "iPhone 14 Plus": { cpu: "A15 Bionic", ram: "6GB", gpu: "Apple GPU (5-core)" },
  "iPhone 14": { cpu: "A15 Bionic", ram: "6GB", gpu: "Apple GPU (5-core)" },

  // iPhone 13 系列 (2021)
  "iPhone 13 Pro Max": { cpu: "A15 Bionic", ram: "6GB", gpu: "Apple GPU (5-core)" },
  "iPhone 13 Pro": { cpu: "A15 Bionic", ram: "6GB", gpu: "Apple GPU (5-core)" },
  "iPhone 13": { cpu: "A15 Bionic", ram: "4GB", gpu: "Apple GPU (4-core)" },
  "iPhone 13 mini": { cpu: "A15 Bionic", ram: "4GB", gpu: "Apple GPU (4-core)" },

  // iPhone 12 系列 (2020)
  "iPhone 12 Pro Max": { cpu: "A14 Bionic", ram: "6GB", gpu: "Apple GPU (4-core)" },
  "iPhone 12 Pro": { cpu: "A14 Bionic", ram: "6GB", gpu: "Apple GPU (4-core)" },
  "iPhone 12": { cpu: "A14 Bionic", ram: "4GB", gpu: "Apple GPU (4-core)" },
  "iPhone 12 mini": { cpu: "A14 Bionic", ram: "4GB", gpu: "Apple GPU (4-core)" },

  // iPhone SE 系列
  "iPhone SE (3rd generation)": { cpu: "A15 Bionic", ram: "4GB", gpu: "Apple GPU (4-core)" },
  "iPhone SE (2nd generation)": { cpu: "A13 Bionic", ram: "3GB", gpu: "Apple GPU (4-core)" },

  // ========== iPad 系列 ==========
  "iPad Pro 13-inch (M4)": { cpu: "Apple M4", ram: "8GB", gpu: "Apple GPU (10-core)" },
  "iPad Pro 11-inch (M4)": { cpu: "Apple M4", ram: "8GB", gpu: "Apple GPU (10-core)" },
  "iPad Air 13-inch (M2)": { cpu: "Apple M2", ram: "8GB", gpu: "Apple GPU (10-core)" },
  "iPad Air 11-inch (M2)": { cpu: "Apple M2", ram: "8GB", gpu: "Apple GPU (10-core)" },
  "iPad (10th generation)": { cpu: "A14 Bionic", ram: "4GB", gpu: "Apple GPU (4-core)" },
  "iPad mini (6th generation)": { cpu: "A15 Bionic", ram: "4GB", gpu: "Apple GPU (5-core)" },

  // ========== Samsung Galaxy 系列 ==========
  // Galaxy S24 系列 (2024)
  "Samsung Galaxy S24 Ultra": { cpu: "Snapdragon 8 Gen 3", ram: "12GB", gpu: "Adreno 750" },
  "Samsung Galaxy S24+": { cpu: "Snapdragon 8 Gen 3", ram: "12GB", gpu: "Adreno 750" },
  "Samsung Galaxy S24": { cpu: "Snapdragon 8 Gen 3", ram: "8GB", gpu: "Adreno 750" },

  // Galaxy S23 系列 (2023)
  "Samsung Galaxy S23 Ultra": { cpu: "Snapdragon 8 Gen 2", ram: "12GB", gpu: "Adreno 740" },
  "Samsung Galaxy S23+": { cpu: "Snapdragon 8 Gen 2", ram: "8GB", gpu: "Adreno 740" },
  "Samsung Galaxy S23": { cpu: "Snapdragon 8 Gen 2", ram: "8GB", gpu: "Adreno 740" },

  // Galaxy Z Fold 系列
  "Samsung Galaxy Z Fold5": { cpu: "Snapdragon 8 Gen 2", ram: "12GB", gpu: "Adreno 740" },
  "Samsung Galaxy Z Fold4": { cpu: "Snapdragon 8+ Gen 1", ram: "12GB", gpu: "Adreno 730" },

  // Galaxy Z Flip 系列
  "Samsung Galaxy Z Flip5": { cpu: "Snapdragon 8 Gen 2", ram: "8GB", gpu: "Adreno 740" },
  "Samsung Galaxy Z Flip4": { cpu: "Snapdragon 8+ Gen 1", ram: "8GB", gpu: "Adreno 730" },

  // ========== Google Pixel 系列 ==========
  "Google Pixel 9 Pro XL": { cpu: "Google Tensor G4", ram: "16GB", gpu: "Mali-G715" },
  "Google Pixel 9 Pro": { cpu: "Google Tensor G4", ram: "16GB", gpu: "Mali-G715" },
  "Google Pixel 9": { cpu: "Google Tensor G4", ram: "12GB", gpu: "Mali-G715" },
  "Google Pixel 8 Pro": { cpu: "Google Tensor G3", ram: "12GB", gpu: "Mali-G715" },
  "Google Pixel 8": { cpu: "Google Tensor G3", ram: "8GB", gpu: "Mali-G715" },
  "Google Pixel 7 Pro": { cpu: "Google Tensor G2", ram: "12GB", gpu: "Mali-G710" },
  "Google Pixel 7": { cpu: "Google Tensor G2", ram: "8GB", gpu: "Mali-G710" },
};

/**
 * 根據裝置型號查詢已知規格
 * @param modelName AI 識別出的裝置型號
 * @returns 匹配的規格，或 null 若無匹配
 */
export function lookupDeviceSpecs(modelName: string): DeviceSpec | null {
  if (!modelName) return null;

  // 嘗試直接匹配
  if (DEVICE_SPECS[modelName]) {
    return DEVICE_SPECS[modelName];
  }

  // 嘗試模糊匹配 (忽略大小寫)
  const normalizedName = modelName.toLowerCase().trim();
  for (const [key, spec] of Object.entries(DEVICE_SPECS)) {
    if (key.toLowerCase() === normalizedName) {
      return spec;
    }
  }

  // 嘗試部分匹配 (處理 "的 iPhone 17 Pro" 這類情況)
  for (const [key, spec] of Object.entries(DEVICE_SPECS)) {
    if (normalizedName.includes(key.toLowerCase())) {
      return spec;
    }
  }

  return null;
}
