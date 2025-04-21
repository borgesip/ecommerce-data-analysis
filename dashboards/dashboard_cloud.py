# scripts/dashboard_cloud.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Título
st.title("📊 Dashboard de Análise de E-commerce")

# Carregar dados do CSV
df = pd.read_csv('data/processed/sales_processed.csv')
df['invoicedate'] = pd.to_datetime(df['invoicedate'])

# === RFM Analysis ===
st.header("Segmentação RFM")

# Calcular RFM
reference_date = df['invoicedate'].max() + pd.Timedelta(days=1)
rfm = df.groupby('customerid').agg({
    'invoicedate': lambda x: (reference_date - x.max()).days,
    'invoiceno': 'nunique',
    'totalvalue': 'sum'
}).rename(columns={
    'invoicedate': 'recency',
    'invoiceno': 'frequency',
    'totalvalue': 'monetary'
})

# Resetar o índice para que 'customerid' se torne uma coluna
rfm = rfm.reset_index()

# Segmentação
rfm['R_score'] = pd.qcut(rfm['recency'], 4, labels=[4, 3, 2, 1])
rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
rfm['M_score'] = pd.qcut(rfm['monetary'], 4, labels=[1, 2, 3, 4])
rfm['RFM_score'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str) + rfm['M_score'].astype(str)

def rfm_segment(row):
    if row['RFM_score'] in ['444', '443', '434', '433']:
        return 'Campeões'
    elif row['R_score'] >= 3 and row['F_score'] >= 2:
        return 'Leais'
    elif row['R_score'] <= 2 and row['F_score'] >= 3:
        return 'Promissores'
    else:
        return 'Em Risco'

rfm['Segment'] = rfm.apply(rfm_segment, axis=1)

# Scatter Plot Interativo
fig_rfm = px.scatter(
    rfm,
    x='recency',
    y='monetary',
    color='Segment',
    size='frequency',
    hover_data=['customerid', 'recency', 'frequency', 'monetary'],
    log_y=True,
    title='Segmentação RFM: Recência vs. Monetário (Frequência como tamanho)',
    labels={
        'recency': 'Recência (dias desde a última compra)',
        'monetary': 'Monetário (valor total em log)'
    },
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_rfm.update_layout(
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=1.05),
    margin=dict(r=150)
)
st.plotly_chart(fig_rfm, use_container_width=True)

# Distribuição de Segmentos
segment_counts = rfm['Segment'].value_counts()
total_customers = len(rfm)
percentages = (segment_counts / total_customers * 100).round(1)

fig_segments = px.bar(
    x=segment_counts.values,
    y=segment_counts.index,
    orientation='h',
    text=[f'{p}%' for p in percentages],
    title='Distribuição de Segmentos RFM',
    labels={'x': 'Número de Clientes', 'y': 'Segmento'},
    color_discrete_sequence=px.colors.qualitative.Set2
)
st.plotly_chart(fig_segments, use_container_width=True)

# === Cohort Analysis ===
st.header("Retenção por Cohort")
df['CohortMonth'] = df.groupby('customerid')['invoicedate'].transform('min').dt.to_period('M')
df['InvoiceMonth'] = df['invoicedate'].dt.to_period('M')
df['CohortIndex'] = df.apply(lambda x: (x['InvoiceMonth'].year - x['CohortMonth'].year) * 12 + x['InvoiceMonth'].month - x['CohortMonth'].month, axis=1)
cohort_data = df.groupby(['CohortMonth', 'CohortIndex'])['customerid'].nunique().reset_index()

# Converter CohortMonth para string para evitar problemas de serialização
cohort_data['CohortMonth'] = cohort_data['CohortMonth'].astype(str)

cohort_pivot = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='customerid')
cohort_size = cohort_pivot[0]
retention = cohort_pivot.divide(cohort_size, axis=0)

