import os
import sys
import pandas as pd
import numpy as np

def extract_winery_from_title(title):
    words = str(title).split()
    if len(words) > 0:
        if words[0].lower() in ['finca', 'bodega', 'casa', 'viña', 'viñas'] and len(words) > 1:
            return " ".join(words[:2])
        return words[0]
    return "Bodega Desconocida"

def extract_vintage_from_title(title):
    import re
    match = re.search(r'\b(20\d{2})\b', str(title))
    if match:
        return int(match.group(1))
    return 2023

def generate_catalog():
    print("Generando catálogo robusto de vinos del cliente 'demo_vinoteca' de forma determinista...")
    profiles_path = "data/processed/wine_profiles_argentina_v2.csv"
    
    if not os.path.exists(profiles_path):
        print(f"Error: No se encontró el archivo de perfiles {profiles_path}")
        return
        
    df = pd.read_csv(profiles_path)
    
    # 1. Filtrar candidatos por estilo/color
    espumantes_df = df[df['variedad'].str.lower().str.contains('sparkling|espumante|brut', na=False) | 
                       df['title'].str.lower().str.contains('sparkling|espumante|brut', na=False)].copy()
                       
    rosados_df = df[df['variedad'].str.lower().str.contains('rose|rosé|rosado', na=False) | 
                    df['title'].str.lower().str.contains('rose|rosé|rosado', na=False)].copy()
                    
    blancos_df = df[(df['variedad'].str.lower().str.contains('chardonnay|torrontes|torrontés|sauvignon|viognier', na=False) | 
                     df['title'].str.lower().str.contains('chardonnay|torrontes|torrontés|sauvignon|viognier', na=False)) &
                    (~df['title'].isin(espumantes_df['title'])) & (~df['title'].isin(rosados_df['title']))].copy()
                    
    tintos_df = df[df['variedad'].str.lower().str.contains('malbec|cabernet|merlot|syrah|blend|bonarda|tempranillo|pinot noir', na=False) & 
                   (~df['title'].isin(espumantes_df['title'])) & (~df['title'].isin(rosados_df['title'])) & (~df['title'].isin(blancos_df['title']))].copy()

    # Seleccionar cuotas mínimas garantizadas
    espumantes_sel = espumantes_df.head(10)
    rosados_sel = rosados_df.head(10)
    blancos_sel = blancos_df.head(12)
    tintos_sel = tintos_df.head(28)
    
    catalog_raw = pd.concat([espumantes_sel, rosados_sel, blancos_sel, tintos_sel]).drop_duplicates(subset=['title'])
    
    rows = []
    for i, (_, row) in enumerate(catalog_raw.iterrows(), 1):
        title = row['title']
        winery = extract_winery_from_title(title)
        variety = row['variedad']
        variety_lower = variety.lower()
        title_lower = title.lower()
        vintage = extract_vintage_from_title(title)
        
        import re
        region_match = re.search(r'\(([^)]+)\)', str(title))
        region = region_match.group(1) if region_match else "Mendoza"
        
        # Mapeo de estilos
        is_sparkling = any(s in variety_lower or s in title_lower for s in ['sparkling', 'espumante', 'brut', 'champagne', 'extra brut', 'prosecco'])
        is_rose = 'rosé' in variety_lower or 'rose' in variety_lower or 'rosado' in title_lower
        is_white = any(w in variety_lower for w in ['chardonnay', 'sauvignon', 'torrontes', 'torrontés', 'pinot grigio', 'chenin', 'semillon', 'semillón', 'viognier']) or 'blanco' in title_lower
        is_tinto = not is_white and not is_sparkling and not is_rose

        # Distribución determinista de precios (Económico <15k, Medio 15k-35k, Premium >35k)
        if is_sparkling:
            # Espumantes: bajo, medio y alto
            if i % 3 == 0:
                price = 12000  # Económico
            elif i % 3 == 1:
                price = 24000  # Medio
            else:
                price = 48000  # Premium Alto
        elif is_rose:
            # Rosados
            if i % 3 == 0:
                price = 11500
            elif i % 3 == 1:
                price = 19800
            else:
                price = 42000
        elif is_white:
            # Blancos
            if i % 3 == 0:
                price = 9500
            elif i % 3 == 1:
                price = 22000
            else:
                price = 38000
        else:
            # Tintos
            if i % 3 == 0:
                price = 14500
            elif i % 3 == 1:
                price = 28000
            else:
                price = 68000

        # Control de stock: asegurar que la gran mayoría tengan stock > 0
        # Ponemos stock nulo solo en un 5% de vinos no críticos
        stock = 0 if i in [7, 18, 33] else 25
        
        # Activos: el 95% de los vinos están activos
        active = "False" if i in [11, 29] else "True"
        
        sku = f"DEMO-WINE-{i:03d}"
        image_url = f"/static/images/wines/{sku.lower()}.png"
        product_url = f"https://www.demovinoteca.com.ar/productos/{sku.lower()}"
        
        desc = str(row['full_text']).split('.')[0] + "." if pd.notna(row['full_text']) else "Excelente etiqueta seleccionada por su tipicidad argentina."
        
        tags_list = []
        if is_tinto:
            tags_list.append("tinto")
            tags_list.append("asado")
        if is_white:
            tags_list.append("blanco")
            tags_list.append("fresco")
        if is_sparkling:
            tags_list.append("espumante")
            tags_list.append("celebracion")
        if is_rose:
            tags_list.append("rose")
            tags_list.append("fresco")
        if price > 35000:
            tags_list.append("premium")
            
        tags = ", ".join(tags_list) if tags_list else "recomendado"
        
        rows.append({
            'sku': sku,
            'title': title,
            'winery': winery,
            'variety': variety,
            'vintage': vintage,
            'region': region,
            'price': price,
            'stock': stock,
            'image_url': image_url,
            'product_url': product_url,
            'description': desc,
            'tags': tags,
            'active': active
        })
        
    output_df = pd.DataFrame(rows)
    
    output_dir = "data/clients/demo_vinoteca"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "catalog.csv")
    output_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Catálogo generado de forma determinista: {output_file} (Total: {len(output_df)} registros)")

if __name__ == '__main__':
    generate_catalog()
