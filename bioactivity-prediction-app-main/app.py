import streamlit as st
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle

# Calculadora de descritores moleculares
def desc_calc():
    # Realiza o cálculo dos descritores
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

# Download de arquivo
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # conversões de strings <-> bytes
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Baixar Previsões</a>'
    return href

# Construção do modelo
def build_model(input_data):
    # Carrega o modelo de regressão salvo
    load_model = pickle.load(open('acetylcholinesterase_model.pkl', 'rb'))
    # Aplica o modelo para fazer previsões
    prediction = load_model.predict(input_data)
    st.header('**Saída da Previsão**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='nome_da_molécula')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)

# Imagem do logotipo
image = Image.open('logo.png')

st.image(image, use_column_width=True)

# Título da página
st.markdown("""
# Aplicativo de Previsão de Bioatividade (Acetilcolinesterase)

Este aplicativo permite prever a bioatividade para inibir a enzima `Acetilcolinesterase`. A `Acetilcolinesterase` é um alvo terapêutico para a doença de Alzheimer.

**Créditos**
- Aplicativo construído em `Python` + `Streamlit`
- Descritores calculados usando [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/) [[Leia o artigo]](https://doi.org/10.1002/jcc.21707).
---
""")

# Barra lateral
with st.sidebar.header('1. Carregue seu arquivo CSV'):
    uploaded_file = st.sidebar.file_uploader("Carregue seu arquivo de entrada", type=['txt'])
    st.sidebar.markdown("""
[Arquivo de entrada de exemplo](https://raw.githubusercontent.com/dataprofessor/bioactivity-prediction-app/main/example_acetylcholinesterase.txt)
""")

if st.sidebar.button('Prever'):
    load_data = pd.read_table(uploaded_file, sep=' ', header=None)
    load_data.to_csv('molecule.smi', sep='\t', header=False, index=False)

    st.header('**Dados de entrada originais**')
    st.write(load_data)

    with st.spinner("Calculando descritores..."):
        desc_calc()

    # Lê os descritores calculados e exibe o dataframe
    st.header('**Descritores moleculares calculados**')
    desc = pd.read_csv('descriptors_output.csv')
    st.write(desc)
    st.write(desc.shape)

    # Lê a lista de descritores usados no modelo previamente construído
    st.header('**Subconjunto de descritores dos modelos previamente construídos**')
    Xlist = list(pd.read_csv('descriptor_list.csv').columns)
    desc_subset = desc[Xlist]
    st.write(desc_subset)
    st.write(desc_subset.shape)

    # Aplica o modelo treinado para fazer previsões nos compostos consultados
    build_model(desc_subset)
else:
    st.info('Carregue os dados de entrada na barra lateral para começar!')
