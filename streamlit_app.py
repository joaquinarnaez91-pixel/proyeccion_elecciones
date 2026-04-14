import streamlit as st
import json
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ONPE 2026 - Proyección Electoral",
    page_icon="🗳️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .candidate-card {
        background-color: #ffffff;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.3rem;
    }
    .winner-card {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

def load_election_data():
    """Load election data from JSON file"""
    try:
        with open('election_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo election_data.json")
        st.info("💡 Ejecuta primero: python scrape_onpe.py")
        return None
    except json.JSONDecodeError:
        st.error("❌ Error al leer election_data.json")
        return None

def create_dashboard(data):
    """Create the main dashboard"""
    
    # Header
    st.markdown('<div class="main-header">🗳️ Elecciones Perú 2026 - Proyección en Tiempo Real</div>', unsafe_allow_html=True)
    
    # Last update info
    st.markdown(f"**📅 Última actualización:** {data['last_update']}")
    st.markdown(f"**📊 Fuente:** {data.get('source', 'ONPE')}")
    
    st.markdown("---")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    completion = data['regional_completion']
    
    with col1:
        st.metric("📊 Progreso Nacional", f"{completion['National']*100:.0f}%")
    with col2:
        st.metric("🏙️ Lima", f"{completion['Lima']*100:.0f}%")
    with col3:
        st.metric("🌾 Provincias", f"{completion['Provinces']*100:.0f}%")
    with col4:
        st.metric("🗳️ Votos Contados", f"{data['total_votes_counted']:,}")
    
    st.markdown("---")
    
    # Top candidates
    st.subheader("🏆 Top 6 Candidatos - Resultados y Proyecciones")
    
    candidates = data['candidates']
    
    # Create comparison chart data
    chart_data = []
    for candidate in candidates:
        chart_data.append({
            'Candidato': candidate['name'][:30] + '...',
            'Votos Actuales': candidate['current_votes'],
            'Votos Proyectados': candidate['projected_votes']
        })
    
    # Display bar chart
    df_chart = pd.DataFrame(chart_data)
    st.bar_chart(df_chart.set_index('Candidato'))
    
    st.markdown("---")
    
    # Detailed results
    st.subheader("📋 Resultados Detallados")
    
    for i, candidate in enumerate(candidates, 1):
        # Determine if winner
        is_leader = (i == 1)
        card_class = "candidate-card winner-card" if is_leader else "candidate-card"
        
        with st.container():
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                st.markdown(f"### {medal} {candidate['name']}")
                st.markdown(f"**Perfil:** {candidate['profile']}")
            
            with col2:
                st.markdown("**Resultados Actuales**")
                st.metric("Votos", f"{candidate['current_votes']:,}")
                st.metric("Porcentaje", f"{candidate['current_pct']:.2f}%")
            
            with col3:
                st.markdown("**Proyección Final**")
                st.metric("Votos Proyectados", f"{candidate['projected_votes']:,}")
                change = candidate['projected_pct'] - candidate['current_pct']
                st.metric("% Proyectado", f"{candidate['projected_pct']:.2f}%", 
                         delta=f"{change:+.2f}%")
            
            # Progress bar
            progress = candidate['current_pct'] / 100
            st.progress(progress)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Comparison table
    st.subheader("📊 Tabla Comparativa")
    
    table_data = []
    for candidate in candidates:
        table_data.append({
            'Candidato': candidate['name'][:40],
            'Votos Actuales': f"{candidate['current_votes']:,}",
            '% Actual': f"{candidate['current_pct']:.2f}%",
            'Votos Proyectados': f"{candidate['projected_votes']:,}",
            '% Proyectado': f"{candidate['projected_pct']:.2f}%",
            'Cambio': f"{candidate['projected_pct'] - candidate['current_pct']:+.2f}%",
            'Perfil': candidate['profile']
        })
    
    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Segunda vuelta prediction
    st.subheader("🎯 Proyección Segunda Vuelta")
    
    top_two = candidates[:2]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1️⃣ Primer Lugar")
        st.markdown(f"**{top_two[0]['name']}**")
        st.metric("Votos Proyectados", f"{top_two[0]['projected_votes']:,}")
        st.metric("Porcentaje Proyectado", f"{top_two[0]['projected_pct']:.2f}%")
    
    with col2:
        st.markdown("### 2️⃣ Segundo Lugar")
        st.markdown(f"**{top_two[1]['name']}**")
        st.metric("Votos Proyectados", f"{top_two[1]['projected_votes']:,}")
        st.metric("Porcentaje Proyectado", f"{top_two[1]['projected_pct']:.2f}%")
    
    st.info("""
    📅 **Segunda Vuelta Electoral: 7 de Junio de 2026**
    
    Según las proyecciones actuales, estos dos candidatos pasarían a la segunda vuelta.
    """)
    
    # Methodology
    with st.expander("📖 Metodología de Proyección"):
        st.markdown(f"""
        ### Modelo Estadístico
        
        **Estado actual del conteo:**
        - Progreso nacional: {completion['National']*100:.0f}% contabilizado
        - Lima: {completion['Lima']*100:.0f}% contabilizado
        - Provincias: {completion['Provinces']*100:.0f}% contabilizado
        
        **Supuestos del modelo:**
        - Lima representa 32% del electorado nacional
        - Provincias representan 68% del electorado
        - Candidatos tienen diferentes fortalezas urbanas/rurales
        
        **Fuentes:**
        - Datos oficiales: ONPE
        - Elección: 12 de abril de 2026
        - Segunda vuelta: 7 de junio de 2026
        """)

def main():
    """Main application"""
    
    # Load data
    data = load_election_data()
    
    if data is None:
        st.stop()
    
    # Create dashboard
    create_dashboard(data)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    🔄 **Para actualizar:** Ejecuta `python scrape_onpe.py` y sube el nuevo `election_data.json` a GitHub
    """)

if __name__ == "__main__":
    main()
