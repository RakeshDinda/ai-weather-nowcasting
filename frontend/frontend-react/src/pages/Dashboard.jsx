import React, { useState, useEffect, useRef } from 'react';
import Sidebar from '../components/Sidebar';
import TopHeader from '../components/TopHeader';
import HeroBanner from '../components/HeroBanner';
import AlertBanner from '../components/AlertBanner';
import MapSection from '../components/MapSection';
import RightPanel from '../components/RightPanel';
import Timeline from '../components/Timeline';
import RiskDistribution from '../components/RiskDistribution';

const Dashboard = () => {
    // 1. Single Source of Truth States
    const [allCities, setAllCities] = useState([]);
    const [selectedCity, setSelectedCity] = useState(null);
    const [loading, setLoading] = useState(true);
    const [searchLoading, setSearchLoading] = useState(false);
    const [error, setError] = useState(null);
    const [activeLayers, setActiveLayers] = useState({
        thunderstorm: true,
        cloudburst: true,
        flood: true
    });

    const isFetchingRef = useRef(false);

    const loadAllData = async () => {
        // Prevent overlapping/duplicate concurrent API calls
        if (isFetchingRef.current) return;
        isFetchingRef.current = true;

        setLoading(true);
        setError(null);
        try {
            const response = await fetch("http://127.0.0.1:8000/batch_predict?limit=100");
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            console.log("BATCH API RESPONSE:", data);

            const formatted = data.map((item, index) => ({
                id: index,
                city: item.city,
                fullName: item.city,
                state: item.state,
                lat: item.lat,
                lon: item.lon,
                risk: (item.risk_level || item.risk || "LOW").toUpperCase(),
                risk_level: (item.risk_level || item.risk || "LOW").toUpperCase(),
                weather: item.weather || {
                    temperature: item.temperature,
                    humidity: item.humidity,
                    rainfall: item.rainfall,
                    wind_speed: item.wind_speed,
                },
                probabilities: item.probabilities || null,
                prediction: item.prediction || null,
                reason: item.reason || item.prediction?.reason || null,
                timestamp: item.timestamp || null
            }));

            console.log("Loaded cities:", formatted.length);
            setAllCities(formatted);

            // Maintain user selection across background refreshes
            setSelectedCity(prev => {
                if (prev) {
                    const match = formatted.find(c => 
                        (c.city && prev.city && c.city.toLowerCase() === prev.city.toLowerCase()) ||
                        (c.fullName && prev.fullName && c.fullName.toLowerCase() === prev.fullName.toLowerCase())
                    );
                    return match || prev;
                }
                const savedCity = localStorage.getItem('selected_city');
                if (savedCity) {
                    const match = formatted.find(c => c.city && c.city.toLowerCase() === savedCity.toLowerCase());
                    if (match) return match;
                }
                if (formatted.length > 0) return formatted[0];
                return null;
            });
        } catch (err) {
            setError(err.message || "Failed to load India locations dataset.");
        } finally {
            setLoading(false);
            isFetchingRef.current = false;
        }
    };

    useEffect(() => {
        console.log("useEffect triggered");
        loadAllData();

        // Real-Time 5-Minute Auto-Refresh Interval (300,000 ms)
        const interval = setInterval(() => {
            console.log("Auto refresh triggered");
            loadAllData();
        }, 300000); // 5 minutes

        return () => {
            clearInterval(interval);
        };
    }, []);

    // Sync selected city to localStorage so Forecast and other pages share the active city seamlessly
    useEffect(() => {
        if (selectedCity?.city) {
            try {
                localStorage.setItem('selected_city', selectedCity.city);
            } catch (e) {
                // Ignore storage errors if disabled
            }
        }
    }, [selectedCity]);

    // 3. SEARCH HANDLING
    const handleSearch = async (cityName) => {
        const trimmed = cityName?.trim();
        if (!trimmed) {
            setError("Please enter a valid city name.");
            return;
        }

        setSearchLoading(true);
        setError(null);
        try {
            // Fetch coordinates (Nominatim)
            const geoRes = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(trimmed)}&format=json&limit=1`);
            const geoData = await geoRes.json();
            
            if (!geoData || geoData.length === 0) {
                throw new Error("Location not found.");
            }

            const location = geoData[0];
            const lat = parseFloat(location.lat);
            const lon = parseFloat(location.lon);

            if (isNaN(lat) || isNaN(lon)) {
                throw new Error("Invalid coordinates received for location.");
            }

            const display_name = location.display_name;
            const shortName = display_name.split(",")[0].trim();

            // Call backend: POST http://127.0.0.1:8000/predict
            let data = {};
            try {
                const response = await fetch("http://127.0.0.1:8000/predict", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        lat,
                        lon,
                        location: cityName
                    })
                });
                
                if (response.ok) {
                    data = await response.json();
                } else {
                    console.warn("Backend /predict returned non-OK status:", response.status);
                }
            } catch (apiErr) {
                console.error("Backend /predict call failed:", apiErr);
            }

            console.log("Search API response:", data);

            const risk = (data.risk || data.risk_level || "LOW").toUpperCase();

            const newLocation = {
                id: Date.now(),
                city: shortName,
                fullName: display_name,
                lat,
                lon,
                risk,
                weather: data.weather || null,
                prediction: data.prediction || null,
                reason: data.reason || data.prediction?.reason || null,
                timestamp: data.timestamp || null
            };

            console.log("Final Location Object:", newLocation);
            
            let resolvedCity = newLocation;
            setAllCities(prev => {
                const existingIndex = prev.findIndex(
                    c => (c.city && c.city.toLowerCase() === shortName.toLowerCase()) ||
                         (c.fullName && c.fullName.toLowerCase() === display_name.toLowerCase()) ||
                         (Math.abs(c.lat - lat) < 0.05 && Math.abs(c.lon - lon) < 0.05)
                );

                if (existingIndex !== -1) {
                    const updated = [...prev];
                    const existingItem = updated[existingIndex];
                    resolvedCity = {
                        ...existingItem,
                        ...newLocation,
                        id: existingItem.id
                    };
                    updated[existingIndex] = resolvedCity;
                    return updated;
                } else {
                    resolvedCity = newLocation;
                    return [newLocation, ...prev];
                }
            });

            setSelectedCity(resolvedCity);
        } catch (err) {
            setError(err.message || `City '${trimmed}' could not be retrieved. Please check city name.`);
        } finally {
            setSearchLoading(false);
        }
    };

    // Marker Click / Select Handler
    const handleSelectCity = (location) => {
        if (!location) return;
        setSelectedCity(location);
    };

    const handleRegionSelect = (region) => {
        if (region === "India") {
            loadAllData();
        } else {
            handleSearch(region);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-slate-50 dark:bg-[#0f172a] text-slate-900 dark:text-slate-100 font-sans overflow-hidden transition-colors duration-300">
            {/* Top Navigation Bar */}
            <TopHeader 
                onSearch={handleSearch} 
                searchLoading={searchLoading} 
                selectedCity={selectedCity?.city} 
            />
            
            <div className="flex flex-1 overflow-hidden">
                {/* Left Sidebar with Toggles & Monitor India */}
                <Sidebar 
                    activeLayers={activeLayers} 
                    setActiveLayers={setActiveLayers} 
                    onMonitorIndia={loadAllData} 
                    onRegionSelect={handleRegionSelect}
                    loading={loading}
                />
                
                <div className="flex-1 flex flex-col overflow-hidden relative">
                    {/* Scrollable Content Area */}
                    <div className="flex-1 overflow-y-auto pb-4 flex flex-col">
                        
                        {/* Error Handling Banner */}
                        {error && (
                            <div className="bg-red-600 text-white px-6 py-3 font-semibold text-sm shadow-md flex justify-between items-center z-50 shrink-0 animate-in fade-in duration-200">
                                <div className="flex items-center gap-2">
                                    <span className="text-base">⚠️</span>
                                    <span>{error}</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <button 
                                        onClick={() => { setError(null); loadAllData(); }} 
                                        className="bg-red-700 hover:bg-red-800 rounded px-2.5 py-1 text-xs font-bold transition-colors"
                                    >
                                        Retry
                                    </button>
                                    <button 
                                        onClick={() => setError(null)} 
                                        className="hover:bg-red-700 rounded px-2 py-1 text-xs font-bold transition-colors"
                                    >
                                        Dismiss
                                    </button>
                                </div>
                            </div>
                        )}
                        
                        {/* Top Hero Banner */}
                        <HeroBanner cityData={selectedCity} />
                        
                        {/* Alert Banner: Pure component using central locations */}
                        <div className="px-6 pt-4">
                            <AlertBanner locations={allCities} />
                        </div>
                        
                        {/* Interactive Main Map & Right Panel */}
                        <div className="flex-1 flex px-6 py-4 gap-6 min-h-[500px]">
                            {/* Map Container */}
                            <div className="flex-1 relative rounded-2xl overflow-hidden shadow-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col">
                                {/* Map Controls Header */}
                                <div className="absolute top-4 left-4 z-[400] flex gap-2">
                                    <div className="bg-white/90 dark:bg-slate-800/90 backdrop-blur shadow-sm rounded-lg p-1 flex border border-slate-200 dark:border-slate-700">
                                        <button className="px-4 py-1.5 bg-blue-600 text-white rounded-md text-sm font-medium shadow-sm">Map</button>
                                        <button className="px-4 py-1.5 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-md text-sm font-medium transition-colors">Satellite</button>
                                        <button className="px-4 py-1.5 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-md text-sm font-medium transition-colors">Terrain</button>
                                    </div>
                                </div>
                                
                                <div className="absolute top-4 right-4 z-[400]">
                                    <div className="bg-white/90 dark:bg-slate-800/90 backdrop-blur shadow-sm rounded-lg px-4 py-2 border border-slate-200 dark:border-slate-700 flex items-center gap-2">
                                        <span className={`w-2.5 h-2.5 rounded-full ${loading ? "bg-blue-500 animate-spin" : "bg-emerald-500 animate-pulse"}`}></span>
                                        <span className="text-sm font-bold text-slate-800 dark:text-slate-100">
                                            {loading && allCities.length > 0 ? "Updating Feeds..." : "Live AI Nowcasting"}
                                        </span>
                                    </div>
                                </div>
                                
                                {loading && allCities.length === 0 ? (
                                    <div className="flex-1 flex flex-col items-center justify-center bg-slate-100 dark:bg-slate-900 z-50">
                                        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                                        <div className="mt-4 text-slate-600 dark:text-slate-300 font-bold">Loading map data...</div>
                                    </div>
                                ) : (
                                    <MapSection 
                                        key={allCities.length}
                                        allCities={allCities}
                                        selectedCity={selectedCity} 
                                        onSelectCity={handleSelectCity} 
                                        activeLayers={activeLayers}
                                    />
                                )}
                                
                                {/* Rain Intensity Legend */}
                                <div className="absolute bottom-6 left-6 z-[400] bg-white/90 dark:bg-slate-800/90 backdrop-blur-md rounded-xl p-4 shadow-lg border border-slate-200 dark:border-slate-700 w-64">
                                    <p className="text-xs font-bold mb-2 uppercase text-slate-500 dark:text-slate-400">Risk Severity</p>
                                    <div className="h-3 w-full rounded-full bg-gradient-to-r from-emerald-400 via-amber-400 to-red-600 mb-1"></div>
                                    <div className="flex justify-between text-[10px] font-semibold text-slate-600 dark:text-slate-400">
                                        <span>Low (&lt;40%)</span>
                                        <span>Moderate</span>
                                        <span>High (&ge;70%)</span>
                                    </div>
                                </div>
                            </div>
                            
                            {/* Right Panel: Pure component using central selectedCity */}
                            <div className="w-[360px] flex-shrink-0">
                                <RightPanel 
                                    selectedCity={selectedCity} 
                                    onClose={() => setSelectedCity(null)}
                                />
                            </div>
                        </div>
                        
                        {/* Timeline and Risk Distribution */}
                        <div className="h-28 px-6 pb-2 flex gap-6 shrink-0">
                            <div className="flex-1">
                                <Timeline />
                            </div>
                            <div className="w-[360px] flex-shrink-0">
                                <RiskDistribution locations={allCities} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
