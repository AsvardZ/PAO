
import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="Albion Online - Precios", layout="wide")
st.title("📊 Precios del Marketplace - Albion Online (Versión Original)")
st.markdown("Consulta precios de ítems por ciudad y genera un Excel con los datos.")

cities = ["Bridgewatch", "Martlock", "Thetford", "Fort Sterling", "Lymhurst", "Caerleon"]

@st.cache_data
def obtener_items_ids():
    return [
        "T4_SOLDIER_BOOTS", "T4_SOLDIER_ARMOR", "T4_SOLDIER_HELMET",
        "T4_MOUNT_HORSE", "T4_ORE", "T4_WOOD", "T4_FIBER",
        "T4_HIDE", "T4_STONE", "T4_TOOL_PICK", "T4_TOOL_AXE"
    ]

if st.button("🔄 Consultar Precios"):
    st.info("Obteniendo datos...")

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
                    if sell > 0 and buy > 0:
                        resultados.append({
                            "Ciudad": entry["city"],
                            "Ítem": entry["item_id"],
                            "Precio Venta": sell,
                            "Precio Compra": buy,
                            "Ganancia": sell - buy
                        })
        except Exception as e:
            st.error(f"Error consultando datos: {e}")

    if resultados:
        df = pd.DataFrame(resultados)
        st.success("✅ Datos cargados correctamente.")
        st.dataframe(df.sort_values("Ganancia", ascending=False), use_container_width=True)

        st.markdown("### 🏆 Top Ganancias por Ciudad")
        resumen = df.sort_values("Ganancia", ascending=False).groupby("Ciudad").first().reset_index()
        st.dataframe(resumen[["Ciudad", "Ítem", "Ganancia"]], use_container_width=True)

        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button(
            label="📥 Descargar Excel",
            data=output.getvalue(),
            file_name="precios_albion_original.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No se encontraron precios válidos.")
