// Skeleton loader component for device cards
export function DeviceCardSkeleton() {
  return (
    <div className="rounded-lg shadow-md p-6 bg-card border border-border-secondary animate-pulse">
      <div className="flex flex-col items-center space-y-4">
        {/* Device Name Skeleton */}
        <div className="h-6 bg-text-muted rounded w-32"></div>
        
        {/* Device Type Badge Skeleton */}
        <div className="h-5 bg-text-muted rounded-full w-16"></div>
        
        {/* Status Indicator Skeleton */}
        <div className="flex items-center space-x-2">
          <div className="h-3 w-3 bg-text-muted rounded-full"></div>
          <div className="h-4 bg-text-muted rounded w-14"></div>
        </div>
        
        {/* Button Skeleton */}
        <div className="w-full h-10 bg-text-muted rounded-md"></div>
        
        {/* Device ID Skeleton */}
        <div className="h-3 bg-text-muted rounded w-20"></div>
      </div>
    </div>
  );
}

// Loading grid for multiple skeleton cards
export function DeviceGridSkeleton({ count = 6 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {Array.from({ length: count }, (_, i) => (
        <DeviceCardSkeleton key={i} />
      ))}
    </div>
  );
}

// Error state component
export function ErrorMessage({ message, onRetry }) {
  return (
    <div className="text-center py-12">
      <div className="max-w-md mx-auto">
        <div className="mb-4">
          <div className="mx-auto w-16 h-16 bg-danger rounded-full flex items-center justify-center">
            <span className="text-2xl text-white">⚠️</span>
          </div>
        </div>
        <h3 className="text-lg font-semibold text-text mb-2">
          Connection Error
        </h3>
        <p className="text-text-secondary mb-6">
          {message || "Unable to connect to the hub. Please check if the backend is running."}
        </p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="px-6 py-2 bg-primary text-white rounded-md hover:opacity-80 transition-opacity"
          >
            Try Again
          </button>
        )}
      </div>
    </div>
  );
}

// Empty state component
export function EmptyState({ title, description, action }) {
  return (
    <div className="text-center py-16">
      <div className="max-w-md mx-auto">
        <div className="mb-4">
          <div className="mx-auto w-16 h-16 bg-text-muted rounded-full flex items-center justify-center">
            <span className="text-2xl text-white">📱</span>
          </div>
        </div>
        <h3 className="text-lg font-semibold text-text mb-2">
          {title || "No Devices Found"}
        </h3>
        <p className="text-text-secondary mb-6">
          {description || "No smart devices are currently connected to your hub."}
        </p>
        {action && (
          <div>
            {action}
          </div>
        )}
      </div>
    </div>
  );
}
