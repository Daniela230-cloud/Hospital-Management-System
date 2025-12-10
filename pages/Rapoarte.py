import streamlit as st
from database.connection import db
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Rapoarte & Statistici",
    page_icon="📊",
    layout="wide"
)

# CSS Custom
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)


# ===== FUNCȚII PENTRU STATISTICI =====

def get_statistics_overview():
    """Statistici generale"""
    try:
        stats = {}
        
        # Total pacienți
        query = "SELECT COUNT(*) as total FROM Pacient"
        df = db.fetch_dataframe(query)
        stats['total_pacienti'] = int(df['total'].iloc[0]) if not df.empty else 0
        
        # Total doctori
        query = "SELECT COUNT(*) as total FROM Doctor"
        df = db.fetch_dataframe(query)
        stats['total_doctori'] = int(df['total'].iloc[0]) if not df.empty else 0
        
        # Total programări
        query = "SELECT COUNT(*) as total FROM Programare"
        df = db.fetch_dataframe(query)
        stats['total_programari'] = int(df['total'].iloc[0]) if not df.empty else 0
        
        # Total diagnostice
        query = "SELECT COUNT(*) as total FROM Diagnostic"
        df = db.fetch_dataframe(query)
        stats['total_diagnostice'] = int(df['total'].iloc[0]) if not df.empty else 0
        
        # Programări luna curentă
        query = """
            SELECT COUNT(*) as total 
            FROM Programare 
            WHERE MONTH(data_programare) = MONTH(GETDATE()) 
            AND YEAR(data_programare) = YEAR(GETDATE())
        """
        df = db.fetch_dataframe(query)
        stats['programari_luna'] = int(df['total'].iloc[0]) if not df.empty else 0
        
        # Pacienți internați
        query = """
            SELECT COUNT(*) as total 
            FROM Pacient 
            WHERE data_internare IS NOT NULL AND data_externare IS NULL
        """
        df = db.fetch_dataframe(query)
        stats['pacienti_internati'] = int(df['total'].iloc[0]) if not df.empty else 0
        
        return stats
    except Exception as e:
        st.error(f"Eroare la obținerea statisticilor: {e}")
        return {}


def get_top_doctori():
    """Top 10 doctori după număr de programări"""
    try:
        query = """
            SELECT TOP 10
                d.nume + ' ' + d.prenume as Doctor,
                d.specializare as Specializare,
                COUNT(pr.id_programare) as [Număr Programări]
            FROM Doctor d
            LEFT JOIN Programare pr ON d.id_doctor = pr.id_doctor
            GROUP BY d.nume, d.prenume, d.specializare
            ORDER BY COUNT(pr.id_programare) DESC
        """
        return db.fetch_dataframe(query)
    except Exception as e:
        st.error(f"Eroare: {e}")
        return pd.DataFrame()


def get_top_boli():
    """Top 10 cele mai frecvente boli"""
    try:
        query = """
            SELECT TOP 10
                boala as Boala,
                COUNT(*) as [Număr Cazuri],
                SUM(CASE WHEN severitate = 'severa' THEN 1 ELSE 0 END) as [Cazuri Severe]
            FROM Diagnostic
            GROUP BY boala
            ORDER BY COUNT(*) DESC
        """
        return db.fetch_dataframe(query)
    except Exception as e:
        return pd.DataFrame()


def get_programari_pe_luna():
    """Programări pe ultimele 6 luni"""
    try:
        query = """
            SELECT 
                FORMAT(data_programare, 'yyyy-MM') as Luna,
                COUNT(*) as [Număr Programări]
            FROM Programare
            WHERE data_programare >= DATEADD(month, -6, GETDATE())
            GROUP BY FORMAT(data_programare, 'yyyy-MM')
            ORDER BY FORMAT(data_programare, 'yyyy-MM')
        """
        return db.fetch_dataframe(query)
    except Exception as e:
        return pd.DataFrame()


def get_distributie_gen():
    """Distribuție pacienți pe gen"""
    try:
        query = """
            SELECT 
                gen as Gen,
                COUNT(*) as Numar
            FROM Pacient
            GROUP BY gen
        """
        df = db.fetch_dataframe(query)
        if not df.empty:
            df['Gen'] = df['Gen'].map({'M': 'Masculin', 'F': 'Feminin'})
        return df
    except Exception as e:
        return pd.DataFrame()


def get_pacienti_pe_sectie():
    """Număr pacienți per secție"""
    try:
        query = """
            SELECT 
                s.nume_sectie as Sectie,
                COUNT(p.id_pacient) as [Număr Pacienți]
            FROM Sectie s
            LEFT JOIN Pacient p ON s.id_sectie = p.id_sectie
            GROUP BY s.nume_sectie
            ORDER BY COUNT(p.id_pacient) DESC
        """
        return db.fetch_dataframe(query)
    except Exception as e:
        return pd.DataFrame()


def get_severitate_diagnostice():
    """Distribuție diagnostice pe severitate"""
    try:
        query = """
            SELECT 
                severitate as Severitate,
                COUNT(*) as Numar
            FROM Diagnostic
            GROUP BY severitate
        """
        return db.fetch_dataframe(query)
    except Exception as e:
        return pd.DataFrame()


