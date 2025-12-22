
import React, { useState, useEffect, useCallback, useRef } from 'react';

interface TouchTestModalProps {
  isOpen: boolean;
  onClose: (completed: boolean) => void;
}

const TouchTestModal: React.FC<TouchTestModalProps> = ({ isOpen, onClose }) => {
  const [touchedIndices, setTouchedIndices] = useState<Set<number>>(new Set());
  const gridRef = useRef<HTMLDivElement>(null);
  const totalCells = 100;

  useEffect(() => {
    if (isOpen) {
      setTouchedIndices(new Set());
    }
  }, [isOpen]);

  const handleCellActivation = useCallback((index: number) => {
    setTouchedIndices((prev) => {
      if (prev.has(index)) return prev;
      const next = new Set(prev);
      next.add(index);
      return next;
    });
  }, []);

  useEffect(() => {
    if (touchedIndices.size === totalCells && isOpen) {
      const timer = setTimeout(() => {
        onClose(true);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [touchedIndices.size, isOpen, onClose]);

  const onPointerMove = (e: React.PointerEvent) => {
    const target = document.elementFromPoint(e.clientX, e.clientY) as HTMLElement;
    if (target && target.dataset.index) {
      handleCellActivation(parseInt(target.dataset.index, 10));
    }
  };

  if (!isOpen) return null;

  const progress = Math.round((touchedIndices.size / totalCells) * 100);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-95 z-[60] flex flex-col items-center justify-center p-4">
      <div className="text-white mb-6 text-center">
        <h3 className="text-2xl font-bold mb-2">螢幕觸控測試</h3>
        <p className="text-gray-400 text-sm">請用手指滑過所有方塊將其變綠</p>
        <p className="text-emerald-400 font-mono text-3xl mt-4">{progress}%</p>
      </div>

      <div 
        ref={gridRef}
        onPointerMove={onPointerMove}
        className="grid grid-cols-10 grid-rows-10 gap-1 bg-gray-800 p-1 rounded-lg touch-none select-none w-full max-w-[360px] aspect-square"
      >
        {Array.from({ length: totalCells }).map((_, i) => (
          <div
            key={i}
            data-index={i}
            className={`touch-grid-cell border border-gray-700 rounded-sm ${
              touchedIndices.has(i) ? 'bg-emerald-500 border-emerald-400' : 'bg-gray-700'
            }`}
          />
        ))}
      </div>

      <button 
        onClick={() => onClose(false)}
        className="mt-10 px-8 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-full font-medium transition-colors"
      >
        放棄測試
      </button>
    </div>
  );
};

export default TouchTestModal;
