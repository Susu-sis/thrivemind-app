'use client';

import { forwardRef, InputHTMLAttributes } from 'react';

export interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange' | 'value'> {
  value?: number[];
  onValueChange?: (value: number[]) => void;
  min?: number;
  max?: number;
  step?: number;
}

const Slider = forwardRef<HTMLInputElement, SliderProps>(
  ({ className = '', value = [5], onValueChange, min = 0, max = 10, step = 1, ...props }, ref) => {
    return (
      <input
        ref={ref}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value[0]}
        onChange={(e) => onValueChange?.([Number(e.target.value)])}
        className={`w-full h-2 rounded-lg appearance-none cursor-pointer bg-slate-700 accent-accent ${className}`}
        {...props}
      />
    );
  }
);
Slider.displayName = 'Slider';

export { Slider };
