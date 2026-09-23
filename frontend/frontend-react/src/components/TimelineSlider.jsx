import { useState } from 'react';

const TimelineSlider = () => {
    const [hours, setHours] = useState(0);

    return (
        <div className="h-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-6 rounded-xl shadow-sm flex items-center gap-6 transition-colors duration-300">
            <span className="text-sm font-semibold text-slate-600 dark:text-slate-300 whitespace-nowrap uppercase tracking-wider">Forecast Timeline:</span>
            <input 
                type="range" 
                min="0" 
                max="6" 
                value={hours} 
                onChange={(e) => setHours(e.target.value)}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer dark:bg-slate-700 accent-blue-500"
            />
            <span className="text-sm font-bold text-blue-600 dark:text-blue-400 w-16 text-right whitespace-nowrap">
                {hours == 0 ? "Live Now" : `+${hours} hrs`}
            </span>
        </div>
    );
};

export default TimelineSlider;
