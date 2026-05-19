import type React from 'react';

type Props<T> = {
  columns: { key: keyof T | string; label: string; render?: (row: T) => React.ReactNode }[];
  rows: T[];
  onRowClick?: (row: T) => void;
};

export function SimpleTable<T extends object>({ columns, rows, onRowClick }: Props<T>) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/70">
      <table className="min-w-full divide-y divide-slate-800 text-sm">
        <thead className="bg-slate-900">
          <tr>
            {columns.map((column) => (
              <th key={String(column.key)} className="px-4 py-3 text-left font-semibold text-slate-300">{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {rows.map((row, index) => (
            <tr
              key={index}
              onClick={() => onRowClick?.(row)}
              className={`${onRowClick ? 'cursor-pointer' : ''} hover:bg-slate-800/50`}
            >
              {columns.map((column) => (
                <td key={String(column.key)} className="px-4 py-3 text-slate-200">
                  {column.render ? column.render(row) : String((row as Record<string, unknown>)[column.key as string] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
