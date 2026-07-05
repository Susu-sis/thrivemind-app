import { forwardRef, ButtonHTMLAttributes } from 'react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost' | 'destructive';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = '', variant = 'default', size = 'default', ...props }, ref) => {
    const base = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50';
    const variants: Record<string, string> = {
      default: 'bg-accent text-white hover:bg-accent/90',
      outline: 'border border-border bg-transparent hover:bg-card',
      ghost: 'hover:bg-card',
      destructive: 'bg-red-600 text-white hover:bg-red-700',
    };
    const sizes: Record<string, string> = {
      default: 'h-10 px-4 py-2 text-sm',
      sm: 'h-8 px-3 text-xs',
      lg: 'h-12 px-6 text-base',
      icon: 'h-10 w-10',
    };
    return (
      <button
        ref={ref}
        className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';

export { Button };
