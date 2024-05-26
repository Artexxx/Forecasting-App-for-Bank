import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_pandas_profiling import st_profile_report
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px



@st.cache_data
def get_data_info(df):
    info = pd.DataFrame()
    info.index = df.columns
    info['Тип данных'] = df.dtypes
    info['Уникальных'] = df.nunique()
    info['Количество значений'] = df.count()
    return info


@st.cache_data
def get_profile_report(df):
    from pandas_profiling import ProfileReport
    pr = ProfileReport(df)
    return pr


@st.cache_data
def create_histogram(df, column_name):
    fig = px.histogram(
        df,
        x=column_name,
        marginal="box",
        color='TARGET',
        title=f"Распределение {column_name}",
        template="plotly"
    )
    return fig


# @st.cache_data
# def create_correlation_matrix(df, features):
#     corr = df.corr().round(2)
#     fig1 = ff.create_annotated_heatmap(
#         z=corr.values,
#         x=list(corr.columns),
#         y=list(corr.index),
#         colorscale='ice',
#         annotation_text=corr.values
#     )
#     fig1.update_layout(height=800)
#
#     # Выбираем только корреляцию с целевым признаком 'cnt'
#     corr = corr['TARGET'].drop('TARGET')
#     corr = corr[abs(corr).argsort()]
#     fig2 = go.Figure()
#     fig2.add_trace(go.Bar(
#         x=corr.values,
#         y=corr.index,
#         orientation='h',
#         marker_color=list(range(len(corr.index)))
#     ))
#     fig2.update_layout(
#         title='Корреляция с TARGET',
#         height=700,
#         xaxis=dict(title='Признак'),  # Название оси x
#         yaxis=dict(title='Корреляция'),
#     )
#     return fig1, fig2


@st.cache_data
def get_simple_histograms(df, selected_category):
    fig = px.histogram(
        df,
        x=selected_category,
        color=selected_category,
        title=f'Распределение по {selected_category}'
    )
    return fig


@st.cache_data
def create_pairplot(df, selected_features, hue=None):
    sns.set_theme(style="whitegrid")
    pairplot_fig = sns.pairplot(
        df,
        vars=selected_features,
        hue=hue,
        palette='viridis',
        plot_kws={'alpha': 0.5, 's': 80, 'edgecolor': 'k'},
        height=3
    )
    plt.subplots_adjust(top=0.95)
    return pairplot_fig


@st.cache_data
def display_metrics(df):
    total_clients = len(df)
    avg_income = df['INCOME'].mean()
    high_pdn_rate = (df['PDN'] > 50).mean() * 100
    avg_term = df['TERM'].mean()
    avg_curr_rate = df['CURR_RATE_NVAL'].mean()

    col1, col2, col3 = st.columns(3)

    # Отображение метрик
    with col1:
        st.metric(label="Общее количество клиентов", value=f"{total_clients:,}")
        st.metric(label="Средний срок кредита", value=f"{avg_term:.2f} месяцев")
    with col2:
        st.metric(label="Средний доход клиента", value=f"{avg_income:,.2f} руб.")
    with col3:
        st.metric(label="Процент клиентов с высоким PDN", value=f"{high_pdn_rate:.2f}%")
        st.metric(label="Средний процент по кредиту", value=f"{avg_curr_rate:.2f}%")


def display_box_plot(df, numerical_features, categorical_features):
    c1, c2, c3 = st.columns(3)
    feature1 = c1.selectbox('Первый признак', numerical_features, key='box_feature1')
    feature2 = c2.selectbox('Второй признак', categorical_features, key='box_feature2', index=2)
    filter_by = c3.selectbox('Фильтровать по', [None, *categorical_features+numerical_features], key='box_filter_by', index=12)

    if feature2 == filter_by:
        filter_by = None

    fig = px.box(
        df,
        x=feature1, y=feature2,
        color=filter_by,
        title=f"Распределение {feature1} по разным {feature2}",
    )
    fig.update_layout(height=900)
    st.plotly_chart(fig, use_container_width=True)


