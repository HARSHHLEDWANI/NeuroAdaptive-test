"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";

interface MarkdownMessageProps {
  content: string;
  className?: string;
}

const components: Components = {
  h1: ({ children }) => (
    <h1 className="text-2xl font-black mb-3 mt-4 leading-tight">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-xl font-bold mb-2 mt-4 pb-1 border-b-2 border-black leading-tight">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-base font-bold mb-2 mt-3 leading-tight">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="mb-3 leading-relaxed last:mb-0">{children}</p>
  ),
  ul: ({ children }) => (
    <ul className="mb-3 space-y-1.5 pl-1">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="mb-3 space-y-1.5 pl-5 list-decimal">{children}</ol>
  ),
  li: ({ children }) => (
    <li className="flex items-start gap-2 leading-relaxed">
      <span className="mt-2 w-1.5 h-1.5 rounded-full bg-black flex-shrink-0" />
      <span>{children}</span>
    </li>
  ),
  code: (props) => {
    const { children, className } = props;
    const isBlock = className?.startsWith("language-");
    const language = className?.replace("language-", "") ?? "";

    if (isBlock) {
      return (
        <div className="mb-3 rounded-xl overflow-hidden border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
          {language && (
            <div className="bg-black text-white px-4 py-1.5 text-xs font-mono font-bold uppercase tracking-widest">
              {language}
            </div>
          )}
          <pre className="bg-gray-900 text-green-300 p-4 overflow-x-auto">
            <code className="text-sm font-mono leading-relaxed">{children}</code>
          </pre>
        </div>
      );
    }
    return (
      <code className="bg-gray-100 border border-gray-300 px-1.5 py-0.5 rounded text-sm font-mono text-purple-700">
        {children}
      </code>
    );
  },
  pre: ({ children }) => <>{children}</>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-purple-500 bg-purple-50 pl-4 pr-2 py-2 italic text-gray-700 mb-3 rounded-r-lg">
      {children}
    </blockquote>
  ),
  strong: ({ children }) => (
    <strong className="font-black text-black">{children}</strong>
  ),
  em: ({ children }) => <em className="italic text-gray-700">{children}</em>,
  hr: () => <hr className="border-t-2 border-dashed border-gray-300 my-4" />,
  table: ({ children }) => (
    <div className="overflow-x-auto mb-3 rounded-xl border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
      <table className="border-collapse w-full">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-black text-white">{children}</thead>,
  th: ({ children }) => (
    <th className="px-4 py-2 text-left font-bold text-sm tracking-wide border-r border-gray-700 last:border-0">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="px-4 py-2 border-t border-gray-200 border-r border-gray-200 last:border-r-0 text-sm">
      {children}
    </td>
  ),
  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-purple-600 font-semibold underline underline-offset-2 hover:text-purple-800"
    >
      {children}
    </a>
  ),
};

export function MarkdownMessage({ content, className = "" }: MarkdownMessageProps) {
  return (
    <div className={`prose-custom text-black text-sm md:text-base ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
