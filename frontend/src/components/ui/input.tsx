import { forwardRef, InputHTMLAttributes } from 'react';

const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className = '', ...props }, ref) => (
    <input
      ref={ref}
      className={`flex h-10 w-full rounded-md border border-border bg-slate-800 px-3 py-2 text-sm text-foreground placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-accent disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    />
  )
);
Input.displayName = 'Input';

export { Input };
