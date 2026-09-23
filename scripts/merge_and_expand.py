"""
Merge existing 790 locations with 250+ additional locations to achieve 1000+ locations
with dense North-East, Himalayan, Coastal, and Central coverage across all 36 States & UTs.
"""
import os
import csv
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "india_locations.csv")

# 250+ new high-priority locations across North-East, Himalayan, Western, Peninsular regions
ADDITIONAL_LOCATIONS = [
    # --- NORTH-EAST EXPANSION ---
    # Assam
    ("Digboi", "Assam", 27.3800, 95.6200),
    ("Duliajan", "Assam", 27.3500, 95.3200),
    ("Margherita", "Assam", 27.2800, 95.6800),
    ("Sualkuchi", "Assam", 26.1700, 91.5700),
    ("Hajo", "Assam", 26.2500, 91.5300),
    ("Rangia", "Assam", 26.4700, 91.6300),
    ("Bokakhat", "Assam", 26.6300, 93.5800),
    ("Sarupathar", "Assam", 26.1800, 93.8200),
    ("Namrup", "Assam", 27.1800, 95.3500),
    ("Badarpur", "Assam", 24.9000, 92.5700),
    ("Lakhipur", "Assam", 24.8000, 93.0200),
    ("Moranhat", "Assam", 27.1800, 94.9300),
    ("Bokajan", "Assam", 26.0200, 93.7800),
    ("Abhayapuri", "Assam", 26.3300, 90.6700),
    ("Bilasipara", "Assam", 26.2300, 90.2300),
    ("Gauripur", "Assam", 26.0800, 89.9700),
    ("Mankachar", "Assam", 25.5300, 89.8700),
    ("Chapar", "Assam", 26.2700, 90.4700),
    ("Tangla", "Assam", 26.6500, 91.9200),
    ("Kharupetia", "Assam", 26.5200, 92.1300),
    ("Dergaon", "Assam", 26.7000, 93.9700),
    ("Titabor", "Assam", 26.6000, 94.2000),
    ("Mariani", "Assam", 26.6700, 94.3300),
    ("Nazira", "Assam", 26.9200, 94.7300),
    ("Sonari", "Assam", 27.0700, 95.0300),
    ("Amguri", "Assam", 26.8000, 94.5300),
    ("Bihpuria", "Assam", 27.0300, 93.9000),
    ("Narayanpur", "Assam", 26.9800, 93.8500),
    ("Gohpur", "Assam", 26.8800, 93.6300),
    ("Dhekiajuli", "Assam", 26.7000, 92.5000),

    # Arunachal Pradesh
    ("Hawai", "Arunachal Pradesh", 27.8800, 96.8000),
    ("Koloriang", "Arunachal Pradesh", 27.9000, 93.3500),
    ("Boleng", "Arunachal Pradesh", 28.3300, 94.9700),
    ("Lemmi", "Arunachal Pradesh", 27.2500, 93.1500),
    ("Likabali", "Arunachal Pradesh", 27.6500, 94.7000),
    ("Raga", "Arunachal Pradesh", 27.8000, 94.0500),
    ("Tato", "Arunachal Pradesh", 28.5300, 94.3700),
    ("Jamin", "Arunachal Pradesh", 27.7500, 93.4500),
    ("Dambuk", "Arunachal Pradesh", 28.2500, 95.5500),
    ("Namsing", "Arunachal Pradesh", 27.9500, 95.3800),
    ("Bhalukpong", "Arunachal Pradesh", 27.0100, 92.6500),
    ("Dirang", "Arunachal Pradesh", 27.3500, 92.2300),
    ("Rupa", "Arunachal Pradesh", 27.2000, 92.4000),
    ("Miao", "Arunachal Pradesh", 27.4800, 96.2000),
    ("Jairampur", "Arunachal Pradesh", 27.3500, 96.0500),
    ("Deomali", "Arunachal Pradesh", 27.1500, 95.4800),

    # Meghalaya
    ("Sohra", "Meghalaya", 25.3000, 91.7000),
    ("Mawsynram", "Meghalaya", 25.3000, 91.5800),
    ("Dawki", "Meghalaya", 25.1900, 92.0200),
    ("Mawlynnong", "Meghalaya", 25.2000, 91.9200),
    ("Byrnihat", "Meghalaya", 26.0500, 91.8800),
    ("Nongstoin", "Meghalaya", 25.5200, 91.2700),
    ("Ampati", "Meghalaya", 25.4700, 89.9300),
    ("Ranikor", "Meghalaya", 25.1800, 91.2300),
    ("Mawkyrwat", "Meghalaya", 25.3700, 91.4500),

    # Manipur
    ("Moirang", "Manipur", 24.5000, 93.7700),
    ("Mayang Imphal", "Manipur", 24.6200, 93.8800),
    ("Lilong", "Manipur", 24.7200, 93.9300),
    ("Wangoi", "Manipur", 24.6700, 93.9000),
    ("Yairipok", "Manipur", 24.6700, 94.0700),
    ("Sugnu", "Manipur", 24.2800, 93.8700),
    ("Nambol", "Manipur", 24.7200, 93.8300),
    ("Kangpokpi", "Manipur", 25.1500, 93.9700),
    ("Noney", "Manipur", 24.8200, 93.6000),
    ("Pherzawl", "Manipur", 24.2500, 93.1800),
    ("Kamjong", "Manipur", 24.9700, 94.4800),
    ("Tengnoupal", "Manipur", 24.3800, 94.1500),
    ("Moreh", "Manipur", 24.2500, 94.3000),

    # Nagaland
    ("Pfutsero", "Nagaland", 25.5700, 94.3200),
    ("Chumoukedima", "Nagaland", 25.8000, 93.7800),
    ("Tseminyu", "Nagaland", 25.9200, 94.2200),
    ("Shamator", "Nagaland", 26.0700, 94.9000),
    ("Noklak", "Nagaland", 26.2000, 95.0300),
    ("Medziphema", "Nagaland", 25.7500, 93.8500),
    ("Jalukie", "Nagaland", 25.5700, 93.7200),
    ("Changtongya", "Nagaland", 26.5300, 94.6800),
    ("Tizit", "Nagaland", 26.9000, 95.0700),
    ("Naganimora", "Nagaland", 26.7800, 94.8200),

    # Mizoram
    ("Vairengte", "Mizoram", 24.5000, 92.7700),
    ("Bilkhawthlir", "Mizoram", 24.3300, 92.7300),
    ("Zawlnuam", "Mizoram", 24.1300, 92.3500),
    ("Bairabi", "Mizoram", 24.1800, 92.5300),
    ("Darlawn", "Mizoram", 24.0200, 92.9300),
    ("Thenzawl", "Mizoram", 23.3200, 92.7500),
    ("Khawhai", "Mizoram", 23.3700, 93.1800),
    ("North Vanlaiphai", "Mizoram", 23.1300, 93.0700),
    ("Hnahthial", "Mizoram", 22.9700, 92.9300),
    ("Khawzawl", "Mizoram", 23.5300, 93.1800),
    ("Saitual", "Mizoram", 23.9700, 92.5800),

    # Tripura
    ("Sonamura", "Tripura", 23.4700, 91.2700),
    ("Bishalgarh", "Tripura", 23.6800, 91.2700),
    ("Ranirbazar", "Tripura", 23.8300, 91.3700),
    ("Santirbazar", "Tripura", 23.3000, 91.5700),
    ("Sabroom", "Tripura", 23.0000, 91.7000),
    ("Kamalpur", "Tripura", 24.2000, 91.8300),
    ("Kumarghat", "Tripura", 24.1700, 92.0300),
    ("Melaghar", "Tripura", 23.4800, 91.3300),
    ("Amarpur", "Tripura", 23.5300, 91.6500),

    # Sikkim
    ("Singtam", "Sikkim", 27.2300, 88.5000),
    ("Rangpo", "Sikkim", 27.1700, 88.5300),
    ("Rhenock", "Sikkim", 27.1800, 88.6300),
    ("Ravangla", "Sikkim", 27.3000, 88.3700),
    ("Jorethang", "Sikkim", 27.1300, 88.3200),
    ("Yuksom", "Sikkim", 27.3700, 88.2200),
    ("Chungthang", "Sikkim", 27.6000, 88.6500),
    ("Lachen", "Sikkim", 27.7200, 88.5500),
    ("Lachung", "Sikkim", 27.6800, 88.7500),

    # --- HIMALAYAN & NORTHERN REGION EXPANSION ---
    # Ladakh
    ("Dras", "Ladakh", 34.4300, 75.7500),
    ("Diskit", "Ladakh", 34.5700, 77.5500),
    ("Hunder", "Ladakh", 34.5800, 77.4700),
    ("Nyoma", "Ladakh", 33.2000, 78.6700),
    ("Padum", "Ladakh", 33.4700, 76.8800),
    ("Turtuk", "Ladakh", 34.8500, 76.8300),

    # Jammu and Kashmir
    ("Gulmarg", "Jammu and Kashmir", 34.0500, 74.3800),
    ("Pahalgam", "Jammu and Kashmir", 34.0200, 75.3300),
    ("Sonamarg", "Jammu and Kashmir", 34.3000, 75.3000),
    ("Katra", "Jammu and Kashmir", 32.9900, 74.9300),
    ("Bhadarwah", "Jammu and Kashmir", 32.9800, 75.7200),
    ("Akhnoor", "Jammu and Kashmir", 32.8700, 74.7300),
    ("RS Pura", "Jammu and Kashmir", 32.6300, 74.7300),
    ("Uri", "Jammu and Kashmir", 34.0800, 74.0300),
    ("Tangmarg", "Jammu and Kashmir", 34.0700, 74.4300),
    ("Tral", "Jammu and Kashmir", 33.9300, 75.1200),
    ("Pampore", "Jammu and Kashmir", 34.0200, 74.9300),
    ("Qazigund", "Jammu and Kashmir", 33.5800, 75.1700),
    ("Banihal", "Jammu and Kashmir", 33.4300, 75.2000),
    ("Batote", "Jammu and Kashmir", 33.1700, 75.3200),

    # Himachal Pradesh
    ("Manali", "Himachal Pradesh", 32.2396, 77.1887),
    ("Kaza", "Himachal Pradesh", 32.2300, 78.0700),
    ("Tabo", "Himachal Pradesh", 32.1000, 78.3800),
    ("Kalpa", "Himachal Pradesh", 31.5300, 78.2500),
    ("Sangla", "Himachal Pradesh", 31.4200, 78.2700),
    ("Kasol", "Himachal Pradesh", 32.0100, 77.3200),
    ("Palampur", "Himachal Pradesh", 32.1200, 76.5300),
    ("Jogindernagar", "Himachal Pradesh", 31.9800, 76.7700),
    ("Rampur Bushahr", "Himachal Pradesh", 31.4500, 77.6300),
    ("Nalagarh", "Himachal Pradesh", 31.0500, 76.7200),
    ("Parwanoo", "Himachal Pradesh", 30.8300, 76.9500),
    ("Dalhousie", "Himachal Pradesh", 32.5300, 75.9800),
    ("Nurpur", "Himachal Pradesh", 32.3000, 75.8800),

    # Uttarakhand
    ("Joshimath", "Uttarakhand", 30.5500, 79.5700),
    ("Badrinath", "Uttarakhand", 30.7400, 79.4900),
    ("Kedarnath", "Uttarakhand", 30.7300, 79.0700),
    ("Gangotri", "Uttarakhand", 30.9800, 78.9300),
    ("Yamunotri", "Uttarakhand", 31.0200, 78.4500),
    ("Auli", "Uttarakhand", 30.5300, 79.5700),
    ("Lansdowne", "Uttarakhand", 29.8300, 78.6800),
    ("Ranikhet", "Uttarakhand", 29.6400, 79.4200),
    ("Kausani", "Uttarakhand", 29.8500, 79.6000),
    ("Mukteshwar", "Uttarakhand", 29.4700, 79.6500),
    ("Bhimtal", "Uttarakhand", 29.3500, 79.5500),
    ("Ramnagar", "Uttarakhand", 29.4000, 79.1200),
    ("Tanakpur", "Uttarakhand", 29.0700, 80.1200),
    ("Dharchula", "Uttarakhand", 29.8500, 80.5300),
    ("Didihat", "Uttarakhand", 29.8000, 80.2500),

    # --- PENINSULAR & SOUTHERN EXPANSION ---
    # Karnataka
    ("Gokarna", "Karnataka", 14.5500, 74.3200),
    ("Murudeshwar", "Karnataka", 14.1000, 74.4800),
    ("Dandeli", "Karnataka", 15.2300, 74.6200),
    ("Sirsi", "Karnataka", 14.6200, 74.8500),
    ("Bhatkal", "Karnataka", 13.9800, 74.5500),
    ("Kumta", "Karnataka", 14.4200, 74.4200),
    ("Sringeri", "Karnataka", 13.4200, 75.2500),
    ("Kudremukh", "Karnataka", 13.2200, 75.2500),
    ("Hampi", "Karnataka", 15.3350, 76.4600),
    ("Badami", "Karnataka", 15.9200, 75.6800),
    ("Pattadakal", "Karnataka", 15.9500, 75.8200),
    ("Belur", "Karnataka", 13.1600, 75.8600),
    ("Halebidu", "Karnataka", 13.2200, 75.9800),
    ("Shravanabelagola", "Karnataka", 12.8500, 76.4800),
    ("Nanjangud", "Karnataka", 12.1200, 76.6800),
    ("Srirangapatna", "Karnataka", 12.4200, 76.7000),
    ("Kundapura", "Karnataka", 13.6200, 74.6800),
    ("Karkala", "Karnataka", 13.2200, 74.9800),
    ("Puttur", "Karnataka", 12.7700, 75.2000),
    ("Sullia", "Karnataka", 12.5700, 75.3800),

    # Kerala
    ("Munnar", "Kerala", 10.0889, 77.0595),
    ("Thekkady", "Kerala", 9.6000, 77.1700),
    ("Varkala", "Kerala", 8.7300, 76.7100),
    ("Kovalam", "Kerala", 8.4000, 76.9800),
    ("Kumarakom", "Kerala", 9.6200, 76.4300),
    ("Bekal", "Kerala", 12.4000, 75.0300),
    ("Guruvayur", "Kerala", 10.6000, 76.0300),
    ("Sabarimala", "Kerala", 9.4300, 77.0800),
    ("Vagamon", "Kerala", 9.6800, 76.9000),
    ("Athirappilly", "Kerala", 10.3200, 76.5700),
    ("Sultan Bathery", "Kerala", 11.6700, 76.2500),
    ("Mananthavady", "Kerala", 11.8000, 76.0000),
    ("Changanassery", "Kerala", 9.4500, 76.5300),
    ("Kattappana", "Kerala", 9.7700, 77.1200),
    ("Cherthala", "Kerala", 9.6800, 76.3300),

    # Tamil Nadu
    ("Rameswaram", "Tamil Nadu", 9.2876, 79.3129),
    ("Dhanushkodi", "Tamil Nadu", 9.1800, 79.4200),
    ("Kodaikanal", "Tamil Nadu", 10.2381, 77.4892),
    ("Yercaud", "Tamil Nadu", 11.7800, 78.2000),
    ("Mamallapuram", "Tamil Nadu", 12.6200, 80.1900),
    ("Chidambaram", "Tamil Nadu", 11.4000, 79.7000),
    ("Velankanni", "Tamil Nadu", 10.6800, 79.8500),
    ("Courtallam", "Tamil Nadu", 8.9300, 77.2700),
    ("Valparai", "Tamil Nadu", 10.3200, 76.9500),
    ("Coonoor", "Tamil Nadu", 11.3500, 76.8000),
    ("Kotagiri", "Tamil Nadu", 11.4200, 76.8700),
    ("Pollachi", "Tamil Nadu", 10.6600, 77.0100),
    ("Mettupalayam", "Tamil Nadu", 11.3000, 76.9500),
    ("Tiruchendur", "Tamil Nadu", 8.5000, 78.1200),
    ("Palani", "Tamil Nadu", 10.4500, 77.5200),

    # Andhra Pradesh & Telangana
    ("Araku Valley", "Andhra Pradesh", 18.3300, 82.8800),
    ("Horsley Hills", "Andhra Pradesh", 13.6500, 78.4000),
    ("Srisailam", "Andhra Pradesh", 16.0700, 78.8700),
    ("Lepakshi", "Andhra Pradesh", 13.8000, 77.6000),
    ("Puttaparthi", "Andhra Pradesh", 14.1700, 77.8100),
    ("Mangalagiri", "Andhra Pradesh", 16.4300, 80.5700),
    ("Amaravati", "Andhra Pradesh", 16.5100, 80.5200),
    ("Bhadrachalam", "Telangana", 17.6700, 80.8800),
    ("Yadagirigutta", "Telangana", 17.5800, 78.9300),
    ("Alampur", "Telangana", 15.8800, 78.1300),
    ("Vemulawada", "Telangana", 18.4700, 78.8700),
    ("Basar", "Telangana", 18.9800, 77.9500),

    # --- WESTERN & CENTRAL EXPANSION ---
    # Rajasthan
    ("Pokhran", "Rajasthan", 26.9200, 71.9200),
    ("Phalodi", "Rajasthan", 27.1300, 72.3700),
    ("Osian", "Rajasthan", 26.7300, 72.9000),
    ("Bilara", "Rajasthan", 26.1800, 73.7000),
    ("Sojat", "Rajasthan", 26.0000, 73.6700),
    ("Sumerpur", "Rajasthan", 25.1500, 73.0800),
    ("Abu Road", "Rajasthan", 24.4800, 72.7800),
    ("Sanchore", "Rajasthan", 24.7500, 71.7700),
    ("Bhinmal", "Rajasthan", 25.0000, 72.2500),
    ("Balotra", "Rajasthan", 25.8300, 72.2300),
    ("Rawatbhata", "Rajasthan", 24.9300, 75.5800),
    ("Nathdwara", "Rajasthan", 24.9300, 73.8200),
    ("Kankroli", "Rajasthan", 25.0500, 73.8800),
    ("Chomu", "Rajasthan", 27.1700, 75.7200),

    # Gujarat
    ("Mandvi", "Gujarat", 22.8300, 69.3500),
    ("Mundra", "Gujarat", 22.8400, 69.7300),
    ("Anjar", "Gujarat", 23.1100, 70.0300),
    ("Gandhidham", "Gujarat", 23.0800, 70.1300),
    ("Dwarka", "Gujarat", 22.2400, 68.9700),
    ("Khambhalia", "Gujarat", 22.2000, 69.6500),
    ("Keshod", "Gujarat", 21.3000, 70.2500),
    ("Mangrol", "Gujarat", 21.1200, 70.1200),
    ("Talala", "Gujarat", 21.0500, 70.5300),
    ("Kodinar", "Gujarat", 20.7900, 70.7000),
    ("Una", "Gujarat", 20.8200, 71.0400),
    ("Palitana", "Gujarat", 21.5200, 71.8300),
    ("Sanand", "Gujarat", 22.9800, 72.3800),
    ("Dholka", "Gujarat", 22.7200, 72.4400),
    ("Dhrangadhra", "Gujarat", 22.9900, 71.4700),
    ("Halvad", "Gujarat", 23.0100, 71.1800),
    ("Wankaner", "Gujarat", 22.6200, 70.9700),
    ("Chotila", "Gujarat", 22.4200, 71.1900),

    # Maharashtra
    ("Lonavala", "Maharashtra", 18.7500, 73.4100),
    ("Khandala", "Maharashtra", 18.7600, 73.3700),
    ("Mahabaleshwar", "Maharashtra", 17.9200, 73.6600),
    ("Panchgani", "Maharashtra", 17.9200, 73.8000),
    ("Alibag", "Maharashtra", 18.6600, 72.8700),
    ("Shirdi", "Maharashtra", 19.7700, 74.4800),
    ("Igatpuri", "Maharashtra", 19.7000, 73.5500),
    ("Trimbak", "Maharashtra", 19.9300, 73.5300),
    ("Baramati", "Maharashtra", 18.1500, 74.5800),
    ("Karad", "Maharashtra", 17.2800, 74.2000),
    ("Sangamner", "Maharashtra", 19.5700, 74.2200),
    ("Shrirampur", "Maharashtra", 19.6200, 74.6500),
    ("Chiplun", "Maharashtra", 17.5300, 73.5200),
    ("Dapoli", "Maharashtra", 17.7500, 73.1800),
    ("Sawantwadi", "Maharashtra", 15.9000, 73.8200),
    ("Malvan", "Maharashtra", 16.0600, 73.4700),

    # Madhya Pradesh & Chhattisgarh
    ("Khajuraho", "Madhya Pradesh", 24.8500, 79.9300),
    ("Orchha", "Madhya Pradesh", 25.3500, 78.6400),
    ("Pachmarhi", "Madhya Pradesh", 22.4700, 78.4300),
    ("Mandu", "Madhya Pradesh", 22.3700, 75.4000),
    ("Sanchi", "Madhya Pradesh", 23.4800, 77.7400),
    ("Maheshwar", "Madhya Pradesh", 22.1800, 75.5800),
    ("Omkareshwar", "Madhya Pradesh", 22.2500, 76.1500),
    ("Amarkantak", "Madhya Pradesh", 22.6700, 81.7600),
    ("Mainpat", "Chhattisgarh", 22.8200, 83.2800),
    ("Chitrakote", "Chhattisgarh", 19.2000, 81.7000),
    ("Ratanpur", "Chhattisgarh", 22.3000, 82.1700),
    ("Sirpur", "Chhattisgarh", 21.3400, 82.1800),

    # --- EASTERN EXPANSION ---
    # Bihar & Jharkhand
    ("Nalanda", "Bihar", 25.1300, 85.4500),
    ("Rajgir", "Bihar", 25.0300, 85.4200),
    ("Bodh Gaya", "Bihar", 24.7000, 84.9900),
    ("Pawapuri", "Bihar", 25.0800, 85.5200),
    ("Netarhat", "Jharkhand", 23.4800, 84.2700),
    ("Parasnath", "Jharkhand", 23.9600, 86.1300),
    ("Patratu", "Jharkhand", 23.6700, 85.3000),
    ("Rajrappa", "Jharkhand", 23.6300, 85.7000),

    # West Bengal & Odisha
    ("Shantiniketan", "West Bengal", 23.6800, 87.6900),
    ("Digha", "West Bengal", 21.6300, 87.5200),
    ("Mandarmani", "West Bengal", 21.6700, 87.7000),
    ("Bishnupur", "West Bengal", 23.0700, 87.3200),
    ("Murshidabad", "West Bengal", 24.1800, 88.2700),
    ("Mayapur", "West Bengal", 23.4300, 88.3900),
    ("Mirik", "West Bengal", 26.8900, 88.1800),
    ("Kurseong", "West Bengal", 26.8800, 88.2800),
    ("Lava", "West Bengal", 27.0800, 88.6600),
    ("Konark", "Odisha", 19.8900, 86.1000),
    ("Chilika", "Odisha", 19.7000, 85.3200),
    ("Gopalpur", "Odisha", 19.2600, 84.9100),
    ("Chandipur", "Odisha", 21.4700, 87.0200),
]

def main():
    df_existing = pd.read_csv(CSV_PATH)
    seen = set()
    combined_rows = []
    
    for _, row in df_existing.iterrows():
        c = str(row["city"]).strip()
        s = str(row["state"]).strip()
        lat = float(row["lat"])
        lon = float(row["lon"])
        key = (c.lower(), s.lower())
        if key not in seen:
            seen.add(key)
            combined_rows.append((c, s, round(lat, 4), round(lon, 4)))
            
    for c, s, lat, lon in ADDITIONAL_LOCATIONS:
        key = (c.strip().lower(), s.strip().lower())
        if key not in seen:
            seen.add(key)
            assert 6.0 <= lat <= 38.0
            assert 68.0 <= lon <= 98.0
            combined_rows.append((c.strip(), s.strip(), round(lat, 4), round(lon, 4)))
            
    # Write back to CSV
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["city", "state", "lat", "lon"])
        for r in combined_rows:
            writer.writerow(r)
            
    print(f"Total locations written to {CSV_PATH}: {len(combined_rows)}")
    states = set(r[1] for r in combined_rows)
    print(f"Total States & UTs represented: {len(states)}")

if __name__ == "__main__":
    main()
