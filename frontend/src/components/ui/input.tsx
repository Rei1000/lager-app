import * as React from "react";

import { cn } from "@/lib/utils";

type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export function Input({ className, ...props }: InputProps) {
  return (
    <input
      className={cn(
        "w-full rounded-md border border-slate-300 px-3 py-2.5 text-base outline-none ring-offset-white focus:border-slate-900 focus:ring-2 focus:ring-slate-900",
        className
      )}
      {...props}
    />
  );
}