def get_programari_per_tip():
    """Programări pe tipuri"""
    try:
        query = """
            SELECT 
                tip_programare as Tip,
                COUNT(*) as Numar
            FROM Programare
            GROUP BY tip_programare
            ORDER BY COUNT(*) DESC
        """
        return db.fetch_dataframe(query)
    except Exception as e:
        return pd.DataFrame()


def get_activitate_doctori():
    """Activitate doctori - programări și diagnostice"""
    try:
        query = """
            SELECT 
                d.nume + ' ' + d.prenume as Doctor,
                d.specializare as Specializare,
                COUNT(DISTINCT pr.id_programare) as Programari,
                COUNT(DISTINCT dg.id_diagnostic) as Diagnostice
            FROM Doctor d
            LEFT JOIN Programare pr ON d.id_doctor = pr.id_doctor
            LEFT JOIN Diagnostic dg ON d.id_doctor = dg.id_doctor
            GROUP BY d.nume, d.prenume, d.specializare
            HAVING COUNT(DISTINCT pr.id_programare) > 0 OR COUNT(DISTINCT dg.id_diagnostic) > 0
            ORDER BY COUNT(DISTINCT pr.id_programare) DESC
        """
        return db.fetch_dataframe(query)
    except Exception as e:
        return pd.DataFrame()


# ===== INTERFAȚA UTILIZATOR =====

