# BILIOTECAS NECESSÁRIAS
import pandas as pd
import ast
import re
import streamlit as st

# Ajustar as configurações de exibição do Pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Carregar os dados dos arquivos fornecidos
authors_df = pd.read_csv('DataSets/authors.csv')
categories_df = pd.read_csv('DataSets/categories.csv')
formats_df = pd.read_csv('DataSets/formats.csv')
dataset_df = pd.read_csv('DataSets/dataset.csv')

# Função de tratamento do authors_df atualizada para remover datas no início
def process_author_name(name):
    if pd.isna(name):
        return "Não informado"
    
    name = str(name)  # Garantir que estamos lidando com uma string

    # Ajustar nomes divididos por vírgula
    if ", " in name:
        parts = name.split(", ")
        name = f"{parts[1]} {parts[0]}"
    
    # Limpar e formatar os nomes dos autores
    name = name.strip()
    name = name.strip('.-')
    name = ' '.join(word.capitalize() for word in name.split())
    
    # Remover datas no início do nome (padrão de quatro dígitos seguidos de - ou .)
    name = re.sub(r'^\d{4}-\d{4}\.?\s*', '', name)
    name = re.sub(r'^\d{4}-\s*', '', name)
    
    # Remover vírgulas internas
    name = name.replace(',', '')
    
    return name

# Aplicar a função combinada na coluna 'author_name'
authors_df['author_name'] = authors_df['author_name'].apply(process_author_name)

authors_df.head(20)

# Substituir as vírgulas por " /" na coluna 'category_name' do categories_df
categories_df['category_name'] = categories_df['category_name'].str.replace(',', ' /')
categories_df.head()

# Converter IDs de autores e categorias de representação de string para lista
dataset_df['authors'] = dataset_df['authors'].apply(ast.literal_eval)
dataset_df['categories'] = dataset_df['categories'].apply(ast.literal_eval)

# Explodir a coluna de autores e fazer a junção dos nomes dos autores
dataset_expanded_authors = dataset_df.explode('authors').merge(authors_df, left_on='authors', right_on='author_id', how='left')
dataset_expanded_authors['author_name'] = dataset_expanded_authors['author_name'].fillna('Não Informado')
dataset_expanded_authors['author_name'] = dataset_expanded_authors.groupby('id')['author_name'].transform(lambda x: ', '.join(x))
dataset_expanded_authors = dataset_expanded_authors.drop_duplicates(subset='id')

# Explodir a coluna de categorias e fazer a junção dos nomes das categorias
dataset_expanded_categories = dataset_expanded_authors.explode('categories').merge(categories_df, left_on='categories', right_on='category_id', how='left')
dataset_expanded_categories['category_name'] = dataset_expanded_categories['category_name'].fillna('Não Informado')
dataset_expanded_categories['category_name'] = dataset_expanded_categories.groupby('id')['category_name'].transform(lambda x: ', '.join(x))
dataset_expanded_categories = dataset_expanded_categories.drop_duplicates(subset='id')

# Fazer a junção dos formatos
final_dataset = dataset_expanded_categories.merge(formats_df, left_on='format', right_on='format_id', how='left')

selected_columns = [
    'id', 'title', 'author_name', 'category_name', 'format_name',
    'bestsellers-rank', 'rating-avg', 'publication-date'
]

questions_df = final_dataset[selected_columns]

questions_df.head()

# Pergunta 1: Qual a quantidade total de livros da base?
total_books = questions_df['id'].nunique()
print(f'A quantidade de livros é: {total_books}')

# Pergunta 2: Qual a quantidade de livros que possui apenas 1 autor?
books_with_one_author = questions_df[questions_df['author_name'].str.count(',') == 0]['id'].nunique()
print(f'A quantidade de livros que possui apenas 1 autor é: {books_with_one_author}')

