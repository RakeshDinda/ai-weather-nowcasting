import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

const AlertBanner = ({ locations = [] }) => {
    const highRiskLocations = locations.filter(
        loc => loc.risk === "HIGH" || loc.prediction?.risk_label === 2 || loc.prediction?.risk_text === "HIGH"
    );
    const modRiskLocations = locations.filter(
        loc => loc.risk === "MODERATE" || loc.prediction?.risk_label === 1 || loc.prediction?.risk_text === "MODERATE"
    );

    // Exact required logic:
    // IF any location has risk_label === 2:
    //    show "High Risk in X locations"
    // ELSE IF any location has risk_label === 1:
    //    show "Moderate Risk present"
    // ELSE:
    //    show "All Clear"
    if (highRiskLocations.length > 0) {
        return (
            <div className="w-full bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-900/50 rounded-xl p-3.5 flex items-center justify-between shadow-sm transition-all duration-300">
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 text-red-600 dark:text-red-400 font-black text-sm">
                        <AlertTriangle size={18} className="fill-red-100 dark:fill-transparent" />
                        <span>High Risk in {highRiskLocations.length} locations</span>
                    </div>
                </div>
                <span className="text-[11px] font-black uppercase tracking-wider text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-950/60 px-2.5 py-1 rounded-md border border-red-200 dark:border-red-800">
                    High Alert
                </span>
            </div>
        );
    }

    if (modRiskLocations.length > 0) {
        return (
            <div className="w-full bg-orange-50 dark:bg-orange-950/20 border border-orange-200 dark:border-orange-900/50 rounded-xl p-3.5 flex items-center justify-between shadow-sm transition-all duration-300">
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 text-orange-600 dark:text-orange-400 font-black text-sm">
                        <AlertTriangle size={18} className="fill-orange-100 dark:fill-transparent" />
                        <span>Moderate Risk present</span>
                    </div>
                </div>
                <span className="text-[11px] font-black uppercase tracking-wider text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-950/60 px-2.5 py-1 rounded-md border border-orange-200 dark:border-orange-800">
                    Advisory
                </span>
            </div>
        );
    }

    return (
        <div className="w-full bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/50 rounded-xl p-3.5 flex items-center justify-between shadow-sm transition-all duration-300">
            <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-black text-sm">
                    <ShieldCheck size={18} />
                    <span>All Clear</span>
                </div>
            </div>
            <span className="text-[11px] font-black uppercase tracking-wider text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-950/60 px-2.5 py-1 rounded-md border border-emerald-200 dark:border-emerald-800">
                Safe
            </span>
        </div>
    );
};

export default AlertBanner;