def app(df, current_dir: Path):
    st.title("Анализ просрочек у клиентов банка")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
             ## Область применения
             Эта система анализа данных предназначена для банковского сектора с целью предсказания вероятности просрочек платежей по кредитам и кредитным картам. 
             Она помогает в повышении эффективности управления рисками, улучшении клиентского обслуживания и принятии более обоснованных решений о выдаче кредитов. 
             Система позволяет банкам:
             - Выявлять клиентов с высоким риском просрочки платежей и принимать соответствующие меры для снижения риска.
             - Оптимизировать процессы кредитного скоринга и улучшать качество кредитного портфеля.
             - Улучшать клиентский сервис путем предложения персонализированных финансовых продуктов и услуг.
             - Проводить анализ и мониторинг кредитных портфелей для своевременного выявления и реагирования на потенциальные проблемы.
        """)
    with col2:
        st.image(str(current_dir / "images" / "main.webp"), use_column_width='auto')

    st.markdown("""
        ## Ключевые параметры и характеристики данных
    """)
    tab1, tab2 = st.tabs(["Показать описание данных",  "Показать пример данных"])
    with tab1:
        c1, c2 = st.columns(2)
        c1.markdown("""
            ## Данные по кредитам клиента
            - **CLIENT_ID**: ИД клиента
            - **CREDIT_TYPE**: тип кредита
            - **CREDIT_PURCHASE**: цель кредита
            - **PRODUCT_CODE**: код кредитного продукта
            - **TERM**: срок кредита
            - **ORIG_AMOUNT**: сумма кредита
            - **CURR_RATE_NVAL**: процентная ставка
            - **VALUE_DT**: дата выдачи кредита
            - **OVERDUE_IND**: признак наличия просрочки по кредиту
    
            ## Данные по картам клиента
            - **CLIENT_ID**: ИД клиента
            - **CARD_TYPE**: тип карты
            - **PRODUCT_CODE**: код продукта
            - **CС_LIMIT_NVAL**: лимит по карте
            - **СС_GRACE_PERIOD**: грейс-период
            - **CURR_RATE**: процентная ставка
            - **OPEN_DT**: дата открытия карты
            - **СС_OVERDUE_IND**: признак наличия просрочки платежа
        """)
        c2.markdown("""
            ## Данные клиента
            - **CLIENT_ID**: ИД клиента
            - **AGE**: возраст
            - **REGION**: регион проживания
            - **GENDER**: пол
            - **ORGANIZATION**: организация
            - **INCOME**: доход
            - **MARITAL_STATUS**: семейное положение
            - **IP_FLAG**: является ИП?
            - **SME_FLAG**: является сотрудником организации?
            - **EMPLOYEE_FLAG**: является сотрудником?
            - **REFUGEE_FLAG**: является беженцем?
            - **PDN**: показатель долговой нагрузки в % (ПДН)
        """)

    with tab2:
        st.header("Пример данных")
        st.dataframe(df.head(50), height=600)

    categorical_features = df.select_dtypes(include=['category', 'object']).columns.tolist()
    numerical_features = df.select_dtypes(include=['int', 'int32', 'int64', 'float64']).columns.tolist()

    st.header("Предварительный анализ данных")
    st.dataframe(get_data_info(df), use_container_width=True)

    st.markdown("""
        ## Предварительный анализ
        
        **Возраст клиентов**
        * Средний возраст клиентов составляет около 42 лет. Возраст варьируется от 20 до 77 лет, что свидетельствует о широком возрастном диапазоне клиентов банка.
        
        **Доход клиентов**
        * Средний доход клиентов составляет около 75,075.30 рублей. Доходы сильно варьируются от 0 до 2,450,000 рублей, что указывает на значительные различия в финансовом положении клиентов.
        
        **Долговая нагрузка (PDN)**
        * Средний показатель долговой нагрузки составляет около 57%. Значения варьируются от 0.10% до 934.20%, что свидетельствует о различиях в финансовой устойчивости клиентов.
    """)

    st.header("Основные статистики для признаков")
    display_metrics(df)

    tab1, tab2 = st.tabs(["Числовые признаки", "Категориальные признаки"])
    with tab1:
        st.header("Рассчитаем основные статистики для числовых признаков")
        st.dataframe(df.describe(), use_container_width=True)

    with tab2:
        st.header("Рассчитаем основные статистики для категориальных признаков")
        st.dataframe(df.describe(include='category'), use_container_width=True)

    st.markdown("""
      #### Основные статистики:
    
      - **Средний возраст клиентов** составляет примерно 42 года, при этом минимальный и максимальный возраст - 20 и 77 лет соответственно.
      - **Средний доход клиентов** составляет около 75,075 рублей, варьируясь от 0 до 2,450,000 рублей.
      - **Средний показатель долговой нагрузки (PDN)** составляет 57%, с диапазоном от 0.10% до 934.20%.
      - **Средний срок кредита** составляет примерно 38 месяцев, с минимальным и максимальным сроком - 4 и 84 месяца соответственно.
      - **Средняя процентная ставка по кредиту** составляет около 14.37%, варьируясь от 1.00% до 34.90%.
      - **Процент клиентов с просрочками** составляет около 12.15%.
      - **Процент клиентов с высоким уровнем долговой нагрузки (PDN > 50%)** составляет 25.20%.
      - **Процент клиентов с доходом выше 100,000 рублей** составляет 22.45%.
      - **Процент клиентов с доходом ниже 20,000 рублей** составляет 5.35%.
    
      Эти основные статистики предоставляют общее представление о профиле клиентов и их финансовом состоянии, что помогает в дальнейших анализах и принятии решений.
    """)

    st.header("Визуализация данных")

    st.subheader("Визуализация числовых признаков")
    selected_feature = st.selectbox(
        "Выберите признак",
        numerical_features,
        key="create_histogram_selectbox1"
    )
    hist_fig = create_histogram(
        df,
        selected_feature
    )
    st.plotly_chart(hist_fig, use_container_width=True)

    st.markdown("""
        ## Гистограммы и ящики с усами
    
        Гистограмма — это вид диаграммы, представляющий распределение числовых данных. Она помогает оценить плотность вероятности распределения данных. Гистограммы идеально подходят для иллюстрации распределений признаков, таких как возраст клиентов или продолжительность контакта в секундах.
        
        Ящик с усами — это еще один тип графика для визуализации распределения числовых данных. Он показывает медиану, первый и третий квартили, а также "усы", которые простираются до крайних точек данных, не считая выбросов. Ящики с усами особенно полезны для сравнения распределений между несколькими группами и выявления выбросов.
    """)
    display_box_plot(
        df,
        numerical_features,
        categorical_features
    )

    tab1, tab2 = st.tabs(["Простые графики", "Показать отчет о данных"])
    with tab1:
        st.subheader("Распределение клиентов")
        st.subheader("Столбчатые диаграммы для категориальных признаков")
        selected_category_simple_histograms = st.selectbox(
            'Категория для анализа',
            categorical_features,
            key='category_get_simple_histograms'
        )
        st.plotly_chart(get_simple_histograms(df, selected_category_simple_histograms), use_container_width=True)
        st.subheader("Распределение числовых признаков c группировкой по отклику")
        selected_feature = st.selectbox(
            "Выберите признак",
            numerical_features,
            key="create_histogram_selectbox2"
        )
        hist_fig = create_histogram(
            df,
            selected_feature
        )
        st.plotly_chart(hist_fig, use_container_width=True)

    with tab2:
        if st.button("Сформировать отчёт", use_container_width=True, type='primary'):
            st_profile_report(get_profile_report(df))

    # st.header("Корреляционный анализ")
    # st.markdown("""
    #        Матрица корреляции позволяет определить связи между признаками. Значения в матрице колеблются от -1 до 1, где:
    #
    #        - 1 означает положительную линейную корреляцию,
    #        - -1 означает отрицательную линейную корреляцию,
    #        - 0 означает отсутствие линейной корреляции.
    #    """)
    # fig1, fig2 = create_correlation_matrix(df, numerical_features)
    # st.plotly_chart(fig1, use_container_width=True)
    #
    # markdown_col1, markdown_col2 = st.columns(2)
    # markdown_col1.markdown("""
    #        Корреляционная матрица представляет связь между различными числовыми параметрами. В данном случае:
    #    """)
    # markdown_col2.plotly_chart(fig2, use_container_width=True)


    st.markdown(
        """
        ## Точечные диаграммы для пар числовых признаков
        """
    )
    selected_features = st.multiselect(
        'Выберите признаки',
        numerical_features,
        default=numerical_features[:5],
        key='pairplot_vars'
    )

    # Опциональный выбор категориальной переменной для цветовой дифференциации
    hue_option = st.selectbox(
        'Выберите признак для цветового кодирования (hue)',
        ['None'] + categorical_features + numerical_features,
        index=12,
        key='pairplot_hue'
    )
    if hue_option == 'None':
        hue_option = None
    if selected_features:
        st.pyplot(create_pairplot(df, selected_features, hue=hue_option))
    else:
        st.error("Пожалуйста, выберите хотя бы один признак для создания pairplot.")