# Pergunta 3: Quais os 5 autores com a maior quantidade de livros?
author_book_counts = questions_df.explode('author_name').groupby('author_name')['id'].nunique().sort_values(ascending=False)
top_5_authors = author_book_counts.iloc[1:6]
top_5_authors_df = top_5_authors.reset_index()
top_5_authors_df.columns = ['nome_autor', 'quantidade_livros']
print(top_5_authors_df)

# Pergunta 4: Qual a quantidade de livros por categoria?
category_book_counts = questions_df.explode('category_name').groupby('category_name')['id'].nunique().sort_values(ascending=False)
category_book_counts_df = category_book_counts.reset_index()
category_book_counts_df.columns = ['nome_categoria', 'quantidade_livros']
print(category_book_counts_df)

# Pergunta 5: Quais as 5 categorias com a maior quantidade de livros?
top_5_categories = (category_book_counts_df.head(5))
print(top_5_categories)

# Pergunta 6: Qual o formato com a maior quantidade de livros?
format_book_counts = questions_df.groupby('format_name')['id'].nunique()
most_common_format = format_book_counts.idxmax()
print(f'O formato com maior quantidade de livros é: {most_common_format}')

# Pergunta 7: Considerando a coluna “bestsellers-rank”, quais os 10 livros mais bem posicionados?
top_10_bestsellers = questions_df.sort_values(by='bestsellers-rank', ascending=True).head(10)
top_10_bestsellers.head(10)

# Pergunta 8: Considerando a coluna “rating-avg”, quais os 10 livros mais bem posicionados?
top_10_rated_books = questions_df.sort_values(by='rating-avg', ascending=False).head(10)
top_10_rated_books.head(10)

# Pergunta 9: Quantos livros possuem “rating-avg” maior do que 3,5?
books_above_3_5_rating = questions_df[questions_df['rating-avg'] > 3.5]['id'].nunique()
print(f'A quantidade de livros que possuem "rating-avg" maior que 3,5 é: books_above_3_5_rating')

# Pergunta 10: Quantos livros têm data de publicação (publication-date) maior do que 01-01-2020?
questions_df['publication-date'] = pd.to_datetime(questions_df['publication-date'], errors='coerce')
books_after_2020 = questions_df[questions_df['publication-date'] > '2020-01-01']['id'].nunique()
print(f'A quantidade de livros que tem data de publicação maior que 01-01-2020 é: {books_after_2020}')

# Configurar a página para ser mais larga (wide mode)
st.set_page_config(layout="wide")

# Criar o Dashboard com Streamlit
st.title('Dashboard de Análise de Livros')

# Criar colunas para os cards no topo com números maiores
col1, col2, col3, col4, col5 = st.columns(5)

# Preencher cada coluna com um card
with col1:
    st.metric(label="Total de Livros", value=total_books)

with col2:
    st.metric(label="Livros com Apenas 1 Autor", value=books_with_one_author)

with col3:
    st.metric(label="Livros com nota maior que 3.5", value=books_above_3_5_rating)

with col4:
    st.metric(label="Livros publicados após 01-01-2020", value=books_after_2020)

with col5:
    st.metric(label="Formato com Mais Livros", value=most_common_format)

# Exibir as outras informações abaixo dos cards em layout expandido
st.subheader('Top 5 Autores com Mais Livros')
st.dataframe(top_5_authors_df, use_container_width=True, hide_index=True)

st.subheader('Quantidade de Livros por Categoria')
st.dataframe(category_book_counts.reset_index().rename(columns={'id': 'quantidade_livros'}), use_container_width=True, hide_index=True)

st.subheader('Top 5 Categorias com Mais Livros')
st.dataframe(top_5_categories, use_container_width=True, hide_index=True)

st.subheader('Top 10 Livros Mais Bem Posicionados')
st.dataframe(top_10_bestsellers, use_container_width=True, hide_index=True)

st.subheader('Top 10 Livros Melhor Avaliados')
st.dataframe(top_10_rated_books, use_container_width=True, hide_index=True)