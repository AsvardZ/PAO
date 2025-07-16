
import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="Precios Albion Online", layout="wide")
st.title("📊 Precios del Marketplace - Versión Básica")

cities = ["Bridgewatch", "Martlock", "Thetford", "Fort Sterling", "Lymhurst", "Caerleon"]

@st.cache_data(ttl=3600)
def obtener_items_ids():
    url = "https://www.albion-online-data.com/api/v2/items"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [item["uniqueName"] for item in data if item.get("uniqueName", "").startswith("T")]
    return []

if st.button("🔄 Obtener precios básicos"):
    st.info("Cargando datos...")
    items = obtener_items_ids()
    base_url = "https://www.albion-online-data.com/api/v2/stats/prices/"
    resultados = []

    for i in range(0, len(items), 50):
        grupo = items[i:i+50]
        url = f"{base_url}{','.join(grupo)}?locations={','.join(cities)}"
        try:
            res = requests.get(url)
            if res.status_code == 200:
                for entry in res.json():
                    sell = entry.get("sell_price_min", 0)
                    buy = entry.get("buy_price_max", 0)
                    if sell > 0 or buy > 0:
                        resultados.append({
                            "Ciudad": entry["city"],
                            "Ítem (código)": entry["item_id"],
                            "Venta (min)": sell,
                            "Compra (max)": buy,
                            "Ganancia": sell - buy if sell > 0 and buy > 0 else 0
                        })
        except Exception:
            continue

    if resultados:
        df = pd.DataFrame(resultados)
        st.success("✅ Datos cargados.")
        st.dataframe(df, use_container_width=True)

        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button(
            label="📥 Descargar Excel",
            data=output.getvalue(),
            file_name="precios_basicos_albion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No se encontraron precios válidos.")