# Heatmap
fig_cohort = px.imshow(
    retention,
    labels=dict(x="Cohort Index (Meses)", y="Cohort Month", color="Retenção (%)"),
    title="Retenção por Cohort",
    color_continuous_scale='YlGnBu',
    text_auto='.0%'
)
st.plotly_chart(fig_cohort, use_container_width=True)

# Retenção Média
avg_retention = retention.mean()
fig_avg_retention = px.line(
    x=avg_retention.index,
    y=avg_retention.values,
    markers=True,
    title='Retenção Média por Mês Após Primeira Compra',
    labels={'x': 'Cohort Index (Meses)', 'y': 'Retenção Média (%)'}
)
st.plotly_chart(fig_avg_retention, use_container_width=True)

# === Top Products ===
st.header("Produtos Mais Vendidos")
top_products_quantity = df.groupby('description')['quantity'].sum().sort_values(ascending=False).head(10)
top_products_revenue = df.groupby('description')['totalvalue'].sum().sort_values(ascending=False).head(10)

# Por Quantidade
fig_top_quantity = px.bar(
    x=top_products_quantity.values,
    y=top_products_quantity.index,
    orientation='h',
    title='Top 10 Produtos por Quantidade Vendida',
    labels={'x': 'Quantidade Vendida', 'y': 'Produto'},
    color_discrete_sequence=['#636EFA']
)
st.plotly_chart(fig_top_quantity, use_container_width=True)

# Por Receita
fig_top_revenue = px.bar(
    x=top_products_revenue.values,
    y=top_products_revenue.index,
    orientation='h',
    title='Top 10 Produtos por Receita',
    labels={'x': 'Receita Total', 'y': 'Produto'},
    color_discrete_sequence=['#EF553B']
)
st.plotly_chart(fig_top_revenue, use_container_width=True)

# === Sales Trends ===
st.header("Tendências de Vendas")
df['YearMonth'] = df['invoicedate'].dt.to_period('M').astype(str)
monthly_sales = df.groupby('YearMonth')['totalvalue'].sum().reset_index()

fig_sales = px.line(
    monthly_sales,
    x='YearMonth',
    y='totalvalue',
    title='Vendas Mensais ao Longo do Tempo',
    labels={'YearMonth': 'Mês', 'totalvalue': 'Receita Total'}
)
st.plotly_chart(fig_sales, use_container_width=True)

# === Customer Demographics ===
st.header("Análise por País")
country_sales = df.groupby('country')['totalvalue'].sum().sort_values(ascending=False).head(10)
country_customers = df.groupby('country')['customerid'].nunique().sort_values(ascending=False).head(10)

# Receita por País
fig_country_sales = px.bar(
    x=country_sales.values,
    y=country_sales.index,
    orientation='h',
    title='Top 10 Países por Receita',
    labels={'x': 'Receita Total', 'y': 'País'},
    color_discrete_sequence=['#00CC96']
)
st.plotly_chart(fig_country_sales, use_container_width=True)

# Número de Clientes por País
fig_country_customers = px.bar(
    x=country_customers.values,
    y=country_customers.index,
    orientation='h',
    title='Top 10 Países por Número de Clientes',
    labels={'x': 'Número de Clientes', 'y': 'País'},
    color_discrete_sequence=['#AB63FA']
)
st.plotly_chart(fig_country_customers, use_container_width=True)

# === Insights ===
st.header("Insights e Recomendações")
st.markdown("""
- **RFM**: Os 'Campeões' (20.5% dos clientes) geram 48.3% da receita. Implemente um programa de fidelidade para mantê-los engajados.
- **Cohort**: A retenção cai significativamente após o primeiro mês (e.g., 37% para o cohort de 2010-12). Introduza e-mails de onboarding para novos clientes.
- **Produtos**: Identifique os produtos mais vendidos para promoções direcionadas (e.g., os top 10 por quantidade e receita).
- **Vendas**: Picos sazonais (e.g., dezembro) sugerem campanhas de Natal para aumentar a receita.
- **Países**: A maioria das vendas vem de poucos países (e.g., Reino Unido). Considere estratégias de marketing para expandir em outros mercados.
""")
