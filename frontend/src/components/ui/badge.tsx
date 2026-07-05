import { HTMLAttributes, forwardRef } from 'react';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'secondary' | 'outline';
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className = '', variant = 'default', ...props }, ref) => {
    const variants: Record<string, string> = {
      default: 'bg-accent text-white',
      secondary: 'bg-slate-700 text-slate-200',
      outline: 'border border-border text-slate-300',
    };
    return (
      <span
        ref={ref}
        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variants[variant]} ${className}`}
        {...props}
      />
    );
  }
);
Badge.displayName = 'Badge';

export { Badge };