def main():
    st.title("📊 Rapoarte & Statistici")
    st.markdown("---")
    
    # ===== SECȚIUNEA 1: STATISTICI GENERALE =====
    st.markdown("## 📈 Statistici Generale")
    
    stats = get_statistics_overview()
    
    if stats:
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("👥 Pacienți", stats.get('total_pacienti', 0))
        
        with col2:
            st.metric("👨‍⚕️ Doctori", stats.get('total_doctori', 0))
        
        with col3:
            st.metric("📅 Programări", stats.get('total_programari', 0))
        
        with col4:
            st.metric("🩺 Diagnostice", stats.get('total_diagnostice', 0))
        
        with col5:
            st.metric("📆 Luna Aceasta", stats.get('programari_luna', 0))
        
        with col6:
            st.metric("🏥 Internați", stats.get('pacienti_internati', 0))
    
    st.markdown("---")
    
    # ===== TABS PENTRU RAPOARTE =====
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Grafice Generale",
        "👨‍⚕️ Raport Doctori",
        "🩺 Raport Diagnostic",
        "📅 Raport Programări"
    ])
    
    # ===== TAB 1: GRAFICE GENERALE =====
    with tab1:
        st.markdown("### 📊 Vizualizări Generale")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Grafic Distribuție Gen
            st.markdown("#### 👥 Distribuție Pacienți pe Gen")
            df_gen = get_distributie_gen()
            if not df_gen.empty:
                fig = px.pie(
                    df_gen,
                    values='Numar',
                    names='Gen',
                    color_discrete_sequence=['#3498db', '#e74c3c'],
                    hole=0.4
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nu există date")
            
            # Grafic Pacienți pe Secție
            st.markdown("#### 🏥 Pacienți pe Secție")
            df_sectii = get_pacienti_pe_sectie()
            if not df_sectii.empty:
                fig = px.bar(
                    df_sectii,
                    x='Sectie',
                    y='Număr Pacienți',
                    color='Număr Pacienți',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nu există date")
        
        with col_right:
            # Grafic Severitate Diagnostice
            st.markdown("#### 🩺 Severitate Diagnostice")
            df_sev = get_severitate_diagnostice()
            if not df_sev.empty:
                colors_map = {
                    'usoara': '#27ae60',
                    'medie': '#f39c12',
                    'severa': '#e74c3c'
                }
                df_sev['Color'] = df_sev['Severitate'].map(colors_map)
                
                fig = px.bar(
                    df_sev,
                    x='Severitate',
                    y='Numar',
                    color='Severitate',
                    color_discrete_map=colors_map
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nu există date")
            
            # Grafic Tipuri Programări
            st.markdown("#### 📅 Tipuri Programări")
            df_tip = get_programari_per_tip()
            if not df_tip.empty:
                fig = px.pie(
                    df_tip,
                    values='Numar',
                    names='Tip',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nu există date")
        
        # Grafic Programări în Timp (full width)
        st.markdown("#### 📈 Evoluție Programări (Ultimele 6 Luni)")
        df_luna = get_programari_pe_luna()
        if not df_luna.empty:
            fig = px.line(
                df_luna,
                x='Luna',
                y='Număr Programări',
                markers=True,
                line_shape='spline'
            )
            fig.update_traces(line_color='#3498db', line_width=3)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nu există date pentru ultimele 6 luni")
    
    # ===== TAB 2: RAPORT DOCTORI =====
    with tab2:
        st.markdown("### 👨‍⚕️ Raport Activitate Doctori")
        
        # Top Doctori
        st.markdown("#### 🏆 Top 10 Doctori după Programări")
        df_top_doc = get_top_doctori()
        if not df_top_doc.empty:
            st.dataframe(df_top_doc, use_container_width=True, hide_index=True)
            
            # Grafic
            fig = px.bar(
                df_top_doc,
                x='Doctor',
                y='Număr Programări',
                color='Specializare',
                text='Număr Programări'
            )
            fig.update_layout(height=500, xaxis_tickangle=-45)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nu există date")
        
        st.markdown("---")
        
        # Activitate Completă Doctori
        st.markdown("#### 📊 Activitate Completă Doctori")
        df_activitate = get_activitate_doctori()
        if not df_activitate.empty:
            st.dataframe(df_activitate, use_container_width=True, hide_index=True)
            
            # Export
            csv = df_activitate.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descarcă Raport Doctori (CSV)",
                data=csv,
                file_name=f"raport_doctori_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Nu există date")
    
    # ===== TAB 3: RAPORT DIAGNOSTIC =====
    with tab3:
        st.markdown("### 🩺 Raport Diagnostice")
        
        # Top Boli
        st.markdown("#### 🦠 Top 10 Cele Mai Frecvente Boli")
        df_boli = get_top_boli()
        if not df_boli.empty:
            st.dataframe(df_boli, use_container_width=True, hide_index=True)
            
            # Grafic
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_boli['Boala'],
                y=df_boli['Număr Cazuri'],
                name='Total Cazuri',
                marker_color='#3498db'
            ))
            fig.add_trace(go.Bar(
                x=df_boli['Boala'],
                y=df_boli['Cazuri Severe'],
                name='Cazuri Severe',
                marker_color='#e74c3c'
            ))
            fig.update_layout(
                barmode='group',
                height=500,
                xaxis_tickangle=-45,
                title="Distribuție Boli - Total vs Severe"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Export
            csv = df_boli.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descarcă Raport Boli (CSV)",
                data=csv,
                file_name=f"raport_boli_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Nu există diagnostice înregistrate")
    
    # ===== TAB 4: RAPORT PROGRAMĂRI =====
    with tab4:
        st.markdown("### 📅 Raport Programări")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Statistici Programări")
            
            # Programări pe perioada
            query_stats = """
                SELECT 
                    COUNT(*) as Total,
                    SUM(CASE WHEN data_programare >= CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) as Viitoare,
                    SUM(CASE WHEN data_programare < CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) as Trecute,
                    SUM(CASE WHEN CAST(data_programare AS DATE) = CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) as Astazi
                FROM Programare
            """
            df_stats = db.fetch_dataframe(query_stats)
            
            if not df_stats.empty:
                st.metric("📊 Total Programări", int(df_stats['Total'].iloc[0]))
                st.metric("⏭️ Programări Viitoare", int(df_stats['Viitoare'].iloc[0]))
                st.metric("✅ Programări Trecute", int(df_stats['Trecute'].iloc[0]))
                st.metric("📅 Programări Astăzi", int(df_stats['Astazi'].iloc[0]))
        
        with col2:
            st.markdown("#### 🕐 Distribuție Ore Programări")
            
            # Programări pe ore
            query_ore = """
                SELECT 
                    DATEPART(HOUR, ora_programare) as Ora,
                    COUNT(*) as Numar
                FROM Programare
                GROUP BY DATEPART(HOUR, ora_programare)
                ORDER BY DATEPART(HOUR, ora_programare)
            """
            df_ore = db.fetch_dataframe(query_ore)
            
            if not df_ore.empty:
                fig = px.bar(
                    df_ore,
                    x='Ora',
                    y='Numar',
                    labels={'Ora': 'Ora Zilei', 'Numar': 'Număr Programări'},
                    color='Numar',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nu există date")
        
        st.markdown("---")
        
        # Tabel complet programări
        st.markdown("#### 📋 Lista Completă Programări Recente")
        query_recent = """
            SELECT TOP 20
                p.nume + ' ' + p.prenume as Pacient,
                d.nume + ' ' + d.prenume as Doctor,
                pr.tip_programare as Tip,
                CONVERT(VARCHAR, pr.data_programare, 103) as Data,
                CONVERT(VARCHAR(5), pr.ora_programare, 108) as Ora
            FROM Programare pr
            JOIN Pacient p ON pr.id_pacient = p.id_pacient
            JOIN Doctor d ON pr.id_doctor = d.id_doctor
            ORDER BY pr.data_programare DESC, pr.ora_programare DESC
        """
        df_recent = db.fetch_dataframe(query_recent)
        
        if not df_recent.empty:
            st.dataframe(df_recent, use_container_width=True, hide_index=True)
            
            csv = df_recent.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descarcă Raport Programări (CSV)",
                data=csv,
                file_name=f"raport_programari_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Nu există programări")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #7f8c8d; padding: 2rem;'>
            <p>📊 Rapoarte generate automat • Actualizat: {}</p>
        </div>
    """.format(datetime.now().strftime('%d.%m.%Y %H:%M')), unsafe_allow_html=True)


if __name__ == "__main__":
    main()