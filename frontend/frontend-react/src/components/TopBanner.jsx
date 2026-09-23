import { AlertTriangle } from 'lucide-react';

const TopBanner = ({ activeAlerts = 0 }) => {
  if (activeAlerts === 0) return null;

  return (
    <div className="bg-gradient-to-r from-red-600 to-red-500 text-white px-4 py-2.5 flex items-center justify-center gap-3 shadow-md animate-[pulse_2s_ease-in-out_infinite] z-50">
      <AlertTriangle size={20} className="animate-bounce" />
      <span className="text-sm font-bold tracking-widest uppercase">
        {activeAlerts} High-Risk Alert{activeAlerts > 1 ? 's' : ''} Active Across Monitored Regions!
      </span>
    </div>
  );
};

export default TopBanner;
