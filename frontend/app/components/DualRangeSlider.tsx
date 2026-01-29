import React, { useCallback, useEffect, useState, useRef } from 'react'

interface DualRangeSliderProps {
    min: number
    max: number
    step?: number
    value: [number, number]
    onChange: (value: [number, number]) => void
    className?: string
}

const DualRangeSlider: React.FC<DualRangeSliderProps> = ({
    min,
    max,
    step = 1,
    value,
    onChange,
    className = ""
}) => {
    const [minVal, setMinVal] = useState(value[0])
    const [maxVal, setMaxVal] = useState(value[1])
    const minValRef = useRef(value[0])
    const maxValRef = useRef(value[1])
    const range = useRef<HTMLDivElement>(null)

    // Convert to percentage
    const getPercent = useCallback(
        (value: number) => Math.round(((value - min) / (max - min)) * 100),
        [min, max]
    )

    // Sync state if props change externally
    useEffect(() => {
        setMinVal(value[0])
        setMaxVal(value[1])
        minValRef.current = value[0]
        maxValRef.current = value[1]
    }, [value])

    // Update range style (progress bar)
    useEffect(() => {
        const minPercent = getPercent(minVal)
        const maxPercent = getPercent(maxVal)

        if (range.current) {
            range.current.style.left = `${minPercent}%`
            range.current.style.width = `${maxPercent - minPercent}%`
        }
    }, [minVal, maxVal, getPercent])

    return (
        <div className={`relative w-full h-8 flex items-center ${className}`}>
            {/* Hidden Input for Min */}
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={minVal}
                onChange={(event) => {
                    const value = Math.min(Number(event.target.value), maxVal - step)
                    setMinVal(value)
                    minValRef.current = value
                    onChange([value, maxVal])
                }}
                className="absolute w-full z-[3] h-0 opacity-0 cursor-pointer pointer-events-none [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:h-6 [&::-moz-range-thumb]:pointer-events-auto [&::-moz-range-thumb]:w-6 [&::-moz-range-thumb]:h-6"
                style={{ zIndex: minVal > max - 100 ? 5 : 3 }} // Fix z-index stacking if needed
            />

            {/* Hidden Input for Max */}
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={maxVal}
                onChange={(event) => {
                    const value = Math.max(Number(event.target.value), minVal + step)
                    setMaxVal(value)
                    maxValRef.current = value
                    onChange([minVal, value])
                }}
                className="absolute w-full z-[4] h-0 opacity-0 cursor-pointer pointer-events-none [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:h-6 [&::-moz-range-thumb]:pointer-events-auto [&::-moz-range-thumb]:w-6 [&::-moz-range-thumb]:h-6"
            />

            {/* Visual Track */}
            <div className="relative w-full h-2 rounded-full bg-slate-800">
                {/* Active Range */}
                <div
                    ref={range}
                    className="absolute h-full rounded-full bg-purple-500 z-[2]"
                />

                {/* Visual Thumbs (Optional, or rely on input thumbs if not hidden. 
                    Here we rely on the fact that inputs are transparent but their thumbs capture events.
                    To make custom styled thumbs visible, we can add divs that follow the percent.
                ) */}

                {/* Custom Thumb - Min */}
                <div
                    className="absolute w-5 h-5 bg-white border-2 border-purple-500 rounded-full z-[2] -translate-x-1/2 shadow pointer-events-none transition-transform active:scale-110"
                    style={{ left: `${getPercent(minVal)}%` }}
                />

                {/* Custom Thumb - Max */}
                <div
                    className="absolute w-5 h-5 bg-white border-2 border-purple-500 rounded-full z-[2] -translate-x-1/2 shadow pointer-events-none transition-transform active:scale-110"
                    style={{ left: `${getPercent(maxVal)}%` }}
                />
            </div>

            {/* Value Labels (Floating below) */}
            {/* Not included inside the slider to avoid layout issues, parent handles labels */}
        </div>
    )
}

export default DualRangeSlider
