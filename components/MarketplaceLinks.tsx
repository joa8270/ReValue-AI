
import React, { useState } from 'react';
import { Facebook, ShoppingBag, Terminal, Copy, Check, ExternalLink } from 'lucide-react';

interface MarketplaceLinksProps {
  content: string;
  deviceInfo: string;
}

const MarketplaceLinks: React.FC<MarketplaceLinksProps> = ({ content, deviceInfo }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const platforms = [
    {
      name: 'FB Marketplace',
      icon: <Facebook className="w-5 h-5" />,
      url: 'https://www.facebook.com/marketplace/create/item',
      color: 'bg-[#1877F2]',
      hover: 'hover:bg-[#166fe5]'
    },
    {
      name: 'eBay Sell',
      icon: <ShoppingBag className="w-5 h-5" />,
      url: 'https://www.ebay.com/sl/sell',
      color: 'bg-[#e53238]',
      hover: 'hover:bg-[#d42d32]'
    }
  ];

  return (
    <div className="mt-12 pt-10 border-t border-slate-800">
      <h4 className="text-sm font-black text-slate-100 mb-6 flex items-center gap-2 uppercase tracking-widest">
        <ExternalLink className="w-4 h-4 text-indigo-400" /> Quick Sell Platforms / 快速刊登至二手平台
      </h4>
      
      {/* 修正：優化 Grid 響應式點，增加 Gap 以防重疊 */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-2 gap-4 lg:gap-5">
        
        {/* 複製文案按鈕 */}
        <button
          onClick={handleCopy}
          className="flex items-center gap-4 px-5 py-5 bg-slate-800 border border-slate-700 rounded-2xl hover:border-indigo-500/50 hover:bg-slate-750 transition-all group shadow-sm min-h-[84px] w-full"
        >
          <div className="flex-shrink-0 p-3 bg-indigo-500/10 text-indigo-400 rounded-xl group-hover:bg-indigo-500/20 transition-colors">
            {copied ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
          </div>
          <div className="text-left overflow-hidden">
            <p className="text-xs font-black text-slate-100 uppercase tracking-tight truncate">複製文案 / Copy Content</p>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-0.5">AI Optimized Description</p>
          </div>
        </button>

        {/* 平台按鈕循環 */}
        {platforms.map((platform) => (
          <a
            key={platform.name}
            href={platform.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={handleCopy}
            className={`flex items-center gap-4 px-5 py-5 ${platform.color} ${platform.hover} text-white rounded-2xl transition-all shadow-lg active:scale-95 group min-h-[84px] w-full`}
          >
            <div className="flex-shrink-0 p-3 bg-white/10 rounded-xl group-hover:bg-white/20 transition-colors">
              {platform.icon}
            </div>
            <div className="text-left overflow-hidden">
              <p className="text-xs font-black uppercase tracking-tight truncate">{platform.name}</p>
              <p className="text-[10px] opacity-80 font-bold uppercase tracking-wider mt-0.5">Copy & Open Platform</p>
            </div>
          </a>
        ))}

        {/* PTT 格式按鈕 */}
        <button
          onClick={() => {
            const pttTemplate = `[販售] ${deviceInfo}\n\n${content}\n\n--\nSent from ValueCheck AI`;
            navigator.clipboard.writeText(pttTemplate);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
          }}
          className="flex items-center gap-4 px-5 py-5 bg-slate-950 border border-slate-800 hover:bg-black text-white rounded-2xl transition-all shadow-lg active:scale-95 group min-h-[84px] w-full"
        >
          <div className="flex-shrink-0 p-3 bg-white/5 rounded-xl group-hover:bg-white/10 transition-colors">
            <Terminal className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-left overflow-hidden">
            <p className="text-xs font-black uppercase tracking-tight truncate">PTT [販售] 格式</p>
            <p className="text-[10px] opacity-60 font-bold uppercase tracking-wider mt-0.5">Copy PTT Template</p>
          </div>
        </button>
      </div>

      <div className="mt-8 flex flex-col items-center gap-2">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-900/50 rounded-full border border-slate-800">
           <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse"></div>
           <p className="text-[10px] text-slate-500 italic font-medium">
             點擊連結將自動複製生成文案至您的剪貼簿
           </p>
        </div>
        <p className="text-[9px] text-slate-600 uppercase font-black tracking-[0.2em]">
          * Auto-copy enabled for all platform links
        </p>
      </div>
    </div>
  );
};

export default MarketplaceLinks;
