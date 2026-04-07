/**
 * Reusable Input component with label and error display.
 */

export function Input({
  label,
  type = "text",
  value,
  onChange,
  placeholder,
  error,
  required = false,
  icon: Icon,
  disabled = false,
  className = "",
}) {
  return (
    <div className={`space-y-1 ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon className="w-4 h-4 text-gray-400" />
          </div>
        )}
        <input
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          className={`w-full rounded-lg border ${
            error ? "border-red-400 focus:ring-red-500" : "border-gray-300 focus:ring-indigo-500"
          } px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:border-transparent transition-all disabled:bg-gray-50 disabled:text-gray-500 ${
            Icon ? "pl-10" : ""
          }`}
        />
      </div>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
