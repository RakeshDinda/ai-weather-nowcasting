from utils.v2_predictor import compute_hybrid_risk

cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Guwahati', 'Jaipur', 'Lucknow', 'Patna', 'Bhopal']
states = ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal', 'Assam', 'Rajasthan', 'Uttar Pradesh', 'Bihar', 'Madhya Pradesh']

ml_confs = [0.9, 0.9, 0.75, 0.8, 0.9, 0.6, 0.1, 0.2, 0.5, 0.3]
rains =    [0.0, 3.0, 12.0, 0.0, 4.0, 0.0, 6.0, 0.5, 0.0, 20.0]
humids =   [70,  85,  85,   70,  75,  70,  65,  55,  60,  80]
temps =    [30,  32,  32,   30,  31,  30,  35,  28,  30,  30]

print(f"{'City':<12} | {'Rain':<6} | {'Conf':<4} | {'Hum':<3} | {'Tmp':<3} | {'Risk':<8} | {'Probabilities'}")
print("-" * 95)
for c, s, conf, r, h, t in zip(cities, states, ml_confs, rains, humids, temps):
    res = compute_hybrid_risk(r, {'city': c, 'state': s, 'confidence': conf}, humidity=h, temperature=t, state=s, city=c)
    print(f"{c:<12} | {f'{r}':<6} | {conf:<4} | {h:<3} | {t:<3} | {res['risk_text']:<8} | {res['probabilities']}")
