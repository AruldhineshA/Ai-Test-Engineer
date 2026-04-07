/**
 * Reusable Card component for consistent container styling.
 */

export function Card({ children, className = "", onClick, hoverable = false }) {
  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-xl border border-gray-200 shadow-sm ${
        hoverable ? "hover:shadow-md hover:border-indigo-200 cursor-pointer transition-all duration-200" : ""
      } ${className}`}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = "" }) {
  return (
    <div className={`px-6 py-4 border-b border-gray-100 ${className}`}>
      {children}
    </div>
  );
}

export function CardBody({ children, className = "" }) {
  return <div className={`px-6 py-4 ${className}`}>{children}</div>;
}
